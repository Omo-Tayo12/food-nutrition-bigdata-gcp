from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when

def main():
    spark = SparkSession.builder.appName("FoodNutrition-SparkClean").getOrCreate()
    
    # Read the big file from your Google Storage Bucket
    raw_path = "gs://food-nutrition-raw/openfoodfacts/openfoodfacts_products.csv.gz"
    df = spark.read.option("header", "true").option("inferSchema", "true").csv(raw_path)
    
    # Clean step: Drop rows where half or more of the columns are empty
    threshold = int(len(df.columns) * 0.5)
    df = df.dropna(thresh=threshold)
    
    # Feature Engineering: Calculate Nutrient Density Score (NDS)
    if "sugars_g" in df.columns and "sodium_mg" in df.columns:
        df = df.withColumn(
            "nutrient_density_score",
            (col("protein_g") + col("fibre_g")) / 
            (col("saturated_fat_g") + col("sugars_g") + (col("sodium_mg") / 1000.0) + 0.0001)
        )
        
    # Save the beautiful clean data as a fast Parquet folder
    output_path = "gs://food-nutrition-processed/clean_nutrition_parquet"
    df.write.mode("overwrite").partitionBy("food_group").parquet(output_path)
    
    spark.stop()

if __name__ == "__main__":
    main()