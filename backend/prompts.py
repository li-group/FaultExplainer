INTRO_MESSAGE = """
The process produces two products from four reactants. Also present are an inert and a byproduct, 
making a total of eight components: A, B, C, D, E, F, G, and H. The reactions are:

1. A(g) + C(g) + D(g) → G(liq): Product 1,
2. A(g) + C(g) + E(g) → H(liq): Product 2,
3. A(g) + E(g) → F(liq): Byproduct,
4. 3D(g) → 2F(liq): Byproduct.

All the reactions are irreversible and exothermic. The reaction rates are a function of temperature 
through an Arrhenius expression. The reaction to produce G has a higher activation energy, 
resulting in greater sensitivity to temperature. Also, the reactions are approximately 
first-order with respect to the reactant concentrations.

The process has five major unit operations: 
1. The reactor, 
2. The product condenser, 
3. A vapor-liquid separator, 
4. A recycle compressor, and 
5. A product stripper. 

A diagram of the process is attached, with different streams labeled as numbers 1-12.

The gaseous reactants A (stream 1), D (stream 2), and E (stream 3) are the direct feeds to the reactor. 
Another stream, stream 4, includes a mixture of A, B, and C, which passes through the stripper 
and then combines with the recycle stream (stream 8) and streams 1, 2, and 3 to form the reactor feed (stream 6). 

The total feed to the reactor, called stream 6, includes A, B, C, D, E, and F. Stream 6 not only contains the 
reactants (A, C, D, and E) but also includes the inert B and the byproduct F. 
The composition of stream 6 is monitored by sensors.

The gas-phase reactions are catalyzed by a nonvolatile catalyst dissolved in the liquid phase. 
The reactor has an internal cooling bundle for removing the heat of reaction. The reactor level, 
temperature, pressure, and coolant flow rate are monitored by sensors.

The products leave the reactor as vapors along with unreacted feeds. The catalyst remains in the reactor. 
The reactor product stream passes through a condenser to condense the products and then moves 
to a vapor-liquid separator. The separator's level, pressure, and temperature are monitored by sensors.

Non-condensed components from the separator recycle back through a centrifugal compressor to the reactor feed. 
The compressor work is monitored. The inert and byproduct are primarily purged as vapor from the vapor-liquid separator. 
The purge rate (stream 9) and its composition, which includes A, B, C, D, E, F, G, and H, are monitored by sensors.

Condensed components move to a product stripping column to remove remaining reactants by stripping with stream 4. 
The stripper underflow (stream 11) is monitored by sensors, and its composition includes D, E, F, G, and H.

Products G and H exit the stripper base and are separated in a downstream refining section, 
which is not included in this problem.

The measured variables in the TEP are listed below. Note that the measured variables are those
measured by the sensors but cannot be changed by the controller.
A Feed (Stream 1) kscmh
D Feed (Stream 2) kg/hr
E Feed (Stream 3) kg/hr
A and C Feed (Stream 4) kscmh
Recycle Flow (Stream 8) kscmh
Reactor Feed Rate (Stream 6)  kscmh
Reactor Pressure  kPa gauge
Reactor Level %
Reactor Temperature Deg C
Purge Rate (Stream 9) kscmh
Product Sep Temp  Deg C
Product Sep Level %
Product Sep Pressure  kPa gauge
Product Sep Underflow (Stream 10) m3/hr
Stripper Level  %
Stripper Pressure kPa gauge
Stripper Underflow (Stream 11)  m3/hr
Stripper Temp Deg C
Stripper Steam Flow kg/hr
Compressor Work kW
Reactor Coolant Temp  Deg C
Separator Coolant Temp  Deg C
Component A to Reactor (Stream 6) mole %
Component B to Reactor (Stream 6) mole %
Component C to Reactor (Stream 6) mole %
Component D to Reactor (Stream 6) mole %
Component E to Reactor (Stream 6) mole %
Component F to Reactor (Stream 6) mole %
Component A in Purge (Stream 9) mole %
Component B in Purge (Stream 9) mole %
Component C in Purge (Stream 9) mole %
Component D in Purge (Stream 9) mole %
Component E in Purge (Stream 9) mole %
Component F in Purge (Stream 9) mole %
Component G in Purge (Stream 9) mole %
Component H in Purge (Stream 9) mole %
Component D in Product (Stream 11)  mole %
Component E in Product (Stream 11)  mole %
Component F in Product (Stream 11)  mole %
Component G in Product (Stream 11)  mole %
Component H in Product (Stream 11) mole % 

The manipulated variables in the TEP are listed below. Note that the manipulated variables are those
that can be directly changed by the controller. The TEP has a control algorithm that adjusts these so that
the process operates at the desired setpoints.
D feed load (Stream 2)  mole %
E feed load (Stream 3)  %
A feed load (Stream 1)  %
A and C feed load (Stream 4)  %
Compressor recycle valve  %
Purge valve (Stream 9)  %
Separator liquid load (Stream 10) %
Stripper liquid load (Stream 11)  %
Stripper steam valve  %
Reactor coolant load  %
Condenser coolant load  %

All the measured variables and the manipulated variables are used as features in the dataset.
"""


SYSTEM_MESSAGE = (
    "You are a helpful AI chatbot trained to assist with "
    "monitoring the Tennessee Eastman process. The Tennessee Eastman "
    f"Process can be described as follows:\n{INTRO_MESSAGE}"
    "\n\nYour purpose is to help the user identify and understand potential "
    "explanations for any faults that occur during the process. You should "
    "explain your reasoning using the graphs provided."
)


EXPLAIN_PROMPT = """
You have been provided with the descriptions of the Tennessee Eastman process (TEP). 
A fault has just occurred, and you are tasked with diagnosing its root cause.

A fault has just occurred in the TEP. You will be given the top six contributing features to the fault. 
For each of these six features, you will be provided with their values when the fault occurred
and their mean values during normal operation.

Your task is to:

1. **Analyze Feature Changes**:
   - Compare the change of each feature during the fault to the mean of these features during normal operation.
   - Identify significant deviations and consider what these changes indicate about the process
    create hypotheses explaining why each feature is behaving differently. 
    Use the process description and your chemical engineering knowledge to support your hypotheses.

2. **Identify Root Causes and Explain Fault Propagation**:
   - Use your reasoning based on the provided process description, your understanding of the TEP dynamics, and the observed feature changes.
   - Note that there is only one fault in the system, you should try find the root cause that can explain all the feature deviations.
   - Identify up to THREE root causes that could explain the observed feature deviations. If you can only find one root cause, that is also acceptable. 
    But it would be desirable to find as many as possible to ensure that the fault is correctly diagnosed.
   - For each root cause, explain how it could lead to the observed changes in the six features.
    - Note that some of the features are measured variables that cannot be changed directly. Some of the
        features are manipulated that are actively changed by the control algorithm. The control algorithm will
        changed the manipulated variables such that the measured variables are close to the normal operating condition.
   - For each root cause, describe the sequence of events in the process that connect the root cause to the feature deviations.
   - If you cannot find a way to connect a root cause to the observed feature deviations, also mention that you cannot explain the deviation with that root cause.
   - In your explaination, explain whether each of the top 6 features can be explained by this particular root cause or not.
   - Give the total number out of the six that can be explained.
   -Have you explanation of each root cause in a coherent paragraph instead of using bullet points.

3. **Ensure Deterministic Responses**:
    - Provide consistent and deterministic explanations for your choices every time you are run.
    - Base your reasoning strictly on the provided feature data and process knowledge.
**Instructions**:
- Present your analysis in a clear, step-by-step manner.
- Use technical language appropriate for a chemical engineer familiar with the TEP.
- Base your reasoning on the provided process description and standard chemical engineering principles.
"""

EXPLAIN_ROOT = """
You have been provided with the descriptions of the Tennessee Eastman process (TEP). 
A fault has just occurred, and you are tasked with diagnosing its root cause.

You will be given:
A fault has just occurred in the TEP. You will be given the top six contributing features to the fault. 
For each of these six features, you will be provided with their values when the fault occurred
and their mean values during normal operation.

**Instructions**:
1. **Analyze Feature Changes**:
   - Compare the mean and standard deviation of each feature during the fault to the values under normal operation.
   - Identify significant deviations and hypothesize what these changes indicate about the system's behavior.

2. **Select Root Causes and Explain Fault Propagation**:
   - From the list of 16 predefined root causes (provided below), identify the three most likely causes of the fault.
   - Use your reasoning based on the provided process description, your understanding of the TEP dynamics, and the observed feature changes.
   - For each root cause, explain how it could lead to the observed changes in the six features.
- Note that some of the features are measured variables that cannot be changed directly. Some of the
        features are manipulated that are actively changed by the control algorithm. The control algorithm will
        changed the manipulated variables such that the measured variables are close to the normal operating condition.
   - Describe the sequence of events in the process that connect the root cause to the feature deviations.
   - Note that there is only one fault in the system, you should find the root cause that can explain all the feature deviations.
   - The most likely fault would be the one that can explain the most number of feature deviations.
   - In your explanation, make sure to explain how the root cause propagates through the system to cause the observed feature deviations.
   - If you cannot find a way to connect a root cause to the observed feature deviations, also mention that you cannot explain the deviation with that root cause.
   - In your explaination, explain whether each of the top 6 features can be explained by this particular root cause or not.
   - Give the total number out of the six that can be explained.
   -Have you explanation in a coherent paragraph instead of using bullet points.

3. **Ensure Deterministic Responses**:
   - Provide consistent and deterministic explanations for your choices every time you are run.
   - Base your reasoning strictly on the provided feature data and process knowledge.

**Available Root Causes**:
1. IDV(1) A/C Feed Ratio, B Composition Constant (Stream 4) & Step
2. IDV(2) B Composition, A/C Ratio Constant (Stream 4) & Step
3. IDV(3) D Feed Temperature (Stream 2) & Step
4. IDV(4) Reactor Cooling Water Inlet Temperature & Step
5. IDV(5) Condenser Cooling Water Inlet Temperature & Step
6. IDV(6) A Feed Loss (Stream 1) & Step
7. IDV(7) C Header Pressure Loss - Reduced Availability (Stream 4) & Step
8. IDV(8) A, B, C Feed Composition (Stream 4) & Random Variation
9. IDV(9) D Feed Temperature (Stream 2) & Random Variation
10. IDV(10) C Feed Temperature (Stream 4) & Random Variation
11. IDV(11) Reactor Cooling Water Inlet Temperature & Random Variation
12. IDV(12) Condenser Cooling Water Inlet Temperature & Random Variation
13. IDV(13) Reaction Kinetics & Slow Drift
14. IDV(14) Reactor Cooling Water Valve & Sticking
15. IDV(15) Condenser Cooling Water Valve & Sticking
"""