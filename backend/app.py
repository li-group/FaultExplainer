from flask import Flask, jsonify, request
from flask_socketio import SocketIO
from flask_cors import CORS
import redis
import threading
from csvSimulator import DataFrameSimulator
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.schema import StrOutputParser
from langchain.schema.messages import HumanMessage, SystemMessage

import json
import datetime
import io
import base64
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


# Fault Datacetion model integration
from model import FaultDetectionModel
import pandas as pd

train_data = pd.read_csv("./data/fault0.csv")
fault_detector = FaultDetectionModel(alpha=0.001)
fault_detector.fit(train_data.iloc[:, 1:])

fault_history = []

def top_feature_graphs(top_features, timestamp):
    target_idx = fault_detector.data_buffer[fault_detector.data_buffer['timestamp'] == timestamp].index[0]
    start_index = max(0, target_idx - 50)  # 30 points before the fault
    graphs = []
    for feature in top_features:
        # Plot the feature's historical data
        fig, ax = plt.subplots()
        ax.plot(fault_detector.data_buffer['timestamp'][start_index:target_idx], fault_detector.data_buffer[feature][start_index:target_idx], label=feature)

        ax.axvline(x=timestamp-datetime.timedelta(minutes=fault_detector.post_fault_threshold*3), color='r', linestyle='--', label='Fault Start')


        # Format the x-axis to display dates correctly
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))

        # Rotate date labels for better readability
        plt.xticks(rotation=45)

        # Set labels and title
        ax.set_xlabel('Time')
        ax.set_ylabel(feature)
        ax.set_title(f'{feature} over Time around Fault')

        # Ensure layout is neat
        plt.tight_layout()

        # Convert plot to a format that can be sent over WebSocket
        img_bytes = io.BytesIO()
        plt.savefig(img_bytes, format='png')
        img_bytes.seek(0)
        img_base64 = base64.b64encode(img_bytes.read()).decode()

        # Send the image to the frontend
        graphs.append({'feature': feature, 'image': img_base64})

        # with open(f"debug_{feature}.txt", "w") as file:
        #     file.write(img_base64)

        plt.close(fig)
    return graphs


def handle_fault_detection(processed_data_point):
    data_point = processed_data_point['data']
    fault_id = processed_data_point['fault_id']
    # Identify the top contributing features
    top_features_contrib = fault_detector.t2_contrib(data_point.iloc[0]['timestamp'])
    paired_list = sorted(zip(top_features_contrib, fault_detector.feature_names), reverse=True)[:6]
    top_features = [s for _, s in paired_list]

    graphs = top_feature_graphs(top_features, data_point.iloc[0]['timestamp'])

    with open("./tep_flowsheet.png", "rb") as image_file:
        schematic_img_base64 = base64.b64encode(image_file.read()).decode('utf-8')
    # Add the schematic image
    image_data = [
        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{schematic_img_base64}"}}
    ]
    image_data.extend([
        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{graph['image']}"}}
        for graph in graphs
    ])
    ai_introduction = SystemMessage(
        content=[
            {
                "type": "text",
                "text": "I am a helpful AI chatbot trained to assist with monitoring the Tennessee Eastman process. My purpose is to help you identify and understand potential explanations for any faults that occur during the process."
            }
        ]
    )
    user_prompt = HumanMessage(
        content=[
            {
                "type": "text",
                "text": "You are provided with the general schematics of the Tennessee Eastman reactor and graphs showing the values of the top contributing features for a recent fault. Based on this information, please generate an explanation as to why this fault occurred and how it is propagating."
            }
        ] + image_data # type: ignore
    )
    response = chain.invoke([ai_introduction, user_prompt])
    explanation = response.content if response else "No response received."
    # Convert the fault information into a readable message
    fault_message = f"Fault detected at {data_point.iloc[0]['timestamp']-datetime.timedelta(minutes=fault_detector.post_fault_threshold*3)}\n {explanation}"
    print("Fault explanation sent")
    # Send this message to the frontend via WebSocket
    socketio.emit('chat_reply', {'images': graphs, 'message': fault_message})

    # import pdb; pdb.set_trace()
    target_idx = fault_detector.data_buffer[fault_detector.data_buffer['timestamp'] == data_point.iloc[0]['timestamp']].index[0]
    start_idx = max(0, target_idx-50)
    data_df = fault_detector.data_buffer.loc[start_idx:target_idx, top_features+["timestamp"]]
    df_melted = data_df.melt(id_vars='timestamp', var_name='key', value_name='value')
    result = df_melted.groupby('key').apply(lambda x: x[['timestamp', 'value']].to_dict('records')).to_json()
    fault_info = {
        'start_time': int((data_point.iloc[0]['timestamp']-datetime.timedelta(minutes=fault_detector.post_fault_threshold*3)).timestamp()*1000),
        'explanation': explanation,
        'top_features': result
    }
    fault_history.append(fault_info)

fault_detector.register_fault_callback(handle_fault_detection)


# LLM Integration

import os

k = os.environ["OPENAI_API_KEY"]
chain = ChatOpenAI(model='gpt-4-vision-preview', api_key=k, max_tokens=2048)
prompt = PromptTemplate.from_template(
"""
{text}
"""
)
runnable = prompt | chain | StrOutputParser()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
CORS(app)  # Enable CORS for all routes
socketio = SocketIO(app, cors_allowed_origins="*")

import configparser
config = configparser.ConfigParser()
config.read('config.ini')

redis_host = config['Redis']['host']
redis_port = int(config['Redis']['port'])  # Port should be an integer
redis_db = int(config['Redis']['db'])     # DB should be an integer


redis_client = redis.Redis(host=redis_host, port=redis_port, db=redis)

simulator = DataFrameSimulator()
simulator.start()

def data_listener():
    TIME_DELTA = datetime.timedelta(minutes=3)
    PREV_TIME = datetime.datetime.now() - TIME_DELTA
    while True:
        # Block until data is available
        _, data = redis_client.blpop('simulator_data') # type: ignore
        data_point = json.loads(data.decode('utf-8'))
        df_data_point = pd.DataFrame([data_point]).iloc[:, 1:]
        df_data_point['timestamp'] = (PREV_TIME + TIME_DELTA)
        PREV_TIME = (PREV_TIME + TIME_DELTA)

        socketio.emit('data_update', {'data': df_data_point.iloc[0].to_json()})
        # print(df_data_point.iloc[0].to_json())
        # print(df_data_point.iloc[0]['timestamp'].timestamp() )
        t2_stat, anomaly = fault_detector.process_data_point(df_data_point)
        socketio.emit('t2_update', {'t2_stat': t2_stat, 'anomaly': anomaly.item(), 'timestamp': int(df_data_point.iloc[0]['timestamp'].timestamp()*1000) } )
        # handle through callback
        # if anomaly:
        #     handle_fault_detection(df_data_point)



# Start the data listener in a separate thread
listener_thread = threading.Thread(target=data_listener, daemon=True)
listener_thread.start()

@app.route('/')
def hello_world():
    return "<p>Hello, World!</p>"

@app.route('/set_rate', methods=['POST'])
def set_rate():
    data = request.get_json()
    new_rate = float(data.get('rate', 1))  # Default to 1 if not specified
    print(new_rate)
    simulator.change_rate(new_rate)
    return jsonify({'message': f'Rate updated to {new_rate}'})

@app.route('/change_state', methods=['POST'])
def change_state():
    data = request.get_json()
    new_state = int(data.get('state', 0))  # Default to 0 if not specified
    simulator.induce_fault(new_state)
    return jsonify({'message': f'State updated to {new_state}'})

@app.route('/pause', methods=['POST'])
def pause_sim():
    data = request.get_json()
    simulator.pause()
    print(simulator.paused)
    return jsonify({'message': f'Simulator status updated to Paused'})

@app.route('/resume', methods=['POST'])
def resume_sim():
    data = request.get_json()
    simulator.resume()
    print(simulator.paused)
    return jsonify({'message': f'Simulator status updated to Running'})


@app.route('/get_state', methods=['GET'])
def get_state():
    return jsonify({'state': simulator.fault_id})

@app.route('/get_rate', methods=['GET'])
def get_rate():
    return jsonify({'rate': float(simulator.rate)})

@app.route('/get_pause_status', methods=['GET'])
def get_pause_status():
    return jsonify({'status': simulator.paused})

@app.route('/fault_history')
def get_fault_history():
    return jsonify(fault_history)

# @socketio.on('change_state')
# def handle_change_state(message):
#     print(f"Received state change request: {message}")
#     fault_id = int(message.split()[-1]) if message.split()[-1].isdigit() else 0
#     simulator.induce_fault(fault_id)

@socketio.on('chat_message')
def handle_chat_message(message):
    print(f"Received chat message: {message}")
    # Process the message and generate a reply
    # reply = f"SERVER Reply to: {message}"  # Example reply
    reply = runnable.invoke({"text": message})
    socketio.emit('chat_reply', reply)  # Send reply back to the frontend


if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5001) # type: ignore
