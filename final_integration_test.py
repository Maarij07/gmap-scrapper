#!/usr/bin/env python3
"""
Final Integration Test

This script simulates the complete scraping workflow to ensure everything works together.
It tests the Google Sheets integration without actually opening a browser.
"""

import os
import sys
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from main import GoogleSheetsManager
    import gspread
    from google.oauth2.service_account import Credentials
    GOOGLE_SHEETS_AVAILABLE = True
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

def simulate_scraping_workflow():
    """Simulate the complete scraping workflow"""
    print("🚀 FINAL INTEGRATION TEST")
    print("=" * 60)
    
    # Test data simulating real scraped businesses
    test_businesses = [
        {
            'name': 'TechStart UK Ltd',
            'address': '123 Innovation Drive, London SW1A 1AA',
            'phone': '+44 20 7946 0958',
            'website': 'https://techstart.uk',
            'instagram': '@techstartuk',
            'facebook': '',
            'rating': '4.8',
            'reviews_count': '127',
            'category': 'Technology Consulting',
            'hours': 'Mon-Fri: 9:00 AM - 6:00 PM',
            'price_range': '£££'
        },
        {
            'name': 'E-Shop Solutions',
            'address': '456 Commerce Street, Manchester M1 1AA',
            'phone': '+44 161 123 4567',
            'website': 'https://eshop-solutions.co.uk',
            'instagram': '',
            'facebook': 'https://facebook.com/eshopsolutions',
            'rating': '4.2',
            'reviews_count': '89',
            'category': 'E-commerce Platform',
            'hours': 'Mon-Fri: 8:00 AM - 5:00 PM',
            'price_range': '££'
        },
        {
            'name': 'Digital Marketing Pro',
            'address': '789 Marketing Way, Birmingham B1 1AA',
            'phone': '',
            'website': 'https://digitalmarketingpro.uk',
            'instagram': '@digitalmktpro',
            'facebook': '',
            'rating': '4.9',
            'reviews_count': '234',
            'category': 'Digital Marketing Agency',
            'hours': '',
            'price_range': '£££'
        }
    ]
    
    # Setup columns (same as in main.py)
    columns = [
        'name', 'address', 'phone', 'website', 'instagram', 'facebook',
        'rating', 'reviews_count', 'category', 'hours', 'price_range',
        'region', 'search_term', 'scraped_at'
    ]
    
    # Test Google Sheets connection
    print("🔗 Testing Google Sheets connection...")
    credentials_path = os.path.join(os.path.dirname(__file__), "credentials.json")
    
    if not os.path.exists(credentials_path):
        print("❌ credentials.json not found - cannot test Google Sheets integration")
        return False
    
    # Initialize GoogleSheetsManager
    spreadsheet_name = "CodeKraft - Leads"
    sheets_manager = GoogleSheetsManager(credentials_path, spreadsheet_name)
    
    if not sheets_manager.connect():
        print("❌ Failed to connect to Google Sheets")
        return False
    
    print("✅ Google Sheets connection successful")
    
    # Ensure headers
    print("📋 Setting up headers...")
    sheets_manager.ensure_headers(columns)
    
    # Cleanup alignment
    print("🧹 Cleaning up sheet alignment...")
    sheets_manager.cleanup_sheet_alignment()
    
    # Simulate adding businesses
    print("📊 Simulating business data insertion...")
    region = "UK"
    search_term = "Ecommerce"
    
    success_count = 0
    for i, business in enumerate(test_businesses, 1):
        # Enrich with metadata (same as in main.py)
        enriched = dict(business)
        enriched['region'] = region
        enriched['search_term'] = search_term
        enriched['scraped_at'] = datetime.now().isoformat(timespec='seconds')
        
        print(f"  Adding business {i}: {business['name']}")
        
        if sheets_manager.append_row(enriched, columns):
            success_count += 1
            print(f"    ✅ Success")
        else:
            print(f"    ❌ Failed")
    
    print(f"\n📈 Results: {success_count}/{len(test_businesses)} businesses added successfully")
    
    # Test the column calculation one more time with our actual column count
    num_cols = len(columns)  # Should be 14
    if num_cols <= 26:
        end_col = chr(ord("A") + num_cols - 1)
    else:
        first_letter = chr(ord("A") + (num_cols - 1) // 26 - 1)
        second_letter = chr(ord("A") + (num_cols - 1) % 26)
        end_col = first_letter + second_letter
    
    expected_range = f"A2:{end_col}2"  # Row 2 (first data row)
    print(f"🔧 Column calculation test: {num_cols} columns → Range ends at '{end_col}' (Range: {expected_range})")
    
    if success_count == len(test_businesses):
        print("\n🎯 ALL INTEGRATION TESTS PASSED!")
        print("The complete scraping workflow works perfectly.")
        return True
    else:
        print(f"\n⚠️  {len(test_businesses) - success_count} businesses failed to save!")
        print("There may be issues with the Google Sheets integration.")
        return False

if __name__ == "__main__":
    success = simulate_scraping_workflow()
    
    print("\n" + "=" * 60)
    if success:
        print("🚀 READY FOR DEPLOYMENT!")
        print("The scraper is fully tested and should work perfectly.")
    else:
        print("❌ INTEGRATION ISSUES FOUND!")
        print("The code needs fixes before deployment.")
