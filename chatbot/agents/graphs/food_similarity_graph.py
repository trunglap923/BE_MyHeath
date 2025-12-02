from langgraph.graph import StateGraph, START, END
from chatbot.agents.states.state import SwapState

from chatbot.agents.nodes.app_functions import get_user_profile, find_replacement_candidates, calculate_top_options, llm_finalize_choice

def food_similarity_graph() -> StateGraph:
    swap_workflow = StateGraph(SwapState)

    swap_workflow.add_node("get_profile", get_user_profile)
    swap_workflow.add_node("find_candidates", find_replacement_candidates)
    swap_workflow.add_node("optimize_select", calculate_top_options)
    swap_workflow.add_node("select_meal", llm_finalize_choice)

    swap_workflow.set_entry_point("get_profile")
    swap_workflow.add_edge("get_profile", "find_candidates")
    swap_workflow.add_edge("find_candidates", "optimize_select")
    swap_workflow.add_edge("optimize_select", "select_meal")
    swap_workflow.add_edge("select_meal", END)

    app = swap_workflow.compile()
    return app
