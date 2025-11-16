from langgraph.graph import StateGraph, START, END
from chatbot.agents.states.state import AgentState

# Import các node
from chatbot.agents.nodes.functions import get_user_profile, generate_food_similarity, generate_best_food_choice, enrich_food_with_nutrition

def food_similarity_graph() -> StateGraph:
    workflow = StateGraph(AgentState)

    workflow.add_node("Get_User_Profile", get_user_profile)
    workflow.add_node("Generate_Food_Similarity", generate_food_similarity)
    workflow.add_node("Generate_Best_Food_Choice", generate_best_food_choice)
    workflow.add_node("Enrich_Food_With_Nutrition", enrich_food_with_nutrition)

    workflow.set_entry_point("Get_User_Profile")

    workflow.add_edge("Get_User_Profile", "Generate_Food_Similarity")
    workflow.add_edge("Generate_Food_Similarity", "Generate_Best_Food_Choice")
    workflow.add_edge("Generate_Best_Food_Choice", "Enrich_Food_With_Nutrition")
    workflow.add_edge("Enrich_Food_With_Nutrition", END)

    graph = workflow.compile()
    return graph
