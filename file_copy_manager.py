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
    def __init__(self, source_paths: List[str], destination_base: str, csv_directory: str):
        """
        Initialize the File Copy Manager
        
        Args:
            source_paths: List of source directories containing design files
            destination_base: Base destination directory
            csv_directory: Directory containing CSV files
        """
        self.source_paths = [Path(path) for path in source_paths]
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
        self.logger.info(f"Source paths: {len(self.source_paths)} directories")
        for i, source_path in enumerate(self.source_paths, 1):
            self.logger.info(f"  {i}. {source_path}")
        self.logger.info(f"Destination base: {self.destination_base}")
        self.logger.info(f"CSV directory: {self.csv_directory}")

    def setup_logging(self):
        """Setup logging configuration"""
        log_filename = f"file_copy_log_{int(time.time())}.log"
        
        logging.basicConfig(
            level=logging.DEBUG,  # Changed to DEBUG for more detailed logging
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
        
        # Check all source paths with detailed logging
        for i, source_path in enumerate(self.source_paths, 1):
            self.logger.info(f"Checking source path {i}: {source_path}")
            try:
                if not source_path.exists():
                    self.logger.error(f"Source path {i} does not exist: {source_path}")
                    return False
                else:
                    self.logger.info(f"Source path {i} accessible: {source_path}")
                    # Try to list some files to verify read access
                    try:
                        file_count = len(list(source_path.iterdir()))
                        self.logger.info(f"Source path {i} contains {file_count} items")
                    except Exception as e:
                        self.logger.warning(f"Cannot list source path {i} contents: {e}")
            except Exception as e:
                self.logger.error(f"Error accessing source path {i}: {e}")
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

    def read_csv_data(self, csv_file: Path) -> List[Dict[str, str]]:
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
        """Find DXF files matching the product name using efficient two-step search"""
        self.logger.info(f"Searching for DXF files matching: {product_name}")
        
        found_files = []
        
        try:
            # Search in all source paths
            for source_idx, source_path in enumerate(self.source_paths, 1):
                self.logger.info(f"Searching in source path {source_idx}: {source_path}")
                
                # Convert source_path to string for glob module
                source_str = str(source_path)
                
                # Step 1: Find any file with the product name (to locate the directory)
                self.logger.debug(f"Step 1: Searching for any file with name: {product_name}")
                
                # Search for exact product name with any extension
                any_file_pattern = os.path.join(source_str, "**", f"{product_name}.*")
                any_files = glob.glob(any_file_pattern, recursive=True)
                
                # Also search for partial matches
                if not any_files:
                    partial_pattern = os.path.join(source_str, "**", f"*{product_name}*.*")
                    any_files = glob.glob(partial_pattern, recursive=True)
                
                if any_files:
                    self.logger.debug(f"Found {len(any_files)} file(s) with product name, now searching for DXF")
                    
                    # Step 2: For each found file, look for DXF files in the same directory
                    directories_checked = set()
                    
                    for any_file_str in any_files:
                        any_file_path = Path(any_file_str)
                        parent_dir = any_file_path.parent
                        
                        # Skip if we already checked this directory
                        if str(parent_dir) in directories_checked:
                            continue
                        directories_checked.add(str(parent_dir))
                        
                        self.logger.debug(f"Step 2: Searching for DXF files in directory: {parent_dir}")
                        
                        # Look for DXF files with exact product name in this directory
                        dxf_pattern_exact = os.path.join(str(parent_dir), f"{product_name}.dxf")
                        dxf_files_exact = glob.glob(dxf_pattern_exact)
                        
                        # Also try uppercase extension
                        dxf_pattern_exact_upper = os.path.join(str(parent_dir), f"{product_name}.DXF")
                        dxf_files_exact_upper = glob.glob(dxf_pattern_exact_upper)
                        
                        # Combine exact matches
                        exact_dxf_files = dxf_files_exact + dxf_files_exact_upper
                        
                        for dxf_file_str in exact_dxf_files:
                            dxf_file = Path(dxf_file_str)
                            if dxf_file.is_file() and dxf_file not in found_files:
                                found_files.append(dxf_file)
                                self.logger.info(f"Found exact DXF match in source {source_idx}: {dxf_file}")
                        
                        # If no exact DXF matches, try partial matches in this directory
                        if not exact_dxf_files:
                            dxf_pattern_partial = os.path.join(str(parent_dir), f"*{product_name}*.dxf")
                            dxf_files_partial = glob.glob(dxf_pattern_partial)
                            
                            # Also try uppercase extension for partial
                            dxf_pattern_partial_upper = os.path.join(str(parent_dir), f"*{product_name}*.DXF")
                            dxf_files_partial_upper = glob.glob(dxf_pattern_partial_upper)
                            
                            # Combine partial matches
                            partial_dxf_files = dxf_files_partial + dxf_files_partial_upper
                            
                            for dxf_file_str in partial_dxf_files:
                                dxf_file = Path(dxf_file_str)
                                if dxf_file.is_file() and dxf_file not in found_files:
                                    found_files.append(dxf_file)
                                    self.logger.info(f"Found partial DXF match in source {source_idx}: {dxf_file}")
                
                # If we found DXF files in this source path, stop searching other source paths
                if found_files:
                    self.logger.info(f"Found {len(found_files)} DXF file(s) in source {source_idx}, stopping search")
                    break
                else:
                    self.logger.debug(f"No files found with product name '{product_name}' in source {source_idx}")
                    
        except Exception as e:
            self.logger.error(f"Critical error during DXF file search for {product_name}: {e}")
            
        if not found_files:
            self.logger.warning(f"No DXF files found for product: {product_name} in any source path")
        else:
            self.logger.info(f"Found {len(found_files)} DXF file(s) total for product: {product_name}")
            
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
                else:
                    # For quantity > 1, copy with numbered prefixes
                    for i in range(1, quantity + 1):
                        # Create new filename with prefix
                        new_name = f"{i}_{source_file.name}"
                        dest_file = dest_folder / new_name
                        
                        # Copy the file
                        shutil.copy2(source_file, dest_file)
                        copied_count += 1
                    
            except Exception as e:
                self.logger.error(f"Error copying file {source_file} to {dest_folder}: {e}")
                self.stats['errors'] += 1
        
        # Log summary message after all files are copied
        if quantity == 1:
            self.logger.info(f"Done with copying {len(source_files)} file(s) for '{product_name}' (quantity: 1)")
        else:
            self.logger.info(f"Done with pre-namespacing of {quantity} quantity of '{product_name}' - copied {copied_count} files")
                
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
        for row_index, row in enumerate(csv_data, start=1):
            try:
                self.logger.info(f"Processing row {row_index}/{len(csv_data)}: {row.get('Product Name', 'Unknown')}")
                self.process_row(row, material)
            except Exception as e:
                self.logger.error(f"Error processing row {row.get('row_number', 'unknown')}: {e}")
                self.stats['errors'] += 1
                
        self.logger.info(f"Completed processing {csv_file.name}")

    def process_row(self, row: Dict[str, str], material: str):
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
            
            # Happy completion message
            self.logger.info(f"\n{'='*60}")
            self.logger.info("🎉 ALL CSV FILES PROCESSED SUCCESSFULLY! 🎉")
            self.logger.info("😊 😊 😊 HAPPY HAPPY SMILEYS! 😊 😊 😊")
            self.logger.info(f"{'='*60}")
            
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
    # Configuration - Multiple source paths with efficient DXF-focused search
    SOURCE_PATHS = [
        r"\\172.16.70.71\mechanical data\Nishant\CRM V2 27-12-2018\DA03_25-1-2019 EPDM\001 DA SM\Drawing & BOM",
        r"\\172.16.70.71\mechanical data\Nishant\Drug Dispensor DD01",
        r"\\172.16.70.71\mechanical data\Nishant\CRM V2 27-12-2018"
    ]
    DESTINATION_BASE = r"\\172.16.70.71\mechanical data\Nishant\CRM V2 27-12-2018\DA03_25-1-2019 EPDM\001 DA SM\Factory layout\Drawing Files"
    CSV_DIRECTORY = "db"  # Current directory's db folder
    
    print("File Copy Manager v2.1 - Efficient DXF Search")
    print("=" * 60)
    print(f"Source Paths ({len(SOURCE_PATHS)} directories):")
    for i, path in enumerate(SOURCE_PATHS, 1):
        print(f"  {i}. {path}")
    print(f"Destination: {DESTINATION_BASE}")
    print(f"CSV Directory: {CSV_DIRECTORY}")
    print(f"File Type: DXF files only (efficient search)")
    print("=" * 60)
    
    # Confirm before proceeding
    response = input("Do you want to proceed? (y/N): ").strip().lower()
    if response not in ['y', 'yes']:
        print("Operation cancelled by user.")
        return
    
    # Create and run the manager
    manager = FileCopyManager(SOURCE_PATHS, DESTINATION_BASE, CSV_DIRECTORY)
    success = manager.run()
    
    if success:
        print("\n" + "="*60)
        print("🎉 OPERATION COMPLETED SUCCESSFULLY! 🎉")
        print("😊 😊 😊 ALL CSV FILES PROCESSED! 😊 😊 😊")
        print("🚀 Ready for production use! 🚀")
        print("="*60)
    else:
        print("\n❌ Operation completed with errors. Check the log file for details.")
        
    input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()
