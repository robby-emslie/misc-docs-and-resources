"""
scraper.py
a simple commandline scraper to convert HTML tables to CSV

requires BeautifulSoup (v4) and requests:
pip install requests beautifulsoup4
"""

import argparse
import requests
from bs4 import BeautifulSoup
import csv
import re
from urllib.parse import urlparse
from pathlib import Path

def sanitize_filename(filename):
    """Replace spaces and special characters with underscores."""
    filename = re.sub(r'[^\w\s-]', '', filename)
    filename = re.sub(r'[\s-]+', '_', filename)
    return filename.strip('_') + '.csv'

def get_default_filename(url, html_content):
    """
    Generate a default filename from the HTML title or URL.
    Priority: <title> tag > URL filename > 'output'
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    title_tag = soup.find('title')
    
    if title_tag and title_tag.string:
        return sanitize_filename(title_tag.string)
    
    # Fall back to URL filename
    parsed_url = urlparse(url)
    filename = Path(parsed_url.path).stem
    
    if filename:
        return sanitize_filename(filename) + '.csv'
    
    return 'output.csv'

def scrape_tables(url):
    """Fetch HTML and extract all tables."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=60)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching URL: {e}")
        return None

def parse_tables_to_csv(html_content):
    """Parse HTML tables and return as list of lists."""
    soup = BeautifulSoup(html_content, 'html.parser')
    tables = soup.find_all('table')
    
    if not tables:
        print("No tables found in the HTML.")
        return []
    
    all_tables_data = []
    
    for table_idx, table in enumerate(tables):
        table_data = []
        rows = table.find_all('tr')
        
        for row in rows:
            cols = row.find_all(['td', 'th'])
            row_data = [col.get_text(strip=True) for col in cols]
            if row_data:
                table_data.append(row_data)
        
        if table_data:
            all_tables_data.append(table_data)
    
    return all_tables_data

def write_csv(output_file, tables_data):
    """Write table data to CSV file."""
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            for table_idx, table_data in enumerate(tables_data):
                if table_idx > 0:
                    csvfile.write('\n')
                
                writer = csv.writer(csvfile)
                writer.writerows(table_data)
        
        print(f"Successfully wrote tables to {output_file}")
    except IOError as e:
        print(f"Error writing to file: {e}")

def main():
    parser = argparse.ArgumentParser(
        description='Scrape HTML tables from a URL and export to CSV'
    )
    parser.add_argument(
        '--source',
        required=True,
        help='URL to scrape data from'
    )
    parser.add_argument(
        '--output',
        help='Output CSV filename (optional)'
    )
    
    args = parser.parse_args()
    
    # Fetch HTML
    html_content = scrape_tables(args.source)
    if not html_content:
        return
    
    # Determine output filename
    output_file = args.output or get_default_filename(args.source, html_content)
    
    # Parse tables
    tables_data = parse_tables_to_csv(html_content)
    if not tables_data:
        return
    
    # Write to CSV
    write_csv(output_file, tables_data)

if __name__ == '__main__':
    main()
 