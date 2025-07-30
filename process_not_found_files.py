"""
Process Not Found Files - Recovery Script
Processes the not_found_files.txt and copies manually recovered files.

Author: GitHub Copilot
Date: July 30, 2025
"""

import os
import re
import shutil
import logging
import glob
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import time
import sys


class NotFoundFilesProcessor:
    def __init__(self, not_found_file: str, source_paths: List[str], destination_base: str):
        """
        Initialize the Not Found Files Processor
        
        Args:
            not_found_file: Path to the not_found_files.txt
            source_paths: List of source directories (will use first one for search)
            destination_base: Base destination directory
        """
        self.not_found_file = Path(not_found_file)
        self.source_paths = [Path(path) for path in source_paths]
        self.destination_base = Path(destination_base)
        
        # Setup logging
        self.setup_logging()
        
        # Statistics tracking
        self.stats = {
            'files_processed': 0,
            'files_copied': 0,
            'files_not_found': 0,
            'errors': 0
        }
        
        self.logger.info(f"Initialized NotFoundFilesProcessor")
        self.logger.info(f"Not found file: {self.not_found_file}")
        self.logger.info(f"Source paths: {len(self.source_paths)} directories")
        for i, source_path in enumerate(self.source_paths, 1):
            self.logger.info(f"  {i}. {source_path}")
        self.logger.info(f"Destination base: {self.destination_base}")

    def setup_logging(self):
        """Setup logging configuration"""
        log_filename = f"recovery_log_{int(time.time())}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_filename),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)

    def parse_not_found_file(self) -> List[Dict[str, str]]:
        """Parse the not_found_files.txt and extract product information"""
        self.logger.info(f"Parsing not found file: {self.not_found_file}")
        
        products = []
        
        try:
            with open(self.not_found_file, 'r', encoding='utf-8') as file:
                content = file.read()
                
                # Regex pattern to extract product information
                pattern = r'Product Name: (.+?)\s+Material: (.+?)\s+Thickness: (.+?)\s+Quantity: (\d+)'
                matches = re.findall(pattern, content)
                
                for match in matches:
                    product_name, material, thickness, quantity = match
                    products.append({
                        'Product Name': product_name.strip(),
                        'Material': material.strip(),
                        'Thickness': thickness.strip(),
                        'Quantity': quantity.strip()
                    })
                    
        except Exception as e:
            self.logger.error(f"Error parsing not found file: {e}")
            
        self.logger.info(f"Extracted {len(products)} products from not found file")
        return products

    def find_dxf_file(self, product_name: str) -> List[Path]:
        """Find DXF files matching the product name in the first source path"""
        self.logger.info(f"Searching for DXF files matching: {product_name}")
        
        found_files = []
        
        # Use only the first source path (where manually copied files are)
        source_path = self.source_paths[0]
        source_str = str(source_path)
        
        try:
            # Step 1: Search for exact product name with DXF extension
            dxf_pattern_exact = os.path.join(source_str, "**", f"{product_name}.dxf")
            matches_exact = glob.glob(dxf_pattern_exact, recursive=True)
            
            for match_str in matches_exact:
                match = Path(match_str)
                if match.is_file():
                    found_files.append(match)
                    self.logger.info(f"Found exact DXF match: {match}")
            
            # Also try uppercase extension
            dxf_pattern_exact_upper = os.path.join(source_str, "**", f"{product_name}.DXF")
            matches_exact_upper = glob.glob(dxf_pattern_exact_upper, recursive=True)
            
            for match_str in matches_exact_upper:
                match = Path(match_str)
                if match.is_file() and match not in found_files:
                    found_files.append(match)
                    self.logger.info(f"Found exact DXF match (uppercase): {match}")
            
            # Step 2: If no exact matches, try partial matches
            if not found_files:
                dxf_pattern_partial = os.path.join(source_str, "**", f"*{product_name}*.dxf")
                matches_partial = glob.glob(dxf_pattern_partial, recursive=True)
                
                for match_str in matches_partial:
                    match = Path(match_str)
                    if match.is_file():
                        found_files.append(match)
                        self.logger.info(f"Found partial DXF match: {match}")
                
                # Try uppercase for partial matches
                dxf_pattern_partial_upper = os.path.join(source_str, "**", f"*{product_name}*.DXF")
                matches_partial_upper = glob.glob(dxf_pattern_partial_upper, recursive=True)
                
                for match_str in matches_partial_upper:
                    match = Path(match_str)
                    if match.is_file() and match not in found_files:
                        found_files.append(match)
                        self.logger.info(f"Found partial DXF match (uppercase): {match}")
                        
        except Exception as e:
            self.logger.error(f"Error searching for {product_name}: {e}")
            
        if not found_files:
            self.logger.warning(f"No DXF files found for product: {product_name}")
        else:
            self.logger.info(f"Found {len(found_files)} DXF file(s) for product: {product_name}")
            
        return found_files

    def create_destination_folder(self, material: str, thickness: str) -> Path:
        """Create destination folder structure"""
        # Clean thickness value
        clean_thickness = thickness.replace('mm', '').strip()
        clean_thickness = ''.join(c for c in clean_thickness if c.isdigit() or c == '.')
        
        if not clean_thickness:
            clean_thickness = "unknown"
            
        dest_folder = self.destination_base / material / clean_thickness
        
        try:
            dest_folder.mkdir(parents=True, exist_ok=True)
            self.logger.debug(f"Created/verified destination folder: {dest_folder}")
        except Exception as e:
            self.logger.error(f"Error creating destination folder {dest_folder}: {e}")
            raise
            
        return dest_folder

    def copy_files_with_quantity(self, source_files: List[Path], dest_folder: Path, 
                                product_name: str, quantity: int) -> int:
        """Copy files with numbered prefixes based on quantity"""
        copied_count = 0
        
        for source_file in source_files:
            try:
                if quantity == 1:
                    # For quantity = 1, copy with original filename
                    dest_file = dest_folder / source_file.name
                    shutil.copy2(source_file, dest_file)
                    copied_count += 1
                else:
                    # For quantity > 1, copy with numbered prefixes
                    for i in range(1, quantity + 1):
                        new_name = f"{i}_{source_file.name}"
                        dest_file = dest_folder / new_name
                        shutil.copy2(source_file, dest_file)
                        copied_count += 1
                    
            except Exception as e:
                self.logger.error(f"Error copying file {source_file}: {e}")
                self.stats['errors'] += 1
        
        # Log summary
        if quantity == 1:
            self.logger.info(f"Done with copying {len(source_files)} file(s) for '{product_name}' (quantity: 1)")
        else:
            self.logger.info(f"Done with pre-namespacing of {quantity} quantity of '{product_name}' - copied {copied_count} files")
                
        return copied_count

    def process_product(self, product: Dict[str, str]):
        """Process a single product from the not found list"""
        product_name = product['Product Name']
        material = product['Material']
        thickness = product['Thickness']
        quantity = int(product['Quantity'])
        
        self.logger.info(f"Processing: {product_name} | Material: {material} | Thickness: {thickness} | Quantity: {quantity}")
        
        self.stats['files_processed'] += 1
        
        # Find DXF files
        source_files = self.find_dxf_file(product_name)
        
        if not source_files:
            self.logger.warning(f"No DXF files found for: {product_name}")
            self.stats['files_not_found'] += 1
            return
            
        # Create destination folder
        try:
            dest_folder = self.create_destination_folder(material, thickness)
        except Exception as e:
            self.logger.error(f"Failed to create destination folder for {product_name}: {e}")
            self.stats['errors'] += 1
            return
            
        # Copy files with quantity-based naming
        copied_count = self.copy_files_with_quantity(source_files, dest_folder, product_name, quantity)
        self.stats['files_copied'] += copied_count

    def run(self):
        """Main execution method"""
        self.logger.info("Starting Not Found Files Recovery")
        self.logger.info(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        start_time = time.time()
        
        try:
            # Check if not found file exists
            if not self.not_found_file.exists():
                self.logger.error(f"Not found file does not exist: {self.not_found_file}")
                return False
                
            # Parse the not found file
            products = self.parse_not_found_file()
            
            if not products:
                self.logger.error("No products found in the not found file")
                return False
                
            # Process each product
            for product in products:
                try:
                    self.process_product(product)
                except Exception as e:
                    self.logger.error(f"Error processing product {product.get('Product Name', 'unknown')}: {e}")
                    self.stats['errors'] += 1
                    
            # Print summary
            self.print_summary(time.time() - start_time)
            
            # Happy completion message
            self.logger.info(f"\n{'='*60}")
            self.logger.info("🎉 NOT FOUND FILES RECOVERY COMPLETED! 🎉")
            self.logger.info("😊 😊 😊 HAPPY RECOVERY SMILEYS! 😊 😊 😊")
            self.logger.info(f"{'='*60}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            return False

    def print_summary(self, elapsed_time: float):
        """Print execution summary"""
        self.logger.info(f"\n{'='*50}")
        self.logger.info("RECOVERY SUMMARY")
        self.logger.info(f"{'='*50}")
        self.logger.info(f"Products processed: {self.stats['files_processed']}")
        self.logger.info(f"Files copied: {self.stats['files_copied']}")
        self.logger.info(f"Files not found: {self.stats['files_not_found']}")
        self.logger.info(f"Errors encountered: {self.stats['errors']}")
        self.logger.info(f"Execution time: {elapsed_time:.2f} seconds")
        self.logger.info(f"{'='*50}")


def main():
    """Main function"""
    # Configuration
    NOT_FOUND_FILE = "not_found_files_1753824143.txt"
    SOURCE_PATHS = [
        r"\\172.16.70.71\mechanical data\Nishant\CRM V2 27-12-2018\DA03_25-1-2019 EPDM\001 DA SM\Factory layout\Missing file",
        r"\\172.16.70.71\mechanical data\Nishant\CRM V2 27-12-2018\DA03_25-1-2019 EPDM\001 DA SM\Drawing & BOM"
    ]
    DESTINATION_BASE = r"\\172.16.70.71\mechanical data\Nishant\CRM V2 27-12-2018\DA03_25-1-2019 EPDM\001 DA SM\Factory layout\Drawing Files"
    
    print("Not Found Files Recovery v1.0")
    print("=" * 60)
    print(f"Not Found File: {NOT_FOUND_FILE}")
    print(f"Search Path: {SOURCE_PATHS[0]}")
    print(f"Destination: {DESTINATION_BASE}")
    print(f"File Type: DXF files only")
    print("=" * 60)
    
    # Confirm before proceeding
    response = input("Do you want to proceed with recovery? (y/N): ").strip().lower()
    if response not in ['y', 'yes']:
        print("Recovery cancelled by user.")
        return
    
    # Create and run the processor
    processor = NotFoundFilesProcessor(NOT_FOUND_FILE, SOURCE_PATHS, DESTINATION_BASE)
    success = processor.run()
    
    if success:
        print("\n" + "="*60)
        print("🎉 RECOVERY COMPLETED SUCCESSFULLY! 🎉")
        print("😊 😊 😊 ALL MISSING FILES PROCESSED! 😊 😊 😊")
        print("🚀 Recovery mission accomplished! 🚀")
        print("="*60)
    else:
        print("\n❌ Recovery completed with errors. Check the log file for details.")
        
    input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()
