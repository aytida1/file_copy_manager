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
        """Find all files matching the product name in multiple source directories with depth limit"""
        self.logger.info(f"Searching for files matching: {product_name}")
        
        found_files = []
        max_depth = 7  # Search up to 7 levels deep
        
        try:
            # Try different file extensions commonly used for CAD files
            extensions = ['dwg', 'dxf', 'step', 'stp', 'iges', 'igs', 'sat', '3dm', 'catpart', 'catproduct', 'prt', 'asm']
            
            # Search in all source paths
            for source_idx, source_path in enumerate(self.source_paths, 1):
                self.logger.debug(f"Searching in source path {source_idx}: {source_path}")
                
                # Strategy 1: Search in root directory first (fastest)
                self.logger.debug(f"Searching in root of source {source_idx}: {source_path}")
                for ext in extensions:
                    try:
                        # Exact name match in root
                        exact_file = source_path / f"{product_name}.{ext}"
                        if exact_file.exists() and exact_file.is_file():
                            found_files.append(exact_file)
                            self.logger.debug(f"Found exact match in root of source {source_idx}: {exact_file}")
                            
                        # Also try uppercase extension
                        exact_file_upper = source_path / f"{product_name}.{ext.upper()}"
                        if exact_file_upper.exists() and exact_file_upper.is_file():
                            found_files.append(exact_file_upper)
                            self.logger.debug(f"Found exact match in root of source {source_idx} (uppercase): {exact_file_upper}")
                            
                    except Exception as e:
                        self.logger.debug(f"Error checking {product_name}.{ext} in source {source_idx}: {e}")
                        continue
                        
                # If found files in root, continue to next source path (but don't return yet)
                if found_files:
                    self.logger.info(f"Found {len(found_files)} file(s) in root of source {source_idx}")
                    continue
                    
                # Strategy 2: Iterative breadth-first search through directory tree with depth limit
                self.logger.debug(f"Starting iterative deep search in source {source_idx}...")
                
                # Use a queue for breadth-first traversal with depth tracking
                dirs_to_search = [(source_path, 0)]  # (directory, depth)
                searched_count = 0
                max_dirs = 500  # Limit per source path to prevent infinite searching
                
                while dirs_to_search and searched_count < max_dirs:
                    current_dir, current_depth = dirs_to_search.pop(0)
                    searched_count += 1
                    
                    # Skip if we've reached maximum depth
                    if current_depth >= max_depth:
                        continue
                    
                    try:
                        self.logger.debug(f"Searching directory {searched_count} at depth {current_depth}: {current_dir.name}")
                        
                        # Search for files in current directory
                        for ext in extensions:
                            try:
                                # Exact name match
                                exact_file = current_dir / f"{product_name}.{ext}"
                                if exact_file.exists() and exact_file.is_file():
                                    found_files.append(exact_file)
                                    self.logger.debug(f"Found exact match in source {source_idx} at depth {current_depth}: {exact_file}")
                                    
                                # Uppercase extension
                                exact_file_upper = current_dir / f"{product_name}.{ext.upper()}"
                                if exact_file_upper.exists() and exact_file_upper.is_file():
                                    found_files.append(exact_file_upper)
                                    self.logger.debug(f"Found exact match in source {source_idx} at depth {current_depth} (uppercase): {exact_file_upper}")
                                    
                            except Exception as e:
                                self.logger.debug(f"Error checking file in {current_dir}: {e}")
                                continue
                        
                        # Add subdirectories to search queue (only if under depth limit)
                        if current_depth < max_depth - 1:
                            try:
                                subdirs = [d for d in current_dir.iterdir() if d.is_dir()]
                                for subdir in subdirs:
                                    dirs_to_search.append((subdir, current_depth + 1))
                                self.logger.debug(f"Added {len(subdirs)} subdirectories at depth {current_depth + 1}")
                            except Exception as e:
                                self.logger.debug(f"Error listing subdirectories in {current_dir}: {e}")
                                continue
                                
                    except Exception as e:
                        self.logger.debug(f"Error searching directory {current_dir}: {e}")
                        continue
                        
                self.logger.debug(f"Searched {searched_count} directories in source {source_idx}")
                
                # Strategy 3: If still no exact matches, try partial name matching in limited directories
                if not found_files:
                    self.logger.debug(f"Trying partial name matching in source {source_idx}...")
                    try:
                        # Search root directory for partial matches
                        for ext in extensions:
                            pattern = f"*{product_name}*.{ext}"
                            matches = list(source_path.glob(pattern))
                            for match in matches:
                                if match.is_file() and match not in found_files:
                                    found_files.append(match)
                                    self.logger.debug(f"Found partial match in root of source {source_idx}: {match}")
                                    
                            # Also try uppercase
                            pattern_upper = f"*{product_name}*.{ext.upper()}"
                            matches_upper = list(source_path.glob(pattern_upper))
                            for match in matches_upper:
                                if match.is_file() and match not in found_files:
                                    found_files.append(match)
                                    self.logger.debug(f"Found partial match in root of source {source_idx} (uppercase): {match}")
                        
                        # If still no files, try partial matching in first level subdirectories
                        if not found_files:
                            try:
                                first_level_dirs = [d for d in source_path.iterdir() if d.is_dir()][:10]  # Limit to first 10
                                for subdir in first_level_dirs:
                                    for ext in extensions:
                                        try:
                                            pattern = f"*{product_name}*.{ext}"
                                            matches = list(subdir.glob(pattern))
                                            for match in matches:
                                                if match.is_file() and match not in found_files:
                                                    found_files.append(match)
                                                    self.logger.debug(f"Found partial match in source {source_idx} subdir {subdir.name}: {match}")
                                                    
                                        except Exception as e:
                                            continue
                                            
                                    if found_files:  # Stop after finding files
                                        break
                                        
                            except Exception as e:
                                self.logger.debug(f"Error in partial matching for source {source_idx}: {e}")
                                
                    except Exception as e:
                        self.logger.warning(f"Error with partial name matching in source {source_idx}: {e}")
                
                # If we found files in this source path, we can break and return them
                if found_files:
                    self.logger.info(f"Found {len(found_files)} file(s) in source {source_idx}: {source_path}")
                    break
                    
        except Exception as e:
            self.logger.error(f"Critical error during file search for {product_name}: {e}")
            
        if not found_files:
            self.logger.warning(f"No files found for product: {product_name} in any source path")
        else:
            self.logger.info(f"Found {len(found_files)} file(s) total for product: {product_name}")
            
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
        for row_index, row in enumerate(csv_data, start=1):
            try:
                self.logger.info(f"Processing row {row_index}/{len(csv_data)}: {row.get('Product Name', 'Unknown')}")
                self.process_row(row, material)
            except Exception as e:
                self.logger.error(f"Error processing row {row.get('row_number', 'unknown')}: {e}")
                self.stats['errors'] += 1
                
        self.logger.info(f"Completed processing {csv_file.name}")

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
    # Configuration - Multiple source paths with depth-limited search
    SOURCE_PATHS = [
        r"\\172.16.70.71\mechanical data\Nishant\CRM V2 27-12-2018\DA03_25-1-2019 EPDM\001 DA SM\Drawing & BOM",
        r"\\172.16.70.71\mechanical data\Nishant\Drug Dispensor DD01",
        r"\\172.16.70.71\mechanical data\Nishant\CRM V2 27-12-2018"
    ]
    DESTINATION_BASE = r"\\172.16.70.71\mechanical data\Nishant\CRM V2 27-12-2018\DA03_25-1-2019 EPDM\001 DA SM\Factory layout\Drawing Files"
    CSV_DIRECTORY = "db"  # Current directory's db folder
    
    print("File Copy Manager v2.0 - Multi-Source Search")
    print("=" * 60)
    print(f"Source Paths ({len(SOURCE_PATHS)} directories):")
    for i, path in enumerate(SOURCE_PATHS, 1):
        print(f"  {i}. {path}")
    print(f"Destination: {DESTINATION_BASE}")
    print(f"CSV Directory: {CSV_DIRECTORY}")
    print(f"Search Depth: Up to 7 levels deep")
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
        print("\nOperation completed successfully!")
    else:
        print("\nOperation completed with errors. Check the log file for details.")
        
    input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()
