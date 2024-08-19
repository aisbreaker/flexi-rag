from langgraph.graph import END, StateGraph, START
from workflow.graph_state import GraphState
from workflow.simple_graph_nodes import generate, generate9
from workflow.simple_graph_nodes import generate2

def create_workflow():
    workflow = StateGraph(GraphState)

    # Define the nodes
    #workflow.add_node("generate", generate)  # generatae
    workflow.add_node("generate", generate9)  # generatae

    # Build graph
    workflow.add_edge(START, "generate")
    workflow.add_edge("generate", END)
 
    # Compile
    app = workflow.compile()
    return app
