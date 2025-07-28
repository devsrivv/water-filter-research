# A Unified Adsorption Performance Framework for Selecting Biochar-Nanoparticle Systems in Heavy Metal Water Filtration
# Dev Srivastava and Aashka Doshi

import pandas as pd
import numpy as np
import os

# file paths
script_dir = os.path.dirname(os.path.abspath(__file__))
input_file = os.path.join(script_dir, "MAPI_dataset.csv")
ranked_output_file = os.path.join(script_dir, "Ranked_Water_Filter_MAPI.csv")
metalwise_rank_file = os.path.join(script_dir, "best_filter_per_metal.csv")

# load csv
df = pd.read_csv(input_file)

# sustainability score calculations
df["sustainability_score"] = df["biochar_sustainability_score"] * df["microbe_sustainability_score"]

# reusability score calculations
def calculate_reusability(cycles):
    try:
        cycles = int(cycles)
        if cycles <= 1:
            return 0.4
        else:
            return min(1.0, 0.4 + np.log10(cycles) / 2.5)
    except:
        return 0.5  # Default if "not reported"

df["reusability_score"] = df["Reausability_cycles"].apply(calculate_reusability)

# MAPI Calculation
df["MAPI"] = (df["Removal_%"] * df["sustainability_score"] * df["reusability_score"]) / df["cost_per_L_filtered"]

# overall ranking
df["MAPI_rank"] = df["MAPI"].rank(ascending=False).astype(int)

# metal-specific ranking
df["MAPI_metal_rank"] = df.groupby("Target_Metal")["MAPI"].rank(ascending=False).astype(int)

# save overall ranking
df_sorted = df.sort_values(by="MAPI", ascending=False)
df_sorted.to_csv(ranked_output_file, index=False)

# save filters ranked by metal
df_metal_sorted = df.sort_values(by=["Target_Metal", "MAPI_metal_rank"])
df_metal_sorted.to_csv(metalwise_rank_file, index=False)

# print top rows
print("Top 5 MAPI")
print(df_sorted[["Biochar", "Microbe", "Removal_%", "sustainability_score", "reusability_score", "cost_per_L_filtered", "MAPI", "MAPI_rank"]].head())
print(" ")
print("Best MAPI per metal")
top_per_metal = df_metal_sorted[df_metal_sorted["MAPI_metal_rank"] == 1]
print(top_per_metal[["Target_Metal", "Biochar", "Microbe", "MAPI"]])
