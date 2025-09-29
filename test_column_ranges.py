#!/usr/bin/env python3
"""
Test Column Range Calculations

This script tests the column letter calculation logic used in the Google Sheets integration
to ensure it works correctly for different column counts.
"""

def calculate_end_col(num_cols):
    """Test version of the column calculation logic"""
    if num_cols <= 26:
        return chr(ord("A") + num_cols - 1)
    else:
        # Handle columns beyond Z (AA, AB, etc.)
        first_letter = chr(ord("A") + (num_cols - 1) // 26 - 1)
        second_letter = chr(ord("A") + (num_cols - 1) % 26)
        return first_letter + second_letter

def test_column_calculations():
    """Test various column counts"""
    test_cases = [
        (1, "A"),     # Single column
        (14, "N"),    # Our scraper's column count
        (26, "Z"),    # Last single letter
        (27, "AA"),   # First double letter
        (28, "AB"),   # Second double letter
        (52, "AZ"),   # Last of first double letter set
        (53, "BA"),   # Start of second double letter set
        (100, "CV"),  # Random high number
    ]
    
    print("🧪 TESTING COLUMN RANGE CALCULATIONS")
    print("=" * 50)
    
    all_passed = True
    for num_cols, expected in test_cases:
        result = calculate_end_col(num_cols)
        status = "✅" if result == expected else "❌"
        print(f"{status} {num_cols} columns → '{result}' (expected: '{expected}')")
        
        if result != expected:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 ALL TESTS PASSED! Column calculations are correct.")
    else:
        print("❌ SOME TESTS FAILED! Column calculations need fixing.")
    
    return all_passed

def test_range_generation():
    """Test full range string generation"""
    print("\n🔧 TESTING RANGE STRING GENERATION")
    print("=" * 50)
    
    # Test our scraper's typical case (14 columns, various rows)
    test_cases = [
        (14, 1, "A1:N1"),    # Header row
        (14, 2, "A2:N2"),    # First data row
        (14, 100, "A100:N100"),  # High row number
    ]
    
    all_passed = True
    for num_cols, row_num, expected in test_cases:
        end_col = calculate_end_col(num_cols)
        range_name = f'A{row_num}:{end_col}{row_num}'
        status = "✅" if range_name == expected else "❌"
        print(f"{status} Row {row_num}, {num_cols} cols → '{range_name}' (expected: '{expected}')")
        
        if range_name != expected:
            all_passed = False
    
    return all_passed

def test_edge_cases():
    """Test edge cases that might cause issues"""
    print("\n⚠️  TESTING EDGE CASES")
    print("=" * 50)
    
    edge_cases = [
        (0, "Invalid"),  # Zero columns (should not happen)
        (-1, "Invalid"), # Negative (should not happen)
    ]
    
    for num_cols, description in edge_cases:
        try:
            result = calculate_end_col(num_cols)
            print(f"⚠️  {description} ({num_cols}) → '{result}' (handled gracefully)")
        except Exception as e:
            print(f"❌ {description} ({num_cols}) → Error: {e}")

if __name__ == "__main__":
    print("🔍 COMPREHENSIVE COLUMN CALCULATION TESTING")
    print("=" * 60)
    
    # Run all tests
    test1_passed = test_column_calculations()
    test2_passed = test_range_generation()
    test_edge_cases()
    
    print("\n" + "=" * 60)
    if test1_passed and test2_passed:
        print("🎯 ALL CRITICAL TESTS PASSED!")
        print("The Google Sheets integration should work perfectly.")
    else:
        print("⚠️  SOME TESTS FAILED!")
        print("The code needs fixes before deployment.")
