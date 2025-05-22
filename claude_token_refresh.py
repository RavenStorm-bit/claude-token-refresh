#!/usr/bin/env python3
"""
Claude OAuth Token Auto-Refresh Tool

A Python script that automatically finds and updates Claude CLI OAuth tokens.
Supports both .claude/.credentials.json and .claude.json configuration files.

Author: Claude Code Assistant
License: MIT
"""

import json
import os
import sys
import time
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple

# Claude OAuth configuration
CLAUDE_TOKEN_URL = "https://console.anthropic.com/v1/oauth/token"
CLAUDE_CLIENT_ID = "9d1c250a-e61b-44d9-88ed-5944d1962f5e"

class ClaudeTokenRefresher:
    def __init__(self, base_dir: str = None):
        """
        Initialize the token refresher.
        
        Args:
            base_dir: Base directory to search for Claude config files. 
                     Defaults to current directory.
        """
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
        self.config_file = None
        self.config_data = None
        
    def find_claude_config(self) -> Optional[Path]:
        """
        Find Claude configuration file in the following order:
        1. .claude/.credentials.json
        2. .claude.json
        3. ~/.claude/.credentials.json
        4. ~/.claude.json
        
        Returns:
            Path to the configuration file, or None if not found
        """
        search_paths = [
            # Local directory
            self.base_dir / ".claude" / ".credentials.json",
            self.base_dir / ".claude.json",
            # Home directory
            Path.home() / ".claude" / ".credentials.json", 
            Path.home() / ".claude.json",
        ]
        
        for path in search_paths:
            if path.exists() and path.is_file():
                print(f"✅ Found Claude config: {path}")
                return path
                
        return None
    
    def load_config(self) -> bool:
        """
        Load Claude configuration file.
        
        Returns:
            True if config loaded successfully, False otherwise
        """
        self.config_file = self.find_claude_config()
        if not self.config_file:
            print("❌ No Claude configuration file found!")
            print("   Searched for:")
            print("   - .claude/.credentials.json")
            print("   - .claude.json")
            print("   - ~/.claude/.credentials.json")
            print("   - ~/.claude.json")
            return False
            
        try:
            with open(self.config_file, 'r') as f:
                self.config_data = json.load(f)
            return True
        except Exception as e:
            print(f"❌ Failed to load config file: {e}")
            return False
    
    def get_oauth_config(self) -> Optional[Dict]:
        """
        Extract OAuth configuration from the config file.
        
        Returns:
            OAuth configuration dict or None if not found
        """
        if not self.config_data:
            return None
            
        # Check different possible locations for OAuth data
        oauth_keys = ['claudeAiOauth', 'oauthAccount', 'oauth']
        
        for key in oauth_keys:
            if key in self.config_data:
                oauth_config = self.config_data[key]
                if 'refreshToken' in oauth_config:
                    return oauth_config
                    
        return None
    
    def is_token_expired(self, expires_at: int) -> bool:
        """
        Check if token is expired.
        
        Args:
            expires_at: Token expiration timestamp in milliseconds
            
        Returns:
            True if token is expired, False otherwise
        """
        current_time = int(time.time() * 1000)
        return current_time > expires_at
    
    def refresh_token(self, refresh_token: str) -> Optional[Dict]:
        """
        Refresh OAuth token using the refresh token.
        
        Args:
            refresh_token: The refresh token
            
        Returns:
            Token response dict or None if failed
        """
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": CLAUDE_CLIENT_ID
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        try:
            print("🔄 Refreshing OAuth token...")
            response = requests.post(
                CLAUDE_TOKEN_URL,
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Token refresh failed: HTTP {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"   Error: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Request failed: {str(e)}")
            return None
    
    def update_config(self, new_token_data: Dict) -> bool:
        """
        Update the configuration file with new token data.
        
        Args:
            new_token_data: New token data from refresh response
            
        Returns:
            True if update successful, False otherwise
        """
        try:
            # Find the OAuth config key in the original config
            oauth_key = None
            for key in ['claudeAiOauth', 'oauthAccount', 'oauth']:
                if key in self.config_data:
                    oauth_key = key
                    break
            
            if not oauth_key:
                # Default to claudeAiOauth if no existing key found
                oauth_key = 'claudeAiOauth'
                self.config_data[oauth_key] = {}
            
            # Calculate expiration timestamp
            expires_at = int(time.time() * 1000) + (new_token_data.get('expires_in', 3600) * 1000)
            
            # Update OAuth configuration
            oauth_config = self.config_data[oauth_key]
            oauth_config.update({
                'accessToken': new_token_data['access_token'],
                'refreshToken': new_token_data.get('refresh_token', oauth_config.get('refreshToken')),
                'expiresAt': expires_at,
                'scopes': new_token_data.get('scope', '').split() if new_token_data.get('scope') else oauth_config.get('scopes', [])
            })
            
            # Add organization and account info if present
            if 'organization' in new_token_data:
                oauth_config['organizationUuid'] = new_token_data['organization']['uuid']
                oauth_config['organizationName'] = new_token_data['organization']['name']
            
            if 'account' in new_token_data:
                oauth_config['accountUuid'] = new_token_data['account']['uuid']
                oauth_config['emailAddress'] = new_token_data['account']['email_address']
            
            # Create backup
            backup_file = self.config_file.with_suffix('.json.backup')
            with open(backup_file, 'w') as f:
                json.dump(self.config_data, f, indent=2)
            print(f"💾 Backup created: {backup_file}")
            
            # Write updated config
            with open(self.config_file, 'w') as f:
                json.dump(self.config_data, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to update config: {e}")
            return False
    
    def run(self, force: bool = False) -> bool:
        """
        Run the token refresh process.
        
        Args:
            force: Force refresh even if token is not expired
            
        Returns:
            True if successful, False otherwise
        """
        print("🎯 Claude OAuth Token Auto-Refresh Tool")
        print("=" * 50)
        
        # Load configuration
        if not self.load_config():
            return False
        
        # Get OAuth configuration
        oauth_config = self.get_oauth_config()
        if not oauth_config:
            print("❌ No OAuth configuration found in config file!")
            return False
        
        # Check token expiration
        expires_at = oauth_config.get('expiresAt', 0)
        expires_datetime = datetime.fromtimestamp(expires_at / 1000) if expires_at > 0 else None
        is_expired = self.is_token_expired(expires_at) if expires_at > 0 else True
        
        print(f"⏰ Current time: {datetime.now()}")
        if expires_datetime:
            print(f"⏰ Token expires: {expires_datetime}")
        print(f"📊 Token expired: {'Yes' if is_expired else 'No'}")
        
        if not is_expired and not force:
            print("✅ Token is still valid. Use --force to refresh anyway.")
            return True
        
        # Refresh token
        refresh_token = oauth_config.get('refreshToken')
        if not refresh_token:
            print("❌ No refresh token found in configuration!")
            return False
        
        new_token_data = self.refresh_token(refresh_token)
        if not new_token_data:
            return False
        
        # Update configuration
        if self.update_config(new_token_data):
            new_expires = datetime.fromtimestamp((int(time.time()) + new_token_data.get('expires_in', 3600)))
            print("✅ Token refresh successful!")
            print(f"⏰ New token expires: {new_expires}")
            print(f"📁 Config updated: {self.config_file}")
            return True
        else:
            return False

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Claude OAuth Token Auto-Refresh Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Auto-refresh if token is expired
  %(prog)s --force            # Force refresh even if not expired
  %(prog)s --dir /path/to/project  # Search specific directory
        """
    )
    
    parser.add_argument(
        '--force', 
        action='store_true',
        help='Force refresh even if token is not expired'
    )
    
    parser.add_argument(
        '--dir',
        type=str,
        help='Base directory to search for Claude config files'
    )
    
    args = parser.parse_args()
    
    # Initialize refresher
    refresher = ClaudeTokenRefresher(base_dir=args.dir)
    
    # Run refresh process
    success = refresher.run(force=args.force)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()