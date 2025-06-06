# Nebius API Setup Guide

## 🚀 Quick Setup

### 1. Get Your Nebius API Key
1. Visit [Nebius Studio](https://studio.nebius.com/)
2. Sign up or log in to your account
3. Navigate to the API section
4. Generate a new API key

### 2. Configure the API Key

**Option A: Environment Variable (Recommended)**
```bash
# Windows PowerShell
$env:NEBIUS_API_KEY="your-api-key-here"

# Windows Command Prompt
set NEBIUS_API_KEY=your-api-key-here

# Linux/Mac
export NEBIUS_API_KEY="your-api-key-here"
```

**Option B: Configuration File**
1. Edit `config/nebius_config.json`
2. Replace `"your-api-key-here"` with your actual API key

```json
{
  "api_key": "your-actual-api-key-here",
  "base_url": "https://api.studio.nebius.ai/v1",
  "model": "meta-llama/Llama-3.3-70B-Instruct",
  "max_tokens": 2048,
  "temperature": 0.4,
  "timeout": 30
}
```

### 3. Test the Integration

1. Start the application: `python app.py`
2. Open your browser to: http://localhost:7862
3. Select "nebius-llama-3.3-70b" from the model dropdown
4. Choose a medical specialty
5. Ask a medical question

### 4. Usage Tips

- **Lower Temperature (0.2-0.4)**: More factual, medical accuracy
- **Higher Temperature (0.6-0.8)**: More conversational responses
- **Medical Context**: Provide relevant medical history for better responses
- **Specialty Selection**: Choose the appropriate medical field for specialized responses

### 5. Troubleshooting

**API Key Issues:**
- Verify your API key is correctly set
- Check the Nebius Studio dashboard for key status
- Ensure sufficient API credits

**Connection Issues:**
- Check your internet connection
- Verify the Nebius Studio service status
- Check firewall settings

**Model Issues:**
- Fallback models will work if Nebius is unavailable
- Check the console for detailed error messages

### 6. Security Notes

- Never commit API keys to version control
- Use environment variables in production
- Regularly rotate your API keys
- Monitor API usage in the Nebius dashboard

## 🏥 Medical AI Features

The integration provides:
- **Medical Consultations**: Specialized prompts for different medical fields
- **Symptom Analysis**: Intelligent interpretation of patient symptoms
- **Medical Summaries**: Comprehensive analysis of medical information
- **Safety Disclaimers**: Automatic medical disclaimers for all responses
- **Specialty Routing**: Context-aware responses based on medical specialty

---

**⚠️ Important**: This tool is for educational and informational purposes only and should not replace professional medical advice, diagnosis, or treatment. 