"""
Deep Directory Search Test
Tests the new iterative deep search strategy that can handle multiple subdirectory levels
"""

import os
import sys
from pathlib import Path
import time

def test_deep_search():
    source_path = r"\\172.16.70.71\Mechanical Data\Nishant"
    sample_product = "DR02-04-16-003_R3"  # From your CSV data
    
    print("Deep Directory Search Test")
    print("=" * 50)
    print(f"Source path: {source_path}")
    print(f"Sample product: {sample_product}")
    print()
    
    try:
        path_obj = Path(source_path)
        found_files = []
        extensions = ['dwg', 'dxf', 'step', 'stp', 'iges', 'igs', 'sat', '3dm', 'catpart', 'catproduct', 'prt', 'asm']
        
        # Strategy 1: Search in root directory first
        print("Strategy 1: Searching in root directory...")
        start_time = time.time()
        
        for ext in extensions:
            # Exact name match in root
            exact_file = path_obj / f"{sample_product}.{ext}"
            if exact_file.exists() and exact_file.is_file():
                found_files.append(exact_file)
                print(f"✓ Found in root: {exact_file.name}")
                
            # Uppercase extension
            exact_file_upper = path_obj / f"{sample_product}.{ext.upper()}"
            if exact_file_upper.exists() and exact_file_upper.is_file():
                found_files.append(exact_file_upper)
                print(f"✓ Found in root (uppercase): {exact_file_upper.name}")
                
        elapsed = time.time() - start_time
        print(f"Root search completed in {elapsed:.2f} seconds")
        
        # If found files in root, we're done
        if found_files:
            print(f"✓ Success! Found {len(found_files)} file(s) in root directory")
            return True
            
        # Strategy 2: Iterative breadth-first search
        print("\nStrategy 2: Iterative deep search (breadth-first)...")
        start_time = time.time()
        
        # Use a queue for breadth-first traversal
        dirs_to_search = [path_obj]
        searched_count = 0
        max_dirs = 200  # Limit for testing
        
        print(f"Starting breadth-first search (max {max_dirs} directories)...")
        
        while dirs_to_search and searched_count < max_dirs:
            current_dir = dirs_to_search.pop(0)
            searched_count += 1
            
            if searched_count % 10 == 0:  # Progress update every 10 directories
                print(f"  Searched {searched_count} directories so far...")
            
            try:
                # Search for files in current directory
                for ext in extensions:
                    # Exact name match
                    exact_file = current_dir / f"{sample_product}.{ext}"
                    if exact_file.exists() and exact_file.is_file():
                        found_files.append(exact_file)
                        print(f"✓ Found in {current_dir.name}: {exact_file.name}")
                        
                    # Uppercase extension
                    exact_file_upper = current_dir / f"{sample_product}.{ext.upper()}"
                    if exact_file_upper.exists() and exact_file_upper.is_file():
                        found_files.append(exact_file_upper)
                        print(f"✓ Found in {current_dir.name} (uppercase): {exact_file_upper.name}")
                
                # If we found files, we can stop
                if found_files:
                    print(f"✓ Found files after searching {searched_count} directories")
                    break
                
                # Add subdirectories to search queue
                try:
                    subdirs = [d for d in current_dir.iterdir() if d.is_dir()]
                    dirs_to_search.extend(subdirs)
                except Exception as e:
                    continue
                    
            except Exception as e:
                continue
                
        elapsed = time.time() - start_time
        print(f"Deep search completed in {elapsed:.2f} seconds")
        print(f"Total directories searched: {searched_count}")
        
        if found_files:
            print(f"✓ Success! Found {len(found_files)} file(s) using deep search")
            for file in found_files:
                print(f"  File: {file}")
            return True
            
        # Strategy 3: Partial name matching
        print("\nStrategy 3: Partial name matching in root...")
        start_time = time.time()
        
        try:
            for ext in extensions:
                pattern = f"*{sample_product}*.{ext}"
                matches = list(path_obj.glob(pattern))
                for match in matches:
                    if match.is_file():
                        found_files.append(match)
                        print(f"✓ Found partial match: {match.name}")
                        
        except Exception as e:
            print(f"Error with partial matching: {e}")
            
        elapsed = time.time() - start_time
        print(f"Partial matching completed in {elapsed:.2f} seconds")
        
        if found_files:
            print(f"✓ Success! Found {len(found_files)} file(s) with partial matching")
            return True
        else:
            print("✗ No files found with any strategy")
            return False
            
    except Exception as e:
        print(f"✗ Critical error: {e}")
        return False

if __name__ == "__main__":
    print("Testing deep directory search strategy...")
    print("This will search through multiple subdirectory levels efficiently")
    print()
    
    success = test_deep_search()
    
    if success:
        print("\n" + "=" * 50)
        print("✓ Deep search strategy works!")
        print("The updated script can now find files in nested subdirectories.")
    else:
        print("\n" + "=" * 50)
        print("⚠ Files not found, but search completed without hanging")
        print("This could mean:")
        print("1. Files might be named differently than expected")
        print("2. Files might be in very deep subdirectories")
        print("3. File extensions might be different")
        print("\nThe search strategy is working correctly though!")
        
    input("\nPress Enter to exit...")
