import os
from typing import List
from google.cloud import vision
from pdf2image import convert_from_path
import logging

from config import Config

class OCRService:
    """Service for extracting text from images and PDFs using Google Vision API"""
    
    def __init__(self):
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = Config.GOOGLE_APPLICATION_CREDENTIALS
        self.client = vision.ImageAnnotatorClient()
        self.logger = logging.getLogger(__name__)
    
    def extract_text_from_image(self, image_path: str) -> str:
        """Extract text from a single image using Google Vision API"""
        try:
            with open(image_path, 'rb') as image_file:
                content = image_file.read()
            
            image = vision.Image(content=content)
            response = self.client.text_detection(image=image)
            
            if response.error.message:
                raise Exception(f'Google Vision API error: {response.error.message}')
            
            texts = response.text_annotations
            if texts:
                return texts[0].description
            return ""
            
        except Exception as e:
            self.logger.error(f"Error extracting text from image {image_path}: {str(e)}")
            raise
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Convert PDF to images and extract text from each page"""
        try:
            # Convert PDF to images  pdf2image
            images = convert_from_path(pdf_path)
            all_text = []
            
            for i, image in enumerate(images):
                # Save temporary image
                temp_image_path = f"temp_page_{i}.png"
                image.save(temp_image_path, "PNG")
                
                # Extract text from the image
                page_text = self.extract_text_from_image(temp_image_path)
                all_text.append(page_text)
                
                # Clean up temporary file
                os.remove(temp_image_path)
            
            return "\n".join(all_text)
            
        except Exception as e:
            self.logger.error(f"Error extracting text from PDF {pdf_path}: {str(e)}")
            raise
    
    def extract_text(self, file_path: str) -> str:
        """Extract text from file (image or PDF)"""
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext in Config.SUPPORTED_IMAGE_FORMATS:
            return self.extract_text_from_image(file_path)
        elif file_ext in Config.SUPPORTED_PDF_FORMATS:
            return self.extract_text_from_pdf(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}") 