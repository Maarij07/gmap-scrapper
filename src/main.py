import tkinter as tk
from tkinter import messagebox
import os
from datetime import datetime
import time
from typing import List
import json

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

try:
    import gspread
    from google.oauth2.service_account import Credentials
    GOOGLE_SHEETS_AVAILABLE = True
except ImportError:
    GOOGLE_SHEETS_AVAILABLE = False
    print("Warning: Google Sheets packages not installed. Run: pip install gspread google-auth")


def slugify(value: str) -> str:
    """Create a filesystem-safe slug from a string."""
    if not value:
        return ""
    safe = []
    for ch in value:
        if ch.isalnum():
            safe.append(ch)
        else:
            safe.append('_')
    # collapse multiple underscores and trim length
    slug = ''.join(safe)
    while '__' in slug:
        slug = slug.replace('__', '_')
    return slug.strip('_')[:80]


def get_user_input():
    """Shows a GUI dialog to collect region and search term from user."""
    
    root = tk.Tk()
    root.title("Google Maps Lead Scraper")
    root.geometry("400x200")
    root.resizable(False, False)
    
    # Center the window
    root.eval('tk::PlaceWindow . center')
    
    # Variables to store user input
    region_var = tk.StringVar(value="UK")
    search_var = tk.StringVar(value="Ecommerce")
    result = {"region": None, "search_term": None, "cancelled": True}
    
    def on_ok():
        result["region"] = region_var.get()
        result["search_term"] = search_var.get()
        result["cancelled"] = False
        root.destroy()
    
    def on_cancel():
        root.destroy()
    
    # Create form layout
    tk.Label(root, text="Google Maps Lead Scraper", font=("Arial", 14, "bold")).pack(pady=10)
    
    # Region input
    frame1 = tk.Frame(root)
    frame1.pack(pady=5)
    tk.Label(frame1, text="Region:", width=12, anchor="w").pack(side=tk.LEFT)
    tk.Entry(frame1, textvariable=region_var, width=30).pack(side=tk.LEFT)
    
    # Search term input
    frame2 = tk.Frame(root)
    frame2.pack(pady=5)
    tk.Label(frame2, text="Search Word:", width=12, anchor="w").pack(side=tk.LEFT)
    tk.Entry(frame2, textvariable=search_var, width=30).pack(side=tk.LEFT)
    
    # Buttons
    button_frame = tk.Frame(root)
    button_frame.pack(pady=20)
    tk.Button(button_frame, text="OK", command=on_ok, width=10).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="Cancel", command=on_cancel, width=10).pack(side=tk.LEFT, padx=5)
    
    root.mainloop()
    
    return result


class GoogleSheetsManager:
    """Manages Google Sheets connection and operations."""
    
    def __init__(self, credentials_path: str, spreadsheet_name: str):
        self.credentials_path = credentials_path
        self.spreadsheet_name = spreadsheet_name
        self.sheet = None
        self.worksheet = None
        
    def connect(self):
        """Initialize connection to Google Sheets."""
        try:
            if not GOOGLE_SHEETS_AVAILABLE:
                raise Exception("Google Sheets packages not installed")
                
            # Define the scope
            scope = [
                "https://spreadsheets.google.com/feeds",
                "https://www.googleapis.com/auth/drive"
            ]
            
            # Load credentials
            creds = Credentials.from_service_account_file(self.credentials_path, scopes=scope)
            client = gspread.authorize(creds)
            
            # Try to open existing spreadsheet or create new one
            try:
                self.sheet = client.open(self.spreadsheet_name)
                print(f"Connected to existing Google Sheet: {self.spreadsheet_name}")
            except gspread.SpreadsheetNotFound:
                self.sheet = client.create(self.spreadsheet_name)
                print(f"Created new Google Sheet: {self.spreadsheet_name}")
            
            # Get or create 'Businesses' worksheet
            try:
                self.worksheet = self.sheet.worksheet('Businesses')
            except gspread.WorksheetNotFound:
                self.worksheet = self.sheet.add_worksheet('Businesses', 1000, 20)
                
            return True
            
        except Exception as e:
            print(f"Failed to connect to Google Sheets: {e}")
            return False
    
    def ensure_headers(self, columns: List[str]):
        """Ensure the worksheet has proper headers; replace if mismatched."""
        try:
            header = self.worksheet.row_values(1)
            if not header:
                self.worksheet.insert_row(columns, 1)
                print(f"Added headers to Google Sheet: {columns}")
            else:
                # If existing header doesn't match desired columns, replace row 1
                if header != columns[:len(header)] or len(header) != len(columns):
                    self.worksheet.update('A1', [columns])
                    print(f"Replaced headers to: {columns}")
        except Exception as e:
            print(f"Failed to ensure headers: {e}")
    
    def append_row(self, business: dict, columns: List[str]):
        """Append a business row to the Google Sheet."""
        try:
            row = [str(business.get(col, '')) for col in columns]
            self.worksheet.append_row(row)
            print(f"  → Saved to Google Sheets: {business.get('name', 'Unknown')}")
            return True
        except Exception as e:
            print(f"Failed to append to Google Sheets: {e}")
            return False


def extract_business_details(driver, wait):
    """Extract detailed information from a business page."""
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
    
    try:
        # Wait a moment for the page to load
        time.sleep(2)
        
        # Extract business name
        try:
            name_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1.DUwDvf.lfPIob")))
            business['name'] = name_element.text.strip()
            print(f"  Found business: {business['name']}")
        except:
            try:
                name_element = driver.find_element(By.CSS_SELECTOR, "[data-attrid='title'] span")
                business['name'] = name_element.text.strip()
            except:
                print("  Could not find business name")
        
        # Extract rating and reviews
        try:
            rating_element = driver.find_element(By.CSS_SELECTOR, "div.F7nice span[aria-hidden='true']")
            business['rating'] = rating_element.text.strip()
            
            reviews_element = driver.find_element(By.CSS_SELECTOR, "div.F7nice span[aria-label*='reviews']")
            business['reviews_count'] = reviews_element.text.strip().replace('(', '').replace(')', '')
        except:
            pass
        
        # Extract category
        try:
            category_element = driver.find_element(By.CSS_SELECTOR, "button[jsaction*='category'] span")
            business['category'] = category_element.text.strip()
        except:
            pass
        
        # Extract address
        try:
            address_element = driver.find_element(By.CSS_SELECTOR, "button[data-item-id='address'] div.Io6YTe")
            business['address'] = address_element.text.strip()
        except:
            pass
        
        # Extract phone number
        try:
            phone_element = driver.find_element(By.CSS_SELECTOR, "button[data-item-id*='phone'] div.Io6YTe")
            business['phone'] = phone_element.text.strip()
        except:
            pass
        
        # Extract website
        try:
            website_element = driver.find_element(By.CSS_SELECTOR, "a[data-item-id='authority'] div.Io6YTe")
            business['website'] = website_element.text.strip()
        except:
            pass
        
        # Extract hours
        try:
            hours_element = driver.find_element(By.CSS_SELECTOR, "div[data-attrid='kc:/location:hours'] span")
            business['hours'] = hours_element.text.strip()
        except:
            pass
        
        # Look for social media links
        try:
            social_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='facebook.com'], a[href*='instagram.com']")
            for link in social_links:
                href = link.get_attribute('href')
                if 'facebook.com' in href:
                    business['facebook'] = href
                elif 'instagram.com' in href:
                    business['instagram'] = href
        except:
            pass
        
    except Exception as e:
        print(f"  Error extracting details: {str(e)}")
    
    return business


def scrape_google_maps_infinite(region, search_term, sheets_manager: GoogleSheetsManager = None, columns: List[str] = None):
    """Opens Google Maps, searches for businesses, and continuously scrapes with infinite scrolling.
    Saves each business to Google Sheets immediately.
    """
    
    print(f"Starting INFINITE Google Maps scraping for '{search_term}' in '{region}'...")
    print("⚠️  This will run until you manually close the browser window!")
    businesses_found = 0
    
    # Set up Chrome options
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Initialize the Chrome driver with automatic version management
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        # Navigate to Google Maps
        print("Opening Google Maps...")
        driver.get("https://maps.google.com")
        
        # Wait for the search box to be present
        wait = WebDriverWait(driver, 15)
        search_box = wait.until(EC.presence_of_element_located((By.ID, "searchboxinput")))
        
        # Construct search query
        search_query = f"{search_term} in {region}"
        print(f"Searching for: {search_query}")
        
        # Enter search query
        search_box.clear()
        search_box.send_keys(search_query)
        
        # Click search button
        search_button = driver.find_element(By.ID, "searchbox-searchbutton")
        search_button.click()
        
        # Wait for results to load
        print("Waiting for search results to load...")
        time.sleep(5)
        
        # Wait for the results panel to appear
        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='main']"))) 
            print("Search results loaded successfully!")
        except:
            print("Results may still be loading, proceeding anyway...")
        
        time.sleep(3)

        # Find all business result links
        
        processed_businesses = set()
        scroll_attempts_without_new_results = 0
        max_scroll_attempts_without_results = 5
        
        print("\n🔄 Starting infinite scraping loop...")
        print("   Close the browser window to stop scraping.\n")
        
        while True:  # Infinite loop
            
            # Find business result links
            try:
                # Look for clickable business results
                business_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/maps/place/']")
                
                if not business_links:
                    print("No business links found, trying alternative selectors...")
                    business_links = driver.find_elements(By.CSS_SELECTOR, "div[data-result-id] a")
                
                print(f"Found {len(business_links)} business links on current view")
                
                initial_businesses_count = businesses_found
                
                # Click on each business link
                for i, link in enumerate(business_links):
                    
                    try:
                        # Get business identifier to avoid duplicates
                        href = link.get_attribute('href')
                        if href in processed_businesses:
                            continue
                        processed_businesses.add(href)
                        
                        print(f"\nClicking on business {businesses_found + 1}...")
                        
                        # Scroll to the element and click
                        driver.execute_script("arguments[0].scrollIntoView(true);", link)
                        time.sleep(1)
                        
                        # Click the business link
                        driver.execute_script("arguments[0].click();", link)
                        
                        # Wait for the business page to load
                        time.sleep(3)
                        
                        # Extract business details
                        business = extract_business_details(driver, wait)

                        # Enrich with metadata and append to Google Sheets immediately
                        enriched = dict(business)
                        enriched['region'] = region
                        enriched['search_term'] = search_term
                        enriched['scraped_at'] = datetime.now().isoformat(timespec='seconds')

                        if business['name']:
                            # Append immediately to Google Sheets
                            if sheets_manager and columns:
                                sheets_manager.append_row(enriched, columns)
                            businesses_found += 1
                            print(f"  ✓ Business #{businesses_found}: {business['name']}")
                        else:
                            print(f"  ✗ Could not extract business name")
                        
                        # Go back to search results
                        driver.back()
                        time.sleep(2)
                        
                    except Exception as e:
                        print(f"  Error processing business {i+1}: {str(e)}")
                        try:
                            driver.back()
                            time.sleep(1)
                        except:
                            pass
                        continue
                
                # Check if we found new businesses in this iteration
                if businesses_found > initial_businesses_count:
                    scroll_attempts_without_new_results = 0
                    print(f"\n📊 Total businesses found so far: {businesses_found}")
                else:
                    scroll_attempts_without_new_results += 1
                    print(f"\n⏳ No new businesses found (attempt {scroll_attempts_without_new_results}/{max_scroll_attempts_without_results})")
                
                # Always try to scroll down to load more results
                print("🔄 Scrolling to load more results...")
                try:
                    # Find the scrollable results container
                    results_container = driver.find_element(By.CSS_SELECTOR, "div[role='main']")
                    driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", results_container)
                    time.sleep(4)
                    
                    # Also try scrolling within the page
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)
                except Exception as scroll_error:
                    print(f"Scroll error: {scroll_error}")
                    time.sleep(3)
                
                # If no new results found for several attempts, try a longer wait
                if scroll_attempts_without_new_results >= max_scroll_attempts_without_results:
                    print("\n⏸️  No new results found after multiple scrolls. Waiting longer...")
                    time.sleep(10)
                    scroll_attempts_without_new_results = 0  # Reset counter
                
            except Exception as e:
                print(f"Error in main scraping loop: {str(e)}")
                break
        
        # This should never be reached in infinite mode
        print(f"\n✅ Scraping ended. Total businesses found: {businesses_found}")
        return businesses_found
        
    except KeyboardInterrupt:
        print(f"\n\n🛑 Scraping stopped by user. Total businesses found: {businesses_found}")
        return businesses_found
    except Exception as e:
        print(f"\n❌ An error occurred: {str(e)}")
        print(f"Total businesses found before error: {businesses_found}")
        return businesses_found
        
    finally:
        print("\n🔄 Browser will close in 10 seconds...")
        time.sleep(10)
        try:
            driver.quit()
        except:
            pass


def main():
    """Main function to run the Google Maps scraper."""
    
    print("Google Maps Lead Scraper")
    print("=" * 40)
    
    # Get user input
    user_input = get_user_input()
    
    if user_input["cancelled"]:
        print("Operation cancelled by user.")
        return
    
    region = user_input["region"].strip()
    search_term = user_input["search_term"].strip()
    
    if not region or not search_term:
        messagebox.showerror("Error", "Both region and search term are required!")
        return
    
    # Perform the infinite scraping with Google Sheets
    try:
        # Setup Google Sheets connection
        credentials_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "credentials.json")
        spreadsheet_name = "CodeKraft - Leads"
        
        sheets_manager = None
        if os.path.exists(credentials_path):
            sheets_manager = GoogleSheetsManager(credentials_path, spreadsheet_name)
            if sheets_manager.connect():
                # Define column order for Google Sheets
                columns = [
                    'name', 'address', 'phone', 'website', 'instagram', 'facebook',
                    'rating', 'reviews_count', 'category', 'hours', 'price_range',
                    'region', 'search_term', 'scraped_at'
                ]
                sheets_manager.ensure_headers(columns)
                print(f"✅ Connected to Google Sheets: {spreadsheet_name}")
            else:
                sheets_manager = None
        else:
            print("❌ credentials.json not found. Google Sheets integration disabled.")
            print("   See setup instructions after scraping.")
        
        if not sheets_manager:
            response = messagebox.askyesno(
                "No Google Sheets", 
                "Google Sheets not configured.\n\nContinue anyway? (Data will be lost)\n\nClick 'Yes' to continue or 'No' to cancel."
            )
            if not response:
                return
        
        # Run infinite scraper
        total_found = scrape_google_maps_infinite(
            region,
            search_term,
            sheets_manager,
            columns if sheets_manager else None
        )
        
        if total_found > 0:
            message = f"🎉 Infinite scraping completed!\n\nTotal businesses found: {total_found}"
            if sheets_manager:
                message += f"\n\n📊 All data saved to Google Sheets:\n{spreadsheet_name}"
            messagebox.showinfo("Scraping Complete", message)
        else:
            message = "No businesses were found.\n\nThis could be because:\n- No search results available\n- Page structure changed\n- Network issues"
            messagebox.showwarning("No Results", message)
            
    except Exception as e:
        error_msg = f"An error occurred: {str(e)}"
        print(error_msg)
        messagebox.showerror("Error", error_msg)


if __name__ == "__main__":
    main()
