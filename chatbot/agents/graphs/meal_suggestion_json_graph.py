from langgraph.graph import StateGraph, START, END
from chatbot.agents.states.state import AgentState

# Import các node
from chatbot.agents.nodes.functions import get_user_profile, generate_food_plan, generate_meal_plan_day_json, enrich_meal_plan_with_nutrition

def workflow_meal_suggestion_json() -> StateGraph:
    workflow = StateGraph(AgentState)

    workflow.add_node("Get_User_Profile", get_user_profile)
    workflow.add_node("Generate_Food_Plan", generate_food_plan)
    workflow.add_node("Generate_Meal_Plan_Day_Json", generate_meal_plan_day_json)
    workflow.add_node("Enrich_Meal_Plan_With_Nutrition", enrich_meal_plan_with_nutrition)

    workflow.set_entry_point("Get_User_Profile")

    workflow.add_edge("Get_User_Profile", "Generate_Food_Plan")
    workflow.add_edge("Generate_Food_Plan", "Generate_Meal_Plan_Day_Json")
    workflow.add_edge("Generate_Meal_Plan_Day_Json", "Enrich_Meal_Plan_With_Nutrition")
    workflow.add_edge("Enrich_Meal_Plan_With_Nutrition", END)

    graph = workflow.compile()
    return graph
