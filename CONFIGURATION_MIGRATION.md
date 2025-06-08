# Configuration Migration Guide

This document explains the migration from JSON configuration files to environment variables.

## What Changed

The project has been migrated from using JSON configuration files in the `config/` directory to using environment variables stored in a `.env` file. This provides better security and easier deployment.

### Removed Files
- `config/app_config.json`
- `config/nebius_config.json` 
- `config/neon_config.json`
- `config/neon_config.template.json` (kept as reference)

### New Configuration Method
All configuration is now handled through environment variables defined in a `.env` file in the project root.

## Environment Variables

### Database Configuration (Neon)
```bash
NEON_HOST=your-neon-host.aws.neon.tech
NEON_DATABASE=your-database-name
NEON_USER=your-username
NEON_PASSWORD=your-password
NEON_PORT=5432
NEON_SSLMODE=require

# Database Upload Settings
CLEAR_EXISTING_DATA=true
BATCH_SIZE=1000
LOG_LEVEL=INFO
```

### Nebius API Configuration
```bash
NEBIUS_API_KEY=your-nebius-api-key-here
NEBIUS_MODEL=meta-llama/Llama-3.3-70B-Instruct
NEBIUS_MAX_TOKENS=2048
NEBIUS_TEMPERATURE=0.7
NEBIUS_TOP_P=0.9
NEBIUS_TIMEOUT=30
```

### Application Configuration
```bash
SERVER_NAME=127.0.0.1
SERVER_PORT=8060
SHARE=false
DEBUG=true
DEFAULT_MODEL=gpt-3.5-turbo
MAX_TOKENS=1000
TEMPERATURE=0.7
APP_TITLE=MCP HF Hackathon
APP_DESCRIPTION=Model Context Protocol Integration with Hugging Face
```

### Model Configuration
```bash
AVAILABLE_MODELS=gpt-3.5-turbo,gpt-4,claude-3-sonnet,llama-2-7b,mistral-7b,nebius-llama-3.3-70b
HF_API_URL=https://api-inference.huggingface.co/models/
HF_CACHE_DIR=./data/models
NEBIUS_MODEL_NAME=meta-llama/Llama-3.3-70B-Instruct
NEBIUS_API_URL=https://api.studio.nebius.ai/v1
NEBIUS_ENABLED=true
```

### MCP Configuration
```bash
MCP_ENABLED=true
MCP_VERSION=1.0
MCP_PROTOCOL_FEATURES=context_management,model_switching,response_streaming
```

## Updated Files

### Core Configuration Files
- `src/utils/config.py` - Updated to read from environment variables
- `config/secure_config.py` - Updated to only use environment variables
- `src/utils/env_loader.py` - New utility to load .env file

### Model Files
- `src/models/nebius_model.py` - Updated to use environment variables
- `src/core/infer.py` - Updated to use environment variables

### Application Files
- `app.py` - Updated to load .env file
- `scripts/setup/setup.py` - Updated to validate environment configuration
- `scripts/debug/status.py` - Updated to check environment variables
- `scripts/setup/create_schema_only.py` - Updated to use environment variables
- `examples/nebius_usage.py` - Updated documentation

## Migration Benefits

1. **Security**: Sensitive data like API keys and passwords are no longer stored in version control
2. **Flexibility**: Easy to override configuration for different environments
3. **Deployment**: Simpler deployment with environment-specific configurations
4. **Maintenance**: Single source of truth for configuration

## Backwards Compatibility

The migration maintains backwards compatibility by:
- Providing default values for all configuration options
- Graceful fallback when environment variables are not set
- Clear error messages when required variables are missing

## Getting Started

1. Copy the provided `.env` file or create your own based on the template above
2. Update the values with your actual configuration
3. Run the application - it will automatically load the environment variables

## Troubleshooting

If you encounter issues:

1. **Check .env file exists**: The file should be in the project root directory
2. **Verify variable names**: Ensure environment variable names match exactly
3. **Check for typos**: Environment variables are case-sensitive
4. **Review logs**: The application will log warnings for missing configuration

For debugging, use the status script:
```bash
python scripts/debug/status.py
```

This will show which environment variables are set and their values (with sensitive data masked). 