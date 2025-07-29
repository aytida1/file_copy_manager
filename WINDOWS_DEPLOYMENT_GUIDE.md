# Windows Deployment Guide - File Copy Manager

## 📋 Prerequisites

### System Requirements
- **Windows 10/11** (any edition)
- **Python 3.7 or higher** installed
- **Network access** to server `172.16.70.71`
- **Administrator privileges** (recommended for network access)

---

## 🚀 Step-by-Step Deployment Instructions

### Step 1: Python Installation (if not installed)

1. **Download Python:**
   - Go to [python.org](https://www.python.org/downloads/)
   - Download Python 3.7 or higher (latest recommended)

2. **Install Python:**
   - Run the installer
   - ⚠️ **IMPORTANT**: Check "Add Python to PATH" during installation
   - Choose "Install for all users" if you have admin rights
   - Complete the installation

3. **Verify Installation:**
   - Open Command Prompt (`Win + R`, type `cmd`, press Enter)
   - Type: `python --version`
   - Should show Python version (e.g., `Python 3.11.0`)

---

### Step 2: File Transfer

1. **Create Project Directory:**
   ```cmd
   mkdir C:\FileCopyManager
   cd C:\FileCopyManager
   ```

2. **Copy ALL these files** to `C:\FileCopyManager\`:
   ```
   file_copy_manager.py          ← Main script
   requirements.txt              ← Dependencies  
   setup.bat                    ← Environment setup
   run_file_copy_manager.bat    ← Quick runner
   validate_setup.bat           ← Network checker
   test_enhanced.py             ← Testing script
   README.md                    ← Documentation
   QUICK_REFERENCE.txt          ← Quick guide
   db\                          ← CSV folder
   ├── Copy of THICKNESS AND MATERIAL DATA - 1060 Alloy.csv
   ├── Copy of THICKNESS AND MATERIAL DATA - AISI 1020.csv
   ├── Copy of THICKNESS AND MATERIAL DATA - AISI 304.csv
   └── Copy of THICKNESS AND MATERIAL DATA - AISI 316 Annealed Stainless Steel Bar (SS).csv
   ```

3. **Final folder structure should look like:**
   ```
   C:\FileCopyManager\
   ├── file_copy_manager.py
   ├── requirements.txt
   ├── setup.bat
   ├── run_file_copy_manager.bat
   ├── validate_setup.bat
   ├── test_enhanced.py
   ├── README.md
   ├── QUICK_REFERENCE.txt
   └── db\
       ├── Copy of THICKNESS AND MATERIAL DATA - 1060 Alloy.csv
       ├── Copy of THICKNESS AND MATERIAL DATA - AISI 1020.csv
       ├── Copy of THICKNESS AND MATERIAL DATA - AISI 304.csv
       └── Copy of THICKNESS AND MATERIAL DATA - AISI 316 Annealed Stainless Steel Bar (SS).csv
   ```

---

### Step 3: Network Access Verification

1. **Open Command Prompt as Administrator:**
   - Right-click on "Command Prompt" in Start Menu
   - Select "Run as administrator"

2. **Navigate to project directory:**
   ```cmd
   cd C:\FileCopyManager
   ```

3. **Run network validation:**
   ```cmd
   validate_setup.bat
   ```

4. **Expected output should show:**
   ```
   ✓ Source path accessible
   ✓ Source path contains files
   ✓ Destination path accessible (or will be created)
   ✓ CSV directory found
   ✓ Found CSV files in db directory
   ```

5. **If you see errors:**
   - Check network connectivity to `172.16.70.71`
   - Verify you have proper permissions
   - Contact IT support if needed

---

### Step 4: Environment Setup

1. **Run the setup script:**
   ```cmd
   setup.bat
   ```

2. **Wait for completion** (should take 1-2 minutes)

3. **Expected output:**
   ```
   Python found. Setting up virtual environment...
   Creating virtual environment...
   Activating virtual environment...
   Upgrading pip...
   Setup completed successfully!
   ```

---

### Step 5: Optional Testing

1. **Test CSV parsing** (recommended first time):
   ```cmd
   venv\Scripts\activate.bat
   python test_enhanced.py
   ```

2. **Review the output** to ensure CSV files are read correctly

3. **Press Enter to exit** the test

---

### Step 6: Production Execution

1. **Run the main program:**
   ```cmd
   run_file_copy_manager.bat
   ```

2. **Review the configuration displayed:**
   ```
   File Copy Manager v1.0
   ==================================================
   Source: \\172.16.70.71\Mechanical Data\Nishant
   Destination: \\172.16.70.71\mechanical data\Nishant\CRM V2 27-12-2018\DA03_25-1-2019 EPDM\001 DA SM\Factory layout
   CSV Directory: db
   ==================================================
   ```

3. **Confirm execution:**
   - Type `y` and press Enter to proceed
   - Type `n` to cancel

4. **Monitor progress:**
   - Watch the console output for progress
   - Check for any error messages
   - Processing will take time depending on file sizes

5. **Completion:**
   - Script will show final statistics
   - Log file will be created with timestamp
   - Press Enter to exit

---

## 📊 Expected Results

### Processing Statistics
- **~1,511 products** will be processed
- **Files copied:** Depends on how many source files are found
- **Folder structure created:** Material/Thickness/ hierarchy
- **Execution time:** Varies by file sizes and network speed

### Output Files
- **Log file:** `file_copy_log_[timestamp].log`
- **Organized folders** in destination directory
- **Copied files** with appropriate naming

---

## ⚠️ Troubleshooting

### Common Issues & Solutions

#### Issue: "Python is not recognized"
**Solution:**
- Reinstall Python with "Add to PATH" checked
- Restart Command Prompt
- Use full path: `C:\Users\[Username]\AppData\Local\Programs\Python\Python311\python.exe`

#### Issue: "Access denied to network path"
**Solution:**
- Run Command Prompt as Administrator
- Check network drive mapping
- Verify server is accessible: `ping 172.16.70.71`
- Contact IT for network permissions

#### Issue: "No CSV files found"
**Solution:**
- Ensure `db` folder is in the same directory as the script
- Check that CSV files are not corrupted
- Verify file names match exactly

#### Issue: "Virtual environment creation failed"
**Solution:**
- Run Command Prompt as Administrator
- Check disk space availability
- Ensure Python installation is complete

---

## 🔄 Re-running the Script

The script is **safe to re-run** multiple times:
- Won't duplicate existing files
- Will process any new/missed files
- Creates new log file each time

To re-run:
```cmd
cd C:\FileCopyManager
run_file_copy_manager.bat
```

---

## 📁 File Organization Created

After successful execution, you'll see this structure in the destination:

```
\\172.16.70.71\mechanical data\Nishant\CRM V2 27-12-2018\DA03_25-1-2019 EPDM\001 DA SM\Factory layout\
├── 1060 Alloy\
│   ├── 0.6\              # 0.6mm thickness files
│   │   ├── 1_filename.dwg
│   │   ├── 2_filename.dwg
│   │   └── ...
│   ├── 1\                # 1mm thickness files
│   │   ├── 1_filename.dwg
│   │   ├── 2_filename.dwg
│   │   └── ...
│   └── ...
├── AISI 1020\
│   ├── 0.6\
│   ├── 1\
│   └── ...
├── AISI 304\
└── AISI 316 Annealed Stainless Steel Bar (SS)\
```

---

## 🆘 Emergency Procedures

### If Script Stops/Crashes
1. **Don't panic** - no source files are modified
2. **Check the log file** for the last processed item
3. **Fix any issues** (network, permissions, etc.)
4. **Re-run the script** - it will continue safely

### If Wrong Files Are Copied
1. **Stop the script** (Ctrl+C)
2. **Check destination folders** manually
3. **Delete incorrect copies** if needed
4. **Verify configuration** and re-run

---

## 📞 Support Checklist

Before asking for help, please have:
- [ ] Log file (`file_copy_log_[timestamp].log`)
- [ ] Screenshot of error message
- [ ] Confirmation that network paths are accessible
- [ ] Python version (`python --version`)
- [ ] Windows version

---

## ✅ Success Verification

After completion, verify:
- [ ] Log shows "Operation completed successfully!"
- [ ] Expected folder structure exists in destination
- [ ] Sample files can be opened correctly
- [ ] File counts match expected quantities
- [ ] No critical errors in log file

**🎉 Congratulations! Your file copy operation is complete!**
