"""
Network Path Diagnostic Script
Tests connectivity and access to the source path
"""

import os
import sys
from pathlib import Path
import time

def test_network_path():
    source_path = r"\\172.16.70.71\Mechanical Data\Nishant"
    
    print("Network Path Diagnostic")
    print("=" * 50)
    print(f"Testing path: {source_path}")
    print()
    
    try:
        # Test 1: Path exists
        print("Test 1: Checking if path exists...")
        path_obj = Path(source_path)
        if path_obj.exists():
            print("✓ Path exists")
        else:
            print("✗ Path does not exist")
            return False
            
        # Test 2: Can list directory
        print("Test 2: Attempting to list directory contents...")
        try:
            start_time = time.time()
            items = list(path_obj.iterdir())
            elapsed = time.time() - start_time
            print(f"✓ Directory listing successful ({len(items)} items found in {elapsed:.2f} seconds)")
            
            # Show first few items
            print("First 10 items:")
            for i, item in enumerate(items[:10]):
                item_type = "DIR" if item.is_dir() else "FILE"
                print(f"  {item_type}: {item.name}")
                
        except Exception as e:
            print(f"✗ Cannot list directory: {e}")
            return False
            
        # Test 3: Test glob search (this is what's likely causing the hang)
        print("\nTest 3: Testing glob search (this might be slow)...")
        try:
            start_time = time.time()
            # Try a simple glob first
            simple_files = list(path_obj.glob("*.dwg"))
            elapsed = time.time() - start_time
            print(f"✓ Simple glob search completed ({len(simple_files)} .dwg files found in {elapsed:.2f} seconds)")
            
            # Try recursive glob (this is what the script uses)
            print("Test 3b: Testing recursive glob search...")
            start_time = time.time()
            recursive_files = list(path_obj.glob("**/*.dwg"))[:5]  # Limit to first 5 to avoid hanging
            elapsed = time.time() - start_time
            print(f"✓ Recursive glob search completed ({len(recursive_files)} files found in {elapsed:.2f} seconds)")
            
        except Exception as e:
            print(f"✗ Glob search failed: {e}")
            return False
            
        print("\n" + "=" * 50)
        print("✓ All network tests passed successfully!")
        print("The network path is accessible and should work with the script.")
        return True
        
    except Exception as e:
        print(f"✗ Critical error: {e}")
        return False

def test_sample_product():
    source_path = r"\\172.16.70.71\Mechanical Data\Nishant"
    sample_product = "DR02-04-16-003_R3"  # From your CSV data
    
    print(f"\nTesting search for sample product: {sample_product}")
    print("-" * 50)
    
    try:
        path_obj = Path(source_path)
        
        # Test exact match
        print("Searching for exact matches...")
        start_time = time.time()
        exact_matches = list(path_obj.glob(f"**/{sample_product}.*"))
        elapsed = time.time() - start_time
        print(f"Found {len(exact_matches)} exact matches in {elapsed:.2f} seconds")
        
        for match in exact_matches[:3]:  # Show first 3
            print(f"  Found: {match}")
            
        # Test partial match
        print("Searching for partial matches...")
        start_time = time.time()
        partial_matches = list(path_obj.glob(f"**/*{sample_product}*.*"))
        elapsed = time.time() - start_time
        print(f"Found {len(partial_matches)} partial matches in {elapsed:.2f} seconds")
        
        for match in partial_matches[:3]:  # Show first 3
            print(f"  Found: {match}")
            
    except Exception as e:
        print(f"Error during product search: {e}")

if __name__ == "__main__":
    print("Starting network diagnostic...")
    success = test_network_path()
    
    if success:
        test_sample_product()
    else:
        print("\nNetwork path test failed. Please check:")
        print("1. Network connectivity to 172.16.70.71")
        print("2. Permissions to access the shared folder")
        print("3. Whether the path is correct")
        
    input("\nPress Enter to exit...")
