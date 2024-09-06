from langgraph.graph import StateGraph, START, END 
from typing import TypedDict, List, Dict, Any, Annotated
from .agents import central_agent, tool_manager, response_generation, judge_agent

class State(TypedDict):
    user_input: Annotated[List[str], "mutable"]
    conversation_history: Annotated[List[str], "mutable"]
    extracted_info: Dict[str, Any]
    tool_output: Dict[str, Any]
    next_step: Annotated[List[str], "mutable"]
    tool_explanation: Annotated[List[str], "mutable"]
    generated_response: Annotated[List[str], "mutable"]
    feedback: str

def create_workflow():
    workflow = StateGraph(State)

    # Initialize agents
    Central_agent = central_agent()
    Tool_manager = tool_manager()
    Response_generation = response_generation()
    Judge_agent = judge_agent()


    # Add nodes
    workflow.add_node("Central_agent", Central_agent)
    workflow.add_node("Tool_manager", Tool_manager)
    workflow.add_node("Response_generation", Response_generation)
    workflow.add_node("Judge_agent", Judge_agent)

    # Connect nodes
    workflow.add_edge(START, "Central_agent")
    workflow.add_edge("Tool_manager", "Response_generation")
    workflow.add_edge("Response_generation", "Judge_agent")

    # Define the conditional logic for agent selection
    def decide_next(state):
        return state["next_step"][-1]

    # Set the conditional edges
    workflow.add_conditional_edges("Central_agent", decide_next, {"central_agent": "Central_agent", "tool_manager": "Tool_manager"})
    workflow.add_conditional_edges("Judge_agent", decide_next, {"central_agent": "Central_agent", "end": END})
    # Compile the graph
    return workflow.compile()

# Create the workflow app
workflow_app = create_workflow()