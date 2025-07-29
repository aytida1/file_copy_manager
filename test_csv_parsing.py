"""
Test script to validate CSV parsing and path operations
This script helps debug the file copy manager without actually copying files
"""

import csv
from pathlib import Path
import sys
import os

def test_csv_parsing():
    """Test CSV file parsing"""
    print("Testing CSV file parsing...")
    print("=" * 50)
    
    csv_dir = Path("db")
    if not csv_dir.exists():
        print(f"ERROR: CSV directory 'db' not found")
        return
    
    csv_files = list(csv_dir.glob("*.csv"))
    print(f"Found {len(csv_files)} CSV files:")
    
    for csv_file in csv_files:
        print(f"\nProcessing: {csv_file.name}")
        print("-" * 30)
        
        # Extract material name
        material = csv_file.name.replace("Copy of THICKNESS AND MATERIAL DATA - ", "").replace(".csv", "")
        print(f"Material: {material}")
        
        # Read CSV
        try:
            with open(csv_file, 'r', encoding='utf-8', errors='ignore') as file:
                sample = file.read(1024)
                file.seek(0)
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                print(f"Detected delimiter: '{delimiter}'")
                
                reader = csv.DictReader(file, delimiter=delimiter)
                
                valid_rows = 0
                quantity_gt_1 = 0
                
                print("\nFirst 5 valid rows with quantity > 1:")
                print("Product Name | Thickness | Quantity")
                print("-" * 60)
                
                shown_rows = 0
                for row in reader:
                    # Skip empty rows
                    if not any(row.values()):
                        continue
                        
                    product_name = row.get('Product Name', '').strip()
                    thickness = row.get('Thickness(mm)', '').strip()
                    quantity_str = row.get('Quantity', '').strip()
                    
                    if product_name:
                        valid_rows += 1
                        
                        try:
                            quantity = int(float(quantity_str)) if quantity_str else 0
                            if quantity > 1:
                                quantity_gt_1 += 1
                                if shown_rows < 5:
                                    print(f"{product_name[:30]:<30} | {thickness:<9} | {quantity}")
                                    shown_rows += 1
                        except ValueError:
                            pass
                
                print(f"\nSummary for {csv_file.name}:")
                print(f"  Valid rows: {valid_rows}")
                print(f"  Rows with quantity > 1: {quantity_gt_1}")
                
        except Exception as e:
            print(f"ERROR reading {csv_file}: {e}")

def test_path_operations():
    """Test path operations"""
    print("\n\nTesting path operations...")
    print("=" * 50)
    
    # Test Windows path handling
    source_path = r"\\172.16.70.71\Mechanical Data\Nishant"
    dest_base = r"\\172.16.70.71\mechanical data\Nishant\CRM V2 27-12-2018\DA03_25-1-2019 EPDM\001 DA SM\Factory layout"
    
    print(f"Source path: {source_path}")
    print(f"Destination base: {dest_base}")
    
    # Test creating folder structure
    materials = ["1060 Alloy", "AISI 1020", "AISI 304"]
    thicknesses = ["0.6", "1", "1.5", "2"]
    
    print("\nExample folder structure that would be created:")
    for material in materials:
        print(f"  {dest_base}\\{material}\\")
        for thickness in thicknesses[:2]:  # Show only first 2 thicknesses
            print(f"    └── {thickness}\\")

def main():
    """Main test function"""
    print("File Copy Manager - Test Suite")
    print("=" * 60)
    
    # Test CSV parsing
    test_csv_parsing()
    
    # Test path operations
    test_path_operations()
    
    print("\n" + "=" * 60)
    print("Test completed. Review the output above.")
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
