---
title: Hospital AI Helper Aid
emoji: 🏥
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 5.33.0
app_file: app.py
pinned: false
license: mit
---

# MCP HF Hackathon - Hospital AI Helper Aid

## 🚀 Model Context Protocol Integration with Hugging Face

This project is part of the MCP (Model Context Protocol) Hugging Face Hackathon, showcasing innovative AI model interactions through a modern Gradio-based web interface.

## 🎯 Project Overview

Our application leverages the Model Context Protocol to create seamless interactions between different AI models from Hugging Face, providing users with an intuitive interface for model experimentation and comparison.

## ✨ Features

- **Multi-Model Support**: Integration with various Hugging Face models
- **Interactive Web Interface**: Built with Gradio for ease of use
- **Model Context Protocol**: Advanced context management capabilities
- **Real-time Processing**: Streaming responses and live updates
- **Configurable Settings**: Customizable model parameters
- **Comprehensive Logging**: Detailed application monitoring

## 🛠️ Tech Stack

- **Frontend**: Gradio (Python-based web interface)
- **Backend**: Python with MCP integration
- **AI Models**: Hugging Face Transformers
- **Configuration**: JSON-based configuration management
- **Testing**: Pytest framework
- **Logging**: Python logging with file and console output

## 📦 Installation

1. **Clone the repository**:

   ```powershell
   git clone <repository-url>
   cd MCP_HF_Hackathon
   ```

2. **Create virtual environment**:

   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. **Install dependencies**:

   ```powershell
   pip install -r requirements.txt
   ```

4. **Set up configuration**:

   - Review and modify `config/app_config.json` as needed
   - **Set up database credentials** (see Database Setup section below)
   - Set environment variables if required (see Configuration section)

5. **Configure database access**:

   ```powershell
   # Option 1: Environment variables (recommended)
   Copy-Item .env.template .env
   # Edit .env with your Neon database credentials

   # Option 2: Configuration file (development)
   Copy-Item neon_config.template.json neon_config.json
   # Edit neon_config.json with your credentials
   ```

## 🚀 Quick Start

1. **Run the application**:

   ```powershell
   python app.py
   ```

2. **Open your browser** and navigate to:

   ```
   http://localhost:7860
   ```

3. **Start interacting** with the AI models through the web interface!

## ⚙️ Configuration

The application can be configured through:

### Configuration File

Edit `config/app_config.json` to customize:

- Server settings (host, port)
- Default model selection
- Model parameters (temperature, max tokens)
- MCP protocol settings

### Environment Variables

- `PORT`: Override server port
- `DEBUG`: Enable/disable debug mode
- `SHARE`: Enable/disable Gradio sharing

## 🏗️ Project Structure

```
MCP_HF_Hackathon/
├── app.py                        # Main application entry point
├── requirements.txt              # Python dependencies
├── README.md                     # This file
├── SECURITY.md                   # Database security guidelines
├── IMPORT_SUCCESS_REPORT.md      # Hospital data import documentation
├── secure_config.py              # Secure database configuration loader
├── .env.template                 # Environment variables template
├── neon_config.template.json     # Database config template
├── create_schema_only.py         # Database schema creation utility
├── generate_sql.py               # SQL generation utility
├── config/                       # Configuration files
│   └── app_config.json          # Main app configuration
├── hospital_data_final/          # Hospital CSV data (8,010+ records)
│   ├── users.csv                # User accounts (3,210 rows)
│   ├── patient_records.csv      # Patient records (3,000 rows)
│   ├── occupancy.csv            # Room occupancy (1,100 rows)
│   ├── tools.csv                # Medical tools (500 rows)
│   ├── rooms.csv                # Hospital rooms (150 rows)
│   ├── hospital_inventory.csv   # Inventory (100 rows)
│   └── storage_rooms.csv        # Storage rooms (50 rows)
├── src/                          # Source code
│   ├── components/              # UI components
│   │   └── interface.py         # Main Gradio interface
│   ├── models/                  # Model handlers
│   │   └── mcp_handler.py       # MCP protocol handler
│   ├── utils/                   # Utility functions
│   │   ├── config.py            # Configuration utilities
│   │   ├── helpers.py           # Helper functions
│   │   └── logger.py            # Logging setup
│   └── api/                     # API endpoints (future)
├── static/                       # Static assets
│   ├── css/                     # Custom stylesheets
│   ├── js/                      # JavaScript files
│   └── images/                  # Image assets
├── templates/                    # HTML templates (if needed)
├── tests/                        # Test files
│   ├── unit/                    # Unit tests
│   └── integration/             # Integration tests
├── data/                         # Data storage
├── docs/                         # Documentation
└── logs/                         # Application logs (created at runtime)
```

## 🧪 Testing

Run the test suite:

```powershell
# Run all tests
pytest

# Run specific test categories
pytest tests/unit/
pytest tests/integration/

# Run with coverage
pytest --cov=src tests/
```

## 🔧 Development

### Adding New Models

1. Update the model list in `config/app_config.json`
2. Modify the `MCPHandler` class in `src/models/mcp_handler.py`
3. Add model-specific configurations as needed

### Customizing the Interface

1. Edit `src/components/interface.py` to modify the Gradio interface
2. Add custom CSS in the `load_custom_css()` function
3. Update static assets in the `static/` directory

### Adding New Features

1. Create new modules in the appropriate `src/` subdirectories
2. Update the main `app.py` file to integrate new features
3. Add corresponding tests in the `tests/` directory

## 📊 Monitoring and Logs

- Application logs are stored in the `logs/` directory
- Log level can be configured in the application settings
- Real-time status updates are available in the web interface

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Commit your changes: `git commit -am 'Add feature'`
5. Push to the branch: `git push origin feature-name`
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🏆 Hackathon Information

This project was developed for the MCP Hugging Face Hackathon 2025, demonstrating innovative applications of the Model Context Protocol with Hugging Face's ecosystem.

## 🆘 Support

If you encounter any issues or have questions:

1. Check the logs in the `logs/` directory
2. Review the configuration in `config/app_config.json`
3. Ensure all dependencies are properly installed
4. Create an issue in the repository for persistent problems

## 🔮 Future Enhancements

- [ ] Add more model providers (OpenAI, Anthropic, etc.)
- [ ] Implement conversation history and context management
- [ ] Add model comparison features
- [ ] Enhance the UI with more customization options
- [ ] Add API endpoints for external integrations
- [ ] Implement user authentication and sessions
- [ ] Add model fine-tuning capabilities
- [ ] Integrate with more MCP features

## 🗄️ Database Setup & Configuration

This project includes a complete hospital management database with 8,010+ records across 7 tables, successfully imported into Neon PostgreSQL.

### 📊 Database Overview

The database contains the following tables with real hospital data:

| Table Name         | Records   | Description                             |
| ------------------ | --------- | --------------------------------------- |
| users              | 3,210     | User accounts (patients, staff, admins) |
| patient_records    | 3,000     | Patient medical records                 |
| occupancy          | 1,100     | Room occupancy records                  |
| tools              | 500       | Medical tools and equipment             |
| rooms              | 150       | Hospital room details                   |
| hospital_inventory | 100       | Hospital inventory items                |
| storage_rooms      | 50        | Hospital storage room information       |
| **TOTAL**          | **8,010** | **Complete hospital management data**   |

### 🔒 Secure Database Configuration

#### For Team Members - Initial Setup

**Option 1: Environment Variables (Recommended)**

1. Copy the environment template:

   ```powershell
   Copy-Item .env.template .env
   ```

2. Edit `.env` with your actual Neon database credentials:

   ```env
   NEON_HOST=your-neon-host.aws.neon.tech
   NEON_DATABASE=maindb
   NEON_USER=your-username
   NEON_PASSWORD=your-actual-password
   NEON_PORT=5432
   NEON_SSLMODE=require
   ```

3. Load environment variables in PowerShell:
   ```powershell
   Get-Content .env | ForEach-Object {
       if ($_ -match '^([^=]+)=(.*)$') {
           [Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process')
       }
   }
   ```

**Option 2: Configuration File (Development Only)**

1. Copy the configuration template:

   ```powershell
   Copy-Item neon_config.template.json neon_config.json
   ```

2. Edit `neon_config.json` with your actual credentials:
   ```json
   {
     "database": {
       "host": "your-actual-host.aws.neon.tech",
       "database": "maindb",
       "user": "your-username",
       "password": "your-actual-password",
       "port": 5432,
       "sslmode": "require"
     }
   }
   ```

#### 🔧 Using Database Configuration in Code

```python
from secure_config import load_database_config, get_connection_string

# Load configuration securely
config = load_database_config()

# Get connection string for SQLAlchemy/psycopg2
conn_string = get_connection_string()

# Example usage with psycopg2
import psycopg2
conn = psycopg2.connect(conn_string)
```

#### 🛡️ Security Best Practices

- **Never commit** `.env` or `neon_config.json` files (they're in `.gitignore`)
- **Use environment variables** in production environments
- **Rotate credentials** regularly in Neon console
- **Review** `SECURITY.md` for comprehensive security guidelines

#### 🔍 Verify Configuration

Test your database setup:

```powershell
python secure_config.py
```

This will verify your configuration without exposing sensitive credentials.

#### 📋 Database Schema & Relationships

The database includes proper foreign key relationships:

```
users (3,210 rows)
├── patient_records (3,000 rows) [FK: user_id → users.id]
└── occupancy (1,100 rows) [FK: patient_id → patient_records.id]

storage_rooms (50 rows)
├── tools (500 rows) [FK: location_storage_id → storage_rooms.id]
└── hospital_inventory (100 rows) [FK: location_storage_id → storage_rooms.id]

rooms (150 rows)
└── occupancy (1,100 rows) [FK: room_id → rooms.id]
```

#### 🚀 Quick Database Queries

Example queries to get started:

```sql
-- Get all active patients
SELECT u.full_name, pr.medical_history->'conditions' as conditions
FROM users u
JOIN patient_records pr ON u.id = pr.user_id
WHERE u.role = 'patient';

-- Check room occupancy
SELECT r.room_number, r.room_type, o.check_in_date
FROM rooms r
LEFT JOIN occupancy o ON r.id = o.room_id
WHERE o.check_out_date IS NULL;

-- View medical equipment by location
SELECT sr.room_name, t.tool_name, t.status
FROM storage_rooms sr
JOIN tools t ON sr.id = t.location_storage_id
ORDER BY sr.room_name;
```

#### 📚 Additional Resources

- **`IMPORT_SUCCESS_REPORT.md`** - Complete import documentation
- **`SECURITY.md`** - Detailed security guidelines
- **`secure_config.py`** - Configuration utilities
- **Neon Console** - [https://console.neon.tech](https://console.neon.tech)

---

**Happy Hacking! 🚀**