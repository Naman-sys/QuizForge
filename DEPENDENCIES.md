# Project Dependencies

This project requires the following Python packages:

## Core Dependencies
```
streamlit>=1.48.1
google-generativeai>=0.3.0
pdfplumber>=0.11.7
python-docx>=1.2.0
pandas>=2.0.0
requests>=2.32.4
```

## Installation Commands

### For Replit
Dependencies are automatically installed via the package manager.

### For Local Development
```bash
pip install streamlit google-generativeai pdfplumber python-docx pandas requests
```

### Using requirements.txt (create this file if needed)
```bash
pip install -r requirements.txt
```

## Environment Variables
Set either of these environment variables for Gemini AI:
- `GEMINI_API_KEY=your_api_key_here`
- `GOOGLE_API_KEY=your_api_key_here`

## Running the Application
```bash
streamlit run app.py
```

The app will fallback to local question generation if no API key is provided.