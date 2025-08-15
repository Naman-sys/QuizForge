# Overview

This is a complete AI Quiz Generator application built with Python and Streamlit. The app processes both PDF files and article text to generate educational quiz questions using Hugging Face's AI models. Teachers can upload PDF chapters or paste article content, generate multiple-choice and true/false questions, edit them interactively, and export the quiz with answer keys as downloadable files. The system uses the Mistral-7B-Instruct model for intelligent question generation with fallback content-based generation.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Core Components

**Content Processing Layer**
- `extract_text_from_pdf()` function uses pdfplumber for clean PDF text extraction
- `extract_text_from_article()` function processes and validates article text input
- Handles text-based PDFs and provides clear error messages for problematic files
- Text cleaning and normalization for article content with minimum length validation
- Graceful error handling for missing dependencies and extraction failures

**AI Question Generation**
- `generate_questions_with_hf()` function integrates with Hugging Face Inference API
- Uses gpt2 model for intelligent question generation
- `create_fallback_questions()` provides content-based question generation when AI responses need formatting
- Supports configurable numbers of multiple-choice and true/false questions

**Interactive Quiz Editor**
- `render_quiz_form()` function creates an editable interface for generated questions
- Teachers can view, edit, delete, and add new questions with real-time updates
- Supports both multiple-choice (4 options) and true/false question types
- Includes explanation fields for educational value

**Export Functionality**
- `export_quiz()` function generates downloadable quiz files
- Supports both TXT and DOCX formats with proper formatting
- Includes questions, options, correct answers, and explanations

## Design Patterns

**Error Handling Strategy**
- Defensive programming with try-catch blocks at multiple levels
- Graceful degradation when optional libraries are unavailable
- User-friendly error messages that don't expose technical details

**Configuration Management**
- Environment variable-based API key management for security
- Hardcoded model selection with clear documentation about version choices
- Configurable quiz parameters (difficulty levels, question types)

**Modular Architecture**
- Separation of concerns between file processing and quiz generation
- Single responsibility principle applied to each class
- Easy to extend with additional file types or quiz features

# External Dependencies

## AI Services
- **Hugging Face Inference API**: Primary service using gpt2 model
- Requires HUGGINGFACE_API_KEY environment variable for authentication
- Advanced JSON parsing with intelligent fallback for non-JSON responses
- Content-based question generation when API calls fail

## File Processing Libraries
- **pdfplumber**: Primary PDF text extraction library with excellent text quality
- **python-docx**: Export functionality for DOCX quiz formats
- **requests**: HTTP client for Hugging Face API interactions

## Web Framework
- **Streamlit**: Main web application framework for user interface
- Provides built-in file upload, form controls, and session management

## Python Standard Libraries
- **json**: API response parsing and data serialization
- **os**: Environment variable access for API key management
- **io**: File stream handling for downloads and uploads
- **streamlit**: Complete web application framework with built-in components

# Recent Changes (August 15, 2025)

- Completely rebuilt as a structured PDF Quiz Generator application
- Implemented four core functions as requested: extract_text_from_pdf(), generate_questions_with_hf(), render_quiz_form(), export_quiz()
- Upgraded to gpt2 model for better instruction following
- Added comprehensive PDF-only upload with pdfplumber integration
- Created interactive quiz editing interface with add/delete/modify capabilities
- Implemented dual export format support (TXT and DOCX) with proper formatting
- Added intelligent fallback question generation based on content analysis
- Structured the application for educational use with teacher-focused features
- Added article text input functionality for web content, blogs, and documents
- Enhanced input method selection with dual support for PDF files and article text
- Implemented text cleaning and validation for article content processing
- Updated UI to support multiple content input methods with clear selection interface