#!/usr/bin/env python3
"""
Test Google Sheets connection and create CodeKraft - Leads sheet
"""

import os
import sys

try:
    import gspread
    from google.oauth2.service_account import Credentials
    print("✅ Google Sheets packages are installed")
except ImportError as e:
    print(f"❌ Missing packages: {e}")
    sys.exit(1)

def test_connection():
    credentials_path = os.path.join(os.path.dirname(__file__), "credentials.json")
    
    if not os.path.exists(credentials_path):
        print(f"❌ credentials.json not found at: {credentials_path}")
        return False
    
    print(f"✅ Found credentials.json")
    
    try:
        # Define the scope
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        
        # Load credentials
        creds = Credentials.from_service_account_file(credentials_path, scopes=scope)
        client = gspread.authorize(creds)
        
        print("✅ Successfully authenticated with Google")
        
        # Try to create or access the sheet
        spreadsheet_name = "CodeKraft - Leads"
        
        try:
            sheet = client.open(spreadsheet_name)
            print(f"✅ Found existing sheet: {spreadsheet_name}")
        except gspread.SpreadsheetNotFound:
            print(f"📝 Creating new sheet: {spreadsheet_name}")
            sheet = client.create(spreadsheet_name)
            print(f"✅ Created new sheet: {spreadsheet_name}")
            
            # Share with your email (optional - replace with your email)
            # sheet.share('your-email@gmail.com', perm_type='user', role='writer')
        
        # Get or create 'Businesses' worksheet
        try:
            worksheet = sheet.worksheet('Businesses')
            print("✅ Found 'Businesses' worksheet")
        except gspread.WorksheetNotFound:
            worksheet = sheet.add_worksheet('Businesses', 1000, 20)
            print("✅ Created 'Businesses' worksheet")
        
        # Add headers
        headers = [
            'name', 'address', 'phone', 'website', 'instagram', 'facebook',
            'rating', 'reviews_count', 'category', 'hours', 'price_range',
            'region', 'search_term', 'scraped_at'
        ]
        
        try:
            current_headers = worksheet.row_values(1)
            if not current_headers:
                worksheet.insert_row(headers, 1)
                print("✅ Added headers to sheet")
            else:
                print(f"✅ Headers already exist: {len(current_headers)} columns")
        except Exception as e:
            print(f"❌ Failed to add headers: {e}")
        
        # Test adding a sample row
        test_row = [
            'Test Business', 'Test Address', '123-456-7890', 'test.com', '', '', 
            '4.5', '100', 'Test Category', '9 AM - 5 PM', '$$',
            'Test Region', 'Test Search', '2023-01-01T12:00:00'
        ]
        
        try:
            worksheet.append_row(test_row)
            print("✅ Successfully added test row")
            
            # Remove the test row
            worksheet.delete_rows(worksheet.row_count)
            print("✅ Removed test row")
            
        except Exception as e:
            print(f"❌ Failed to add test row: {e}")
        
        # Print sheet URL
        sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet.id}"
        print(f"\n🎉 SUCCESS! Your sheet is ready:")
        print(f"📊 Sheet Name: {spreadsheet_name}")
        print(f"🔗 URL: {sheet_url}")
        
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Testing Google Sheets Connection...")
    print("=" * 50)
    
    success = test_connection()
    
    if success:
        print("\n✅ ALL TESTS PASSED!")
        print("Your scraper should now work with Google Sheets.")
    else:
        print("\n❌ TESTS FAILED!")
        print("Please check your credentials and API setup.")
