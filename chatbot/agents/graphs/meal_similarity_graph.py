from langgraph.graph import StateGraph, START, END
from chatbot.agents.states.state import AgentState

# Import các node
from chatbot.agents.nodes.functions import get_user_profile, generate_food_similarity_2, generate_meal_plan_json_2, enrich_meal_plan_with_nutrition_2

def meal_similarity_graph() -> StateGraph:
    workflow = StateGraph(AgentState)

    workflow.add_node("Get_User_Profile", get_user_profile)
    workflow.add_node("Generate_Food_Similarity_2", generate_food_similarity_2)
    workflow.add_node("Generate_Meal_Plan_Json_2", generate_meal_plan_json_2)
    workflow.add_node("Enrich_Meal_Plan_With_Nutrition_2", enrich_meal_plan_with_nutrition_2)

    workflow.set_entry_point("Get_User_Profile")

    workflow.add_edge("Get_User_Profile", "Generate_Food_Similarity_2")
    workflow.add_edge("Generate_Food_Similarity_2", "Generate_Meal_Plan_Json_2")
    workflow.add_edge("Generate_Meal_Plan_Json_2", "Enrich_Meal_Plan_With_Nutrition_2")
    workflow.add_edge("Enrich_Meal_Plan_With_Nutrition_2", END)

    graph = workflow.compile()
    return graph
