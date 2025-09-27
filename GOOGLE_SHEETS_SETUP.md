# Google Sheets Setup Instructions

Your scraper is now configured for **INFINITE SCROLLING** and **GOOGLE SHEETS INTEGRATION**!

## ✨ What's New:

1. **🔄 Infinite Scrolling**: Continuously scrapes businesses until you close the browser
2. **📊 Google Sheets Integration**: Each business is saved to Google Sheets immediately
3. **🚫 No Excel**: Removed Excel functionality completely

## 🔧 Google Sheets API Setup (Required)

To use Google Sheets integration, you need to set up a Google Service Account:

### Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a Project" → "New Project"
3. Name your project (e.g., "Google Maps Scraper")
4. Click "Create"

### Step 2: Enable Google Sheets API

1. In your project dashboard, go to "APIs & Services" → "Library"
2. Search for "Google Sheets API"
3. Click on it and press "Enable"
4. Also search for "Google Drive API" and enable it too

### Step 3: Create Service Account

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "Service Account"
3. Name it (e.g., "sheets-scraper")
4. Click "Create and Continue"
5. For role, select "Editor" (or you can skip this step)
6. Click "Done"

### Step 4: Generate Service Account Key

1. In "Credentials", find your service account
2. Click on the service account email
3. Go to "Keys" tab
4. Click "Add Key" → "Create New Key"
5. Select "JSON" format
6. Click "Create"
7. **A JSON file will download** - this is your credentials file!

### Step 5: Setup Credentials File

1. **Rename** the downloaded JSON file to `credentials.json`
2. **Move** it to your scraper directory:
   ```
   D:\temp\development\python\gmap-scrapper\credentials.json
   ```

The file should look like this:
```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...",
  "client_email": "sheets-scraper@your-project.iam.gserviceaccount.com",
  "client_id": "...",
  ...
}
```

### Step 6: Test Connection (Optional)

Run your scraper once to test the Google Sheets connection:
```powershell
& "D:\temp\development\python\gmap-scrapper\.venv\Scripts\python.exe" "D:\temp\development\python\gmap-scrapper\src\main.py"
```

## 🚀 How It Works Now:

1. **Input**: Enter region and search term (e.g., "UK" + "Ecommerce")
2. **Google Sheet Creation**: A new sheet is created automatically named:
   - `"Google Maps Leads - UK Ecommerce"`
3. **Infinite Scraping**: The scraper will:
   - Open Google Maps
   - Search for businesses
   - Click each business and extract details
   - **Save immediately to Google Sheets**
   - Scroll down for more results
   - Repeat forever until you close the browser
4. **Real-time Updates**: Watch your Google Sheet fill up in real-time!

## 📊 Data Captured:

Each business row includes:
- Name, Address, Phone, Website
- Instagram, Facebook links
- Rating, Reviews count, Category
- Hours, Price range
- Region, Search term, Timestamp

## ⚠️ Important Notes:

- **Manual Stop**: Close the browser window to stop scraping
- **Live Updates**: Data is saved immediately, no waiting for completion
- **Duplicate Prevention**: Same businesses won't be scraped twice
- **Error Handling**: If one business fails, it continues with the next

## 🔍 Troubleshooting:

**Error: "credentials.json not found"**
- Make sure the file is in the correct location
- Check the filename is exactly `credentials.json`

**Error: "Failed to connect to Google Sheets"**
- Verify the APIs are enabled (Sheets API + Drive API)
- Check your service account has proper permissions

**No businesses found**
- Try different search terms
- Check your internet connection
- Make sure Google Maps loads properly

## 🎯 Pro Tips:

1. **Monitor Progress**: Watch the console output to see businesses being found
2. **Multiple Searches**: Run different searches to separate sheets
3. **Data Analysis**: Use Google Sheets built-in tools to analyze your leads
4. **Export Options**: From Google Sheets, you can export to Excel, CSV, etc.

---

**Ready to scrape?** Make sure `credentials.json` is in place, then run your scraper! 🚀
