import re
import json
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
import os
from urllib.parse import urlparse, parse_qs


class GoogleMapsParser:
    """Parse Google Maps HTML data and extract business information."""
    
    def __init__(self, html_file_path):
        self.html_file_path = html_file_path
        self.businesses = []
        self.raw_html = ""
        
    def parse_html_file(self):
        """Load and parse the HTML file."""
        print(f"Loading HTML file: {self.html_file_path}")
        
        with open(self.html_file_path, 'r', encoding='utf-8', errors='ignore') as f:
            self.raw_html = f.read()
        
        # Extract business data from different sources
        self.extract_from_json_data()
        self.extract_from_html_elements()
        
        print(f"Found {len(self.businesses)} businesses")
        return self.businesses
    
    def extract_from_json_data(self):
        """Extract business data from embedded JSON in the HTML."""
        # Look for various patterns of embedded JSON data
        json_patterns = [
            r'window\.APP_INITIALIZATION_STATE\s*=\s*(\[.*?\]);',
            r'window\.APP_OPTIONS\s*=\s*(\[.*?\]);',
            r'"businesses":\s*(\[.*?\])',
            r'"results":\s*(\[.*?\])',
        ]
        
        for pattern in json_patterns:
            matches = re.findall(pattern, self.raw_html, re.DOTALL)
            for match in matches:
                try:
                    data = json.loads(match)
                    self._extract_businesses_from_json(data)
                except json.JSONDecodeError:
                    continue
    
    def _extract_businesses_from_json(self, data):
        """Recursively extract business information from JSON data."""
        if isinstance(data, dict):
            # Look for business-like objects
            if self._is_business_object(data):
                business = self._parse_business_object(data)
                if business:
                    self.businesses.append(business)
            
            # Recursively search in nested objects
            for value in data.values():
                self._extract_businesses_from_json(value)
                
        elif isinstance(data, list):
            for item in data:
                self._extract_businesses_from_json(item)
    
    def _is_business_object(self, obj):
        """Check if a JSON object looks like a business entry."""
        if not isinstance(obj, dict):
            return False
        
        # Look for typical business fields
        business_indicators = ['name', 'address', 'phone', 'website', 'rating', 'reviews']
        return any(key.lower() in str(obj.keys()).lower() for key in business_indicators)
    
    def _parse_business_object(self, obj):
        """Parse a business object and extract relevant fields."""
        business = {
            'name': '',
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
        
        # Extract data with various possible field names
        name_fields = ['name', 'title', 'businessName', 'placeName']
        for field in name_fields:
            if field in obj and obj[field]:
                business['name'] = str(obj[field])
                break
        
        address_fields = ['address', 'location', 'addr', 'fullAddress']
        for field in address_fields:
            if field in obj and obj[field]:
                business['address'] = str(obj[field])
                break
        
        phone_fields = ['phone', 'phoneNumber', 'tel', 'telephone']
        for field in phone_fields:
            if field in obj and obj[field]:
                business['phone'] = str(obj[field])
                break
        
        website_fields = ['website', 'url', 'homepage', 'web']
        for field in website_fields:
            if field in obj and obj[field]:
                business['website'] = str(obj[field])
                break
        
        return business if business['name'] else None
    
    def extract_from_html_elements(self):
        """Extract business data from HTML elements."""
        soup = BeautifulSoup(self.raw_html, 'html.parser')
        
        # Look for common Google Maps result containers
        selectors = [
            '[data-result-id]',
            '[data-cid]',
            '.place-result',
            '[role="article"]',
            '.search-result'
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            for element in elements:
                business = self._parse_html_business_element(element)
                if business and business not in self.businesses:
                    self.businesses.append(business)
    
    def _parse_html_business_element(self, element):
        """Parse a single HTML business element."""
        business = {
            'name': '',
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
        
        # Extract name
        name_selectors = ['h3', '.title', '[aria-label*="name"]', '.business-name']
        for selector in name_selectors:
            name_elem = element.select_one(selector)
            if name_elem:
                business['name'] = name_elem.get_text(strip=True)
                break
        
        # Extract address
        address_selectors = ['.address', '[data-value*="address"]', '.location']
        for selector in address_selectors:
            addr_elem = element.select_one(selector)
            if addr_elem:
                business['address'] = addr_elem.get_text(strip=True)
                break
        
        # Extract phone
        phone_links = element.select('a[href^="tel:"]')
        if phone_links:
            business['phone'] = phone_links[0].get('href', '').replace('tel:', '')
        
        # Extract website
        website_links = element.select('a[href*="http"]')
        for link in website_links:
            href = link.get('href', '')
            if 'facebook.com' in href:
                business['facebook'] = href
            elif 'instagram.com' in href:
                business['instagram'] = href
            elif not business['website'] and href.startswith('http'):
                business['website'] = href
        
        return business if business['name'] else None
    
    def search_businesses(self, query):
        """Search businesses by name, address, or other fields."""
        query = query.lower()
        results = []
        
        for business in self.businesses:
            # Search in all text fields
            searchable_text = ' '.join([
                business.get('name', ''),
                business.get('address', ''),
                business.get('category', ''),
                business.get('phone', ''),
                business.get('website', '')
            ]).lower()
            
            if query in searchable_text:
                results.append(business)
        
        return results
    
    def export_to_excel(self, output_path=None):
        """Export businesses to Excel file."""
        if not self.businesses:
            print("No businesses found to export.")
            return None
        
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"google_maps_businesses_{timestamp}.xlsx"
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
        
        # Create DataFrame
        df = pd.DataFrame(self.businesses)
        
        # Clean up the data
        for col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            df[col] = df[col].replace('', 'N/A')
        
        # Write to Excel with formatting
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Businesses', index=False)
            
            # Get the workbook and worksheet
            workbook = writer.book
            worksheet = writer.sheets['Businesses']
            
            # Auto-adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        print(f"Exported {len(self.businesses)} businesses to: {output_path}")
        return output_path
    
    def print_summary(self):
        """Print a summary of parsed businesses."""
        print(f"\n=== PARSING SUMMARY ===")
        print(f"Total businesses found: {len(self.businesses)}")
        
        if self.businesses:
            print(f"\nSample entries:")
            for i, business in enumerate(self.businesses[:3]):
                print(f"\n{i+1}. {business.get('name', 'N/A')}")
                print(f"   Address: {business.get('address', 'N/A')}")
                print(f"   Phone: {business.get('phone', 'N/A')}")
                print(f"   Website: {business.get('website', 'N/A')}")
        
        # Count fields with data
        field_counts = {}
        for business in self.businesses:
            for field, value in business.items():
                if value and value.strip():
                    field_counts[field] = field_counts.get(field, 0) + 1
        
        print(f"\nData completeness:")
        for field, count in sorted(field_counts.items()):
            percentage = (count / len(self.businesses)) * 100 if self.businesses else 0
            print(f"   {field}: {count}/{len(self.businesses)} ({percentage:.1f}%)")


def main():
    """Command-line interface for the parser."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python parser.py <html_file_path> [output_excel_path]")
        return
    
    html_file = sys.argv[1]
    output_excel = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(html_file):
        print(f"Error: HTML file not found: {html_file}")
        return
    
    # Parse the HTML file
    parser = GoogleMapsParser(html_file)
    businesses = parser.parse_html_file()
    
    # Print summary
    parser.print_summary()
    
    # Export to Excel
    if businesses:
        excel_file = parser.export_to_excel(output_excel)
        print(f"\nExcel file created: {excel_file}")
    
    # Interactive search
    while True:
        query = input("\nEnter search term (or 'quit' to exit): ").strip()
        if query.lower() in ['quit', 'exit', 'q']:
            break
        
        if query:
            results = parser.search_businesses(query)
            print(f"\nFound {len(results)} matches:")
            for i, business in enumerate(results[:10]):  # Show first 10
                print(f"{i+1}. {business.get('name', 'N/A')} - {business.get('address', 'N/A')}")


if __name__ == "__main__":
    main()
