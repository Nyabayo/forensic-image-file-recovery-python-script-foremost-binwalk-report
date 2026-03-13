# 🔍 Forensic Image File Recovery — Python Script, Foremost, Binwalk & Report

**Name:** Ernest Nyabayo Osindo  
**Date:** 13/03/2026  
**Role:** Junior Digital Forensics Analyst

---

## 📌 Overview

In this project, I took on the role of a junior digital forensics analyst investigating a corrupted hard drive. My task was to recover lost files by identifying file signatures and reconstructing them from the forensic disk image named **carveit**.

Deleted, hidden, and renamed files are common techniques used to evade forensic investigation. My goal was to locate as many recoverable files as possible, ensuring they were complete and uncorrupted.

---

## 🔗 Resources

| Resource | Link |
|---|---|
| 📀 Forensic Disk Image | [Download carveit](https://drive.google.com/file/d/1LjUrx9yNfwAdULiLPosLQGSXVuqNjwtN/view) |
| 📄 Forensic Report Template | [Google Docs Template](https://docs.google.com/document/d/1Qcl4UbFiIzwJbWy9iYUiU2sNxwtFaYZfLslGNeCkzxo/copy) |
| 💻 GitHub Repository | [forensic-image-file-recovery-python-script-foremost-binwalk-report](https://github.com/Nyabayo/forensic-image-file-recovery-python-script-foremost-binwalk-report) |

---

## 🛠️ Tools Used

| Tool | Purpose |
|---|---|
| `foremost` | Automated file carving based on known file signatures |
| `binwalk` | Detecting and extracting embedded file structures (ZIP, DOCX) |
| `xxd` | Generating hex dumps of the disk image |
| `egrep` | Searching for file signatures within hex dumps |
| `dd` | Manually extracting files using calculated byte offsets |
| `printf` | Converting hexadecimal offsets to decimal values |
| `fdisk` | Inspecting disk image partition structure |
| `fls` | Attempting filesystem-level listing of the disk image |
| `xdg-open` | Opening and verifying readability of recovered image files |
| `unzip` | Extracting and verifying ZIP archives |
| `md5sum` | Manually verifying MD5 hashes of recovered files |
| `Python (OSINDO.py)` | Custom automated carving script with MD5 hash generation |

---

## ⚙️ Step-by-Step Solution

---

### Step 1: Setting Up the Forensic Environment

I installed all the tools I needed:

```bash
sudo apt update && sudo apt install foremost binwalk -y
```

![Installing Foremost and Binwalk](images/01_install_tools.png)

![Installation Complete](images/02_install_tools_2.png)

---

### Step 2: Inspecting the Disk Image

#### 2.1 Check the File Type

```bash
file carveit
```

![file carveit output](images/03_file_check.png)

> **Result:** `carveit: ASCII text, with very long lines (65536), with no line terminators`

---

#### 2.2 Check Partition Structure

```bash
fdisk -l carveit
```

![fdisk -l carveit output](images/04_fdisk_output.png)

> **Result:** Disk size of **15.78 MiB**, **32327 sectors**, each sector 512 bytes.

---

#### 2.3 List Files in the Disk Image

```bash
sudo fls -r carveit
```

![sudo fls -r carveit output](images/05_fls_output.png)

> **Result:** `Possible encryption detected (High entropy (7.85))`

---

### Step 3: Automated File Recovery

#### 3.1 Extract Files with Foremost

```bash
foremost -i carveit -o recovered_files
```

![foremost running](images/06_foremost_run.png)

```bash
ls -l recovered_files
```

![ls -l recovered_files output](images/07_ls_recovered_files.png)

> Foremost created recovery folders: `docx`, `gif`, `jpg`, `pdf`, `png`

---

#### 3.2 Extract Files with Binwalk

```bash
binwalk -e carveit
```

![binwalk -e carveit output](images/08_binwalk_output.png)

> Binwalk detected several ZIP archive blocks containing DOCX components: `document.xml`, `image1.png`, XML metadata files.

```bash
ls _carveit.extracted
```

![ls _carveit.extracted output](images/09_carveit_extracted.png)

> Extracted files: `8924z`, `8924.zlib`, `0C73E0`, `0C73E0.zlib`

---

### Step 4: Manual File Signature Location and Extraction

#### 4.1 Search for PNG Header (`89 50 4E 47 0D 0A 1A 0A`)

```bash
xxd carveit | egrep "89 ?50 ?4e ?47 ?0d ?0a ?1a ?0a"
```

![PNG header search output](images/10_png_header_search.png)

> **PNG header found at offset:** `0x00dc7390`

---

#### 4.2 Search for PNG Footer (`49 45 4E 44 AE 42 60 82`)

```bash
xxd carveit | egrep "49 ?45 ?4e ?44 ?ae ?42 ?60 ?82"
```

![PNG footer search output](images/11_png_footer_search.png)

> **PNG footer found at:**
> - `0x001def20` ← used as end offset
> - `0x00de5ad0`

---

#### 4.3 Convert Hex Offsets to Decimal

```bash
printf '%d\n' 0x00dc7390   # Start offset → 14447504
printf '%d\n' 0x001def20   # End offset   → 1961760
```

![printf hex to decimal output](images/12_printf_start_offset.png)

---

#### 4.4 Extract the PNG File Using `dd`

```bash
dd if=carveit of=recovered_png.png bs=1 skip=14583472 count=14360040
```

![dd extract output](images/13_dd_extract.png)

> ✅ PNG file successfully extracted as `recovered_png.png`

---

### Step 5: Python Automation Script (OSINDO.py)

I developed a custom Python script to automate the full carving pipeline.

**Script features:**
- Accepts any binary disk image as a command-line argument via `sys.argv`
- Detects file types: **PNG, JPG, ZIP, PDF, GIF**
- Converts hex signatures to bytes for precise binary matching
- Handles both hex (e.g., `FF D8 FF`) and ASCII signatures (e.g., `%PDF-`)
- Saves recovered files to `OSINDO_recovered_files/` with descriptive names
- Generates an MD5 hash per file using `hashlib`
- Logs all hashes to `hashes.txt`
- Skips and logs files where end offset < start offset

**Run the script:**

```bash
python3 OSINDO.py ~/Documents/carveit
```

![Python script running](images/14_python_script_run.png)

![Python script output results](images/15_script_output_results.png)

![Recovered files folder contents](images/16_recovered_files_folder.png)

---

## 📊 File Signatures Identified

| File Type | Header (Hex) | Footer (Hex) | Offsets Found |
|---|---|---|---|
| PNG | `89 50 4E 47 0D 0A 1A 0A` | `49 45 4E 44 AE 42 60 82` | Start: `0x00dc7390`, End: `0x001def20` |
| JPG/JPEG | `FF D8 FF` | `FF D9` | Multiple locations |
| ZIP/DOCX | `50 4B 03 04` | `50 4B 05 06` | Multiple locations |
| PDF | `25 50 44 46 2D` (%PDF-) | `25 25 45 4F 46` (%%EOF) | Found during recovery |
| GIF | `47 49 46 38` | `3B` | Found during recovery |
| Zlib | `78 9C` | N/A | Multiple locations (inside DOCX/ZIP) |

---

## 📋 All Commands Summary

![All commands summary](images/17_all_commands_summary.png)

```bash
# Step 1: Check the disk file type
file carveit

# Step 2: Check the disk partition structure
fdisk -l carveit

# Step 3: List files in the disk image
sudo fls -r carveit

# Step 4: Automated carving with Foremost
foremost -i carveit -o recovered_files
ls -l recovered_files

# Step 5: Automated carving with Binwalk
binwalk -e carveit
ls _carveit.extracted

# Step 6: Search for PNG file header
xxd carveit | egrep "89 ?50 ?4e ?47 ?0d ?0a ?1a ?0a"

# Step 7: Search for PNG file footer
xxd carveit | egrep "49 ?45 ?4e ?44 ?ae ?42 ?60 ?82"

# Step 8: Convert hexadecimal offsets to decimal
printf '%d\n' 0x00dc7390   # Start offset
printf '%d\n' 0x001def20   # End offset

# Step 9: Carve the PNG file using dd
dd if=carveit of=recovered_png.png bs=1 skip=14583472 count=14360040

# Step 10: Verify recovered file is readable
xdg-open recovered_png.png

# Step 11: Run the Python carving script
python3 OSINDO.py ~/Documents/carveit

# Step 12: Compress recovered files for submission
zip -r ~/Documents/OSINDO_recovered_files.zip ~/Documents/OSINDO_recovered_files
```

---

## 📂 Recovered Files & MD5 Hashes

### ✅ PNG Files

| File Name | MD5 Hash |
|---|---|
| recovered_PNG_758970.bin | `5ffd772a0458b81865be224f0c6641d7` |
| recovered_PNG_1965963.bin | `7b59c716858b283cb106456109ed127f` |
| recovered_PNG_14447506.bin | `263651f31e59a46ac560258abcd919ff` |

### ✅ JPG Files

| File Name | MD5 Hash |
|---|---|
| recovered_JPG_117768.bin | `7647210e76584a43e3e96e18050ac283` |
| recovered_JPG_159124.bin | `019bac58092613f8fbf8840c72c05b66` |
| recovered_JPG_190815.bin | `ab0a16522d76795c5164ed145c9762a6` |
| recovered_JPG_194815.bin | `0cf6250826c64b0faf9b49984ac04808` |
| recovered_JPG_584324.bin | `c80904029ce6730cc9368ce2553de7e8` |
| recovered_JPG_609647.bin | `7125c26f2c4933cd31404f137e0ae863` |
| recovered_JPG_620133.bin | `af75b74930fe5cc653f02adc9e9738d3` |

### ✅ ZIP Files

| File Name | MD5 Hash |
|---|---|
| recovered_ZIP_1961982.bin | `8e4971e5e4a2856078e5f34b7af5a82e` |
| recovered_ZIP_1962951.bin | `1b1b7d57c66df02712960210d8491bef` |
| recovered_ZIP_1963780.bin | `aa923c4667c0cd5eb4e80799e741ce88` |
| recovered_ZIP_1964410.bin | `a6ad0cc392c5e7f6af3c4ee8b578c931` |
| recovered_ZIP_1965912.bin | `4899f0c7b8a0a78100c596561c8ec6a1` |
| recovered_ZIP_2150598.bin | `cb8b8183cd1ae70c5f6ade49a3713aca` |
| recovered_ZIP_2152474.bin | `1b0198fac1dca281507514de6052d043` |
| recovered_ZIP_2199623.bin | `0be26b8f18a5dd8a3395ddb7c750e541` |
| recovered_ZIP_2200659.bin | `efbfedcd2e2ba7a89693a352545284c8` |
| recovered_ZIP_2200970.bin | `c8504cfbff7703b1f57e8421dc5e7308` |
| recovered_ZIP_2203138.bin | `b049992d478059dc7332c9d6fd950a5c` |
| recovered_ZIP_2205139.bin | `4858b2b36e81c047065a7c3eb71531d4` |
| recovered_ZIP_2205830.bin | `f0097ccc8683b77af664621caab4af0b` |
| recovered_ZIP_2206488.bin | `49a76ae8d409b7e589ff997b5dc208d2` |

### ✅ PDF Files

| File Name | MD5 Hash |
|---|---|
| recovered_PDF_495315.bin | `1e76326e7bfa1462bf39e8df535b2e1b` |

---

## ✅ Integrity Validation

### MD5 Hash Verification

I ran `md5sum` on each recovered file and compared the result against the hash in `hashes.txt`:

```bash
md5sum ~/Documents/OSINDO_recovered_files/recovered_PNG_758970.bin
```

![MD5 verification part 1](images/18_md5sum_verification_1.png)

![MD5 verification part 2](images/19_md5sum_verification_2.png)

![MD5 verification part 3](images/20_md5sum_verification_3.png)

![MD5 verification part 4](images/21_md5sum_verification_4.png)

![MD5 verification part 5](images/22_md5sum_verification_5.png)

**Verification Results:**

| Status | Count |
|---|---|
| ✅ Matched | 22 files |
| ❌ Not Found / Corrupted | 3 files |

**Files not found (skipped due to offset boundary errors):**
- `recovered_JPG_159124.bin` — No such file or directory
- `recovered_JPG_190815.bin` — No such file or directory
- `recovered_JPG_194815.bin` — No such file or directory

---

### Readability Checks

#### Image Files

```bash
xdg-open ~/Documents/OSINDO_recovered_files/recovered_JPG_117768.bin
```

![Image viewer showing recovered JPG files](images/23_image_viewer_jpg.png)

> ✅ Most JPG files opened successfully — image shows puppies in a basket (735 x 585, 40.8kB)  
> ❌ `recovered_JPG_190815.bin` — *Error interpreting JPEG image (improper call to JPEG library in state 201)*  
> ❌ `recovered_JPG_584324.bin` — *Error interpreting JPEG image (improper call to JPEG library in state 201)*

---

#### PDF Files

![PDF file readable](images/24_pdf_readable.png)

> ✅ `recovered_PDF_495315.bin` — Fully readable. Content: *"Is the Vizsla the Right Breed for You?"*

---

#### ZIP Files

![ZIP files unzipped terminal output](images/25_zip_unzipped.png)

![ZIP file contents in file manager](images/26_zip_compressed.png)

> ✅ All ZIP archives extracted successfully using `unzip`  
> Contents confirmed as **Microsoft Word 2007+ DOCX** files containing `_rels`, `docProps`, `word` directories

---

### Compress Recovered Files

```bash
zip -r ~/Documents/OSINDO_recovered_files.zip \
~/Documents/forensic-image-file-recovery-python-script-foremost-binwalk-report-main/OSINDO_recovered_files
```

---

## ⚠️ Errors & Challenges

| Challenge | Description |
|---|---|
| JPG offset boundary errors | Several JPG files skipped — end offset < start offset, indicating corrupted boundaries |
| JPEG library state 201 error | `recovered_JPG_190815.bin` and `recovered_JPG_584324.bin` structurally damaged, could not render |
| `dd` hex arithmetic error | `dd` does not evaluate hex expressions — converted using `printf` first |
| ZIP boundary ambiguity | Multiple `50 4B 05 06` footers made correct header-footer pairing difficult |
| GitHub 100MB file size limit | `OSINDO_recovered_files.zip` (174MB) rejected by GitHub — submitted via Canvas |

---

## 🏁 Submission Checklist

| # | Item | Status |
|---|---|---|
| 1 | `carveit` — Forensic disk image | ✅ Included in repository |
| 2 | `OSINDO.py` — Python carving script | ✅ Included in repository |
| 3 | `hashes.txt` — MD5 hashes of all recovered files | ✅ Included in repository |
| 4 | `OSINDO_recovered_files.zip` — Recovered files archive | ✅ Submitted via Canvas (174MB) |
| 5 | Forensic Report — Full investigation report | ✅ Submitted via Canvas |

---

## 👤 Author

**Ernest Nyabayo Osindo**  
Junior Digital Forensics Analyst  
📅 13/03/2026  
🔗 [GitHub Profile](https://github.com/Nyabayo)
