from google.cloud import bigquery

def run_analytical_queries():
    client = bigquery.Client()
    
    # Query 1: Top 10 Most Nutrient-Dense Foods
    query_1 = """
    SELECT food_name, food_group, nutrient_density_score
    FROM (
        SELECT food_name, food_group, nutrient_density_score,
               RANK() OVER (PARTITION BY food_group ORDER BY nutrient_density_score DESC) as rnk
        FROM `nutrition.batch_nutrition_facts`
    ) WHERE rnk <= 10;
    """
    
    print("Running Query 1: Top 10 Nutrient-Dense Foods...")
    df_1 = client.query(query_1).to_dataframe()
    print(df_1.head(5))
    
    # Query 2: WHO Regulatory Compliance Check
    query_2 = """
    SELECT food_name, food_group, sugars_g, sodium_mg,
           CASE WHEN sugars_g > 50 THEN 'High Sugar' ELSE 'Acceptable' END as sugar_flag
    FROM `nutrition.batch_nutrition_facts`
    WHERE sugars_g > 50 OR sodium_mg > 2300;
    """
    
    print("\\nRunning Query 2: Regulatory Compliance Flags...")
    df_2 = client.query(query_2).to_dataframe()
    print(df_2.head(5))

if __name__ == "__main__":
    run_analytical_queries()