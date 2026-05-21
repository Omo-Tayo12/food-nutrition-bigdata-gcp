-- Create K-Means Clustering Model for Food Profiles
CREATE OR REPLACE MODEL `nutrition.food_profile_clusters`
OPTIONS (
    model_type = 'kmeans',
    num_clusters = 6,
    distance_type = 'cosine',
    standardize_features = TRUE
) AS 
SELECT 
    calories_per_100g,
    protein_g,
    fat_g,
    carbohydrates_g,
    fibre_g,
    sugars_g,
    sodium_mg
FROM `nutrition.batch_nutrition_facts`
WHERE food_group IS NOT NULL;