# imports
from openai import OpenAI
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import json
from asyncio import sleep
import base64
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import io
import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout


cols = ['A Feed', 'D Feed', 'E Feed', 'A and C Feed', 'Recycle Flow',
    'Reactor Feed Rate', 'Reactor Pressure', 'Reactor Level',
    'Reactor Temperature', 'Purge Rate', 'Product Sep Temp',
    'Product Sep Level', 'Product Sep Pressure', 'Product Sep Underflow',
    'Stripper Level', 'Stripper Pressure', 'Stripper Underflow',
    'Stripper Temp', 'Stripper Steam Flow', 'Compressor Work',
    'Reactor Coolant Temp', 'Separator Coolant Temp', 'D feed load', 'E feed load', 'A feed load',
    'A and C feed load', 'Compressor recycle valve', 'Purge valve',
    'Separator liquid load', 'Stripper liquid load', 'Stripper steam valve',
    'Reactor coolant load', 'Condenser coolant load']
mapping = {f"x{idx+1}":c for idx, c in enumerate(cols)}

G = nx.read_adjlist("./cg.adjlist", create_using=nx.DiGraph)
# G = nx.reverse(G)
G = nx.relabel_nodes(G, mapping)

def get_subgraph(G, nodes):
    subgraph_nodes = set(nodes)
    for node in nodes:
        subgraph_nodes.update(G.predecessors(node))
        subgraph_nodes.update(G.successors(node))
    return G.subgraph(subgraph_nodes)


load_dotenv()


INTRO_MESSAGE = """The process produces two products from four reactants. Also present are an inert and a byproduct making a total of eight components:
A, B, C, D, E, F, G, and H. The reactions are:

A(g) + C(g) + D(g) - G(liq): Product 1,

A(g) + C(g) + E(g) - H(liq): Product 2,

A(g) + E(g) - F(liq): Byproduct,

3D(g) - 2F(liq): Byproduct.

All the reactions are irreversible and exothermic. The reaction rates are a function of temperature through an Arrhenius expression.
The reaction to produce G has a higher activation energy resulting in more sensitivity to temperature.
Also, the reactions are approximately first-order with respect to the reactant concentrations.

The process has five major unit operations: the reactor, the product condenser, a vapor-liquid separator, a recycle compressor and a product stripper.
Figure showing a diagram of the process is attached.

The gaseous reactants are fed to the reactor where they react to form liquid products. The gas phase reactions are catalyzed by a nonvolatile catalyst dissolved
in the liquid phase. The reactor has an internal cooling bundle for removing the heat of reaction. The products leave the reactor as vapors along with the unreacted feeds.
The catalyst remains in the reactor. The reactor product stream passes through a cooler for condensing the products and from there to a vapor-liquid separator.
Noncondensed components recycle back through a centrifugal compressor to the reactor feed.
Condensed components move to a product stripping column to remove remaining reactants by stripping with feed stream number 4.
Products G and H exit the stripper base and are separated in a downstream refining section which is not included in this problem.
The inert and byproduct are primarily purged from the system as a vapor from the vapor-liquid separator."""

SYSTEM_MESSAGE = 'You are a helpful AI chatbot trained to assist with '\
    'monitoring the Tennessee Eastman process. The Tennessee Eastman '\
    f'Process can be described as follows:\n{INTRO_MESSAGE}'\
    '\n\nYour purpose is to help the user identify and understand potential '\
    'explanations for any faults that occur during the process. You should '\
    'explain your reasoning using the graphs provided.'

EXPLAIN_PROMPT = 'You are provided with the general schematics of the Tennessee'\
    'Eastman process, causal graphs of different features and graphs showing '\
    'the values of the top contributing features for a recent fault. For every '\
    'contributing feature reason about the observation graphs (not all '\
    'contributing features might have sudden change around the fault) and '\
    'create hypotheses for these observations based on the causal graph. '\
    'Finally combine these hypotheses in order to generate an explanation as to'\
    'why this fault occurred and how it is propagating.'

client = OpenAI()

# Initialize FastAPI app
app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:5173",
    "*"
]

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

class ExplainationRequest(BaseModel):
    data: dict[str, list[float]]

class Image(BaseModel):
    image: str
    name: str

class MessageResponse(BaseModel):
    content: str
    images: list[Image] = []
    index: int
    id: str

def ChatModelCompletion(messages: list[dict[str, str]], images: list[str]=None):
    # Send the message to OpenAI's GPT-4
    # print(messages)
    response = client.chat.completions.create(
        model="gpt-4o",
        # messages=[
        #     {"role": "user", "content": toModel}
        # ],
        messages=messages,
        stream=True
    )
    print('sending response')
    index = 0
    for chunk in response:
        # print(chunk)
        # Extract the response text
        if chunk.choices[0].delta.content:
            response_text = chunk.choices[0].delta.content
            if index == 0 and images:
                response_str = json.dumps({'index': index, 'content': response_text, 'id': chunk.id, 'images': images})
            else:
                response_str = json.dumps({'index': index, 'content': response_text, 'id': chunk.id, 'images': []})
            index += 1
            yield "data: " + response_str + "\n\n"
    print(f'Sent {index} chunks')

def plot_causal_subgraph(request: ExplainationRequest):
    nodes_of_interest = request.data.keys()
    subgraph = get_subgraph(G, nodes_of_interest)
    # Visualize the subgraph
    pos = graphviz_layout(subgraph, prog='dot')
    nx.draw(subgraph, pos, with_labels=True, node_color='lightblue',
            node_size=500, font_size=10, arrows=True)
    nx.draw_networkx_nodes(subgraph, pos, nodelist=nodes_of_interest,
                        node_color='red', node_size=600)
    plt.title("Causal graph of important features (higlighted in red)")
    plt.axis('off')
    img_bytes = io.BytesIO()
    plt.savefig(img_bytes, format="png")
    img_bytes.seek(0)
    img_base64 = base64.b64encode(img_bytes.read()).decode()
    # DEBUG
    with open(f"./img/causal_graph.png", "wb") as f:
        f.write(base64.b64decode(bytes(img_base64, "utf-8")))
    plt.close()
    return {"image": img_base64, "name": "Causal graph"}

def plot_graphs_to_base64(request: ExplainationRequest):
    graphs = []
    for feature_name in request.data:
        try:
            # Plot the feature's historical data
            fig, ax = plt.subplots()
            ax.plot(request.data[feature_name], label=feature_name)

            ax.axvline(
                x=len(request.data[feature_name])-20,
                color="r",
                linestyle="--",
                label="Fault Start",
            )

            # Format the x-axis to display dates correctly
            # ax.xaxis.set_major_locator(mdates.AutoDateLocator())
            # ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))

            # Rotate date labels for better readability
            # plt.xticks(rotation=45)

            # Set labels and title
            ax.set_xlabel("Time")
            ax.set_ylabel(feature_name)
            ax.set_title(f"{feature_name} over Time around Fault")

            # Ensure layout is neat
            plt.tight_layout()

            # Convert plot to a format that can be sent over WebSocket
            img_bytes = io.BytesIO()
            plt.savefig(img_bytes, format="png")
            img_bytes.seek(0)
            img_base64 = base64.b64encode(img_bytes.read()).decode()
            # DEBUG
            with open(f"./img/{feature_name}.png", "wb") as f:
                f.write(base64.b64decode(bytes(img_base64, "utf-8")))
            # Send the image to the frontend
            graphs.append({"name": feature_name, "image": img_base64})
            plt.close(fig)
        except Exception as e:
            print(e)
    return graphs

@app.post("/explain", response_model=None)
async def explain(request: ExplainationRequest):
    # print(f'Received fault {request.data}')
    try:
        with open("./tep_flowsheet.png", "rb") as image_file:
            schematic_img_base64 = base64.b64encode(image_file.read()).decode("utf-8")
        graphs = plot_graphs_to_base64(request)
        # with open("./cg.png", "rb") as image_file:
        #     cg_base64 = base64.b64encode(image_file.read()).decode("utf-8")
        causal_graph = plot_causal_subgraph(request)
        # causal_graph = {"image": cg_base64, "name": "Causal graph"}
        schema_image = {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{schematic_img_base64}"
            }
        }
        # image_data.append(
        #     {
        #         "type": "image_url",
        #         "image_url": {"url": f"data:image/png;base64,{cg_base64}"},
        #     }
        # )
        emessages=[
            {
                "role": "system",
                "content": SYSTEM_MESSAGE
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": EXPLAIN_PROMPT},
                    schema_image,
                ] + [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{graph['image']}"},
                    }
                    for graph in graphs
                ] + [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{causal_graph['image']}"}
                    }
                ]
            }
        ]
        return StreamingResponse(ChatModelCompletion(emessages, graphs+[causal_graph]), media_type='text/event-stream')
        # return StreamingResponse(ChatModelCompletion(emessages, graphs), media_type='text/event-stream')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/send_message", response_model=MessageResponse)
async def send_message(request: MessageRequest):
    # print(f'Received a new request {request.data}')
    try:
        # async def ChatModelCompletion(somestr):
        #     for i in range(10):
        #         yield "data: " + str(i) + "\n\n"
        #         await sleep(0.5)
        # STREAM: TRUE
        return StreamingResponse(ChatModelCompletion(request.data), media_type='text/event-stream')
        # # FALSE
        # response = client.chat.completions.create(
        #     model="gpt-4o",
        #     messages=[
        #         {"role": "user", "content": request.message}
        #     ],
        #     stream=False
        # )
        # response_text = response.choices[0].message.content
        # return MessageResponse(response=response_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)
