"""
02_upload_to_gcs.py
===================
Uploads the downloaded food nutrition datasets to Google Cloud Storage (GCS).
Creates bucket lifecycle policies (Standard → Nearline → Coldline → Archive).

Usage:
    python ingestion/02_upload_to_gcs.py

Requirements:
    - gcloud auth application-default login
    - pip install google-cloud-storage
"""

import os
import json
from pathlib import Path
from google.cloud import storage
from google.cloud.storage import Blob

# ─── Configuration ────────────────────────────────────────────────────────────
PROJECT_ID      = os.environ.get("GCP_PROJECT_ID", "your-gcp-project-id")
RAW_BUCKET      = "food-nutrition-raw"
PROCESSED_BUCKET = "food-nutrition-processed"
REGION          = "us-central1"
RAW_DATA_DIR    = Path("data/raw")

# Lifecycle rules: migrate to cheaper tiers as data ages
LIFECYCLE_RULES = [
    {   # Move to Nearline after 30 days (accessed < once/month)
        "action": {"type": "SetStorageClass", "storageClass": "NEARLINE"},
        "condition": {"age": 30, "matchesStorageClass": ["STANDARD"]},
    },
    {   # Move to Coldline after 90 days (accessed < once/quarter)
        "action": {"type": "SetStorageClass", "storageClass": "COLDLINE"},
        "condition": {"age": 90, "matchesStorageClass": ["NEARLINE"]},
    },
    {   # Archive after 365 days
        "action": {"type": "SetStorageClass", "storageClass": "ARCHIVE"},
        "condition": {"age": 365, "matchesStorageClass": ["COLDLINE"]},
    },
]


# ─── Helper: Create bucket with lifecycle ────────────────────────────────────
def create_bucket_if_not_exists(client: storage.Client, bucket_name: str) -> storage.Bucket:
    """Create a GCS bucket if it does not exist, with lifecycle rules applied."""
    bucket = client.bucket(bucket_name)

    if not bucket.exists():
        print(f"  Creating bucket: gs://{bucket_name}/")
        bucket = client.create_bucket(bucket, location=REGION)
        print(f"  Bucket created in {REGION}.")
    else:
        print(f"  Bucket gs://{bucket_name}/ already exists.")

    # Apply lifecycle policy
    bucket.lifecycle_rules = LIFECYCLE_RULES
    bucket.patch()
    print(f"  Lifecycle policy applied to gs://{bucket_name}/")

    # Enable versioning for point-in-time recovery
    bucket.versioning_enabled = True
    bucket.patch()
    print(f"  Object versioning enabled on gs://{bucket_name}/")

    return bucket


# ─── Helper: Upload file with progress ───────────────────────────────────────
def upload_file(bucket: storage.Bucket, local_path: Path, gcs_prefix: str = ""):
    """Upload a local file to GCS, printing progress."""
    gcs_path = f"{gcs_prefix}/{local_path.name}" if gcs_prefix else local_path.name
    blob: Blob = bucket.blob(gcs_path)

    size_mb = local_path.stat().st_size / (1024 ** 2)
    print(f"  Uploading {local_path.name} ({size_mb:.1f} MB) → gs://{bucket.name}/{gcs_path}")

    blob.upload_from_filename(
        str(local_path),
        content_type="text/csv" if local_path.suffix == ".csv" else "application/octet-stream",
        timeout=3600,  # 1-hour timeout for large files
    )

    print(f"  Upload complete: gs://{bucket.name}/{gcs_path}")
    return f"gs://{bucket.name}/{gcs_path}"


# ─── Main ────────────────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("  GCS Upload — Food Nutrition Datasets")
    print("=" * 60)

    client = storage.Client(project=PROJECT_ID)

    # 1. Create buckets
    print("\n[1/3] Setting up GCS buckets...")
    raw_bucket       = create_bucket_if_not_exists(client, RAW_BUCKET)
    processed_bucket = create_bucket_if_not_exists(client, PROCESSED_BUCKET)

    # 2. Upload Kaggle dataset
    print("\n[2/3] Uploading Kaggle USDA Nutrition dataset...")
    kaggle_dir = RAW_DATA_DIR / "kaggle_nutrition"
    uploaded = []
    for csv_file in kaggle_dir.glob("*.csv"):
        gcs_uri = upload_file(raw_bucket, csv_file, gcs_prefix="kaggle/usda_nutrition")
        uploaded.append(gcs_uri)

    # 3. Upload OpenFoodFacts
    print("\n[3/3] Uploading OpenFoodFacts compressed dataset (~1.6 GB)...")
    off_file = RAW_DATA_DIR / "openfoodfacts_products.csv.gz"
    if off_file.exists():
        gcs_uri = upload_file(raw_bucket, off_file, gcs_prefix="openfoodfacts")
        uploaded.append(gcs_uri)
    else:
        print(f"  WARNING: {off_file} not found. Run 01_download_dataset.py first.")

    print("\n" + "=" * 60)
    print("  Upload Summary")
    print("=" * 60)
    for uri in uploaded:
        print(f"  ✓ {uri}")
    print(f"\n  Next step: Run  python processing/04_dataflow_etl.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
