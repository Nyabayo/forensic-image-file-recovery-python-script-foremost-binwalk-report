import os
import hashlib
import re
import sys

# Function to calculate MD5 hash of a file
def calculate_md5(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

# Function to search for file signatures in the disk image
def find_signatures(image_path, signature):
    """Search for file headers/footers in the raw disk image."""
    offsets = []
    
    # Check if the signature is hexadecimal
    if all(c in "0123456789ABCDEF" for c in signature.replace(" ", "").upper()):
        # If hexadecimal, convert to bytes
        pattern = bytes.fromhex(signature.replace(" ", ""))
    else:
        # If non-hexadecimal (like %PDF-), use it directly as a string
        pattern = signature.encode()

    with open(image_path, 'rb') as f:
        data = f.read()
        # Find all occurrences of the signature
        offsets = [i for i in range(len(data)) if data[i:i+len(pattern)] == pattern]
    return offsets

# Function to extract a file based on found offsets
def extract_file(image_path, start_offset, end_offset, output_folder, file_type):
    """Extracts file data from the forensic image based on found offsets."""
    # Ensure the end_offset is not smaller than start_offset
    if end_offset < start_offset:
        print(f"Error: End offset {end_offset} is smaller than start offset {start_offset} for {file_type}. Skipping extraction.")
        return None, None

    # Check if end_offset is valid; if not, use the size of the image
    if end_offset == -1:
        with open(image_path, 'rb') as img_file:
            img_file.seek(0, os.SEEK_END)
            end_offset = img_file.tell()

    with open(image_path, 'rb') as img_file:
        img_file.seek(start_offset)
        data = img_file.read(end_offset - start_offset)
    
    output_file = os.path.join(output_folder, f"recovered_{file_type}_{start_offset}.bin")
    
    with open(output_file, 'wb') as out_file:
        out_file.write(data)
    
    # Calculate the MD5 hash of the recovered file
    md5_hash = calculate_md5(output_file)
    print(f"Recovered {file_type}: {output_file}, MD5: {md5_hash}")
    
    return output_file, md5_hash

# Function to create the recovery folder for the files
def create_recovery_folder():
    folder_name = "OSINDO_recovered_files"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    return folder_name

# Main function to recover files based on signatures and write MD5 hashes
def main(image_path):
    # Set up output folder
    output_folder = create_recovery_folder()
    
    # Define file signatures and corresponding types
    file_signatures = {
        "PNG": {
            "header": "89 50 4E 47 0D 0A 1A 0A",
            "footer": "49 45 4E 44 AE 42 60 82"
        },
        "JPG": {
            "header": "FF D8 FF",
            "footer": "FF D9"
        },
        "ZIP": {
            "header": "50 4B 03 04",
            "footer": "50 4B 05 06"
        },
        "PDF": {
            "header": "%PDF-",
            "footer": "%%EOF"
        },
        "GIF": {
            "header": "47 49 46 38",
            "footer": "3B"
        }
    }

    # Open the hashes.txt file to store MD5 hashes
    hashes_file = open(os.path.join(output_folder, "hashes.txt"), "w")
    
    # Process each file type
    for file_type, signatures in file_signatures.items():
        # Search for header and footer offsets
        start_offsets = find_signatures(image_path, signatures["header"])
        end_offsets = find_signatures(image_path, signatures["footer"])
        
        # If both start and end offsets are found, extract the files
        if start_offsets and end_offsets:
            for i, start_offset in enumerate(start_offsets):
                end_offset = end_offsets[i] if i < len(end_offsets) else os.path.getsize(image_path)
                # Extract the file data
                output_file, md5_hash = extract_file(image_path, start_offset, end_offset, output_folder, file_type)
                # Write the MD5 hash and file details to hashes.txt
                if output_file:
                    hashes_file.write(f"{output_file}: {md5_hash}\n")
    
    hashes_file.close()
    print(f"File recovery completed. MD5 hashes saved in {os.path.join(output_folder, 'hashes.txt')}")

# Entry point for the script
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python OSINDO_recover_files.py <path_to_disk_image>")
        sys.exit(1)

    # Path to the disk image file
    image_path = sys.argv[1]
    main(image_path)