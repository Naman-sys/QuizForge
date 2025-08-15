# Overview

This is a complete AI Quiz Generator application built with Python and Streamlit. The app processes both PDF files and article text to generate educational quiz questions using local intelligent content analysis without requiring external APIs. Teachers can upload PDF chapters or paste article content, customize difficulty levels and question types, generate multiple-choice and true/false questions, edit them interactively, and export the quiz with answer keys as downloadable files. The system uses the Mistral-7B-Instruct model for intelligent question generation with fallback content-based generation.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Core Components

**Content Processing Layer**
- `extract_text_from_pdf()` function uses pdfplumber for clean PDF text extraction
- `extract_text_from_article()` function processes and validates article text input
- `FileProcessor` class handles multiple file types including PDF, CSV, DOCX, and TXT
- CSV processing with pandas for data analysis and intelligent content extraction
- Handles text-based PDFs and provides clear error messages for problematic files
- Text cleaning and normalization for article content with minimum length validation
- Graceful error handling for missing dependencies and extraction failures

**Local AI Question Generation**
- `generate_questions_with_local_ai()` function uses intelligent content analysis
- `create_intelligent_questions()` provides sophisticated local question generation
- Advanced text processing with key term extraction and context analysis
- Supports configurable numbers of multiple-choice and true/false questions
- Three difficulty levels: Easy (simple vocabulary), Medium (standard), Hard (advanced analysis)
- Flexible question type selection - choose multiple choice, true/false, or both
- Adaptive question complexity based on difficulty settings
- No external API dependencies - fully offline capable

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

## Local AI Services
- **Local Content Analysis**: Advanced text processing and question generation
- **Key Term Extraction**: Identifies important concepts and terminology
- **Context Analysis**: Creates relevant questions based on content structure
- **No External Dependencies**: Fully offline operation without API requirements

## File Processing Libraries
- **pdfplumber**: Primary PDF text extraction library with excellent text quality
- **pandas**: CSV data processing and analysis for generating data-based questions
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

## CSV File Support Added
- Added comprehensive CSV file processing with pandas integration
- Created intelligent data analysis for generating quiz questions from datasets
- Added support for numeric and categorical data summarization
- Implemented sample data extraction and statistical insights for quiz generation
- Updated UI to include CSV upload option alongside PDF and article text
- Enhanced FileProcessor class with robust CSV handling and error management

## UI Improvements
- Centered all content elements for better visual presentation
- Updated file uploader interface to support multiple file types
- Added separate input methods for PDF files, CSV data, and article text

- Completely rebuilt as a structured PDF Quiz Generator application
- Implemented four core functions as requested: extract_text_from_pdf(), generate_questions_with_local_ai(), render_quiz_form(), export_quiz()
- Converted from API-dependent to completely offline system using intelligent content analysis
- Added comprehensive PDF-only upload with pdfplumber integration
- Created interactive quiz editing interface with add/delete/modify capabilities
- Implemented dual export format support (TXT and DOCX) with proper formatting
- Added intelligent fallback question generation based on content analysis
- Structured the application for educational use with teacher-focused features
- Added article text input functionality for web content, blogs, and documents
- Enhanced input method selection with dual support for PDF files and article text
- Implemented text cleaning and validation for article content processing
- Updated UI to support multiple content input methods with clear selection interface
- Added difficulty levels (Easy, Medium, Hard) with adaptive question complexity
- Implemented flexible question type selection (multiple choice, true/false, or both)
- Added customizable question numbers (1-15 for each type)
- Enhanced UI with modern styling: Poppins/Montserrat headings, Nunito Sans body text
- Implemented floating action buttons for quick actions
- Added dark mode glow effects on active inputs
- Created sticky action bar for easy navigation
- Animated question cards with slide/fade effects
- Applied gradient backgrounds and modern button styling