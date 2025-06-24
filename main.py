
import argparse
import sys
import logging
from pathlib import Path

from config import Config
from pipeline import DocumentPipeline

def setup_logging():
    """Set up logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('pipeline.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def main():
    parser = argparse.ArgumentParser(description='Document Understanding Pipeline')
    parser.add_argument(
        '--input-dir', 
        type=str, 
        default='documents',
        help='Base directory containing document folders (default: documents)'
    )
    parser.add_argument(
        '--document-type',
        type=str,
        choices=['driving_license', 'shop_receipt', 'resume', 'all'],
        default='all',
        help='Type of document to process (default: all)'
    )
    parser.add_argument(
        '--single-file',
        type=str,
        help='Process a single file instead of a directory'
    )
    
    args = parser.parse_args()
    
    # Set up logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Validate configuration
        Config.validate()
        logger.info("Configuration validated successfully")
        
        # Initialize pipeline
        pipeline = DocumentPipeline()
        
        if args.single_file:
            # Process single file
            if not Path(args.single_file).exists():
                logger.error(f"File not found: {args.single_file}")
                sys.exit(1)
            
            logger.info(f"Processing single file: {args.single_file}")
            result = pipeline.process_single_document(args.single_file, args.document_type)
            
            if result['processing_status'] == 'success':
                logger.info("Single file processing completed successfully")
            else:
                logger.error(f"Single file processing failed: {result.get('error', 'Unknown error')}")
                sys.exit(1)
        
        else:
            # Process directory
            input_dir = Path(args.input_dir)
            if not input_dir.exists():
                logger.error(f"Input directory not found: {args.input_dir}")
                sys.exit(1)
            
            if args.document_type == 'all':
                # Process all document types
                logger.info(f"Processing all document types from: {args.input_dir}")
                results = pipeline.process_all_document_types(args.input_dir)
                
                # Print summary
                for doc_type, doc_results in results.items():
                    success_count = sum(1 for r in doc_results if r['processing_status'] == 'success')
                    total_count = len(doc_results)
                    logger.info(f"{doc_type}: {success_count}/{total_count} documents processed successfully")
            
            else:
                # Process specific document type
                folder_name = {
                    'driving_license': 'driving_license',
                    'shop_receipt': 'shop_receipts',
                    'resume': 'resumes'
                }[args.document_type]
                
                folder_path = input_dir / folder_name
                if not folder_path.exists():
                    logger.error(f"Document type folder not found: {folder_path}")
                    sys.exit(1)
                
                logger.info(f"Processing {args.document_type} documents from: {folder_path}")
                results = pipeline.process_directory(str(folder_path), args.document_type)
                
                success_count = sum(1 for r in results if r['processing_status'] == 'success')
                total_count = len(results)
                logger.info(f"{args.document_type}: {success_count}/{total_count} documents processed successfully")
        
        logger.info("Pipeline execution completed")
        
    except Exception as e:
        logger.error(f"Pipeline execution failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 