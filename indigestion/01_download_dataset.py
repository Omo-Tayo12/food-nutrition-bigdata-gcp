"""
01_download_dataset.py
======================
Downloads the Food Nutrition datasets from:
  1. Kaggle  — USDA Nutritional Values dataset
  2. OpenFoodFacts — Full product CSV (>1 GB)

Usage:
    python ingestion/01_download_dataset.py

Requirements:
    - kaggle.json credentials at ~/.kaggle/kaggle.json
    - pip install kaggle requests tqdm
"""

import os
import sys
import requests
import subprocess
from pathlib import Path
from tqdm import tqdm

# ─── Configuration ────────────────────────────────────────────────────────────
RAW_DATA_DIR = Path("data/raw")
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

KAGGLE_DATASET = "trolukovich/nutritional-values-for-common-foods-and-products"
OPENFOODFACTS_URL = (
    "https://static.openfoodfacts.org/data/en.openfoodfacts.org.products.csv.gz"
)
OPENFOODFACTS_FILENAME = RAW_DATA_DIR / "openfoodfacts_products.csv.gz"


# ─── 1. Download from Kaggle ─────────────────────────────────────────────────
def download_kaggle_dataset():
    """Download USDA nutrition dataset using the Kaggle CLI."""
    print("\n[1/2] Downloading USDA Nutrition Dataset from Kaggle...")

    kaggle_creds = Path.home() / ".kaggle" / "kaggle.json"
    if not kaggle_creds.exists():
        print(
            "ERROR: kaggle.json not found at ~/.kaggle/kaggle.json\n"
            "Please download your API token from https://www.kaggle.com/settings/account"
        )
        sys.exit(1)

    dest = RAW_DATA_DIR / "kaggle_nutrition"
    dest.mkdir(exist_ok=True)

    result = subprocess.run(
        [
            "kaggle", "datasets", "download",
            "--dataset", KAGGLE_DATASET,
            "--path", str(dest),
            "--unzip",
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(f"Kaggle download error:\n{result.stderr}")
        sys.exit(1)

    csv_files = list(dest.glob("*.csv"))
    if csv_files:
        print(f"  Downloaded {len(csv_files)} file(s): {[f.name for f in csv_files]}")
        for f in csv_files:
            size_mb = f.stat().st_size / (1024 ** 2)
            print(f"  {f.name} — {size_mb:.1f} MB")
    else:
        print("  Warning: No CSV files found in download directory.")

    print("  Kaggle download complete.")
    return dest


# ─── 2. Download OpenFoodFacts ─────────────────────────────────────────────
def download_openfoodfacts():
    """
    Download the OpenFoodFacts full CSV export (~1.6 GB compressed, 3.1 GB uncompressed).
    Uses streaming download with a progress bar.
    """
    print("\n[2/2] Downloading OpenFoodFacts dataset (~1.6 GB compressed)...")
    print(f"  URL: {OPENFOODFACTS_URL}")
    print(f"  Saving to: {OPENFOODFACTS_FILENAME}")
    print("  NOTE: This download may take 10-30 minutes depending on your connection.\n")

    if OPENFOODFACTS_FILENAME.exists():
        size_gb = OPENFOODFACTS_FILENAME.stat().st_size / (1024 ** 3)
        print(f"  File already exists ({size_gb:.2f} GB). Skipping download.")
        return OPENFOODFACTS_FILENAME

    try:
        response = requests.get(OPENFOODFACTS_URL, stream=True, timeout=60)
        response.raise_for_status()

        total_size = int(response.headers.get("content-length", 0))
        block_size = 1024 * 1024  # 1 MB chunks

        with (
            open(OPENFOODFACTS_FILENAME, "wb") as f,
            tqdm(
                total=total_size,
                unit="B",
                unit_scale=True,
                unit_divisor=1024,
                desc="OpenFoodFacts",
            ) as bar,
        ):
            for chunk in response.iter_content(chunk_size=block_size):
                if chunk:
                    f.write(chunk)
                    bar.update(len(chunk))

        size_gb = OPENFOODFACTS_FILENAME.stat().st_size / (1024 ** 3)
        print(f"\n  Download complete: {size_gb:.2f} GB")

    except requests.exceptions.RequestException as e:
        print(f"  Download failed: {e}")
        sys.exit(1)

    return OPENFOODFACTS_FILENAME


# ─── Main ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("  Food Nutrition Dataset Downloader")
    print("  York St John University — Big Data Assignment")
    print("=" * 60)

    kaggle_path = download_kaggle_dataset()
    off_path = download_openfoodfacts()

    print("\n" + "=" * 60)
    print("  All downloads complete!")
    print(f"  Kaggle data  : {kaggle_path}")
    print(f"  OpenFoodFacts: {off_path}")
    print("  Next step: Run  python ingestion/02_upload_to_gcs.py")
    print("=" * 60)
