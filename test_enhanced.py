"""
Test script to validate CSV parsing and demonstrate the quantity handling logic
This script helps debug the file copy manager without actually copying files
"""

import csv
from pathlib import Path
import sys
import os

def analyze_quantity_distribution():
    """Analyze quantity distribution across all CSV files"""
    print("Analyzing quantity distribution...")
    print("=" * 50)
    
    csv_dir = Path("db")
    if not csv_dir.exists():
        print(f"ERROR: CSV directory 'db' not found")
        return
    
    csv_files = list(csv_dir.glob("*.csv"))
    
    total_stats = {
        'quantity_1': 0,
        'quantity_gt_1': 0,
        'total_products': 0
    }
    
    for csv_file in csv_files:
        print(f"\nAnalyzing: {csv_file.name}")
        print("-" * 40)
        
        # Extract material name
        material = csv_file.name.replace("Copy of THICKNESS AND MATERIAL DATA - ", "").replace(".csv", "")
        print(f"Material: {material}")
        
        file_stats = {
            'quantity_1': 0,
            'quantity_gt_1': 0,
            'total_products': 0
        }
        
        # Read CSV
        try:
            with open(csv_file, 'r', encoding='utf-8', errors='ignore') as file:
                sample = file.read(1024)
                file.seek(0)
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.DictReader(file, delimiter=delimiter)
                
                print("Sample products by quantity:")
                print("Quantity = 1:")
                qty_1_shown = 0
                print("Quantity > 1:")
                qty_gt_1_shown = 0
                
                for row in reader:
                    # Skip empty rows
                    if not any(row.values()):
                        continue
                        
                    product_name = row.get('Product Name', '').strip()
                    thickness = row.get('Thickness(mm)', '').strip()
                    quantity_str = row.get('Quantity', '').strip()
                    
                    if product_name:
                        file_stats['total_products'] += 1
                        
                        try:
                            quantity = int(float(quantity_str)) if quantity_str else 0
                            
                            if quantity == 1:
                                file_stats['quantity_1'] += 1
                                if qty_1_shown < 3:
                                    print(f"  {product_name[:40]:<40} (thickness: {thickness})")
                                    qty_1_shown += 1
                            elif quantity > 1:
                                file_stats['quantity_gt_1'] += 1
                                if qty_gt_1_shown < 3:
                                    print(f"  {product_name[:40]:<40} (thickness: {thickness}, qty: {quantity})")
                                    qty_gt_1_shown += 1
                                    
                        except ValueError:
                            pass
                
                print(f"\nFile Summary:")
                print(f"  Products with quantity = 1: {file_stats['quantity_1']}")
                print(f"  Products with quantity > 1: {file_stats['quantity_gt_1']}")
                print(f"  Total products: {file_stats['total_products']}")
                
                # Add to total stats
                for key in total_stats:
                    total_stats[key] += file_stats[key]
                
        except Exception as e:
            print(f"ERROR reading {csv_file}: {e}")
    
    print(f"\n{'='*50}")
    print("OVERALL SUMMARY")
    print(f"{'='*50}")
    print(f"Products with quantity = 1: {total_stats['quantity_1']} (will copy with original name)")
    print(f"Products with quantity > 1: {total_stats['quantity_gt_1']} (will copy with numbered prefixes)")
    print(f"Total products to process: {total_stats['total_products']}")

def demonstrate_file_naming():
    """Demonstrate the file naming logic"""
    print(f"\n{'='*50}")
    print("FILE NAMING DEMONSTRATION")
    print(f"{'='*50}")
    
    examples = [
        ("SC09-03-52-017_R3.dwg", 1, "1060 Alloy", "1"),
        ("DR02-04-16-003_R3.dwg", 4, "1060 Alloy", "1"),
        ("DD01-04-40-002_R3.step", 2, "AISI 1020", "0.6"),
    ]
    
    for filename, quantity, material, thickness in examples:
        print(f"\nExample: {filename}")
        print(f"Material: {material}, Thickness: {thickness}mm, Quantity: {quantity}")
        print(f"Destination folder: {material}/{thickness}/")
        
        if quantity == 1:
            print(f"Result: 1 file copied with original name:")
            print(f"  - {filename}")
        else:
            print(f"Result: {quantity} files copied with numbered prefixes:")
            for i in range(1, quantity + 1):
                print(f"  - {i}_{filename}")

def main():
    """Main test function"""
    print("File Copy Manager - Enhanced Test Suite")
    print("=" * 60)
    
    # Analyze quantity distribution
    analyze_quantity_distribution()
    
    # Demonstrate file naming
    demonstrate_file_naming()
    
    print(f"\n{'='*60}")
    print("Key Changes:")
    print("- Quantity = 1: Copy with original filename (no prefix)")
    print("- Quantity > 1: Copy with numbered prefixes (1_, 2_, 3_, etc.)")
    print("- All files organized by Material/Thickness/ folder structure")
    print(f"{'='*60}")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
