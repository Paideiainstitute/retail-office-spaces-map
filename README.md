# Retail & Office Spaces Map

An interactive Google Maps application for visualizing retail and office spaces in Manhattan, with the ability to find nearby spaces and manage preferences.

## Features

- **Interactive Map**: View retail (red) and office (blue) spaces on Google Maps
- **Dual Search Modes**: 
  - Search by Retail: Click red dots to see nearby office spaces
  - Search by Office: Click blue dots to see nearby retail spaces
- **Distance Filtering**: Shows spaces within 500 feet of selected location
- **Dislike Functionality**: Mark spaces as grey for the current session
- **PDF Integration**: Direct links to source PDFs with page numbers
- **Geocoding**: Automatic address-to-coordinates conversion

## Files

- `retail_office_map.html` - Main application (requires local server)
- `retail_office_map_github.html` - GitHub Pages version (standalone)
- `simple_parser.py` - Python script to parse PDF text files
- `all_spaces.csv` - Generated data file
- `serve_map.py` - Local development server

## Local Development

1. **Install dependencies**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Run the local server**:
   ```bash
   python serve_map.py
   ```

3. **Open in browser**: http://localhost:8000/retail_office_map.html

## GitHub Pages Deployment

1. **Upload files to GitHub repository**
2. **Enable GitHub Pages** in repository settings
3. **Use the GitHub Pages version**: `retail_office_map_github.html`
4. **Rename to `index.html`** for automatic serving

### GitHub Pages Setup Steps:

1. Create a new repository on GitHub
2. Upload `retail_office_map_github.html` and rename it to `index.html`
3. Go to repository Settings → Pages
4. Select "Deploy from a branch" → "main" → "/ (root)"
5. Your app will be available at: `https://yourusername.github.io/your-repo-name`

## Data Source

The application processes text files extracted from CoStar PDFs:
- `retail_full_text.txt` - Ground floor retail spaces
- `office_full_text.txt` - Office spaces with floor information

## Google Maps API

Requires a Google Maps JavaScript API key with the following APIs enabled:
- Maps JavaScript API
- Geocoding API

## Requirements

- Python 3.7+ (for local development)
- Google Maps API key
- Modern web browser with JavaScript enabled

## Usage

1. **Toggle Search Mode**: Use the switch in the top-left to choose between retail and office search
2. **Click Markers**: Click any marker to see details and nearby spaces
3. **Dislike Spaces**: Use the dislike button to mark spaces as grey for the session
4. **View PDFs**: Click the PDF link to open the source document at the relevant page

## Technical Details

- **Frontend**: HTML, CSS, JavaScript with Google Maps API
- **Backend**: Python for data processing (local development only)
- **Data Format**: CSV with embedded JavaScript for GitHub Pages
- **Geocoding**: Google Maps Geocoding API
- **Distance Calculation**: Google Maps Geometry Library
