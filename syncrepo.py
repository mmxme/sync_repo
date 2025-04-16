#!/usr/bin/env python3
"""
sync_repos.py

Spiegelt GitHub-Repositories zu einem lokalen GitLab-Server und hält sie aktuell.
Einstellungen in .env:
    GITLAB_URL
    GITLAB_TOKEN
    GITLAB_GROUP (optional)
    GITHUB_TOKEN (optional)

Eine Liste der zu synchronisierenden GitHub-URLs in `repos.txt`.
Optionen:
    --cleanup         : Entfernt lokale Mirror-Repos nach erfolgreichem Push.
    --repos-file FILE : Pfad zur Datei mit GitHub-URLs (eine pro Zeile). Standard: repos.txt
    --repo URL        : Synchronisiert nur das angegebene GitHub-Repository.
    --gitlab-url URL  : Überschreibt die GitLab-Ziel-URL aus der .env.
"""

import os
import subprocess
import shutil
import logging
import argparse
from urllib.parse import urlparse

import gitlab
from dotenv import load_dotenv

def load_config():
    load_dotenv()
    config = {
        "gitlab_url": os.getenv("GITLAB_URL"),
        "gitlab_token": os.getenv("GITLAB_TOKEN"),
        "gitlab_group": os.getenv("GITLAB_GROUP", ""),
        "github_token": os.getenv("GITHUB_TOKEN", ""),
    }
    missing = [k for k in ("gitlab_url", "gitlab_token") if not config[k]]
    if missing:
        raise RuntimeError(f"Fehlende Umgebungsvariablen: {', '.join(missing)}")
    return config


def init_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

def init_gitlab(gitlab_url, gitlab_token):
    gl = gitlab.Gitlab(url=gitlab_url, private_token=gitlab_token)
    gl.auth()
    return gl

def sync_repository(gl, config, github_url, cleanup=False):
    parsed = urlparse(github_url)
    path_parts = parsed.path.strip("/").split("/")
    if len(path_parts) < 2:
        logging.error("Ungültige GitHub-URL: %s", github_url)
        return

    owner, name = path_parts[:2]
    project_path = f"{config['gitlab_group']}/{name}" if config["gitlab_group"] else name

    # Prüfen bzw. Erstellen in GitLab
    try:
        project = gl.projects.get(project_path)
        logging.info("Projekt %s existiert. Aktualisiere...", project_path)
    except gitlab.exceptions.GitlabGetError:
        logging.info("Projekt %s existiert nicht. Erstelle...", project_path)
        data = {"name": name, "path": name}
        if config["gitlab_group"]:
            group = gl.groups.get(config["gitlab_group"])
            data["namespace_id"] = group.id
        project = gl.projects.create(data)
        logging.info("Projekt erstellt: %s", project_path)

    # Lokales Bare-Repo-Verzeichnis
    tmp_dir = os.path.join("/tmp", f"{name}.git")
    # Klonen oder Fetch
    if not os.path.isdir(tmp_dir):
        subprocess.run(["git", "clone", "--mirror", github_url, tmp_dir], check=True)
        logging.info("Klonen abgeschlossen: %s", github_url)
    else:
        subprocess.run(["git", "--git-dir", tmp_dir, "fetch", "--all"], check=True)
        logging.info("Fetch abgeschlossen: %s", github_url)

    # Push zu GitLab
    gitlab_url = project.http_url_to_repo
    subprocess.run(["git", "--git-dir", tmp_dir, "push", "--mirror", gitlab_url], check=True)
    logging.info("Push abgeschlossen nach: %s", gitlab_url)

    # Aufräumen
    if cleanup:
        try:
            shutil.rmtree(tmp_dir)
            logging.info("Aufgeräumt: entfernt %s", tmp_dir)
        except Exception as e:
            logging.warning("Fehler beim Entfernen von %s: %s", tmp_dir, e)


def main():
    init_logging()
    parser = argparse.ArgumentParser(
        description="Spiegelt GitHub-Repos nach GitLab und hält sie aktuell."
    )
    parser.add_argument("--cleanup", action="store_true",
                        help="Entfernt lokale Mirror-Repos nach erfolgreichem Push.")
    parser.add_argument("--repos-file", default="repos.txt",
                        help="Pfad zur Datei mit GitHub-URLs (eine pro Zeile).")
    parser.add_argument("--repo", help="Synchronisiert nur dieses eine GitHub-Repository.")
    parser.add_argument("--gitlab-url", help="Überschreibt die GitLab-Ziel-URL aus der .env.")
    args = parser.parse_args()

    config = load_config()
    # Override GitLab-URL aus CLI
    if args.gitlab_url:
        config['gitlab_url'] = args.gitlab_url

    gl = init_gitlab(config["gitlab_url"], config["gitlab_token"])

    # Bestimmen, welche Repos synchronisiert werden:
    repo_list = []
    if args.repo:
        repo_list = [args.repo]
    else:
        if not os.path.isfile(args.repos_file):
            logging.error("Datei %s nicht gefunden.", args.repos_file)
            return
        with open(args.repos_file, "r") as f:
            repo_list = [line.strip() for line in f if line.strip()]

    for url in repo_list:
        try:
            sync_repository(gl, config, url, cleanup=args.cleanup)
        except Exception as e:
            logging.error("Fehler bei %s: %s", url, e)

if __name__ == "__main__":
    main()
