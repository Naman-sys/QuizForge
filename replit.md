# Overview

This project is a quiz generation application that processes uploaded documents and uses AI to create educational quizzes from the content. The system extracts text from various file formats (TXT, PDF, DOCX) and leverages Hugging Face's Inference API to generate customized quizzes with different difficulty levels and question types. It's designed as a Streamlit web application for easy user interaction and file upload functionality.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Core Components

**File Processing Layer**
- `FileProcessor` class handles document parsing and text extraction
- Supports multiple file formats: TXT, PDF (via PyPDF2), and DOCX (via python-docx)
- Implements graceful error handling with encoding fallbacks for text files
- Uses optional imports to handle missing dependencies without breaking the application

**AI Integration Layer**
- `QuizGenerator` class manages Hugging Face Inference API interactions
- Uses microsoft/DialoGPT-medium model for quiz generation
- Implements structured JSON response format with fallback content generation
- Includes temperature control (0.7) for balanced creativity and accuracy

**Web Interface**
- Built on Streamlit framework for rapid web application development
- Provides file upload functionality with drag-and-drop support
- Offers interactive controls for quiz customization (difficulty, question count, types)

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
- **Hugging Face Inference API**: Primary service for quiz generation using microsoft/DialoGPT-medium model
- Requires API key configuration via environment variables
- Includes fallback quiz generation when API responses aren't structured JSON

## File Processing Libraries
- **PyPDF2**: PDF text extraction (optional dependency)
- **python-docx**: Microsoft Word document processing (optional dependency)
- Both libraries are gracefully handled if not installed

## Web Framework
- **Streamlit**: Main web application framework for user interface
- Provides built-in file upload, form controls, and session management

## Python Standard Libraries
- **json**: Response parsing and data serialization
- **os**: Environment variable access and file system operations
- **io**: File stream handling for uploaded content
- **typing**: Type hints for better code documentation