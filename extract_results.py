import json
import os
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

class ResultExtractor:
    """Utility to extract and analyze JSON data from pipeline result files"""
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.results = []
        
    def load_all_results(self) -> List[Dict[str, Any]]:
        """Load all JSON result files from the output directory"""
        if not self.output_dir.exists():
            print(f"Output directory {self.output_dir} not found!")
            return []
            
        result_files = list(self.output_dir.glob("*_result.json"))
        print(f"Found {len(result_files)} result files")
        
        for file_path in result_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    data['_source_file'] = file_path.name
                    self.results.append(data)
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
                
        return self.results
    
    def get_successful_results(self) -> List[Dict[str, Any]]:
        """Get only successfully processed documents"""
        return [r for r in self.results if r.get('processing_status') == 'success']
    
    def get_failed_results(self) -> List[Dict[str, Any]]:
        """Get failed document processing results"""
        return [r for r in self.results if r.get('processing_status') == 'failed']
    
    def get_results_by_type(self, document_type: str) -> List[Dict[str, Any]]:
        """Get results for a specific document type"""
        return [r for r in self.results if r.get('document_type') == document_type]
    
    def extract_structured_data(self) -> List[Dict[str, Any]]:
        """Extract structured data from successful results"""
        successful = self.get_successful_results()
        extracted_data = []
        
        for result in successful:
            doc_type = result.get('document_type')
            structured_data = result.get('structured_data', {})
            
            # Add metadata
            data_entry = {
                'document_type': doc_type,
                'file_path': result.get('file_path'),
                'source_file': result.get('_source_file'),
                'extracted_text_length': len(result.get('extracted_text', '')),
            }
            
            # Add structured data fields
            if isinstance(structured_data, dict):
                data_entry.update(structured_data)
            
            extracted_data.append(data_entry)
            
        return extracted_data
    
    def create_summary_report(self) -> Dict[str, Any]:
        """Create a summary report of all results"""
        total_files = len(self.results)
        successful = len(self.get_successful_results())
        failed = len(self.get_failed_results())
        
        # Group by document type
        by_type = {}
        for result in self.results:
            doc_type = result.get('document_type', 'unknown')
            if doc_type not in by_type:
                by_type[doc_type] = {'success': 0, 'failed': 0}
            
            if result.get('processing_status') == 'success':
                by_type[doc_type]['success'] += 1
            else:
                by_type[doc_type]['failed'] += 1
        
        return {
            'total_files': total_files,
            'successful': successful,
            'failed': failed,
            'success_rate': (successful / total_files * 100) if total_files > 0 else 0,
            'by_document_type': by_type,
            'timestamp': datetime.now().isoformat()
        }

    
    def print_summary(self):
        """Print a formatted summary of results"""
        report = self.create_summary_report()
        
        print("\n" + "="*50)
        print("PIPELINE RESULTS SUMMARY")
        print("="*50)
        print(f"Total Files Processed: {report['total_files']}")
        print(f"Successful: {report['successful']}")
        print(f"Failed: {report['failed']}")
        print(f"Success Rate: {report['success_rate']:.1f}%")
        
        print("\nBy Document Type:")
        for doc_type, stats in report['by_document_type'].items():
            total = stats['success'] + stats['failed']
            success_rate = (stats['success'] / total * 100) if total > 0 else 0
            print(f"  {doc_type}: {stats['success']}/{total} ({success_rate:.1f}%)")
        
        print("\n" + "="*50)
    
    def print_failed_details(self):
        """Print details of failed processing attempts"""
        failed = self.get_failed_results()
        
        if not failed:
            print("No failed results found!")
            return
            
        print(f"\nFAILED PROCESSING DETAILS ({len(failed)} files):")
        print("-" * 50)
        
        for result in failed:
            print(f"File: {result.get('file_path', 'Unknown')}")
            print(f"Type: {result.get('document_type', 'Unknown')}")
            print(f"Error: {result.get('error', 'Unknown error')}")
            print("-" * 30)

def main():
    """Main function to demonstrate usage"""
    extractor = ResultExtractor()
    
    # Load all results
    results = extractor.load_all_results()
    
    if not results:
        print("No results found!")
        return
    
    # Print summary
    extractor.print_summary()
    
    # Print failed details
    extractor.print_failed_details()
    

if __name__ == "__main__":
    main() 