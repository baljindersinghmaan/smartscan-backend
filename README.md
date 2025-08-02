# SmartScan Backend

A FastAPI-based backend service for Hindi/English Named Entity Recognition (NER) on business cards. This service provides language detection and entity extraction capabilities for processing business card text.

## Features

- **Language Detection**: Automatically detects whether text is in Hindi or English
- **Named Entity Recognition**: Extracts entities like names, organizations, locations from text
- **Business Card Pattern Recognition**: Specialized extraction for emails and phone numbers
- **RESTful API**: Clean API endpoints with automatic documentation
- **CORS Support**: Configured for cross-origin requests

## Prerequisites

- Python 3.12 or higher
- pip (Python package manager)
- Virtual environment (recommended)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd smartscan-backend
```

2. Create and activate a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Download SpaCy language models (when compatibility is resolved):
```bash
python -m spacy download en_core_web_sm
python -m spacy download hi_core_news_sm
```

## Running the Application

### Development Mode

Run the application with auto-reload enabled:
```bash
python app/main.py
```

Or using uvicorn directly:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The server will start on `http://localhost:8000`

### Production Mode

For production, run without reload:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## API Endpoints

### Health Check
- **GET** `/`
- Returns server status and SpaCy model loading status

### Language Detection
- **POST** `/detect-language`
- Request body:
```json
{
  "text": "Your text here",
  "language": "optional_language_code"
}
```
- Response:
```json
{
  "detected_language": "en",
  "confidence": 0.95,
  "hindi_score": 0.2,
  "english_score": 0.95
}
```

### Entity Extraction
- **POST** `/extract-entities`
- Request body:
```json
{
  "text": "John Doe, CEO at Tech Corp. Email: john@techcorp.com",
  "language": "optional_language_code"
}
```
- Response:
```json
{
  "language_detected": "en",
  "entities": [
    {
      "text": "john@techcorp.com",
      "label": "EMAIL",
      "start": 36,
      "end": 53,
      "confidence": 0.95
    }
  ],
  "confidence_score": 0.95
}
```

## API Documentation

Once the server is running, you can access:
- Interactive API documentation: `http://localhost:8000/docs`
- Alternative API documentation: `http://localhost:8000/redoc`

## Environment Variables

Create a `.env` file in the root directory:
```env
PORT=8000
HOST=0.0.0.0
```

## Project Structure

```
smartscan-backend/
├── app/
│   ├── main.py          # Main FastAPI application
│   ├── models/          # Pydantic models
│   ├── routes/          # API routes
│   └── services/        # Business logic
├── requirements.txt     # Python dependencies
├── .env                # Environment variables
└── README.md           # This file
```

## Known Issues

- **SpaCy Compatibility**: Currently experiencing numpy version compatibility issues with SpaCy. The regex-based entity extraction for emails and phone numbers works, but full NER functionality is temporarily disabled.

## Development

### Running Tests
```bash
pytest
```

### Code Style
The project follows PEP 8 style guidelines.

## Technologies Used

- **FastAPI**: Modern web framework for building APIs
- **Uvicorn**: ASGI server implementation
- **SpaCy**: Industrial-strength NLP library
- **Transformers**: Hugging Face transformers for advanced NLP
- **Pydantic**: Data validation using Python type annotations

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License.