import os
import json
import logging
from typing import Dict, Any, List
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

from config import Config
from ocr_service import OCRService
from llm_service import LLMService

class DocumentPipeline:
    """Main pipeline for processing documents and extracting structured data"""
    
    def __init__(self):
        self.ocr_service = OCRService()
        self.llm_service = LLMService()
        self.logger = logging.getLogger(__name__)
        
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def process_single_document(self, file_path: str, document_type: str) -> Dict[str, Any]:
        """Process a single document and extract structured data"""
        try:
            self.logger.info(f"Processing document: {file_path}")
            
            # Step 1: Extract text using OCR
            self.logger.info("Extracting text using OCR...")
            extracted_text = self.ocr_service.extract_text(file_path)
            
            if not extracted_text.strip():
                raise ValueError("No text extracted from document")
            
            self.logger.info(f"Extracted {len(extracted_text)} characters of text")
            
            # Step 2: Extract structured data using LLM
            self.logger.info("Extracting structured data using LLM...")
            structured_data = self.llm_service.extract_data(extracted_text, document_type)
            
            # Step 3: Add metadata
            result = {
                "file_path": file_path,
                "document_type": document_type,
                "extracted_text": extracted_text,
                "structured_data": structured_data,
                "processing_status": "success"
            }
            
            self.logger.info("Document processing completed successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing document {file_path}: {str(e)}")
            return {
                "file_path": file_path,
                "document_type": document_type,
                "error": str(e),
                "processing_status": "failed"
            }
    
    def process_directory(self, directory_path: str, document_type: str) -> List[Dict[str, Any]]:
        """Process all documents in a directory in parallel using ThreadPoolExecutor"""
        results = []
        directory = Path(directory_path)
        
        if not directory.exists():
            raise ValueError(f"Directory not found: {directory_path}")
        
        # Get all supported files
        supported_files = []
        for ext in Config.SUPPORTED_IMAGE_FORMATS + Config.SUPPORTED_PDF_FORMATS:
            supported_files.extend(directory.glob(f"*{ext}"))
        
        self.logger.info(f"Found {len(supported_files)} files to process in {directory_path}")
        
        # Process each file in parallel using ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=4) as executor:
            future_to_file = {
                executor.submit(self.process_single_document, str(file_path), document_type): file_path
                for file_path in supported_files
            }
            for future in as_completed(future_to_file):
                result = future.result()
                results.append(result)
                self._save_result(result, future_to_file[future].stem)
        
        return results
    
    def _save_result(self, result: Dict[str, Any], filename: str):
        """Save processing result to JSON file"""
        output_path = os.path.join(Config.OUTPUT_DIR, f"{filename}_result.json")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Result saved to: {output_path}")
    
    def process_all_document_types(self, base_directory: str):
        """Process all document types from their respective directories"""
        document_types = {
            'driving_license': 'driving_license',
            'shop_receipt': 'shop_receipts',
            'resume': 'resumes'
        }
        
        all_results = {}
        
        for doc_type, folder_name in document_types.items():
            folder_path = os.path.join(base_directory, folder_name)
            
            if os.path.exists(folder_path):
                self.logger.info(f"Processing {doc_type} documents from {folder_path}")
                results = self.process_directory(folder_path, doc_type)
                all_results[doc_type] = results
            else:
                self.logger.warning(f"Directory not found: {folder_path}")
        
        return all_results 