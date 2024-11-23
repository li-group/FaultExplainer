# # imports
# from openai import OpenAI
# from fastapi import FastAPI, HTTPException
# from fastapi.responses import StreamingResponse
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# from dotenv import load_dotenv
# import json
# from asyncio import sleep
# import base64
# import matplotlib

# matplotlib.use("Agg")
# import matplotlib.pyplot as plt
# import io
# import networkx as nx
# from networkx.drawing.nx_agraph import graphviz_layout


# cols = [
#     "A Feed",
#     "D Feed",
#     "E Feed",
#     "A and C Feed",
#     "Recycle Flow",
#     "Reactor Feed Rate",
#     "Reactor Pressure",
#     "Reactor Level",
#     "Reactor Temperature",
#     "Purge Rate",
#     "Product Sep Temp",
#     "Product Sep Level",
#     "Product Sep Pressure",
#     "Product Sep Underflow",
#     "Stripper Level",
#     "Stripper Pressure",
#     "Stripper Underflow",
#     "Stripper Temp",
#     "Stripper Steam Flow",
#     "Compressor Work",
#     "Reactor Coolant Temp",
#     "Separator Coolant Temp",
#     "Component A to Reactor",
#     "Component B to Reactor",
#     "Component C to Reactor",
#     "Component D to Reactor",
#     "Component E to Reactor",
#     "Component F to Reactor",
#     "Component A in Purge",
#     "Component B in Purge",
#     "Component C in Purge",
#     "Component D in Purge",
#     "Component E in Purge",
#     "Component F in Purge",
#     "Component G in Purge",
#     "Component H in Purge",
#     "Component D in Product",
#     "Component E in Product",
#     "Component F in Product",
#     "Component G in Product",
#     "Component H in Product"
# ]

# mapping = {f"x{idx+1}": c for idx, c in enumerate(cols)}

# G = nx.read_adjlist("./cg.adjlist", create_using=nx.DiGraph)
# # G = nx.reverse(G)
# G = nx.relabel_nodes(G, mapping)


# # def get_subgraph(G, nodes):
# #     try:
# #         print("get_subgraph called with nodes:", nodes)
# #         subgraph_nodes = set(nodes)
# #         print("subgraph_nodes", subgraph_nodes)
# #         for node in nodes:
# #             subgraph_nodes.update(G.predecessors(node))
# #             print("subg", subgraph_nodes)
# #             subgraph_nodes.update(G.successors(node))
# #             print("subgraph2")
# #         print("hell yeah")
# #         return G.subgraph(subgraph_nodes)
# #     except Exception as e:
# #         print("An error occurred:", e)


# load_dotenv()


# INTRO_MESSAGE = """The process produces two products from four reactants. Also present are an inert and a byproduct making a total of eight components:
# A, B, C, D, E, F, G, and H. The reactions are:

# A(g) + C(g) + D(g) - G(liq): Product 1,

# A(g) + C(g) + E(g) - H(liq): Product 2,

# A(g) + E(g) - F(liq): Byproduct,

# 3D(g) - 2F(liq): Byproduct.

# All the reactions are irreversible and exothermic. The reaction rates are a function of temperature through an Arrhenius expression.
# The reaction to produce G has a higher activation energy resulting in more sensitivity to temperature.
# Also, the reactions are approximately first-order with respect to the reactant concentrations.

# The process has five major unit operations: the reactor, the product condenser, a vapor-liquid separator, a recycle compressor and a product stripper.
# Figure showing a diagram of the process is attached. Different streams are labeled with numbers 1-12 in the figure.

# The gaseous reactants A (stream 1), D (stream 2), E (stream 3), are the direct feeds to the reactor. Another stream of feeds include flow of A, B, and C are denoted as stream 4, which goes through the stripper and then combine with the recycle stream (stream 8) and streams 1,2, 3, to form the reactor feed (stream 6).
#  The total feed to the reactor is called stream 6 which includes feeds A, B, C, D, E, F.
# The components of stream 6 not only has the reactants A, C, D, E, but also as well as the inert b and the byproduct F. The compositions of stream 6 are monitored by the sensors.
# The gas phase reactions are catalyzed by a nonvolatile catalyst dissolved in the liquid phase. The reactor has an internal cooling bundle for removing the heat of reaction. The reactor level, temperature, pressure, and the outlet temperature coolant flow are monitored by the sensors.

# The products leave the reactor as vapors along with the unreacted feeds.
# The catalyst remains in the reactor. The reactor product stream passes through a condenser for condensing the products and from there to a vapor-liquid separator.
# The separator level, pressure, and temperature are monitored by the sensors. 
# Noncondensed components from the separator recycle back through a centrifugal compressor to the reactor feed. The compressor work is being monitored. The inert and byproduct are primarily purged from the system as a vapor from the vapor-liquid separator.  The purge rate (stream 9) and its compositions are monitored by the sensors. Stream 9's compositions are monitored by the sensors which include components, A, B, C, D, E,F, G, H.
# Condensed components move to a product stripping column to remove remaining reactants by stripping with feed stream number 4.
# The stripper underflow (stream 11) is monitored by the sensors. Stream 11's compositions are monitored by the sensors which include components, D, E,F, G, H.
# Products G and H exit the stripper base and are separated in a downstream refining section which is not included in this problem.
# """

# SYSTEM_MESSAGE = (
#     "You are a helpful AI chatbot trained to assist with "
#     "monitoring the Tennessee Eastman process. The Tennessee Eastman "
#     f"Process can be described as follows:\n{INTRO_MESSAGE}"
#     "\n\nYour purpose is to help the user identify and understand potential "
#     "explanations for any faults that occur during the process. You should "
#     "explain your reasoning using the graphs provided."
# )
# print ("System message: ", SYSTEM_MESSAGE)

# EXPLAIN_PROMPT = (
#     "You are provided with the general schematics and descriptions of the Tennessee"
#     "Eastman process, and graphs showing "
#     "the values of the top contributing features for a recent fault. For every "
#     "contributing feature reason about the observation graphs (not all "
#     "contributing features might have sudden change around the fault) and "
#     "create hypotheses for these observations based on features and the process description in the system message. "
#     "Finally combine these hypotheses in order to generate an explanation as to"
#     "why this fault occurred and how it is propagating."
#     "Finally, provide the top three likely root cause of the fault."
# )

# ROOT_CAUSE = """
# 1. IDV(1) A/C Feed Ratio, B Composition Constant (Stream 4) & Step \\
# 2. IDV(2) B Composition, A/C Ratio Constant (Stream 4) & Step \\
# 3. IDV (3) D Feed Temperature (Stream 2) & Step \\
# 4. IDV (4) Reactor Cooling Water Inlet Temperature & Step \\
# 5. IDV(5) Condenser Cooling Water Inlet Temperature & Step \\
# 6. IDV(6) A Feed Loss (Stream 1) & Step \\
# 7. IDV (7) C Header Pressure Loss - Reduced Availability (Stream 4) & Step \\
# 8. IDV (8) A, B, C Feed Composition (Stream 4) & Random Variation \\
# 9. IDV(9) D Feed Temperature (Stream 2) & Random Variation \\
# 10. IDV (10) C Feed Temperature (Stream 4) & Random Variation \\
# 11. IDV(11) Reactor Cooling Water Inlet Temperature & Random Variation \\
# 12. IDV (12) Condenser Cooling Water Inlet Temperature & Random Variation \\
# 13. IDV (13) Reaction Kinetics & Slow Drift \\
# 14. IDV (14) Reactor Cooling Water Valve & Sticking \\
# 15. IDV (15) Condenser Cooling Water Valve & Sticking \\
# 16. IDV(16) The valve for Stream 4 was fixed at the steady state position & Constant Position \\"""

# # EXPLAIN_PROMPT_ROOT = (
# #     "You are provided with the general schematics and descriptions of the Tennessee"
# #     "Eastman process, and graphs showing "
# #     "the values of the top contributing features for a recent fault. For every "
# #     "contributing feature reason about the observation graphs (not all "
# #     "Please pick the top three possible root cause of the fault in descending order using your reasoning and "
# #     "understanding of the background knowledge I provided you in the context from the following list of 16 faults. Do not go outside these 16 causes. \n{ROOT_CAUSE}"
# # )

# EXPLAIN_ROOT = (
#     "You are provided with the general schematics and descriptions of the Tennessee "
#     "Eastman process, and graphs showing "
#     "the values of the top contributing features for a recent fault. For every "
#     "contributing feature reason about the observation graphs. "
#     "Please pick the top six possible root cause from the IDV i will be providing of the fault using your reasoning and "
#     "understanding of the background knowledge I provided you in the context from the following list of 16 faults. "
#     "Do not go outside these 16 causes. also explain in each of the three reasons why they are the likely ones based on the physics"
#     "of the process. Please see the graphs properly and then make a decision. Also, please give a deterministic explanation everytime I run you. "
#     "For example, you can explain how a given root cause of a fault is propagated through the process and how"
#     "it causes the top six features I gave to you to change. If the reasoning is consistent with the trend of the six "
#     "features, then the root cause is likely. Now here are all the 16 possible root causes:\n{root_cause}"
# )

# # Now, format the string with the root_cause variable
# EXPLAIN_PROMPT_ROOT = EXPLAIN_ROOT.format(root_cause=ROOT_CAUSE)
# print(EXPLAIN_PROMPT_ROOT)

# client = OpenAI()

# # Initialize FastAPI app
# app = FastAPI()

# origins = ["http://localhost", "http://localhost:5173", "*"]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


# # Define request and response models
# class MessageRequest(BaseModel):
#     data: list[dict[str, str]]
#     id: str


# class ExplainationRequest(BaseModel):
#     data: dict[str, list[float]]
#     id: str


# class Image(BaseModel):
#     image: str
#     name: str


# class MessageResponse(BaseModel):
#     content: str
#     images: list[Image] = []
#     index: int
#     id: str


# def ChatModelCompletion(
#     messages: list[dict[str, str]], msg_id: str, images: list[str] = None, seed: int = 0
# ):
#     # Send the message to OpenAI's GPT-4
#     # print(messages)
#     response = client.chat.completions.create(
#         model="gpt-4o",
#         messages=messages,
#         stream=True,
#         temperature=0,
#         seed=seed,
#     )
#     index = 0
#     for chunk in response:
#         # print(chunk)
#         # Extract the response text
#         if chunk.choices[0].delta.content:
#             response_text = chunk.choices[0].delta.content
#             if index == 0 and images:
#                 response_str = json.dumps(
#                     {
#                         "index": index,
#                         "content": response_text,
#                         "id": msg_id,
#                         "images": images,
#                     }
#                 )
#             else:
#                 response_str = json.dumps(
#                     {
#                         "index": index,
#                         "content": response_text,
#                         "id": msg_id,
#                         "images": [],
#                     }
#                 )
#             index += 1
#             yield "data: " + response_str + "\n\n"
#     print(f"Sent {index} chunks")


# # def plot_causal_subgraph(request: ExplainationRequest):
# #     print("plotting causal subgraph")
# #     nodes_of_interest = request.data.keys()
# #     print(nodes_of_interest)
# #     subgraph = get_subgraph(G, nodes_of_interest)
# #     # Visualize the subgraph
# #     print("subgraph", subgraph)
# #     pos = graphviz_layout(subgraph, prog="dot")
# #     nx.draw(
# #         subgraph,
# #         pos,
# #         with_labels=True,
# #         node_color="lightblue",
# #         node_size=500,
# #         font_size=10,
# #         arrows=True,
# #     )
# #     nx.draw_networkx_nodes(
# #         subgraph, pos, nodelist=nodes_of_interest, node_color="red", node_size=600
# #     )
# #     plt.title("Causal graph of important features (higlighted in red)")
# #     plt.axis("off")
# #     img_bytes = io.BytesIO()
# #     plt.savefig(img_bytes, format="png")
# #     img_bytes.seek(0)
# #     img_base64 = base64.b64encode(img_bytes.read()).decode()
# #     # # DEBUG
# #     # with open(f"./img/causal_graph.png", "wb") as f:
# #     #     f.write(base64.b64decode(bytes(img_base64, "utf-8")))
# #     plt.close()
# #     return {"image": img_base64, "name": "Causal graph"}


# def plot_graphs_to_base64(request: ExplainationRequest):
#     graphs = []
#     print("plotting graphs", request.data)
#     for feature_name in request.data:
#         print("plotting", feature_name)
#         try:
#             # Plot the feature's historical data
#             fig, ax = plt.subplots()
#             ax.step(
#                 range(len(request.data[feature_name])),
#                 request.data[feature_name],
#                 label=feature_name,
#                 where="mid",
#             )
#             # ax.plot(request.data[feature_name], label=feature_name)

#             ax.axvline(
#                 x=len(request.data[feature_name]) - 20,
#                 color="r",
#                 linestyle="--",
#                 label="Fault Start",
#             )

#             ax.set_xlabel("Time")
#             ax.set_ylabel(feature_name)
#             ax.set_title(f"{feature_name} over Time around Fault")

#             # Ensure layout is neat
#             plt.tight_layout()

#             # Convert plot to a format that can be sent over WebSocket
#             img_bytes = io.BytesIO()
#             plt.savefig(img_bytes, format="png")
#             img_bytes.seek(0)
#             img_base64 = base64.b64encode(img_bytes.read()).decode()
#             # # DEBUG
#             # with open(f"./img/{feature_name}.png", "wb") as f:
#             #     f.write(base64.b64decode(bytes(img_base64, "utf-8")))
#             # Send the image to the frontend
#             graphs.append({"name": feature_name, "image": img_base64})
#             plt.close(fig)
#         except Exception as e:
#             print(e)
#     return graphs


# @app.post("/explain", response_model=None)
# async def explain(request: ExplainationRequest):
#     try:
#         with open("./tep_flowsheet.png", "rb") as image_file:
#             print("Read tep_flowsheet.png")
#             schematic_img_base64 = base64.b64encode(image_file.read()).decode("utf-8")
#         graphs = plot_graphs_to_base64(request)
#         #causal_graph = plot_causal_subgraph(request)
#         print("Sending explaination")
#         schema_image = {
#             "type": "image_url",
#             "image_url": {"url": f"data:image/png;base64,{schematic_img_base64}"},
#         }
#         emessages = [
#             {"role": "system", "content": SYSTEM_MESSAGE},
#             {
#                 "role": "user",
#                 "content": [
#                     {"type": "text", "text": EXPLAIN_PROMPT_ROOT},
#                     schema_image,
#                 ]
#                 + [
#                     {
#                         "type": "image_url",
#                         "image_url": {"url": f"data:image/png;base64,{graph['image']}"},
#                     }
#                     for graph in graphs
#                 ]
#                 # + [
#                 #     {
#                 #         "type": "image_url",
#                 #         "image_url": {
#                 #             "url": f"data:image/png;base64,{causal_graph['image']}"
#                 #         },
#                 #     }
#                 # ],
#             },
#         ]        
#         seed = 12345
#         return StreamingResponse(
#             ChatModelCompletion(
#                 messages=emessages,
#                 msg_id=request.id,
#                 images=graphs,
#                 seed=seed
                
#             ),
#             media_type="text/event-stream",
#         )
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# @app.post("/send_message", response_model=MessageResponse)
# async def send_message(request: MessageRequest):
#     try:
#         return StreamingResponse(
#             ChatModelCompletion(messages=request.data, msg_id=f"reply-{request.id}"),
#             media_type="text/event-stream",
#         )
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


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


cols = [
    "A Feed",
    "D Feed",
    "E Feed",
    "A and C Feed",
    "Recycle Flow",
    "Reactor Feed Rate",
    "Reactor Pressure",
    "Reactor Level",
    "Reactor Temperature",
    "Purge Rate",
    "Product Sep Temp",
    "Product Sep Level",
    "Product Sep Pressure",
    "Product Sep Underflow",
    "Stripper Level",
    "Stripper Pressure",
    "Stripper Underflow",
    "Stripper Temp",
    "Stripper Steam Flow",
    "Compressor Work",
    "Reactor Coolant Temp",
    "Separator Coolant Temp",
    "Component A to Reactor",
    "Component B to Reactor",
    "Component C to Reactor",
    "Component D to Reactor",
    "Component E to Reactor",
    "Component F to Reactor",
    "Component A in Purge",
    "Component B in Purge",
    "Component C in Purge",
    "Component D in Purge",
    "Component E in Purge",
    "Component F in Purge",
    "Component G in Purge",
    "Component H in Purge",
    "Component D in Product",
    "Component E in Product",
    "Component F in Product",
    "Component G in Product",
    "Component H in Product"
]

mapping = {f"x{idx+1}": c for idx, c in enumerate(cols)}

G = nx.read_adjlist("./cg.adjlist", create_using=nx.DiGraph)
# G = nx.reverse(G)
G = nx.relabel_nodes(G, mapping)


# def get_subgraph(G, nodes):
#     try:
#         print("get_subgraph called with nodes:", nodes)
#         subgraph_nodes = set(nodes)
#         print("subgraph_nodes", subgraph_nodes)
#         for node in nodes:
#             subgraph_nodes.update(G.predecessors(node))
#             print("subg", subgraph_nodes)
#             subgraph_nodes.update(G.successors(node))
#             print("subgraph2")
#         print("hell yeah")
#         return G.subgraph(subgraph_nodes)
#     except Exception as e:
#         print("An error occurred:", e)


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
Figure showing a diagram of the process is attached. Different streams are labeled with numbers 1-12 in the figure.

The gaseous reactants A (stream 1), D (stream 2), E (stream 3), are the direct feeds to the reactor. Another stream of feeds include flow of A, B, and C are denoted as stream 4, which goes through the stripper and then combine with the recycle stream (stream 8) and streams 1,2, 3, to form the reactor feed (stream 6).
 The total feed to the reactor is called stream 6 which includes feeds A, B, C, D, E, F.
The components of stream 6 not only has the reactants A, C, D, E, but also as well as the inert b and the byproduct F. The compositions of stream 6 are monitored by the sensors.
The gas phase reactions are catalyzed by a nonvolatile catalyst dissolved in the liquid phase. The reactor has an internal cooling bundle for removing the heat of reaction. The reactor level, temperature, pressure, and the outlet temperature coolant flow are monitored by the sensors.

The products leave the reactor as vapors along with the unreacted feeds.
The catalyst remains in the reactor. The reactor product stream passes through a condenser for condensing the products and from there to a vapor-liquid separator.
The separator level, pressure, and temperature are monitored by the sensors. 
Noncondensed components from the separator recycle back through a centrifugal compressor to the reactor feed. The compressor work is being monitored. The inert and byproduct are primarily purged from the system as a vapor from the vapor-liquid separator.  The purge rate (stream 9) and its compositions are monitored by the sensors. Stream 9's compositions are monitored by the sensors which include components, A, B, C, D, E,F, G, H.
Condensed components move to a product stripping column to remove remaining reactants by stripping with feed stream number 4.
The stripper underflow (stream 11) is monitored by the sensors. Stream 11's compositions are monitored by the sensors which include components, D, E,F, G, H.
Products G and H exit the stripper base and are separated in a downstream refining section which is not included in this problem.
"""

SYSTEM_MESSAGE = (
    "You are a helpful AI chatbot trained to assist with "
    "monitoring the Tennessee Eastman process. The Tennessee Eastman "
    f"Process can be described as follows:\n{INTRO_MESSAGE}"
    "\n\nYour purpose is to help the user identify and understand potential "
    "explanations for any faults that occur during the process. You should "
    "explain your reasoning using the graphs provided."
)
print ("System message: ", SYSTEM_MESSAGE)

EXPLAIN_PROMPT = (
    "You are provided with the general schematics and descriptions of the Tennessee"
    "Eastman process, and graphs showing "
    "the values of the top contributing features for a recent fault. For every "
    "contributing feature reason about the observation graphs (not all "
    "contributing features might have sudden change around the fault) and "
    "create hypotheses for these observations based on features and the process description in the system message. "
    "Finally combine these hypotheses in order to generate an explanation as to"
    "why this fault occurred and how it is propagating."
    "Finally, provide the top three likely root cause of the fault."
)

ROOT_CAUSE = """
1. IDV(1) A/C Feed Ratio, B Composition Constant (Stream 4) & Step \\
2. IDV(2) B Composition, A/C Ratio Constant (Stream 4) & Step \\
3. IDV (3) D Feed Temperature (Stream 2) & Step \\
4. IDV (4) Reactor Cooling Water Inlet Temperature & Step \\
5. IDV(5) Condenser Cooling Water Inlet Temperature & Step \\
6. IDV(6) A Feed Loss (Stream 1) & Step \\
7. IDV (7) C Header Pressure Loss - Reduced Availability (Stream 4) & Step \\
8. IDV (8) A, B, C Feed Composition (Stream 4) & Random Variation \\
9. IDV(9) D Feed Temperature (Stream 2) & Random Variation \\
10. IDV (10) C Feed Temperature (Stream 4) & Random Variation \\
11. IDV(11) Reactor Cooling Water Inlet Temperature & Random Variation \\
12. IDV (12) Condenser Cooling Water Inlet Temperature & Random Variation \\
13. IDV (13) Reaction Kinetics & Slow Drift \\
14. IDV (14) Reactor Cooling Water Valve & Sticking \\
15. IDV (15) Condenser Cooling Water Valve & Sticking \\
16. IDV(16) The valve for Stream 4 was fixed at the steady state position & Constant Position \\"""

# EXPLAIN_PROMPT_ROOT = (
#     "You are provided with the general schematics and descriptions of the Tennessee"
#     "Eastman process, and graphs showing "
#     "the values of the top contributing features for a recent fault. For every "
#     "contributing feature reason about the observation graphs (not all "
#     "Please pick the top three possible root cause of the fault in descending order using your reasoning and "
#     "understanding of the background knowledge I provided you in the context from the following list of 16 faults. Do not go outside these 16 causes. \n{ROOT_CAUSE}"
# )

# EXPLAIN_ROOT = (
#     "You are provided with the general schematics and descriptions of the Tennessee "
#     "Eastman process, and graphs showing "
#     "the values of the top contributing features for a recent fault. For every "
#     "contributing feature reason about the observation graphs. "
#     "Please pick the top six possible root cause from the IDV i will be providing of the fault using your reasoning and "
#     "understanding of the background knowledge I provided you in the context from the following list of 16 faults. "
#     "Do not go outside these 16 causes. also explain in each of the three reasons why they are the likely ones based on the physics"
#     "of the process. Please see the graphs properly and then make a decision. Also, please give a deterministic explanation everytime I run you. "
#     "For example, you can explain how a given root cause of a fault is propagated through the process and how"
#     "it causes the top six features I gave to you to change. If the reasoning is consistent with the trend of the six "
#     "features, then the root cause is likely. Now here are all the 16 possible root causes:\n{root_cause}"
# )

#this is the input to GPT-4o to get the trend
DESCRIPTION_PROMPT = (
    "You are provided with the general schematics and descriptions of the Tennessee."
     "The 12 graphs showingthe values of the top contributing features for a recent fault. For every "
    "contributing feature, generate a very detailed decription of the trend obersved in the graph when the fault occurs."
)

O1_REASONING_PROMPT = ("These are descriptions of the top 12 features contributing to a fault that just occured in the Tennessee Eastman Process. "
   "Can you guess the root cause of this fault? Please pick the top 3 root causes from the following list of 16 faults. \n{root_cause}" 
)

O1_REASONING_PROMPT = O1_REASONING_PROMPT.format(root_cause=ROOT_CAUSE)

# # Now, format the string with the root_cause variable
# EXPLAIN_PROMPT_ROOT = EXPLAIN_ROOT.format(root_cause=ROOT_CAUSE)
# print(EXPLAIN_PROMPT_ROOT)

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
    temperature = 0 if model != "o1-preview" else 1  # o1-preview only supports temperature=1

    # Filter out 'system' role messages if using 'o1-preview' model
    if model == "o1-preview":
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
    print(f"Sent {index} chunks")


def get_full_response(messages: list[dict[str, str]], model: str = "gpt-4o", seed: int = 0):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0,
        seed=seed,
    )
    full_response = ""
    for choice in response.choices:
        full_response += choice.message.content
    return full_response


# def plot_causal_subgraph(request: ExplainationRequest):
#     print("plotting causal subgraph")
#     nodes_of_interest = request.data.keys()
#     print(nodes_of_interest)
#     subgraph = get_subgraph(G, nodes_of_interest)
#     # Visualize the subgraph
#     print("subgraph", subgraph)
#     pos = graphviz_layout(subgraph, prog="dot")
#     nx.draw(
#         subgraph,
#         pos,
#         with_labels=True,
#         node_color="lightblue",
#         node_size=500,
#         font_size=10,
#         arrows=True,
#     )
#     nx.draw_networkx_nodes(
#         subgraph, pos, nodelist=nodes_of_interest, node_color="red", node_size=600
#     )
#     plt.title("Causal graph of important features (higlighted in red)")
#     plt.axis("off")
#     img_bytes = io.BytesIO()
#     plt.savefig(img_bytes, format="png")
#     img_bytes.seek(0)
#     img_base64 = base64.b64encode(img_bytes.read()).decode()
#     # # DEBUG
#     # with open(f"./img/causal_graph.png", "wb") as f:
#     #     f.write(base64.b64decode(bytes(img_base64, "utf-8")))
#     plt.close()
#     return {"image": img_base64, "name": "Causal graph"}


def plot_graphs_to_base64(request: ExplainationRequest):
    graphs = []
    print("plotting graphs", request.data)
    for feature_name in request.data:
        print("plotting", feature_name)
        try:
            # Plot the feature's historical data
            fig, ax = plt.subplots()
            ax.step(
                range(len(request.data[feature_name])),
                request.data[feature_name],
                label=feature_name,
                where="mid",
            )
            # ax.plot(request.data[feature_name], label=feature_name)

            ax.axvline(
                x=len(request.data[feature_name]) - 20,
                color="r",
                linestyle="--",
                label="Fault Start",
            )

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
            # # DEBUG
            # with open(f"./img/{feature_name}.png", "wb") as f:
            #     f.write(base64.b64decode(bytes(img_base64, "utf-8")))
            # Send the image to the frontend
            graphs.append({"name": feature_name, "image": img_base64})
            plt.close(fig)
        except Exception as e:
            print(e)
    return graphs


@app.post("/explain", response_model=None)
async def explain(request: ExplainationRequest):
    try:
        with open("./tep_flowsheet.png", "rb") as image_file:
            schematic_img_base64 = base64.b64encode(image_file.read()).decode("utf-8")
        graphs = plot_graphs_to_base64(request)
        schema_image = {
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{schematic_img_base64}"},
        }
        emessages = [
            {"role": "system", "content": SYSTEM_MESSAGE},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": DESCRIPTION_PROMPT},
                    schema_image,
                ]
                + [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{graph['image']}"},
                    }
                    for graph in graphs
                ],
            },
        ]
        seed = 12345

        # Get the initial explanation from gpt-4o
        initial_explanation = get_full_response(emessages, model="gpt-4o", seed=seed)

        # Prepare messages for o1
        initial_explanation = initial_explanation + "\n" + O1_REASONING_PROMPT
        print ("""Initial explanation: """, initial_explanation)
        print ("""O1 reasoning prompt: """, O1_REASONING_PROMPT)

        # Prepare messages for o1-preview
        o1_messages = [
            {"role": "system", "content": SYSTEM_MESSAGE},
            {"role": "user", "content": initial_explanation},
        ]

        # Stream the refined explanation from o1-preview
        return StreamingResponse(
            ChatModelCompletion(
                messages=o1_messages,
                msg_id=request.id,
                images=graphs,
                seed=seed,
                model="o1-preview",
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


