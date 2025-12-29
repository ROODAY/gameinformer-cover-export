#!/usr/bin/env python3
"""
Script to download Game Informer cover images from the covers gallery page.
"""

import os
import re
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from pathlib import Path


def normalize_url(url):
    """
    Normalize URLs to the format:
    https://gameinformer.com/sites/default/files/styles/no_compression/public/.../...jpg.webp
    """
    # Handle relative URLs
    if not url.startswith('http'):
        url = urljoin('https://gameinformer.com', url)
    
    # Parse the URL
    parsed = urlparse(url)
    
    # Extract the path part after /sites/default/files/
    if '/sites/default/files/' not in parsed.path:
        # This might be a different type of URL, try to handle it
        print(f"Warning: URL doesn't contain /sites/default/files/: {url}")
        return url
    
    # Get everything after /sites/default/files/
    path_after = parsed.path.split('/sites/default/files/')[1]
    
    # Remove any query parameters or fragments
    path_after = path_after.split('?')[0].split('#')[0]
    
    # Remove the /styles/no_compression/public/ prefix if it exists
    if path_after.startswith('styles/no_compression/public/'):
        path_after = path_after[len('styles/no_compression/public/'):]
    
    # Ensure it ends with .jpg.webp (not just .webp)
    if path_after.endswith('.jpg.webp'):
        # Already in correct format
        pass
    elif path_after.endswith('.webp'):
        # Change .webp to .jpg.webp
        path_after = path_after[:-5] + '.jpg.webp'  # Remove .webp and add .jpg.webp
    else:
        # Remove existing image extension and add .jpg.webp
        path_after = re.sub(r'\.(jpg|jpeg|png|webp)$', '', path_after, flags=re.IGNORECASE) + '.jpg.webp'
    
    # Always construct with the /styles/no_compression/public/ prefix
    normalized = f"https://gameinformer.com/sites/default/files/styles/no_compression/public/{path_after}"
    
    return normalized


def scrape_cover_urls():
    """Scrape the covers page and extract all gallery link URLs."""
    url = "https://gameinformer.com/covers"
    
    print(f"Fetching {url}...")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find the covers-container div
    covers_container = soup.find('div', class_='covers-container')
    if not covers_container:
        raise ValueError("Could not find div with class 'covers-container'")
    
    # Find all a tags with class 'gallery' inside the container
    gallery_links = covers_container.find_all('a', class_='gallery')
    
    print(f"Found {len(gallery_links)} gallery links")
    
    # Extract hrefs
    urls = [link.get('href') for link in gallery_links if link.get('href')]
    
    return urls


def download_image(url, output_dir):
    """Download a single image, skipping if it already exists."""
    # Extract filename from URL
    filename = os.path.basename(urlparse(url).path)
    if not filename:
        # Fallback: use a hash or index
        filename = url.split('/')[-1]
    
    filepath = os.path.join(output_dir, filename)
    
    # Skip if already exists
    if os.path.exists(filepath):
        print(f"  Skipping {filename} (already exists)")
        return True
    
    try:
        print(f"  Downloading {filename}...")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        print(f"  ✓ Downloaded {filename}")
        return True
    except Exception as e:
        print(f"  ✗ Error downloading {filename}: {e}")
        return False


def main():
    # Create output directory
    output_dir = Path('output')
    output_dir.mkdir(exist_ok=True)
    
    print("Step 1: Scraping cover URLs from gameinformer.com/covers...")
    raw_urls = scrape_cover_urls()
    
    print(f"\nStep 2: Normalizing {len(raw_urls)} URLs...")
    normalized_urls = []
    for url in raw_urls:
        normalized = normalize_url(url)
        normalized_urls.append(normalized)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_urls = []
    for url in normalized_urls:
        if url not in seen:
            seen.add(url)
            unique_urls.append(url)
    
    print(f"Found {len(unique_urls)} unique URLs after normalization")
    
    # Save URLs to JSON file
    urls_file = 'urls.json'
    with open(urls_file, 'w') as f:
        json.dump(unique_urls, f, indent=4)
    print(f"\nSaved URLs to {urls_file}")
    
    print(f"\nStep 3: Downloading images to {output_dir}...")
    success_count = 0
    skip_count = 0
    
    for i, url in enumerate(unique_urls, 1):
        print(f"[{i}/{len(unique_urls)}] {url}")
        filename = os.path.basename(urlparse(url).path)
        filepath = output_dir / filename
        
        if filepath.exists():
            skip_count += 1
            print(f"  Skipping {filename} (already exists)")
        else:
            if download_image(url, output_dir):
                success_count += 1
            print()
    
    print(f"\nDone! Downloaded {success_count} new images, skipped {skip_count} existing images.")


if __name__ == '__main__':
    main()

