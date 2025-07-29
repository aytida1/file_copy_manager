# File Copy Manager

A robust Python script for automatically copying CAD files based on CSV data containing product information, quantities, and material specifications.

## Overview

This script processes CSV files containing product data and automatically copies design files from a source directory to organized destination folders based on:
- Material type
- Thickness values
- Product quantities

## Features

- **Robust Error Handling**: Comprehensive error checking and logging
- **Automatic Directory Creation**: Creates destination folder structure automatically
- **Multiple File Format Support**: Handles various CAD file formats (DWG, DXF, STEP, etc.)
- **Detailed Logging**: Complete execution logs with timestamps
- **Statistics Tracking**: Reports on files processed, copied, and any errors
- **Virtual Environment Support**: Isolated Python environment for reliability

## Prerequisites

- Windows computer with network access to the server
- Python 3.7 or higher installed
- Access to the source and destination network paths

## Installation & Setup

1. **Copy all files** to your Windows computer:
   - `file_copy_manager.py`
   - `requirements.txt`
   - `setup.bat`
   - `run_file_copy_manager.bat`
   - `db/` folder with CSV files

2. **Run the setup**:
   - Double-click `setup.bat`
   - Wait for the virtual environment to be created and dependencies installed

## Configuration

Before running the script, verify the paths in `file_copy_manager.py`:

```python
SOURCE_PATH = r"\\172.16.70.71\Mechanical Data\Nishant"
DESTINATION_BASE = r"\\172.16.70.71\mechanical data\Nishant\CRM V2 27-12-2018\DA03_25-1-2019 EPDM\001 DA SM\Factory layout"
CSV_DIRECTORY = "db"
```

## Usage

### Quick Start
1. Double-click `run_file_copy_manager.bat`
2. Review the configuration displayed
3. Type 'y' to confirm and start processing

### Manual Execution
```batch
venv\Scripts\activate.bat
python file_copy_manager.py
```

## How It Works

1. **CSV Processing**: Reads each CSV file from the `db` directory
2. **Material Extraction**: Extracts material type from filename
3. **Row Processing**: For each row with quantity ≥ 1:
   - Searches for files matching the Product Name
   - Creates destination folder: `Material/Thickness/`
   - If quantity = 1: Copies file with original name
   - If quantity > 1: Copies files with numbered prefixes (1_, 2_, 3_, etc.)

## CSV File Format

Expected columns:
- `Product Name`: Name of the CAD file to search for
- `Thickness(mm)`: Thickness value for folder organization
- `Quantity`: Number of copies to create
- `Material`: Material type (extracted from filename)

## Example

For a product with:
- Product Name: `SC09-03-52-017_R3`
- Thickness: `1`
- Quantity: `1`
- Material: `1060 Alloy` (from filename)

The script will:
1. Search for `SC09-03-52-017_R3.*` in the source directory
2. Create folder: `destination/1060 Alloy/1/`
3. Copy the file once with original name: `SC09-03-52-017_R3.dwg`

For a product with quantity > 1:
- Product Name: `DR02-04-16-003_R3`
- Thickness: `1`
- Quantity: `4`
- Material: `1060 Alloy` (from filename)

The script will:
1. Search for `DR02-04-16-003_R3.*` in the source directory
2. Create folder: `destination/1060 Alloy/1/`
3. Copy the file 4 times as:
   - `1_DR02-04-16-003_R3.dwg`
   - `2_DR02-04-16-003_R3.dwg`
   - `3_DR02-04-16-003_R3.dwg`
   - `4_DR02-04-16-003_R3.dwg`

## File Search Strategy

The script searches for files using multiple strategies:
1. Exact filename match
2. Filename containing the product name
3. Multiple file extensions (DWG, DXF, STEP, STP, etc.)

## Logging

- Detailed log file created: `file_copy_log_[timestamp].log`
- Console output for real-time monitoring
- Statistics summary at completion

## Troubleshooting

### Common Issues

1. **Network Path Access**:
   - Ensure you have read access to the source path
   - Ensure you have write access to the destination path
   - Check network connectivity

2. **Python Not Found**:
   - Install Python 3.7+ from python.org
   - Ensure Python is added to PATH during installation

3. **Files Not Found**:
   - Check that CSV files are in the `db` directory
   - Verify source path contains the expected files
   - Check product names match actual filenames

4. **Permission Errors**:
   - Run as administrator if needed
   - Check file/folder permissions on network drives

### Log Analysis

Check the log file for:
- Files not found warnings
- Permission errors
- Network connectivity issues
- Invalid CSV data

## Safety Features

- **Confirmation prompt** before starting
- **Comprehensive logging** for audit trail
- **Error recovery** - continues processing after individual failures
- **Statistics tracking** for verification
- **Path validation** before execution

## Directory Structure

```
project/
├── file_copy_manager.py      # Main script
├── requirements.txt          # Python dependencies
├── setup.bat                # Setup script
├── run_file_copy_manager.bat # Execution script
├── README.md                # This file
├── db/                      # CSV files directory
│   ├── Copy of THICKNESS AND MATERIAL DATA - 1060 Alloy.csv
│   ├── Copy of THICKNESS AND MATERIAL DATA - AISI 1020.csv
│   ├── Copy of THICKNESS AND MATERIAL DATA - AISI 304.csv
│   └── Copy of THICKNESS AND MATERIAL DATA - AISI 316 Annealed Stainless Steel Bar (SS).csv
└── venv/                    # Virtual environment (created by setup)
```

## Support

If you encounter issues:
1. Check the log file for detailed error messages
2. Verify network path accessibility
3. Ensure CSV files are properly formatted
4. Confirm Python installation and PATH settings

## Version History

- v1.0: Initial release with full functionality and robust error handling
