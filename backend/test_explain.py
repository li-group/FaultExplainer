faults = ["Fault 1 A/C Feed Ratio, B Composition Constant (Stream 4) \\& Step",
"Fault 2 B Composition, A/C Ratio Constant (Stream 4) \\& Step",
"Fault 3 D Feed Temperature (Stream 2) \\& Step",
"Fault 4 Reactor Cooling Water Inlet Temperature \\& Step",
"Fault 5 Condenser Cooling Water Inlet Temperature \\& Step",
"Fault 6 A Feed Loss (Stream 1) \\& Step",
"Fault 7 C Header Pressure Loss - Reduced Availability (Stream 4) \\& Step",
"Fault 8 A, B, C Feed Composition (Stream 4) \\& Random Variation",
"Fault 9 D Feed Temperature (Stream 2) \\& Random Variation",
"Fault 10 C Feed Temperature (Stream 4) \\& Random Variation",
"Fault 11 Reactor Cooling Water Inlet Temperature \\& Random Variation",
"Fault 12 Condenser Cooling Water Inlet Temperature \\& Random Variation",
"Fault 13 Reaction Kinetics \\& Slow Drift",
"Fault 14 Reactor Cooling Water Valve \\& Sticking",
"Fault 15 Condenser Cooling Water Valve \\& Sticking"]

import sys
import os

#open a text file to write the results
f = open("results.txt", "w")

# Import EXPLAIN_PROMPT from app.py
from prompts import EXPLAIN_PROMPT, EXPLAIN_ROOT, SYSTEM_MESSAGE
from app import generate_feature_comparison, get_full_response
import pandas as pd

all_prompt_types = ["prompt=root causes included,", "prompt=general reasoning,"]
all_gpt_models = ["gpt-4o", "o1-preview"]

#iterate over all faults
for i in range(3, 16):
    print("starting fault ", i)
    f.write(f"\n\\subsection{{{faults[i-1]}}}\n")
    fault_data_path = f'./frontend/public/fault{i}.csv'
    filename = f'fault{i}.csv'
    # Read the fault data and features mean/std files
    fault_data = pd.read_csv(fault_data_path)

    # Ensure `anomaly` column is boolean
    fault_data['anomaly'] = fault_data['anomaly'].astype(bool)

    # Step 1: Identify the first occurrence of three consecutive anomalies
    window_size = 6
    consecutive_anomalies = fault_data['anomaly'].rolling(window=window_size).sum() == window_size
    first_anomaly_index = consecutive_anomalies.idxmax() if consecutive_anomalies.any() else None

    if first_anomaly_index is not None:
        # Extract all T² features
        t2_features = [col for col in fault_data.columns if col.startswith("t2_") and col != "t2_stat"]
        
        # Extract the actual feature names
        feature_names = [col.split("t2_")[-1] for col in t2_features]
        
        # Step 2: Rank T² features at first_anomaly_index and get top 6
        t2_values_at_index = fault_data.loc[first_anomaly_index, t2_features]
        t2_values_at_index = pd.to_numeric(t2_values_at_index, errors='coerce')
        #sort the values
        top_6_t2_features = t2_values_at_index.sort_values(ascending=False).head(6).index
        top_6_features = [feature.split("t2_")[-1] for feature in top_6_t2_features]
        
        # Step 3: Extract data for the top 6 features up to first_anomaly_index
        data_until_anomaly = fault_data.iloc[:first_anomaly_index+1]
        data_values_dict = {
            feature: data_until_anomaly[feature].tolist() for feature in top_6_features if feature in data_until_anomaly.columns
        }
    else:
        f.write(f"PCA is not able to identify Fault {i}\n")
        continue


    comparison_result = generate_feature_comparison(data_values_dict, filename)

    #iterate over prompts and gpt models
    for prompt_type in all_prompt_types:
        for gpt_model in all_gpt_models:
            PROMPT_SELECT = EXPLAIN_ROOT if prompt_type == "prompt=root causes included," else EXPLAIN_PROMPT
            latex_prompt = f"""\n have your reponse in latex format, i.e., if I paste your response
            to my latex editor, it should compile. Do not add any preamble. I plan to 
            put your response in a subsubsection of a latex editor. you can start your response with 
            \\subsubsection{{Fault {i} {prompt_type} model={gpt_model}}}""" + "Use `\\\\` for new lines. Make sure to write `\\%` for percentages. Use `\\textbf` for bold characters. Use `\\begin{itemize} \\item ... \\end{itemize}` for bullet-point lists. Use `\\begin{enumerate} \\item ... \\end{enumerate}` for numbered lists. make sure the \\begin and the \\end do match. Do not use tables."

            EXPLAIN_PROMPT_RESULT = f"{PROMPT_SELECT}\n{comparison_result}"
            emessages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": SYSTEM_MESSAGE + EXPLAIN_PROMPT_RESULT+latex_prompt},
                    ],
                },
            ]
            seed = 12345

            response = get_full_response(model=gpt_model, messages=emessages, seed=seed)
            #write the response to the file
            f.write(response)

f.close()
        