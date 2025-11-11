#!/usr/bin/env python3
"""
Batch Upload Script for Financier

This script uploads multiple PDF files from a local directory to the Financier batch upload endpoint.

Usage:
    python3 batch_upload_pdfs.py /path/to/pdf/folder

Example:
    python3 batch_upload_pdfs.py ~/Documents/statements

Features:
- Uploads all PDF files from specified directory
- Uses the batch upload endpoint for efficiency
- Shows progress and results for each file
- Handles errors gracefully
"""

import sys
import os
import requests
from pathlib import Path


def upload_pdfs_from_directory(directory_path: str, base_url: str = "http://localhost:8000", bank: str = "Chase"):
    """
    Upload all PDF files from a directory to the Financier batch endpoint.
    
    Args:
        directory_path: Path to directory containing PDF files
        base_url: Base URL of the API (default: http://localhost:8000)
        bank: Bank name (default: Chase)
    """
    # Convert to Path object
    dir_path = Path(directory_path)
    
    if not dir_path.exists():
        print(f"❌ Error: Directory '{directory_path}' does not exist")
        return
    
    if not dir_path.is_dir():
        print(f"❌ Error: '{directory_path}' is not a directory")
        return
    
    # Find all PDF files
    pdf_files = list(dir_path.glob("*.pdf"))
    
    if not pdf_files:
        print(f"⚠️  No PDF files found in '{directory_path}'")
        return
    
    print(f"📁 Found {len(pdf_files)} PDF file(s) in '{directory_path}'")
    print(f"📤 Uploading to {base_url}/financier/upload/batch")
    print("-" * 60)
    
    # Prepare files for upload
    files = []
    for pdf_file in pdf_files:
        files.append(('files', (pdf_file.name, open(pdf_file, 'rb'), 'application/pdf')))
    
    try:
        # Make the batch upload request
        response = requests.post(
            f"{base_url}/financier/upload/batch",
            params={"bank": bank},
            files=files
        )
        
        # Close all file handles
        for _, (_, file_handle, _) in files:
            file_handle.close()
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Upload Complete!")
            print(f"Total files: {result['total_files']}")
            print(f"Successful: {result['successful']}")
            print(f"Failed: {result['failed']}")
            print("-" * 60)
            
            # Show successful uploads
            if result['results']:
                print("\n📊 Successfully Processed:")
                for item in result['results']:
                    data = item['data']
                    print(f"  ✓ {item['filename']}")
                    print(f"    - Transactions: {data.get('transaction_count', 'N/A')}")
                    if 'total_charges' in data:
                        print(f"    - Total Charges: ${data['total_charges']:.2f}")
                    if 'file_hash' in data:
                        print(f"    - File Hash: {data['file_hash'][:16]}...")
            
            # Show errors
            if result['errors']:
                print("\n❌ Failed:")
                for error in result['errors']:
                    print(f"  ✗ {error['filename']}: {error['error']}")
        
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
    
    except requests.exceptions.ConnectionError:
        print(f"❌ Error: Could not connect to {base_url}")
        print("   Make sure the backend is running (docker-compose up)")
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 batch_upload_pdfs.py <directory_path> [bank]")
        print()
        print("Examples:")
        print("  python3 batch_upload_pdfs.py ~/Documents/statements")
        print("  python3 batch_upload_pdfs.py /path/to/pdfs Chase")
        sys.exit(1)
    
    directory_path = sys.argv[1]
    bank = sys.argv[2] if len(sys.argv) > 2 else "Chase"
    
    upload_pdfs_from_directory(directory_path, bank=bank)


if __name__ == "__main__":
    main()
