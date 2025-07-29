# Deployment Checklist for File Copy Manager

## Pre-Deployment Steps

### 1. File Preparation
- [ ] Copy all files to Windows computer with server access
- [ ] Ensure `db` folder contains all 4 CSV files
- [ ] Verify Python 3.7+ is installed on target machine

### 2. Files to Copy
```
file_copy_manager.py          # Main script
requirements.txt              # Dependencies (empty for this project)
setup.bat                    # Setup script
run_file_copy_manager.bat    # Execution script  
validate_setup.bat           # Network validation script
test_csv_parsing.py          # Testing script
README.md                    # Documentation
db/                          # CSV files directory
├── Copy of THICKNESS AND MATERIAL DATA - 1060 Alloy.csv
├── Copy of THICKNESS AND MATERIAL DATA - AISI 1020.csv
├── Copy of THICKNESS AND MATERIAL DATA - AISI 304.csv
└── Copy of THICKNESS AND MATERIAL DATA - AISI 316 Annealed Stainless Steel Bar (SS).csv
```

### 3. Path Verification
Current paths in script:
```
SOURCE_PATH = r"\\172.16.70.71\Mechanical Data\Nishant"
DESTINATION_BASE = r"\\172.16.70.71\mechanical data\Nishant\CRM V2 27-12-2018\DA03_25-1-2019 EPDM\001 DA SM\Factory layout"
```

## Deployment Steps

### Step 1: Initial Setup
1. Copy all files to Windows machine
2. Open Command Prompt as Administrator (if needed)
3. Navigate to the project directory
4. Run: `validate_setup.bat`
5. Verify all checks pass

### Step 2: Environment Setup
1. Run: `setup.bat`
2. Wait for virtual environment creation
3. Verify no errors in setup process

### Step 3: Testing (Optional but Recommended)
1. Run: `python test_csv_parsing.py` (from activated venv)
2. Review CSV parsing results
3. Verify material extraction is correct

### Step 4: Production Run
1. **BACKUP IMPORTANT DATA FIRST**
2. Run: `run_file_copy_manager.bat`
3. Review configuration displayed
4. Confirm with 'y' to proceed
5. Monitor progress and logs

## Expected Results

### Processing Statistics
Based on test data:
- **1060 Alloy**: 133 products to process
- **AISI 1020**: 1,190 products to process  
- **AISI 304**: 169 products to process
- **AISI 316**: 19 products to process
- **Total**: ~1,511 products with quantity > 1

### Folder Structure Created
```
destination_base/
├── 1060 Alloy/
│   ├── 1/           # Files with 1mm thickness
│   ├── 0.6/         # Files with 0.6mm thickness
│   └── ...
├── AISI 1020/
│   ├── 1/
│   ├── 0.6/
│   └── ...
├── AISI 304/
│   └── ...
└── AISI 316 Annealed Stainless Steel Bar (SS)/
    └── ...
```

## Troubleshooting Guide

### Common Issues

#### Network Access Problems
```
ERROR: Cannot access source path
```
**Solution**: 
- Check network connectivity to 172.16.70.71
- Verify user has read permissions on source path
- Try accessing path manually in Windows Explorer

#### Permission Issues
```
ERROR: Cannot create directories at destination
```
**Solution**:
- Run Command Prompt as Administrator
- Check write permissions on destination path
- Verify network drive is mapped correctly

#### Python Issues
```
ERROR: Python is not installed or not in PATH
```
**Solution**:
- Install Python 3.7+ from python.org
- Ensure "Add Python to PATH" is checked during installation
- Restart Command Prompt after installation

#### CSV Reading Issues
```
Error reading CSV file
```
**Solution**:
- Verify CSV files are not corrupted
- Check file encoding (should be UTF-8 compatible)
- Ensure no special characters in file paths

### Performance Expectations

#### Estimated Execution Time
- Small files (< 1MB): ~1-2 seconds per file
- Medium files (1-10MB): ~3-5 seconds per file  
- Large files (> 10MB): ~10+ seconds per file

#### Resource Usage
- Memory: < 100MB typically
- Disk I/O: Heavy during copy operations
- Network: Dependent on file sizes and network speed

## Post-Deployment Verification

### Success Indicators
- [ ] Log file shows "Operation completed successfully"
- [ ] No ERROR messages in log (warnings are acceptable)
- [ ] Expected folder structure created
- [ ] File counts match expected quantities
- [ ] Sample files can be opened correctly

### Log Analysis
Check the log file for:
```
Files processed: [expected count]
Files copied: [should be > 0]
Files not found: [should be minimal]
Errors encountered: [should be 0]
```

### Quality Checks
1. Verify random sample of copied files
2. Check file naming convention (1_, 2_, 3_, etc.)
3. Confirm files are in correct material/thickness folders
4. Test file integrity by opening a few files

## Emergency Procedures

### If Script Fails Mid-Execution
1. Check log file for last processed item
2. Note any error messages
3. Fix underlying issue (permissions, network, etc.)
4. Script can be re-run safely (won't duplicate existing files)

### If Files Are Copied to Wrong Location
1. Stop script immediately (Ctrl+C)
2. Review configuration paths
3. Manually move files if needed
4. Update paths and re-run

### Rollback Procedure
1. Keep log file for reference
2. Manually delete created folders if needed
3. No changes made to source files (read-only operations)

## Support Information

### Log Files Location
- Main log: `file_copy_log_[timestamp].log`
- Contains detailed execution information
- Preserve for troubleshooting

### Contact Information
- Script created by: GitHub Copilot
- Date: July 29, 2025
- Version: 1.0

## Final Notes

- **ALWAYS** run `validate_setup.bat` first
- **BACKUP** critical data before running
- **MONITOR** the first few minutes of execution
- **SAVE** log files for audit purposes
- Script is designed to be **robust** and **safe**
- Can be re-run multiple times without issues
