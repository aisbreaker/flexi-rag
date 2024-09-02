from langgraph.graph import END, StateGraph, START
from workflow.graph_state import AnswerWorkflowGraphState
from workflow.simple_graph_nodes import generate, generate_on_last_node
#from workflow.simple_graph_nodes import generate2

#
# make this an ASYNC workflow,
# i.e. all nodes are async functions
#

def create_workflow():
    workflow = StateGraph(AnswerWorkflowGraphState)

    # Define the nodes
    #workflow.add_node("generate", generate)  # generatae
    workflow.add_node("generate", generate_on_last_node)  # generatae

    # Build graph
    workflow.add_edge(START, "generate")
    workflow.add_edge("generate", END)
 
    # Compile
    app = workflow.compile()
    return app
