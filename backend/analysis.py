import pandas as pd
import os

# Directory containing the fault files
directory = "./backend/data/"
output_directory = "./"

# Fault descriptions
fault_descriptions = [
    "Normal Operating Conditions",
    "IDV(1) A/C Feed Ratio, B Composition Constant (Stream 4) & Step",
    "IDV(2) B Composition, A/C Ratio Constant (Stream 4) & Step",
    "IDV(3) D Feed Temperature (Stream 2) & Step",
    "IDV(4) Reactor Cooling Water Inlet Temperature & Step",
    "IDV(5) Condenser Cooling Water Inlet Temperature & Step",
    "IDV(6) A Feed Loss (Stream 1) & Step",
    "IDV(7) C Header Pressure Loss - Reduced Availability (Stream 4) & Step",
    "IDV(8) A, B, C Feed Composition (Stream 4) & Random Variation",
    "IDV(9) D Feed Temperature (Stream 2) & Random Variation",
    "IDV(10) C Feed Temperature (Stream 4) & Random Variation",
    "IDV(11) Reactor Cooling Water Inlet Temperature & Random Variation",
    "IDV(12) Condenser Cooling Water Inlet Temperature & Random Variation",
    "IDV(13) Reaction Kinetics & Slow Drift",
    "IDV(14) Reactor Cooling Water Valve & Sticking",
    "IDV(15) Condenser Cooling Water Valve & Sticking"
]

# # Read fault0.csv for baseline (Normal Operating Conditions)
# fault0_path = os.path.join(directory, "fault0.csv")
# fault0_data = pd.read_csv(fault0_path).iloc[20:]  # Data after 20th time step
# fault0_mean = fault0_data.mean()
# fault0_std = fault0_data.std()

# # Initialize dictionary to store relative percentage changes
# relative_results = {}

# # Iterate through fault files (1 to 15)
# for i in range(1, 16):
#     file_name = f"fault{i}.csv"
#     file_path = os.path.join(directory, file_name)
    
#     # Check if file exists
#     if not os.path.exists(file_path):
#         print(f"File {file_name} does not exist. Skipping...")
#         continue
    
#     # Read the file
#     data = pd.read_csv(file_path)
    
#     # Filter data after the 20th time step (assuming time step is indexed from 0)
#     filtered_data = data.iloc[20:]
    
#     # Calculate mean and std for this fault
#     fault_mean = filtered_data.mean()
#     fault_std = filtered_data.std()
    
#     # Calculate relative percentage change
#     mean_change = ((fault_mean - fault0_mean) / fault0_mean) * 100
#     std_change = ((fault_std - fault0_std) / fault0_std) * 100
    
#     # Combine mean and std changes
#     combined = pd.DataFrame({'Mean_Change (%)': mean_change, 'Std_Change (%)': std_change}).T
#     combined.index = [f"{fault_descriptions[i]}_Mean_Change (%)", f"{fault_descriptions[i]}_Std_Change (%)"]
    
#     # Add to results dictionary
#     relative_results[fault_descriptions[i]] = combined

# # Combine all results into a single DataFrame
# final_df = pd.concat(relative_results, axis=1)

# # Rearrange columns: feature1_Mean_Change (%), feature1_Std_Change (%), feature2_Mean_Change (%), feature2_Std_Change (%), ...
# final_df = final_df.stack(level=0).T.sort_index(axis=1, level=0)

# # Save the analysis to a CSV file
# output_path = os.path.join(output_directory, "fault_relative_changes.csv")
# final_df.to_csv(output_path)

# print(f"Relative percentage changes saved to {output_path}")
window_size = 20
import pandas as pd
import numpy as np

# Load the CSV files
fault_data_path = './frontend/public/fault1.csv'
features_mean_std_path = './backend/stats/features_mean_std.csv'

# Read the fault data and features mean/std files
fault_data = pd.read_csv(fault_data_path)
features_mean_std = pd.read_csv(features_mean_std_path)

# Ensure `anomaly` column is boolean
fault_data['anomaly'] = fault_data['anomaly'].astype(bool)

# Step 1: Identify the first occurrence of three consecutive anomalies
consecutive_anomalies = fault_data['anomaly'].rolling(window=window_size).sum() == window_size
first_anomaly_index = consecutive_anomalies.idxmax() if consecutive_anomalies.any() else None
print("consecutive_anomalies:", consecutive_anomalies)
print("First Anomaly Index:", first_anomaly_index)
# first_anomaly_index=400
if first_anomaly_index is not None:
    # Extract valid t2 features
    t2_features_from_fault = [col for col in fault_data.columns if col.startswith("t2_")]
    actual_features_in_mean_std = features_mean_std['feature'].tolist()
    extracted_features_from_t2 = [col.split("t2_")[-1] for col in t2_features_from_fault]
    present_features = [feature for feature in extracted_features_from_t2 if feature in actual_features_in_mean_std]
    valid_t2_features = [f"t2_{feature}" for feature in present_features]
    
    # Step 2: Rank valid features by t2_stat values and select the top 6
    ranked_features_t2 = fault_data.loc[first_anomaly_index, valid_t2_features].sort_values(ascending=False)
    top_6_features_t2 = ranked_features_t2.index[:6]
    
    # Define `recent_data` for last window_size time steps
    recent_data = fault_data.iloc[first_anomaly_index-window_size+1:first_anomaly_index+1]
    
    # Step 3: Calculate percentage mean changes for the top 6 features by t2
    mean_changes = {}
    for feature in top_6_features_t2:
        feature_name = feature.split("t2_")[-1]  # Extract actual feature name
        reference_mean = features_mean_std.loc[features_mean_std['feature'] == feature_name, 'mean'].values[0]
        recent_mean = recent_data[feature_name].mean()
        mean_changes[feature_name] = ((recent_mean - reference_mean) / reference_mean) * 100  # Percentage change
    
    # Step 4: Calculate std for last 20 time steps and rank features by the absolute value of percentage std changes
    start_index = max(first_anomaly_index - 19, 0)  # Ensure we don't go out of bounds
    recent_20_data = fault_data.iloc[start_index:first_anomaly_index+1]
    percentage_std_changes = {}
    for feature in present_features:
        reference_std = features_mean_std.loc[features_mean_std['feature'] == feature, 'std'].values[0]
        recent_std = recent_20_data[feature].std()
        percentage_std_changes[feature] = ((recent_std - reference_std) / reference_std) * 100  # Percentage std change
    
    # Rank features by the absolute value of percentage std changes and select the top 6
    top_6_features_std = sorted(percentage_std_changes.keys(), key=lambda x: abs(percentage_std_changes[x]), reverse=True)[:6]
    
    # Step 5: Print the fault name, mean changes, and percentage std changes
    print("Fault Name:", fault_data_path.split('/')[-1].split('.')[0])
    print("Top 6 Features by T2 Statistics and their Percentage Mean Changes:")
    for feature, change in mean_changes.items():
        print(f"Feature: {feature}, Mean Change: {change:.2f}%")
    
    print("\nTop 6 Features by Percentage Std Changes (Ranked by Absolute Value):")
    for feature in top_6_features_std:
        print(f"Feature: {feature}, Percentage Std Change: {percentage_std_changes[feature]:.2f}%")
else:
    print("No three consecutive anomalies found in the dataset.")

