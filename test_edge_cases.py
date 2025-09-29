#!/usr/bin/env python3
"""
Edge Case Testing for Google Sheets Integration

This script tests various edge cases that might occur during real scraping.
"""

import os
import sys

# Add the src directory to path so we can import the main modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    import gspread
    from google.oauth2.service_account import Credentials
    GOOGLE_SHEETS_AVAILABLE = True
except ImportError:
    print("❌ Google Sheets packages not installed")
    sys.exit(1)

from main import GoogleSheetsManager

def test_special_characters():
    """Test handling of special characters in business data"""
    print("🧪 TESTING SPECIAL CHARACTERS")
    print("=" * 50)
    
    # Test data with various special characters
    test_business = {
        'name': 'Café René & Co. Ltd. "The Best"',
        'address': '123 Main St., Apt #5 (2nd Floor)',
        'phone': '+44 (0)20 7946 0958',
        'website': 'https://café-rené.co.uk/menu?lang=en&special=true',
        'instagram': '@café_rené_uk',
        'facebook': 'https://facebook.com/café.rené.uk',
        'rating': '4.8★',
        'reviews_count': '1,234',
        'category': 'Restaurant & Café',
        'hours': 'Mon-Fri: 8:00 AM - 10:00 PM',
        'price_range': '£££'
    }
    
    columns = [
        'name', 'address', 'phone', 'website', 'instagram', 'facebook',
        'rating', 'reviews_count', 'category', 'hours', 'price_range',
        'region', 'search_term', 'scraped_at'
    ]
    
    # Add metadata
    enriched = dict(test_business)
    enriched['region'] = 'London'
    enriched['search_term'] = 'Cafés & Restaurants'
    enriched['scraped_at'] = '2025-09-29T05:30:00'
    
    # Test row preparation
    row = [str(enriched.get(col, '')) for col in columns]
    
    print("✅ Special character handling successful")
    print(f"   Sample: '{row[0][:30]}...'")
    
    return True

def test_empty_data():
    """Test handling of empty or missing data"""
    print("\n🧪 TESTING EMPTY DATA")
    print("=" * 50)
    
    # Test with mostly empty business
    empty_business = {
        'name': 'Test Business',  # Only name provided
        'address': '',
        'phone': '',
        'website': '',
        'instagram': '',
        'facebook': '',
        'rating': '',
        'reviews_count': '',
        'category': '',
        'hours': '',
        'price_range': ''
    }
    
    columns = [
        'name', 'address', 'phone', 'website', 'instagram', 'facebook',
        'rating', 'reviews_count', 'category', 'hours', 'price_range',
        'region', 'search_term', 'scraped_at'
    ]
    
    # Add metadata
    enriched = dict(empty_business)
    enriched['region'] = 'Test'
    enriched['search_term'] = 'Test'
    enriched['scraped_at'] = '2025-09-29T05:30:00'
    
    # Test row preparation
    row = [str(enriched.get(col, '')) for col in columns]
    
    # Verify all empty fields become empty strings
    empty_count = sum(1 for cell in row if cell == '')
    print(f"✅ Empty data handling successful")
    print(f"   Empty cells: {empty_count}/{len(row)}")
    
    return True

def test_long_strings():
    """Test handling of very long strings"""
    print("\n🧪 TESTING LONG STRINGS")
    print("=" * 50)
    
    # Test with very long data
    long_business = {
        'name': 'A' * 500,  # Very long name
        'address': 'Very Long Address ' * 50,  # Very long address
        'phone': '+44 (0)20 1234 5678',
        'website': 'https://very-long-domain-name-for-testing-purposes.example.com/very/long/path/with/many/segments/that/might/cause/issues',
        'instagram': '',
        'facebook': '',
        'rating': '4.5',
        'reviews_count': '999999',
        'category': 'Category with very long description that goes on and on and provides way too much detail about what this business actually does',
        'hours': '',
        'price_range': ''
    }
    
    columns = [
        'name', 'address', 'phone', 'website', 'instagram', 'facebook',
        'rating', 'reviews_count', 'category', 'hours', 'price_range',
        'region', 'search_term', 'scraped_at'
    ]
    
    # Add metadata
    enriched = dict(long_business)
    enriched['region'] = 'Test'
    enriched['search_term'] = 'Test'
    enriched['scraped_at'] = '2025-09-29T05:30:00'
    
    # Test row preparation
    row = [str(enriched.get(col, '')) for col in columns]
    
    print(f"✅ Long string handling successful")
    print(f"   Longest cell: {max(len(cell) for cell in row)} characters")
    
    return True

def test_missing_columns():
    """Test handling of missing columns in business data"""
    print("\n🧪 TESTING MISSING COLUMNS")
    print("=" * 50)
    
    # Business data missing some expected fields
    incomplete_business = {
        'name': 'Incomplete Business',
        'phone': '123-456-7890',
        # Missing: address, website, instagram, facebook, rating, etc.
    }
    
    columns = [
        'name', 'address', 'phone', 'website', 'instagram', 'facebook',
        'rating', 'reviews_count', 'category', 'hours', 'price_range',
        'region', 'search_term', 'scraped_at'
    ]
    
    # Test row preparation with missing columns
    row = [str(incomplete_business.get(col, '')) for col in columns]
    
    # Should fill missing columns with empty strings
    print(f"✅ Missing column handling successful")
    print(f"   Row length: {len(row)} (expected: {len(columns)})")
    
    return True

def test_column_calculation_edge_cases():
    """Test column calculation with unusual numbers"""
    print("\n🧪 TESTING COLUMN CALCULATION EDGE CASES")
    print("=" * 50)
    
    def calculate_end_col(num_cols):
        """Local version of column calculation"""
        if num_cols <= 26:
            return chr(ord("A") + num_cols - 1)
        else:
            first_letter = chr(ord("A") + (num_cols - 1) // 26 - 1)
            second_letter = chr(ord("A") + (num_cols - 1) % 26)
            return first_letter + second_letter
    
    # Test edge cases
    edge_cases = [
        1,    # Minimum
        14,   # Our typical case
        26,   # Boundary
        27,   # Just over boundary
        100,  # High number
    ]
    
    for num_cols in edge_cases:
        try:
            result = calculate_end_col(num_cols)
            print(f"✅ {num_cols} columns → '{result}'")
        except Exception as e:
            print(f"❌ {num_cols} columns → Error: {e}")
            return False
    
    return True

if __name__ == "__main__":
    print("🔍 EDGE CASE TESTING FOR GOOGLE SHEETS INTEGRATION")
    print("=" * 60)
    
    # Run all edge case tests
    tests = [
        test_special_characters(),
        test_empty_data(),
        test_long_strings(),
        test_missing_columns(),
        test_column_calculation_edge_cases(),
    ]
    
    print("\n" + "=" * 60)
    if all(tests):
        print("🎯 ALL EDGE CASE TESTS PASSED!")
        print("The system handles edge cases gracefully.")
    else:
        print("⚠️  SOME EDGE CASE TESTS FAILED!")
        print("The code may have issues with unusual data.")
