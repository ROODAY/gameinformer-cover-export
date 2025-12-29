# Game Informer Cover Export

Scripts to download Game Informer magazine cover images from the covers gallery page.

## Setup

1. Install Python dependencies (you should probably make a venv):
```bash
pip install -r requirements.txt
```

## Usage

Run the download script:
```bash
python download_covers.py
```

The script will:
1. Scrape the covers page at https://gameinformer.com/covers
2. Extract all gallery link URLs
3. Normalize URLs to ensure they all have the format:
   `https://gameinformer.com/sites/default/files/styles/no_compression/public/.../...jpg.webp`
4. Save the normalized URLs to `urls.json`
5. Download all images to the `output/` folder (skipping files that already exist)
