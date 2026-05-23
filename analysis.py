"""
=============================================================
 Food Nutrition Dataset – EDA & Cloud Analytics Simulation
 Assignment: Optimizing Big Data Processing in the Cloud
 Cloud Platform: Microsoft Azure
=============================================================
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import warnings
warnings.filterwarnings("ignore")

# ──────────────────────────────────────────
# LOAD CLEANED DATA
# ──────────────────────────────────────────
df = pd.read_csv("food_nutrition_clean_processed.csv")
print(f"Dataset loaded: {df.shape[0]} rows × {df.shape[1]} cols\n")

COLORS = ["#0078D4","#50E6FF","#FFB900","#E74856","#107C10","#8764B8","#00B7C3","#DF0900","#00CC6A"]

# ──────────────────────────────────────────
# FIGURE 1: Calories Distribution by Category
# ──────────────────────────────────────────
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle("Food Nutrition – Exploratory Data Analysis\n(Microsoft Azure Cloud Analytics Simulation)",
             fontsize=14, fontweight="bold", y=1.01)

# Plot 1: boxplot calories by category
ax1 = axes[0, 0]
cats = df.groupby("category")["calories_kcal"].median().sort_values(ascending=False).index.tolist()
data_box = [df[df["category"] == c]["calories_kcal"].dropna().values for c in cats]
bp = ax1.boxplot(data_box, patch_artist=True, vert=True)
for patch, color in zip(bp["boxes"], COLORS * 3):
    patch.set_facecolor(color)
    patch.set_alpha(0.75)
ax1.set_xticklabels(cats, rotation=35, ha="right", fontsize=8)
ax1.set_title("Calorie Distribution by Food Category", fontweight="bold")
ax1.set_ylabel("Calories (kcal)")
ax1.grid(axis="y", alpha=0.3)

# Plot 2: Average macronutrients bar chart
ax2 = axes[0, 1]
macros = df.groupby("category")[["protein_g","fat_g","carbohydrates_g"]].mean()
x = np.arange(len(macros))
w = 0.25
ax2.bar(x - w, macros["protein_g"], width=w, label="Protein (g)", color=COLORS[0])
ax2.bar(x,     macros["fat_g"],     width=w, label="Fat (g)",     color=COLORS[2])
ax2.bar(x + w, macros["carbohydrates_g"], width=w, label="Carbs (g)", color=COLORS[4])
ax2.set_xticks(x)
ax2.set_xticklabels(macros.index, rotation=35, ha="right", fontsize=8)
ax2.set_title("Avg Macronutrients by Category", fontweight="bold")
ax2.set_ylabel("Grams per 100g serving")
ax2.legend(fontsize=8)
ax2.grid(axis="y", alpha=0.3)

# Plot 3: Sodium vs Calories scatter
ax3 = axes[1, 0]
cat_list = df["category"].unique()
for i, cat in enumerate(cat_list):
    sub = df[df["category"] == cat]
    ax3.scatter(sub["sodium_mg"], sub["calories_kcal"],
                alpha=0.35, s=10, color=COLORS[i % len(COLORS)], label=cat)
ax3.set_xlabel("Sodium (mg)")
ax3.set_ylabel("Calories (kcal)")
ax3.set_title("Sodium vs Calories (by Category)", fontweight="bold")
ax3.legend(fontsize=7, markerscale=2, loc="upper right")
ax3.grid(alpha=0.3)

# Plot 4: Pie – record count by data source
ax4 = axes[1, 1]
src_counts = df["data_source"].value_counts()
ax4.pie(src_counts.values, labels=src_counts.index, autopct="%1.1f%%",
        colors=COLORS[:len(src_counts)], startangle=140,
        textprops={"fontsize": 8})
ax4.set_title("Records by Data Source", fontweight="bold")

plt.tight_layout()
plt.savefig("eda_overview.png", dpi=150, bbox_inches="tight")
plt.close()
print("✅ Saved: eda_overview.png")

# ──────────────────────────────────────────
# FIGURE 2: Nutritional heatmap + glycemic index
# ──────────────────────────────────────────
fig2, axes2 = plt.subplots(1, 2, figsize=(14, 5))

# Heatmap: correlation matrix
ax_h = axes2[0]
num_cols = ["calories_kcal","protein_g","fat_g","carbohydrates_g",
            "fiber_g","sugar_g","sodium_mg","calcium_mg","iron_mg"]
corr = df[num_cols].corr()
im = ax_h.imshow(corr, cmap="Blues", vmin=-1, vmax=1)
ax_h.set_xticks(range(len(num_cols)))
ax_h.set_yticks(range(len(num_cols)))
ax_h.set_xticklabels([c.replace("_"," ").replace(" g","").replace(" mg","") for c in num_cols],
                     rotation=45, ha="right", fontsize=8)
ax_h.set_yticklabels([c.replace("_"," ").replace(" g","").replace(" mg","") for c in num_cols], fontsize=8)
for i in range(len(num_cols)):
    for j in range(len(num_cols)):
        ax_h.text(j, i, f"{corr.iloc[i,j]:.2f}", ha="center", va="center", fontsize=6,
                  color="white" if abs(corr.iloc[i,j]) > 0.6 else "black")
plt.colorbar(im, ax=ax_h, fraction=0.04)
ax_h.set_title("Nutrient Correlation Heatmap", fontweight="bold")

# Bar: avg glycemic index by category
ax_gi = axes2[1]
gi_cat = df.groupby("category")["glycemic_index"].mean().sort_values(ascending=False)
bars = ax_gi.barh(gi_cat.index, gi_cat.values, color=COLORS[:len(gi_cat)])
ax_gi.set_xlabel("Average Glycemic Index")
ax_gi.set_title("Average Glycemic Index by Food Category", fontweight="bold")
for bar, val in zip(bars, gi_cat.values):
    ax_gi.text(val + 0.5, bar.get_y() + bar.get_height()/2,
               f"{val:.1f}", va="center", fontsize=8)
ax_gi.grid(axis="x", alpha=0.3)

plt.tight_layout()
plt.savefig("eda_heatmap_gi.png", dpi=150, bbox_inches="tight")
plt.close()
print("✅ Saved: eda_heatmap_gi.png")

# ──────────────────────────────────────────
# ANALYTICAL QUERIES (mimicking Azure SQL / Synapse)
# ──────────────────────────────────────────
print("\n" + "=" * 60)
print("ANALYTICAL QUERIES (Azure Synapse / SQL Analytics Simulation)")
print("=" * 60)

# Q1: Top 10 high-protein, low-fat foods
print("\n[Q1] Top 10 High-Protein, Low-Fat Foods (protein > 20g, fat < 5g):")
q1 = df[(df["protein_g"] > 20) & (df["fat_g"] < 5)][["food_name","category","protein_g","fat_g","calories_kcal"]] \
       .sort_values("protein_g", ascending=False).head(10)
print(q1.to_string(index=False))

# Q2: Average nutrition by country
print("\n[Q2] Average Calorie & Sodium by Country of Origin:")
q2 = df.groupby("country_of_origin")[["calories_kcal","sodium_mg","protein_g"]].mean().round(1)
print(q2.to_string())

# Q3: Foods with dangerously high sodium
print("\n[Q3] High Sodium Alert – foods with >1500 mg sodium:")
q3 = df[df["sodium_mg"] > 1500][["food_name","category","sodium_mg"]].sort_values("sodium_mg", ascending=False).head(10)
print(q3.to_string(index=False))

# Q4: Year trend – average calories recorded per year
print("\n[Q4] Avg Calories Recorded Per Year:")
q4 = df.groupby("year_recorded")["calories_kcal"].agg(["mean","count"]).round(1)
q4.columns = ["avg_calories", "record_count"]
print(q4.to_string())

# ──────────────────────────────────────────
# SIMPLE ML: K-Means Nutritional Clustering
# ──────────────────────────────────────────
print("\n" + "=" * 60)
print("MACHINE LEARNING: K-Means Nutritional Clustering")
print("=" * 60)
try:
    from sklearn.preprocessing import StandardScaler
    from sklearn.cluster import KMeans
    from sklearn.decomposition import PCA

    features = ["calories_kcal","protein_g","fat_g","carbohydrates_g","fiber_g","sugar_g"]
    X = df[features].dropna()
    idx = X.index

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X_scaled)
    df.loc[idx, "cluster"] = labels

    pca = PCA(n_components=2, random_state=42)
    X_pca = pca.fit_transform(X_scaled)

    fig3, ax3 = plt.subplots(figsize=(9, 6))
    cluster_names = ["Low-Calorie\n(Veggies/Fruits)","High-Protein\n(Meat/Legumes)",
                     "High-Fat\n(Oils/Nuts)","High-Carb\n(Grains/Sugary)"]
    for k in range(4):
        mask = labels == k
        ax3.scatter(X_pca[mask, 0], X_pca[mask, 1],
                    s=15, alpha=0.5, color=COLORS[k], label=f"Cluster {k}: {cluster_names[k]}")
    ax3.set_xlabel(f"PC1 ({pca.explained_variance_ratio_[0]*100:.1f}% variance)")
    ax3.set_ylabel(f"PC2 ({pca.explained_variance_ratio_[1]*100:.1f}% variance)")
    ax3.set_title("K-Means Nutritional Clustering (PCA Projection)\nAzure ML Simulation", fontweight="bold")
    ax3.legend(fontsize=8, loc="upper right")
    ax3.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig("ml_clustering.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("✅ Saved: ml_clustering.png")

    cluster_summary = df.groupby("cluster")[features].mean().round(2)
    print("\nCluster Centroids (avg nutritional values):")
    print(cluster_summary.to_string())

except ImportError:
    print("sklearn not available – ML section skipped.")

print("\n✅ Analysis complete.")
