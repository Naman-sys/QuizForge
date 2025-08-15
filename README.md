# PDF Quiz Generator

A complete Python Streamlit application that extracts text from PDF files and generates quiz questions using Hugging Face AI models.

## Features

- **PDF Text Extraction**: Uses pdfplumber to extract clean, readable text from PDF files
- **AI-Powered Question Generation**: Leverages Hugging Face Inference API (Mistral-7B-Instruct) to create:
  - Multiple-choice questions (4 options each)
  - True/False questions
- **Interactive Editing**: Teachers can view, edit, or delete any generated question
- **Export Functionality**: Download quiz + answer key as .txt or .docx files
- **Responsive UI**: Clean, minimal interface built with Streamlit

## Project Structure

```
├── app.py                 # Main Streamlit application
├── README.md             # This file
├── requirements.txt      # Python dependencies
└── .streamlit/
    └── config.toml       # Streamlit configuration
```

## Core Functions

- `extract_text_from_pdf()` - Extracts text from uploaded PDF files
- `generate_questions_with_hf()` - Generates quiz questions using Hugging Face API
- `render_quiz_form()` - Renders editable quiz interface
- `export_quiz()` - Exports quiz to downloadable formats

## Installation & Setup

### 1. Install Dependencies

The following packages are required:

```bash
# Core dependencies
pip install streamlit
pip install pdfplumber
pip install python-docx
pip install requests

# Alternative PDF processing (if needed)
pip install unstructured
```

### 2. Set Hugging Face API Key

#### On Replit:
1. Go to your Replit project
2. Click on "Secrets" in the left sidebar
3. Add a new secret:
   - Key: `HUGGINGFACE_API_KEY`
   - Value: Your Hugging Face API token

#### Locally:
```bash
export HUGGINGFACE_API_KEY="your_hf_token_here"
```

#### Getting a Hugging Face API Key:
1. Visit [https://huggingface.co/](https://huggingface.co/)
2. Create a free account or log in
3. Go to Settings → Access Tokens
4. Create a new token with "read" permissions
5. Copy the token (starts with `hf_`)

### 3. Running on Replit

1. Create a new Python Repl
2. Upload your project files
3. Set the `HUGGINGFACE_API_KEY` in Secrets
4. Run the app:
   ```bash
   streamlit run app.py --server.port 5000
   ```

### 4. Running Locally

```bash
# Clone/download the project
cd pdf-quiz-generator

# Install dependencies
pip install -r requirements.txt

# Set API key
export HUGGINGFACE_API_KEY="your_token"

# Run the app
streamlit run app.py
```

## Usage

1. **Upload PDF**: Click "Choose a PDF file" and select your chapter/document
2. **Configure Settings**: Use the sidebar to set the number of multiple-choice and true/false questions
3. **Generate Questions**: Click "Generate Quiz Questions" to create AI-powered questions
4. **Edit Questions**: Review and modify questions, options, correct answers, and explanations
5. **Export**: Download your quiz as a TXT or DOCX file

## Supported PDF Types

- Text-based PDFs (best results)
- Scanned PDFs with OCR text layer
- Academic papers and textbook chapters
- Any PDF with extractable text content

## AI Models Used

- **Primary**: `mistralai/Mistral-7B-Instruct-v0.2` - Advanced instruction-following model
- **Fallback**: Intelligent content-based question generation when API responses need formatting

## Configuration

The app uses Streamlit's configuration system. The `.streamlit/config.toml` file contains:

```toml
[server]
headless = true
address = "0.0.0.0"
port = 5000
```

## Troubleshooting

### Common Issues:

1. **PDF Text Extraction Fails**:
   - Ensure PDF contains extractable text (not just images)
   - Try a different PDF processing library if needed

2. **API Key Errors**:
   - Verify your Hugging Face API key is correctly set
   - Check that the token has appropriate permissions

3. **Question Generation Issues**:
   - The app includes fallback question generation
   - Try shorter text content if API calls fail

4. **Export Problems**:
   - Ensure all question fields are properly filled
   - Check file permissions for downloads

### Environment Variables:

Required:
- `HUGGINGFACE_API_KEY` - Your Hugging Face API token

## API Limits

- Hugging Face Inference API has rate limits for free accounts
- For production use, consider upgrading to Hugging Face Pro
- The app includes intelligent fallback question generation

## License

This project is open source and available under the MIT License.

## Contributing

Feel free to submit issues and pull requests to improve the application.