# sync_repos.py

This project provides a Python script that mirrors GitHub repositories to a local GitLab server. It checks whether the target project exists on GitLab, updates it if necessary, or creates it otherwise.

## Features

- Mirror GitHub repositories to GitLab via HTTPS
- Automatically create or update projects on GitLab
- Support for single-repo and batch modes
- Configurable via `.env` file and command-line options
- Optional removal of temporary mirror repositories after push (`--cleanup`)

## Prerequisites

### macOS
- **Operating System:** macOS (tested and optimized)
- **Python:** Version 3.7 or higher (installed via Homebrew or python.org)
- **Git:** Installed via Homebrew (`brew install git`)
- **GitLab:** Access to a GitLab server with a personal access token

### Windows
- **Operating System:** Windows 10 or later
- **Python:** Download and install from https://www.python.org/downloads/ (be sure to check "Add Python to PATH")
- **Git:** Install Git for Windows from https://git-scm.com/download/win (Git Bash recommended)
- **GitLab:** Access to a GitLab server with a personal access token

## Installation## Installation

1. **Install Homebrew and Git** (if not already installed):
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   brew install git
   ```

2. **Install Python packages**:
   ```bash
   pip3 install python-gitlab python-dotenv
   ```

3. **Clone this repository and change into its directory**:
   ```bash
   git clone https://github.com/username/sync_repos.git
   cd sync_repos
   ```

## Configuration

Create a `.env` file in the project root with the following entries:

```dotenv
# Base URL of your GitLab server
GITLAB_URL=https://gitlab.example.com

# Personal access token with API scope
GITLAB_TOKEN=yourGitLabAccessToken

# (Optional) GitLab group or namespace for new projects
GITLAB_GROUP=my-group/subgroup

# (Optional) GitHub token for private repositories
GITHUB_TOKEN=yourGitHubAccessToken
``` 

## Command-Line Options

| Option                  | Description                                                                       |
|-------------------------|-----------------------------------------------------------------------------------|
| `--repo URL`            | Synchronize only the specified GitHub repository                                  |
| `--repos-file <FILE>`   | Path to a text file listing GitHub URLs (one per line). Default: `repos.txt`      |
| `--gitlab-url <URL>`    | Override the `GITLAB_URL` from `.env`                                             |
| `--cleanup`             | Remove local mirror repositories under `/tmp` after a successful push              |

## Usage

### Batch Mode

1. Create a file named `repos.txt`, listing each GitHub repository URL on a separate line:
   ```text
   https://github.com/owner1/repo1.git
   https://github.com/owner2/repo2.git
   ```

2. Run the script:
   ```bash
   python3 sync_repos.py --repos-file repos.txt --cleanup
   ```

### Single-Repo Mode

```bash
python3 sync_repos.py --repo https://github.com/owner/repo.git
``` 

With cleanup and custom GitLab URL:
```bash
python3 sync_repos.py \
  --repo https://github.com/owner/repo.git \
  --gitlab-url https://gitlab.another-server.com --cleanup
```

## Logging and Error Handling

- Logs are printed to stdout in the format `YYYY-MM-DD HH:MM:SS [LEVEL] Message`.
- Errors during cloning, fetching, or pushing are logged as `ERROR`.

## Automation

You can schedule this script to run automatically using Cron or a macOS LaunchAgent. Example Cron entry to run daily at 2:00 AM:

```cron
0 2 * * * /usr/local/bin/python3 /path/to/sync_repos.py --cleanup >> /var/log/sync_repos.log 2>&1
```

## Troubleshooting

- **Missing environment variable**: Verify the `.env` file for typos.
- **GitLab access errors**: Ensure your token has API permissions.
- **Network errors during clone**: Check internet connectivity and firewall settings.

---

## License

The MIT License (MIT)

Copyright (c) 2025 Marlon

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

