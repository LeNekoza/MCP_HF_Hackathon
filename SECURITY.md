# Security Configuration Guide

## Database Credentials Security

This project implements secure handling of database credentials to prevent accidental exposure of sensitive information.

## Setup Instructions

### Option 1: Environment Variables (Recommended for Production)

1. Copy the template file:
   ```bash
   copy .env.template .env
   ```

2. Edit `.env` and fill in your actual Neon database credentials:
   ```env
   NEON_HOST=your-actual-host.aws.neon.tech
   NEON_DATABASE=your-database-name
   NEON_USER=your-username
   NEON_PASSWORD=your-actual-password
   NEON_PORT=5432
   NEON_SSLMODE=require
   ```

3. Load environment variables before running your application:
   ```bash
   # PowerShell
   Get-Content .env | ForEach-Object {
       $name, $value = $_.split('=')
       Set-Item -Path "env:$name" -Value $value
   }
   ```

### Option 2: Configuration File (Development Only)

1. Copy the template:
   ```bash
   copy neon_config.template.json neon_config.json
   ```

2. Edit `neon_config.json` with your actual credentials
   ⚠️ **Warning**: This file is now ignored by git, but avoid this method in production

## Using Secure Configuration

Use the provided `secure_config.py` module in your code:

```python
from secure_config import load_database_config, get_connection_string

# Load configuration
config = load_database_config()

# Get connection string
conn_string = get_connection_string()
```

## Files and Security

### Tracked Files (Safe to Commit)
- `.env.template` - Template without sensitive data
- `neon_config.template.json` - Template without sensitive data
- `secure_config.py` - Configuration loader utility
- `SECURITY.md` - This documentation

### Ignored Files (Never Committed)
- `.env` - Contains actual credentials
- `neon_config.json` - Contains actual credentials
- Any file with actual passwords or API keys

## Security Best Practices

1. **Never commit credentials** to version control
2. **Use environment variables** in production
3. **Rotate credentials** regularly
4. **Use different credentials** for different environments
5. **Monitor access logs** in your Neon console

## Emergency Response

If credentials are accidentally committed:

1. **Immediately rotate** the exposed credentials in Neon console
2. **Remove sensitive commits** from git history:
   ```bash
   git filter-branch --force --index-filter \
   'git rm --cached --ignore-unmatch neon_config.json' \
   --prune-empty --tag-name-filter cat -- --all
   ```
3. **Force push** the cleaned history
4. **Update all team members** to pull the cleaned repository

## Verification

Test your configuration:
```bash
python secure_config.py
```

This should display your configuration with the password hidden.
