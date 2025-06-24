# Document Understanding Pipeline

A modular document processing pipeline that extracts structured data from driving licenses, shop receipts, and resumes using Google Vision API for OCR and Google Gemini LLM for data extraction.

## Features

- **OCR Processing**: Uses Google Vision API for high-accuracy text extraction
- **Structured Data Extraction**: Google Gemini LLM or OPENAI LLM with LangChain for intelligent data parsing
- **Multiple Document Types**: Supports driving licenses, shop receipts, and resumes
- **Modular Architecture**: Easy to extend for new document types
- **Robust Error Handling**: Comprehensive logging and error recovery
- **Cost-Effective**: Uses efficient models and token management

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Setup  (take a look at .env.example file)

Create a `.env` file in the project root:

```bash
GOOGLE_API_KEY=your_google_api_key_here
OPENAI_API_KEY=your_openai_key_here
GOOGLE_APPLICATION_CREDENTIALS="path to the service account credentials file"
USE_OPENAI="true if using openai"
```

### 3. Google Cloud Setup

Add the Google Cloud credentials file in the project root.

## Directory Structure

Create the following directory structure for your input documents:

```
documents/
├── driving_license/
│   ├── license1.jpg
│   ├── license2.png
│   └── license3.pdf
├── shop_receipts/
│   ├── receipt1.jpg
│   ├── receipt2.png
│   └── receipt3.pdf
└── resumes/
    ├── resume1.jpg
    ├── resume2.png
    └── resume3.pdf
```

## Usage

### Process All Document Types

```bash
python main.py --input-dir documents
```

### Process Specific Document Type

```bash
# Process only driving licenses
python main.py --input-dir documents --document-type driving_license

# Process only shop receipts
python main.py --input-dir documents --document-type shop_receipt

# Process only resumes
python main.py --input-dir documents --document-type resume
```

### Process Single File

```bash
python main.py --single-file documents/driving_license/license1.jpg --document-type driving_license
```

## Output

Results are saved in the `output/` directory with the following structure:

```
output/
├── license1_result.json
├── receipt1_result.json
├── resume1_result.json
└── ...
```

Each result file contains:
- Original file path
- Document type
- Extracted OCR text
- Structured data in JSON format
- Processing status

## Supported File Formats

- **Images**: JPG, JPEG, PNG
- **Documents**: PDF

## Data Models

### Driving License
```json
{
  "name": "John Doe",
  "date_of_birth": "1990-01-01",
  "license_number": "DL123456789",
  "issuing_state": "California",
  "expiry_date": "2025-01-01"
}
```

### Shop Receipt
```json
{
  "merchant_name": "Walmart",
  "total_amount": 45.67,
  "date_of_purchase": "2024-01-15",
  "items": [
    {
      "name": "Milk",
      "quantity": 2,
      "price": 3.99
    }
  ],
  "payment_method": "Credit Card"
}
```

### Resume
```json
{
  "full_name": "Jane Smith",
  "email": "jane.smith@email.com",
  "phone_number": "+1-555-123-4567",
  "skills": ["Python", "Machine Learning", "Data Analysis"],
  "work_experience": [
    {
      "company": "Tech Corp",
      "role": "Data Scientist",
      "dates": "2020-2023"
    }
  ],
  "education": [
    {
      "institution": "University of Technology",
      "degree": "Master of Science in Computer Science",
      "graduation_year": 2020
    }
  ]
}
```

## Architecture

```
main.py              # Entry point and CLI
├── config.py        # Configuration management
├── models.py        # Pydantic data models
├── ocr_service.py   # Google Vision API integration
├── llm_service.py   # Google Gemini LLM with LangChain
└── pipeline.py      # Main processing pipeline
```

## Error Handling

The pipeline includes comprehensive error handling:
- Invalid file formats
- OCR extraction failures
- LLM processing errors
- Network connectivity issues

All errors are logged to `pipeline.log` and the console.

## Cost Optimization

- Uses `gemini-2.5-flash` for cost-effective processing
- Limits token usage with `MAX_TOKENS` setting
- Efficient prompt design to minimize API calls

## Extending the Pipeline

To add new document types:

1. Add new Pydantic model in `models.py`
2. Create prompt template in `llm_service.py`
3. Update document type mapping in `pipeline.py`
4. Add folder structure for new document type

## Troubleshooting

### Common Issues

1. **Missing Google API Key**: Set `GOOGLE_API_KEY` in `.env` file
2. **Google Cloud Authentication**: Ensure credentials file is present
3. **Missing Dependencies**: Run `pip install -r requirements.txt`
4. **File Format Not Supported**: Check supported formats in `config.py`

### Logs

Check `pipeline.log` for detailed error information and processing status. 
