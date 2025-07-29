"""
File Copy Manager for CAD Files
Processes CSV files and copies design files based on thickness, quantity, and product names.

Author: GitHub Copilot
Date: July 29, 2025
"""

import os
import csv
import shutil
import logging
import glob
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import time
import sys


class FileCopyManager:
    def __init__(self, source_path: str, destination_base: str, csv_directory: str):
        """
        Initialize the File Copy Manager
        
        Args:
            source_path: Source directory containing design files
            destination_base: Base destination directory
            csv_directory: Directory containing CSV files
        """
        self.source_path = Path(source_path)
        self.destination_base = Path(destination_base)
        self.csv_directory = Path(csv_directory)
        
        # Setup logging
        self.setup_logging()
        
        # Statistics tracking
        self.stats = {
            'files_processed': 0,
            'files_copied': 0,
            'files_not_found': 0,
            'errors': 0
        }
        
        self.logger.info(f"Initialized FileCopyManager")
        self.logger.info(f"Source path: {self.source_path}")
        self.logger.info(f"Destination base: {self.destination_base}")
        self.logger.info(f"CSV directory: {self.csv_directory}")

    def setup_logging(self):
        """Setup logging configuration"""
        log_filename = f"file_copy_log_{int(time.time())}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_filename),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def validate_paths(self) -> bool:
        """Validate that all required paths exist"""
        self.logger.info("Validating paths...")
        
        # Check source path
        if not self.source_path.exists():
            self.logger.error(f"Source path does not exist: {self.source_path}")
            return False
        
        # Check CSV directory
        if not self.csv_directory.exists():
            self.logger.error(f"CSV directory does not exist: {self.csv_directory}")
            return False
            
        # Create destination base if it doesn't exist
        try:
            self.destination_base.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Destination directory ready: {self.destination_base}")
        except Exception as e:
            self.logger.error(f"Cannot create destination directory: {e}")
            return False
            
        self.logger.info("Path validation successful")
        return True

    def get_csv_files(self) -> List[Path]:
        """Get all CSV files from the directory"""
        csv_files = list(self.csv_directory.glob("*.csv"))
        self.logger.info(f"Found {len(csv_files)} CSV files")
        for csv_file in csv_files:
            self.logger.info(f"  - {csv_file.name}")
        return csv_files

    def extract_material_from_filename(self, filename: str) -> str:
        """Extract material name from CSV filename"""
        # Remove 'Copy of THICKNESS AND MATERIAL DATA - ' prefix and '.csv' suffix
        material = filename.replace("Copy of THICKNESS AND MATERIAL DATA - ", "").replace(".csv", "")
        self.logger.debug(f"Extracted material '{material}' from filename '{filename}'")
        return material

    def read_csv_data(self, csv_file: Path) -> List[Dict]:
        """Read CSV file and return list of dictionaries"""
        self.logger.info(f"Reading CSV file: {csv_file.name}")
        
        data = []
        try:
            with open(csv_file, 'r', encoding='utf-8', errors='ignore') as file:
                # Use csv.Sniffer to detect delimiter
                sample = file.read(1024)
                file.seek(0)
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.DictReader(file, delimiter=delimiter)
                
                for row_num, row in enumerate(reader, start=2):  # Start from 2 because header is row 1
                    # Skip empty rows
                    if not any(row.values()):
                        continue
                        
                    # Clean up the row data
                    cleaned_row = {}
                    for key, value in row.items():
                        if key:  # Skip empty column names
                            cleaned_row[key.strip()] = value.strip() if value else ""
                    
                    if cleaned_row.get('Product Name'):  # Only add rows with product names
                        cleaned_row['row_number'] = row_num
                        data.append(cleaned_row)
                        
        except Exception as e:
            self.logger.error(f"Error reading CSV file {csv_file}: {e}")
            
        self.logger.info(f"Read {len(data)} valid rows from {csv_file.name}")
        return data

    def find_source_files(self, product_name: str) -> List[Path]:
        """Find all files matching the product name in source directory"""
        self.logger.debug(f"Searching for files matching: {product_name}")
        
        # Try different file extensions commonly used for CAD files
        extensions = ['*', '*.dwg', '*.dxf', '*.step', '*.stp', '*.iges', '*.igs', '*.sat', '*.3dm', '*.catpart', '*.catproduct', '*.prt', '*.asm']
        
        found_files = []
        
        for ext in extensions:
            # Search with exact name
            pattern1 = f"**/{product_name}.{ext[2:]}" if ext != '*' else f"**/{product_name}.*"
            # Search with name containing the product name
            pattern2 = f"**/*{product_name}*.{ext[2:]}" if ext != '*' else f"**/*{product_name}*.*"
            
            for pattern in [pattern1, pattern2]:
                try:
                    matches = list(self.source_path.glob(pattern))
                    for match in matches:
                        if match.is_file() and match not in found_files:
                            found_files.append(match)
                            self.logger.debug(f"Found file: {match}")
                except Exception as e:
                    self.logger.debug(f"Error searching with pattern {pattern}: {e}")
                    
                if found_files:  # If we found files with exact match, don't search with wildcards
                    break
            
            if found_files:
                break
                
        if not found_files:
            self.logger.warning(f"No files found for product: {product_name}")
        else:
            self.logger.info(f"Found {len(found_files)} file(s) for product: {product_name}")
            
        return found_files

    def create_destination_folder(self, material: str, thickness: str) -> Path:
        """Create destination folder structure"""
        # Clean thickness value (remove any non-numeric characters except decimal point)
        clean_thickness = ''.join(c for c in str(thickness) if c.isdigit() or c == '.')
        
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

    def copy_files_based_on_quantity(self, source_files: List[Path], dest_folder: Path, 
                             product_name: str, quantity: int) -> int:
        """Copy files with numbered prefixes if quantity > 1, or original name if quantity = 1"""
        copied_count = 0
        
        for source_file in source_files:
            try:
                if quantity == 1:
                    # For quantity = 1, copy with original filename (no prefix)
                    dest_file = dest_folder / source_file.name
                    shutil.copy2(source_file, dest_file)
                    copied_count += 1
                    self.logger.info(f"Copied: {source_file.name} -> {dest_file}")
                else:
                    # For quantity > 1, copy with numbered prefixes
                    for i in range(1, quantity + 1):
                        # Create new filename with prefix
                        new_name = f"{i}_{source_file.name}"
                        dest_file = dest_folder / new_name
                        
                        # Copy the file
                        shutil.copy2(source_file, dest_file)
                        copied_count += 1
                        
                        self.logger.info(f"Copied: {source_file.name} -> {dest_file}")
                    
            except Exception as e:
                self.logger.error(f"Error copying file {source_file} to {dest_folder}: {e}")
                self.stats['errors'] += 1
                
        return copied_count

    def process_csv_file(self, csv_file: Path):
        """Process a single CSV file"""
        self.logger.info(f"\n{'='*50}")
        self.logger.info(f"Processing CSV file: {csv_file.name}")
        self.logger.info(f"{'='*50}")
        
        # Extract material from filename
        material = self.extract_material_from_filename(csv_file.name)
        
        # Read CSV data
        csv_data = self.read_csv_data(csv_file)
        
        if not csv_data:
            self.logger.warning(f"No data found in {csv_file.name}")
            return
            
        # Process each row
        for row in csv_data:
            try:
                self.process_row(row, material)
            except Exception as e:
                self.logger.error(f"Error processing row {row.get('row_number', 'unknown')}: {e}")
                self.stats['errors'] += 1

    def process_row(self, row: Dict, material: str):
        """Process a single row from CSV"""
        product_name = row.get('Product Name', '').strip()
        thickness = row.get('Thickness(mm)', '').strip()
        quantity_str = row.get('Quantity', '').strip()
        
        self.logger.debug(f"Processing row - Product: {product_name}, Thickness: {thickness}, Quantity: {quantity_str}")
        
        # Validate required fields
        if not product_name:
            self.logger.warning(f"Row {row.get('row_number', 'unknown')}: Missing product name")
            return
            
        if not thickness:
            self.logger.warning(f"Row {row.get('row_number', 'unknown')}: Missing thickness for {product_name}")
            return
            
        # Parse quantity
        try:
            quantity = int(float(quantity_str)) if quantity_str else 0
        except ValueError:
            self.logger.warning(f"Row {row.get('row_number', 'unknown')}: Invalid quantity '{quantity_str}' for {product_name}")
            return
            
        # Skip if quantity < 1, but process if quantity == 1
        if quantity < 1:
            self.logger.debug(f"Skipping {product_name}: quantity ({quantity}) < 1")
            return
            
        self.stats['files_processed'] += 1
        
        # Find source files
        source_files = self.find_source_files(product_name)
        
        if not source_files:
            self.logger.warning(f"No source files found for: {product_name}")
            self.stats['files_not_found'] += 1
            return
            
        # Create destination folder
        try:
            dest_folder = self.create_destination_folder(material, thickness)
        except Exception as e:
            self.logger.error(f"Failed to create destination folder for {product_name}: {e}")
            self.stats['errors'] += 1
            return
            
        # Copy files with appropriate naming
        copied_count = self.copy_files_based_on_quantity(source_files, dest_folder, product_name, quantity)
        self.stats['files_copied'] += copied_count
        
        if quantity == 1:
            self.logger.info(f"Successfully processed {product_name}: {copied_count} file(s) copied with original name")
        else:
            self.logger.info(f"Successfully processed {product_name}: {copied_count} file(s) copied with numbered prefixes")

    def run(self):
        """Main execution method"""
        self.logger.info("Starting File Copy Manager")
        self.logger.info(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        start_time = time.time()
        
        try:
            # Validate paths
            if not self.validate_paths():
                self.logger.error("Path validation failed. Exiting.")
                return False
                
            # Get CSV files
            csv_files = self.get_csv_files()
            
            if not csv_files:
                self.logger.error("No CSV files found. Exiting.")
                return False
                
            # Process each CSV file
            for csv_file in csv_files:
                try:
                    self.process_csv_file(csv_file)
                except Exception as e:
                    self.logger.error(f"Error processing {csv_file.name}: {e}")
                    self.stats['errors'] += 1
                    
            # Print summary
            self.print_summary(time.time() - start_time)
            return True
            
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            return False

    def print_summary(self, elapsed_time: float):
        """Print execution summary"""
        self.logger.info(f"\n{'='*50}")
        self.logger.info("EXECUTION SUMMARY")
        self.logger.info(f"{'='*50}")
        self.logger.info(f"Files processed: {self.stats['files_processed']}")
        self.logger.info(f"Files copied: {self.stats['files_copied']}")
        self.logger.info(f"Files not found: {self.stats['files_not_found']}")
        self.logger.info(f"Errors encountered: {self.stats['errors']}")
        self.logger.info(f"Execution time: {elapsed_time:.2f} seconds")
        self.logger.info(f"{'='*50}")


def main():
    """Main function"""
    # Configuration - Update these paths for your Windows environment
    SOURCE_PATH = r"\\172.16.70.71\Mechanical Data\Nishant"
    DESTINATION_BASE = r"\\172.16.70.71\mechanical data\Nishant\CRM V2 27-12-2018\DA03_25-1-2019 EPDM\001 DA SM\Factory layout"
    CSV_DIRECTORY = "db"  # Current directory's db folder
    
    print("File Copy Manager v1.0")
    print("=" * 50)
    print(f"Source: {SOURCE_PATH}")
    print(f"Destination: {DESTINATION_BASE}")
    print(f"CSV Directory: {CSV_DIRECTORY}")
    print("=" * 50)
    
    # Confirm before proceeding
    response = input("Do you want to proceed? (y/N): ").strip().lower()
    if response not in ['y', 'yes']:
        print("Operation cancelled by user.")
        return
    
    # Create and run the manager
    manager = FileCopyManager(SOURCE_PATH, DESTINATION_BASE, CSV_DIRECTORY)
    success = manager.run()
    
    if success:
        print("\nOperation completed successfully!")
    else:
        print("\nOperation completed with errors. Check the log file for details.")
        
    input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()
