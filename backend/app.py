# imports
from openai import OpenAI
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import json
import base64
import matplotlib
import pandas as pd

matplotlib.use("Agg")


from prompts import EXPLAIN_PROMPT, EXPLAIN_ROOT, SYSTEM_MESSAGE

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load and validate configuration
def load_config(file_path):
    with open(file_path, "r") as config_file:
        config = json.load(config_file)

    # Validate model
    valid_models = ["gpt-4o", "o1-mini", "o1-preview"]
    if config["model"] not in valid_models:
        raise ValueError(f"Invalid model: {config['model']}. Must be one of {valid_models}.")

    # Validate fault_trigger_consecutive_step
    if not isinstance(config["fault_trigger_consecutive_step"], int) or config["fault_trigger_consecutive_step"] < 1:
        raise ValueError(
            f"Invalid fault_trigger_consecutive_step: {config['fault_trigger_consecutive_step']}. "
            f"Must be an integer >= 1."
        )

    # Validate topkfeatures
    if not isinstance(config["topkfeatures"], int) or not (1 <= config["topkfeatures"] <= 20):
        raise ValueError(
            f"Invalid topkfeatures: {config['topkfeatures']}. "
            f"Must be an integer between 1 and 20."
        )

    # Validate prompt
    valid_prompts = ["explain", "explain root"]
    if config["prompt"] not in valid_prompts:
        raise ValueError(f"Invalid prompt: {config['prompt']}. Must be one of {valid_prompts}.")

    return config
try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, "..", "config.json")
    # Load the configuration
    config = load_config(config_path)

    PROMPT_SELECT = EXPLAIN_PROMPT if config["prompt"] == "explain" else EXPLAIN_ROOT
    gpt_model = config["model"]
    fault_trigger_consecutive_step = config["fault_trigger_consecutive_step"]    
    print("Config loaded and validated:", config)
except Exception as e:
    print("Error loading config:", e)


load_dotenv()


client = OpenAI()

# Initialize FastAPI app
app = FastAPI()

origins = ["http://localhost", "http://localhost:5173", "*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Define request and response models
class MessageRequest(BaseModel):
    data: list[dict[str, str]]
    id: str


class ExplainationRequest(BaseModel):
    data: dict[str, list[float]]
    id: str
    file: str


class Image(BaseModel):
    image: str
    name: str


class MessageResponse(BaseModel):
    content: str
    images: list[Image] = []
    index: int
    id: str


def ChatModelCompletion(
    messages: list[dict[str, str]], msg_id: str, images: list[str] = None, seed: int = 0, model: str = "gpt-4o"
):
    # Set temperature based on the model
    temperature = 0 if (model != "o1-preview" and model != "o1-mini") else 1  # o1-preview only supports temperature=1

    # Filter out 'system' role messages if using 'o1-preview' model
    if model == "o1-preview" or model == "o1-mini":
        messages = [msg for msg in messages if msg['role'] != 'system']

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        stream=True,
        temperature=temperature,
        seed=seed,
    )
    index = 0
    for chunk in response:
        if chunk.choices[0].delta.content:
            response_text = chunk.choices[0].delta.content
            response_data = {
                "index": index,
                "content": response_text,
                "id": msg_id,
                "images": images if index == 0 and images else [],
            }
            yield f"data: {json.dumps(response_data)}\n\n"
            index += 1


def get_full_response(messages: list[dict[str, str]], model: str = "gpt-4o", seed: int = 0):
    temperature = 0 if (model != "o1-preview" and model != "o1-mini") else 1     
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        seed=seed,
    )
    full_response = ""
    for choice in response.choices:
        full_response += choice.message.content
    return full_response


import os
import pandas as pd

def generate_feature_comparison(request_data, file_path):
    """
    Compare the value of the last data point (faulty data) of each feature in request
    the std of the whole time series in the original fault file
    with the normal operating conditions and return a string with percentage changes.
    
    Parameters:
    - request

    Returns:
    - str: Explanation of percentage changes in mean and std for each feature.
    """
    # Get the current directory of this script
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Ensure fault file path is relative to this script
    fault_file_path = os.path.join(current_dir, "data", os.path.basename(file_path))

    # Load the fault file
    fault_data = pd.read_csv(fault_file_path)
    # Calculate the standard deviation for each column
    fault_std = fault_data.std()

    # Ensure stats file path is relative to this script
    stats_file_path = os.path.join(current_dir, "stats", "features_mean_std.csv")
    normal_conditions = pd.read_csv(stats_file_path)

    comparison_results = []

    for feature, values in request_data.items():
        # Compute mean and std for the last three data points (faulty data)
        faulty_val = values[-1]

        # Check if the feature exists in the normal_conditions dataset
        match = normal_conditions[normal_conditions['feature'].str.contains(feature, case=False, na=False)]
        if not match.empty:
            # Get normal mean and std from the matched row
            normal_mean = match['mean'].values[0]

            # Calculate percentage changes
            mean_change_percent = ((faulty_val - normal_mean) / normal_mean) * 100

            # Prepare explanation string
            result = (
                f"Feature: {feature}\n"
                f"  - Faulty Data: Value = {faulty_val:.3f},"
                f"  - Normal Conditions: Mean = {normal_mean:.3f},"
                f"  - Percentage Changes: Value Change = {mean_change_percent:.2f}%, "
            )
            comparison_results.append(result)
        else:
            # Handle cases where the feature is not found in normal conditions
            result = f"Feature: {feature} not found in normal conditions dataset.\n"
            comparison_results.append(result)

    # Combine all results into a single string
    return "The top feature changes are\n" + "\n".join(comparison_results)



@app.post("/explain", response_model=None)
async def explain(request: ExplainationRequest):
    try:
        comparison_result = generate_feature_comparison(request.data, request.file)
        EXPLAIN_PROMPT_RESULT = f"{PROMPT_SELECT}\n{comparison_result}"
        
        emessages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": SYSTEM_MESSAGE + EXPLAIN_PROMPT_RESULT},
                ],
            },
        ]
        seed = 12345

        return StreamingResponse(
            ChatModelCompletion(
                messages=emessages,
                msg_id=request.id,
                model = gpt_model
            ),
            media_type="text/event-stream",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/send_message", response_model=MessageResponse)
async def send_message(request: MessageRequest):
    try:
        return StreamingResponse(
            ChatModelCompletion(messages=request.data, msg_id=f"reply-{request.id}"),
            media_type="text/event-stream",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

