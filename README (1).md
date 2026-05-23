# Big Data Cloud Assignment — Food Nutrition Dataset
## Optimizing Big Data Processing in the Cloud with Microsoft Azure

---

## 📁 Deliverables Overview

| File | Description |
|------|-------------|
| `Big_Data_Cloud_Report.docx` | Full Word report covering all 7 assignment sections |
| `food_nutrition_unclean.csv` | Raw dataset with introduced quality issues (5,150 rows) |
| `food_nutrition_clean.csv` | Reference clean dataset (5,000 rows, pre-issues) |
| `food_nutrition_clean_processed.csv` | Final cleaned dataset output by data_cleaning.py (5,075 rows) |
| `data_cleaning.py` | Python script: loads unclean → cleans → saves processed CSV |
| `analysis.py` | Python script: EDA, analytical queries, K-Means ML clustering |
| `eda_overview.png` | Chart: calorie distribution, macronutrients, scatter, pie |
| `eda_heatmap_gi.png` | Chart: correlation heatmap + glycaemic index bar chart |
| `ml_clustering.png` | Chart: K-Means PCA cluster visualisation |

---

## 🗂️ Dataset Information

- **Topic:** Food Nutrition
- **Source:** Synthesised from USDA FoodData Central, OpenFoodFacts, Kaggle
- **Clean Dataset:** 5,000 records × 20 features
- **Unclean Dataset:** 5,150 records (includes duplicates, nulls, outliers, typos)

### Columns
| Column | Type | Description |
|--------|------|-------------|
| food_id | int | Unique identifier |
| food_name | str | Name of food item |
| category | str | Food category (Fruits, Vegetables, Proteins, etc.) |
| calories_kcal | float | Calories per 100g serving |
| protein_g | float | Protein content in grams |
| fat_g | float | Total fat in grams |
| carbohydrates_g | float | Carbohydrate content in grams |
| fiber_g | float | Dietary fiber in grams |
| sugar_g | float | Sugar content in grams |
| sodium_mg | float | Sodium in milligrams |
| potassium_mg | float | Potassium in milligrams |
| vitamin_c_mg | float | Vitamin C in milligrams |
| iron_mg | float | Iron in milligrams |
| calcium_mg | float | Calcium in milligrams |
| water_content_pct | float | Water content percentage |
| glycemic_index | float | Glycaemic index (1–110 scale) |
| serving_size_g | float | Serving size in grams |
| country_of_origin | str | Country where food was sourced |
| data_source | str | Database source (USDA, Kaggle, etc.) |
| year_recorded | int | Year the nutritional data was recorded |

---

## ⚙️ How to Run the Code

### Prerequisites
```bash
pip install pandas numpy matplotlib scikit-learn
```

### Step 1: Clean the Dataset
```bash
python data_cleaning.py
```
**Input:** `food_nutrition_unclean.csv`  
**Output:** `food_nutrition_clean_processed.csv`  
**What it does:**
- Removes 75 duplicate rows
- Fixes data types (year_recorded, glycemic_index)
- Nullifies invalid values (negative protein, extreme calories/sodium)
- Imputes missing values using category-level median
- Standardises text (category typos, food_name casing)

### Step 2: Run Analysis & Generate Charts
```bash
python analysis.py
```
**Input:** `food_nutrition_clean_processed.csv`  
**Output:** `eda_overview.png`, `eda_heatmap_gi.png`, `ml_clustering.png`  
**What it does:**
- Generates 4-panel EDA visualisation
- Plots correlation heatmap and glycaemic index comparison
- Runs analytical queries (high-protein foods, sodium alerts, etc.)
- Trains K-Means clustering model (k=4) and plots PCA projection

---

## ☁️ Azure Cloud Architecture (Summary)

```
[Data Sources: USDA API / Kaggle / OpenFoodFacts]
           ↓
   [Azure Data Factory — Ingestion Pipelines]
           ↓
   [ADLS Gen2 — Bronze Zone (raw Parquet files)]
           ↓
   [Azure Databricks — Silver Zone (cleaned data)]
           ↓
   [Azure Synapse Analytics — Gold Zone (aggregated tables)]
           ↓
   [Power BI — Dashboards] + [Azure ML — ML Models]
```

---

## 📚 References

- Microsoft Azure Documentation: https://learn.microsoft.com/en-us/azure/
- USDA FoodData Central: https://fdc.nal.usda.gov/
- OpenFoodFacts: https://world.openfoodfacts.org/data
- Zaharia et al. (2016) Apache Spark: ACM 59(11), pp. 56–65

---

*York St John University — Big Data & Cloud Computing Assignment*
