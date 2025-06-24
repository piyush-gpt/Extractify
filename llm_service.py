import logging
from typing import Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
import re

from config import Config
from models import DrivingLicense, ShopReceipt, Resume

from langchain_openai import ChatOpenAI

class LLMService:
    """Service for extracting structured data using Google Gemini LLM or OpenAI GPT-3.5 Turbo with LangChain"""
    
    def __init__(self):
        if Config.USE_OPENAI:
            self.llm = ChatOpenAI(
                model=Config.OPENAI_MODEL,
                temperature=0,
                openai_api_key=Config.OPENAI_API_KEY,
                max_tokens=Config.MAX_TOKENS
            )
        else:
            self.llm = ChatGoogleGenerativeAI(
                model=Config.GEMINI_MODEL,
                temperature=0,
                max_output_tokens=Config.MAX_TOKENS,
                google_api_key=Config.GOOGLE_API_KEY
            )
        self.logger = logging.getLogger(__name__)
        
        
        self.prompts = {
            'driving_license': self._get_driving_license_prompt(),
            'shop_receipt': self._get_shop_receipt_prompt(),
            'resume': self._get_resume_prompt()
        }
    
    def _get_driving_license_prompt(self) -> ChatPromptTemplate:
        """Get prompt template for driving license extraction"""
        template = """You are an expert at extracting structured data from driving license documents.

Extract the following information from the provided text:
- Name: Full name of the license holder
- Date of Birth: Date of birth in YYYY-MM-DD format
- License Number: License number/ID
- Issuing State: State that issued the license
- Expiry Date: Expiry date in YYYY-MM-DD format

Text from document:
{text}

Return the data in the following JSON format:
{format_instructions}

If any field cannot be found, use \"Not found\" as the value. Be precise and accurate.
Return ONLY the JSON object, with no extra text, explanation, or formatting."""
        
        parser = PydanticOutputParser(pydantic_object=DrivingLicense)
        return ChatPromptTemplate.from_template(template)
    
    def _get_shop_receipt_prompt(self) -> ChatPromptTemplate:
        """Get prompt template for shop receipt extraction"""
        template = """You are an expert at extracting structured data from shop receipts.

Extract the following information from the provided text:
- Merchant Name: Name of the merchant/store
- Total Amount: Total amount of the purchase (numeric value)
- Date of Purchase: Date of purchase in YYYY-MM-DD format
- Items: List of items with name, quantity, and price
- Payment Method: Payment method used

Text from document:
{text}

Return the data in the following JSON format:
{format_instructions}

Important notes:
- For numeric fields (total_amount, price, quantity), if the value cannot be found, use 0.
- For all other fields, use \"Not found\" if the value cannot be found.
- For items, extract as many as you can identify
- Quantity can be decimal (e.g., 2.5 lbs, 0.5 kg) for items sold by weight
- Use the exact quantity as shown on the receipt, whether it's whole numbers or decimals
- Price should be the price per unit/item
Return ONLY the JSON object, with no extra text, explanation, or formatting."""
        
        parser = PydanticOutputParser(pydantic_object=ShopReceipt)
        return ChatPromptTemplate.from_template(template)
    
    def _get_resume_prompt(self) -> ChatPromptTemplate:
        """Get prompt template for resume extraction"""
        template = """You are an expert at extracting structured data from resumes/CVs.

Extract the following information from the provided text:
- Full Name: Full name of the person
- Email: Email address
- Phone Number: Phone number
- Skills: List of skills mentioned
- Work Experience: List of work experiences with company, role, and dates
- Education: List of educational background with institution, degree, and graduation year

Text from document:
{text}

Return the data in the following JSON format:
{format_instructions}

Important notes:
- You MUST include ALL fields in the response, even if they are empty or not found
- If any field cannot be found, use \"Not found\" as the value
- For skills, work_experience, and education, use empty arrays [] if none are found
- For graduation_year, use the actual year (e.g., 2020) if available, or the date range as a string (e.g., \"6/92-3/93\") if it's a range
- Extract as many skills, work experiences, and education entries as possible
- Be precise with dates and formatting
- Always include the education, skills, and work_experience fields, even if they are empty arrays
Return ONLY the JSON object, with no extra text, explanation, or formatting."""
        
        parser = PydanticOutputParser(pydantic_object=Resume)
        return ChatPromptTemplate.from_template(template)
    
    def extract_data(self, text: str, document_type: str) -> Dict[str, Any]:
        """Extract structured data from OCR text based on document type, with input truncation and retry logic."""
        MAX_CHARS = 2000
        try:
            if not text.strip():
                self.logger.error(f"OCR text is empty for document type: {document_type}")
                raise ValueError("No text extracted from OCR to send to LLM.")
            if document_type not in self.prompts:
                raise ValueError(f"Unsupported document type: {document_type}")

            # Truncate text if too long
            original_length = len(text)
            if original_length > MAX_CHARS:
                self.logger.warning(f"OCR text too long ({original_length} chars), truncating to {MAX_CHARS} chars for LLM.")
                text = text[:MAX_CHARS]

            prompt = self.prompts[document_type]
            parser = PydanticOutputParser(pydantic_object=self._get_model_class(document_type))

            formatted_prompt = prompt.format_messages(
                text=text,
                format_instructions=parser.get_format_instructions()
            )

            response = self.llm.invoke(formatted_prompt)
            raw_output = response.content

            if not raw_output.strip():
                self.logger.error(f"LLM returned empty output for document type: {document_type}")
                self.logger.error(f"Prompt sent to LLM (text length: {len(text)}): {formatted_prompt}")
                # Retry with half the text if possible
                if len(text) > 500:
                    self.logger.warning("Retrying LLM with half the text length.")
                    return self.extract_data(text[:len(text)//2], document_type)
                raise ValueError("LLM returned empty output.")

           
            
            parsed_data = parser.parse(raw_output)

            return parsed_data.model_dump()

        except Exception as e:
            self.logger.error(f"Error extracting data for {document_type}: {str(e)}")
            # Log the raw output for debugging
            if 'raw_output' in locals():
                self.logger.error(f"Raw LLM output: {raw_output}")
            raise
    
    def _get_model_class(self, document_type: str):
        """Get the appropriate Pydantic model class for the document type"""
        model_map = {
            'driving_license': DrivingLicense,
            'shop_receipt': ShopReceipt,
            'resume': Resume
        }
        return model_map.get(document_type) 