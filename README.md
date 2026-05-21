# Big Data Processing on GCP — Food Nutrition Dataset
**York St John University | MSc Data Science | 2025–2026**

## Project Overview
This repository contains all coding artefacts supporting the assignment:
*"Optimizing Big Data Processing in the Cloud with Data Set Extraction and Analysis"*

- **Domain:** Food Nutrition  
- **Cloud Platform:** Google Cloud Platform (GCP)  
- **Datasets:** USDA Food Nutrition (Kaggle) + OpenFoodFacts (>1 GB)

---

## Repository Structure

```
project/
├── README.md                        ← This file
├── requirements.txt                 ← Python dependencies
├── ingestion/
│   ├── 01_download_dataset.py       ← Download datasets from Kaggle & OpenFoodFacts
│   ├── 02_upload_to_gcs.py          ← Upload raw files to Google Cloud Storage
│   └── 03_pubsub_streaming.py       ← Real-time streaming ingestion via Pub/Sub
├── processing/
│   ├── 04_dataflow_etl.py           ← Apache Beam ETL pipeline (Dataflow)
│   ├── 05_spark_preprocessing.py    ← PySpark pre-processing on Cloud Dataproc
│   └── 06_load_to_bigquery.py       ← Load processed Parquet files into BigQuery
├── analysis/
│   ├── 07_bigquery_analytics.py     ← SQL analytical queries via BigQuery Python API
│   ├── 08_kmeans_bigquery_ml.sql    ← BigQuery ML K-Means clustering
│   ├── 09_xgboost_vertex_ai.py      ← XGBoost Nutri-Score classifier on Vertex AI
│   └── 10_visualisations.py        ← Charts and visualisations with matplotlib/seaborn
├── monitoring/
│   └── 11_monitoring_alerts.py      ← Cloud Monitoring alert policy setup
└── data/
    └── sample_nutrition_100rows.csv ← Sample dataset (100 rows) for testing
```

---

## Prerequisites

### 1. GCP Project Setup
```bash
# Authenticate with GCP
gcloud auth application-default login

# Set your project
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable bigquery.googleapis.com \
    storage.googleapis.com \
    dataflow.googleapis.com \
    pubsub.googleapis.com \
    dataproc.googleapis.com \
    aiplatform.googleapis.com \
    monitoring.googleapis.com
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. Kaggle API Setup
```bash
# Place your kaggle.json credentials in ~/.kaggle/
mkdir ~/.kaggle
cp kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json
```

### 4. Create GCS Buckets
```bash
gsutil mb -l us-central1 gs://food-nutrition-raw/
gsutil mb -l us-central1 gs://food-nutrition-processed/
gsutil mb -l us-central1 gs://food-nutrition-dataflow-temp/
```

---

## Running the Pipeline (Step by Step)

### Step 1 — Download Datasets
```bash
python ingestion/01_download_dataset.py
```

### Step 2 — Upload to GCS
```bash
python ingestion/02_upload_to_gcs.py
```

### Step 3 — Run ETL Pipeline (Dataflow)
```bash
python processing/04_dataflow_etl.py \
    --runner DataflowRunner \
    --project YOUR_PROJECT_ID \
    --region us-central1 \
    --temp_location gs://food-nutrition-dataflow-temp/
```

### Step 4 — Run Spark Pre-processing (Dataproc)
```bash
# Submit PySpark job to Dataproc
gcloud dataproc jobs submit pyspark processing/05_spark_preprocessing.py \
    --cluster=food-nutrition-cluster \
    --region=us-central1
```

### Step 5 — Load to BigQuery
```bash
python processing/06_load_to_bigquery.py
```

### Step 6 — Run Analytics
```bash
python analysis/07_bigquery_analytics.py
```

### Step 7 — Train ML Model (Vertex AI)
```bash
python analysis/09_xgboost_vertex_ai.py
```

### Step 8 — Generate Visualisations
```bash
python analysis/10_visualisations.py
```

---

## Dataset Sources

| Dataset | URL | Size | License |
|---|---|---|---|
| USDA Food Nutrition (Kaggle) | https://www.kaggle.com/datasets/trolukovich/nutritional-values-for-common-foods-and-products | ~300 MB | CC BY-SA |
| OpenFoodFacts | https://static.openfoodfacts.org/data/en.openfoodfacts.org.products.csv.gz | ~3.1 GB | ODbL |

---

## References
- Google Cloud BigQuery Documentation: https://cloud.google.com/bigquery/docs
- Apache Beam Python SDK: https://beam.apache.org/documentation/sdks/python/
- Vertex AI Documentation: https://cloud.google.com/vertex-ai/docs
