#!/usr/bin/env python3
"""
Google Sheets Cleanup Utility

This script helps fix misaligned data in your Google Sheets.
Use this if you notice horizontal data spreading instead of proper rows.
"""

import os
import sys

try:
    import gspread
    from google.oauth2.service_account import Credentials
except ImportError as e:
    print(f"❌ Missing packages: {e}")
    print("Run: pip install gspread google-auth")
    sys.exit(1)


class SheetsCleanupTool:
    def __init__(self, credentials_path: str, spreadsheet_name: str):
        self.credentials_path = credentials_path
        self.spreadsheet_name = spreadsheet_name
        self.sheet = None
        self.worksheet = None
    
    def connect(self):
        """Connect to Google Sheets"""
        try:
            scope = [
                "https://spreadsheets.google.com/feeds",
                "https://www.googleapis.com/auth/drive"
            ]
            
            creds = Credentials.from_service_account_file(self.credentials_path, scopes=scope)
            client = gspread.authorize(creds)
            
            self.sheet = client.open(self.spreadsheet_name)
            self.worksheet = self.sheet.worksheet('Businesses')
            
            print(f"✅ Connected to: {self.spreadsheet_name}")
            return True
            
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def analyze_data(self):
        """Analyze the current data structure"""
        print("\n📊 ANALYZING DATA STRUCTURE...")
        print("=" * 50)
        
        all_values = self.worksheet.get_all_values()
        total_rows = len(all_values)
        
        print(f"Total rows in sheet: {total_rows}")
        
        # Find rows with data in first column (proper alignment)
        proper_rows = []
        empty_rows = 0
        misaligned_rows = []
        
        for i, row in enumerate(all_values, 1):
            if not any(cell.strip() for cell in row):
                empty_rows += 1
            elif i == 1 or row[0].strip():  # Header or rows with name
                proper_rows.append(i)
            else:
                misaligned_rows.append(i)
        
        print(f"✅ Properly aligned rows: {len(proper_rows)}")
        print(f"❌ Misaligned rows: {len(misaligned_rows)}")
        print(f"⭕ Empty rows: {empty_rows}")
        
        if misaligned_rows:
            print(f"\n⚠️  Misaligned rows found at: {misaligned_rows[:10]}{'...' if len(misaligned_rows) > 10 else ''}")
        
        return len(proper_rows), len(misaligned_rows), empty_rows
    
    def preview_cleanup(self):
        """Show what the cleanup would do"""
        print("\n🔍 CLEANUP PREVIEW...")
        print("=" * 50)
        
        all_values = self.worksheet.get_all_values()
        properly_aligned_rows = []
        headers_found = False
        
        for i, row in enumerate(all_values, 1):
            # Skip completely empty rows
            if not any(cell.strip() for cell in row):
                continue
            
            # First non-empty row should be headers
            if not headers_found:
                properly_aligned_rows.append((i, row))
                headers_found = True
                continue
            
            # For data rows, check if first column (name) has content
            if row and row[0].strip():
                properly_aligned_rows.append((i, row))
        
        print(f"Will keep {len(properly_aligned_rows)} rows:")
        for i, (row_num, row_data) in enumerate(properly_aligned_rows[:5]):
            print(f"  Row {row_num}: {row_data[0][:50]}...")
        
        if len(properly_aligned_rows) > 5:
            print(f"  ... and {len(properly_aligned_rows) - 5} more rows")
        
        return properly_aligned_rows
    
    def cleanup_data(self, confirm=True):
        """Clean up the misaligned data"""
        print("\n🧹 CLEANING UP DATA...")
        print("=" * 50)
        
        if confirm:
            response = input("⚠️  This will modify your Google Sheet. Continue? (y/N): ")
            if response.lower() != 'y':
                print("Cleanup cancelled.")
                return False
        
        # Get properly aligned data
        all_values = self.worksheet.get_all_values()
        properly_aligned_rows = []
        headers_found = False
        
        for row in all_values:
            if not any(cell.strip() for cell in row):
                continue
            
            if not headers_found:
                properly_aligned_rows.append(row)
                headers_found = True
                continue
            
            if row and row[0].strip():
                properly_aligned_rows.append(row)
        
        if not properly_aligned_rows:
            print("❌ No valid data found!")
            return False
        
        try:
            # Clear the sheet
            print("🗑️  Clearing sheet...")
            self.worksheet.clear()
            
            # Rewrite with clean data
            print("✍️  Writing clean data...")
            # Calculate the end column letter properly
            num_cols = len(properly_aligned_rows[0])
            if num_cols <= 26:
                end_col = chr(ord("A") + num_cols - 1)
            else:
                # Handle columns beyond Z (AA, AB, etc.)
                first_letter = chr(ord("A") + (num_cols - 1) // 26 - 1)
                second_letter = chr(ord("A") + (num_cols - 1) % 26)
                end_col = first_letter + second_letter
            
            range_name = f'A1:{end_col}{len(properly_aligned_rows)}'
            print(f"Writing to range: {range_name}")
            self.worksheet.update(values=properly_aligned_rows, range_name=range_name)
            
            print(f"✅ Cleanup complete! {len(properly_aligned_rows)} rows restored.")
            return True
            
        except Exception as e:
            print(f"❌ Cleanup failed: {e}")
            return False


def main():
    print("🧹 Google Sheets Cleanup Tool")
    print("=" * 50)
    
    # Check for credentials
    credentials_path = os.path.join(os.path.dirname(__file__), "credentials.json")
    
    if not os.path.exists(credentials_path):
        print(f"❌ credentials.json not found at: {credentials_path}")
        return
    
    # Initialize cleanup tool
    spreadsheet_name = "CodeKraft - Leads"
    cleaner = SheetsCleanupTool(credentials_path, spreadsheet_name)
    
    if not cleaner.connect():
        return
    
    # Analyze current data
    proper_count, misaligned_count, empty_count = cleaner.analyze_data()
    
    if misaligned_count == 0:
        print("\n🎉 Your sheet looks good! No cleanup needed.")
        return
    
    # Show preview
    aligned_rows = cleaner.preview_cleanup()
    
    # Ask for cleanup
    print(f"\n📋 SUMMARY:")
    print(f"Current: {proper_count + misaligned_count + empty_count} total rows")
    print(f"After cleanup: {len(aligned_rows)} clean rows")
    print(f"Will remove: {misaligned_count + empty_count} problematic rows")
    
    print("\n🔧 OPTIONS:")
    print("1. Clean up now (recommended)")
    print("2. Exit without changes")
    
    choice = input("\nEnter your choice (1-2): ").strip()
    
    if choice == '1':
        success = cleaner.cleanup_data(confirm=True)
        if success:
            print("\n🎉 Cleanup complete! Your sheet should now work properly.")
        else:
            print("\n❌ Cleanup failed. Please check your sheet manually.")
    else:
        print("\nExiting without changes.")


if __name__ == "__main__":
    main()
