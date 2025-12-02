from langgraph.graph import StateGraph, START, END
from chatbot.agents.states.state import AgentState

# Import các node
from chatbot.agents.nodes.app_functions import get_user_profile, generate_food_candidates, select_menu_structure, optimize_portions_scipy

def meal_plan_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("get_profile", get_user_profile)
    workflow.add_node("generate_candidates", generate_food_candidates)
    workflow.add_node("select_menu", select_menu_structure)
    workflow.add_node("optimize_macros", optimize_portions_scipy)

    workflow.set_entry_point("get_profile")
    workflow.add_edge("get_profile", "generate_candidates")
    workflow.add_edge("generate_candidates", "select_menu")
    workflow.add_edge("select_menu", "optimize_macros")
    workflow.add_edge("optimize_macros", END)

    graph = workflow.compile()
    return graph
