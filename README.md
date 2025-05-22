# Claude OAuth Token Auto-Refresh Tool

🔄 Automatically refresh expired Claude CLI OAuth tokens without manual re-authentication.

[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🚀 Features

- **Auto-Discovery**: Automatically finds Claude configuration files in multiple locations
- **Smart Refresh**: Only refreshes tokens when expired (unless forced)
- **Safe Updates**: Creates backups before modifying configuration files
- **Multiple Config Support**: Works with both `.claude/.credentials.json` and `.claude.json` formats
- **Detailed Logging**: Provides clear feedback about the refresh process
- **Command Line Interface**: Easy to use with various options

## 📋 Requirements

- Python 3.6 or higher
- `requests` library
- Valid Claude CLI OAuth configuration with refresh token

## 🛠 Installation

1. **Download the script:**
   ```bash
   curl -O https://raw.githubusercontent.com/YOUR_USERNAME/claude-token-refresh/main/claude_token_refresh.py
   chmod +x claude_token_refresh.py
   ```

2. **Install dependencies:**
   ```bash
   pip install requests
   ```

## 📁 Configuration File Discovery

The tool searches for Claude configuration files in the following order:

1. `.claude/.credentials.json` (current directory)
2. `.claude.json` (current directory)
3. `~/.claude/.credentials.json` (home directory)
4. `~/.claude.json` (home directory)

### Supported Configuration Formats

The tool works with various OAuth configuration formats:

```json
{
  "claudeAiOauth": {
    "accessToken": "sk-ant-oat01-...",
    "refreshToken": "sk-ant-ort01-...",
    "expiresAt": 1747909518727,
    "scopes": ["user:inference", "user:profile"]
  }
}
```

```json
{
  "oauthAccount": {
    "accessToken": "sk-ant-oat01-...",
    "refreshToken": "sk-ant-ort01-...",
    "expiresAt": 1747909518727
  }
}
```

## 🎯 Usage

### Basic Usage

```bash
# Auto-refresh if token is expired
python3 claude_token_refresh.py

# Force refresh even if token is not expired
python3 claude_token_refresh.py --force

# Search in a specific directory
python3 claude_token_refresh.py --dir /path/to/your/project
```

### Command Line Options

```
usage: claude_token_refresh.py [-h] [--force] [--dir DIR]

Claude OAuth Token Auto-Refresh Tool

options:
  -h, --help     show this help message and exit
  --force        Force refresh even if token is not expired
  --dir DIR      Base directory to search for Claude config files

Examples:
  claude_token_refresh.py                    # Auto-refresh if token is expired
  claude_token_refresh.py --force            # Force refresh even if not expired
  claude_token_refresh.py --dir /path/to/project  # Search specific directory
```

## 📊 Example Output

```
🎯 Claude OAuth Token Auto-Refresh Tool
==================================================
✅ Found Claude config: /home/user/.claude/.credentials.json
⏰ Current time: 2025-05-22 10:25:18.435019
⏰ Token expires: 2025-05-22 18:25:18
📊 Token expired: No
✅ Token is still valid. Use --force to refresh anyway.
```

```
🎯 Claude OAuth Token Auto-Refresh Tool
==================================================
✅ Found Claude config: /home/user/.claude/.credentials.json
⏰ Current time: 2025-05-22 19:30:00.000000
⏰ Token expires: 2025-05-22 18:25:18
📊 Token expired: Yes
🔄 Refreshing OAuth token...
💾 Backup created: /home/user/.claude/.credentials.json.backup
✅ Token refresh successful!
⏰ New token expires: 2025-05-23 03:30:00
📁 Config updated: /home/user/.claude/.credentials.json
```

## 🔧 How It Works

1. **Discovery**: Searches for Claude configuration files in standard locations
2. **Validation**: Checks if the current OAuth token is expired
3. **Refresh**: Makes an API call to Claude's OAuth token endpoint
4. **Backup**: Creates a backup of the original configuration file
5. **Update**: Updates the configuration with new tokens and expiration time

### API Endpoint Details

The tool uses Claude's official OAuth refresh endpoint:

```
POST https://console.anthropic.com/v1/oauth/token
Content-Type: application/json

{
  "grant_type": "refresh_token",
  "refresh_token": "sk-ant-ort01-...",
  "client_id": "9d1c250a-e61b-44d9-88ed-5944d1962f5e"
}
```

## 🛡️ Security Features

- **Backup Creation**: Always creates a backup before modifying configuration files
- **Error Handling**: Comprehensive error handling with clear error messages
- **Token Validation**: Only refreshes when necessary to minimize API calls
- **Local Processing**: All token processing happens locally on your machine

## 🚨 Troubleshooting

### Common Issues

1. **"No Claude configuration file found!"**
   - Ensure you have Claude CLI installed and authenticated
   - Check that configuration files exist in expected locations
   - Use `--dir` to specify a custom search directory

2. **"No OAuth configuration found in config file!"**
   - Make sure your Claude CLI is set up with OAuth (not API key)
   - Re-authenticate with `claude auth` if necessary

3. **"Token refresh failed: HTTP 401"**
   - Your refresh token may be expired or invalid
   - Re-authenticate with `claude auth` to get new tokens

4. **"No refresh token found in configuration!"**
   - Your configuration may be using API key authentication instead of OAuth
   - Switch to OAuth authentication with `claude auth`

## 🔄 Integration Examples

### Cron Job (Linux/macOS)

Add to your crontab to automatically refresh tokens:

```bash
# Refresh Claude tokens every 6 hours
0 */6 * * * /usr/bin/python3 /path/to/claude_token_refresh.py
```

### GitHub Actions

```yaml
- name: Refresh Claude Tokens
  run: |
    python3 claude_token_refresh.py --force
  env:
    PYTHONPATH: ${{ github.workspace }}
```

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit
python3 /path/to/claude_token_refresh.py
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup

```bash
git clone https://github.com/YOUR_USERNAME/claude-token-refresh.git
cd claude-token-refresh
pip install -r requirements.txt
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is not officially affiliated with Anthropic. It uses publicly documented OAuth endpoints and follows the same token refresh process as the official Claude CLI.

## 🙋‍♂️ Support

If you encounter any issues or have questions:

1. Check the [Troubleshooting](#-troubleshooting) section
2. Search existing [Issues](https://github.com/YOUR_USERNAME/claude-token-refresh/issues)
3. Create a new issue with detailed information about your problem

## 🔗 Related Links

- [Claude CLI Documentation](https://docs.anthropic.com/en/docs/agents-and-tools/claude-code)
- [Anthropic Console](https://console.anthropic.com/)
- [OAuth 2.0 RFC](https://tools.ietf.org/html/rfc6749)

---

**Made with ❤️ for the Claude CLI community**