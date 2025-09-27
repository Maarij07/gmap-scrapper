# gmap-scrapper

🚀 **Infinite Google Maps Lead Scraper** with Google Sheets Integration

An automated Python scraper that continuously extracts business leads from Google Maps and saves them directly to Google Sheets in real-time.

## ✨ Features

- 🔄 **Infinite Scrolling**: Continuously scrapes until you stop it manually
- 📊 **Google Sheets Integration**: Real-time data export to a single consolidated sheet
- 🎯 **Comprehensive Data**: Extracts business name, address, phone, website, social media, ratings, and more
- 🔍 **Smart Duplicate Prevention**: Avoids scraping the same business twice
- 🛡️ **Error Handling**: Robust error handling and recovery
- 🖥️ **GUI Interface**: Simple tkinter interface for search inputs

## 📊 Data Captured

Each business entry includes:
- Business name and address
- Phone number and website
- Instagram and Facebook links  
- Google rating and review count
- Business category and hours
- Search region and term
- Timestamp of when scraped

## 🔧 Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/Maarij07/gmap-scrapper.git
cd gmap-scrapper
```

### 2. Create Virtual Environment
```bash
python -m venv .venv
```

### 3. Activate Virtual Environment
**Windows:**
```bash
.venv\Scripts\activate
```

**macOS/Linux:**
```bash
source .venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Google Sheets API Setup

#### A. Create Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable "Google Sheets API" and "Google Drive API"

#### B. Create Service Account
1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "Service Account"
3. Download the JSON key file
4. **Rename it to `credentials.json`** and place in project root

#### C. Create Google Sheet
1. Go to [Google Sheets](https://sheets.google.com)
2. Create new sheet named: **"CodeKraft - Leads"**
3. Share it with your service account email (found in credentials.json)
4. Give "Editor" permissions

## 🚀 Usage

### Run the Scraper
```bash
python src/main.py
```

### How It Works
1. **Input**: Enter region and search term (e.g., "UK" + "Restaurants")
2. **Scraping**: Opens Google Maps and starts infinite scraping
3. **Real-time Export**: Each business is immediately saved to Google Sheets
4. **Stop**: Close the browser window to stop scraping

### Example Searches
- Region: "London", Search: "Coffee shops"
- Region: "New York", Search: "Pizza restaurants"  
- Region: "California", Search: "Tech companies"

## 📁 Project Structure

```
gmap-scrapper/
├── src/
│   ├── main.py           # Main scraper application
│   └── parser.py         # HTML parsing utilities (legacy)
├── data/                 # Output directory
├── .venv/               # Virtual environment
├── credentials.json     # Google Sheets API credentials (not tracked)
├── requirements.txt     # Python dependencies
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

## 🛠️ Requirements

- Python 3.8+
- Chrome browser
- Google account with Sheets access
- Internet connection

## 📦 Dependencies

- `selenium` - Web automation
- `webdriver-manager` - Chrome driver management
- `gspread` - Google Sheets API client
- `google-auth` - Google authentication
- `tkinter` - GUI interface (built-in)

## ⚠️ Important Notes

- **Infinite Scraping**: Runs until manually stopped
- **Rate Limiting**: Built-in delays to avoid being blocked
- **Data Privacy**: All data saved to your private Google Sheet
- **Browser Required**: Needs Chrome browser installed
- **Credentials Security**: Never commit `credentials.json` to Git

## 🔍 Troubleshooting

### Common Issues

**"credentials.json not found"**
- Ensure the file is in the project root directory
- Check filename is exactly `credentials.json`

**"Failed to connect to Google Sheets"**
- Verify APIs are enabled (Sheets + Drive)
- Check service account has sheet access
- Ensure sheet name is exactly "CodeKraft - Leads"

**"No businesses found"**
- Try different search terms
- Check internet connection
- Verify Google Maps loads properly

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is for educational purposes only. Please respect Google's Terms of Service and use responsibly.

## 🔗 Links

- [Google Cloud Console](https://console.cloud.google.com/)
- [Google Sheets API Documentation](https://developers.google.com/sheets/api)
- [Selenium Documentation](https://selenium-python.readthedocs.io/)

---

**⚡ Happy Scraping!** 

Built with ❤️ for lead generation automation.
