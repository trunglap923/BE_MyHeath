from langgraph.graph import StateGraph, START, END
from chatbot.agents.states.state import AgentState

# Import các node
from chatbot.agents.nodes.chatbot import (
    classify_topic,
    route_by_topic,
    meal_identify,
    suggest_meal_node,
    generate_final_response,
    food_suggestion,
    select_food_plan,
    food_query,
    select_food,
    general_chat,
    policy
)

def workflow_chatbot():
    workflow_chatbot = StateGraph(AgentState)

    workflow_chatbot.add_node("classify_topic", classify_topic)
    workflow_chatbot.add_node("meal_identify", meal_identify)
    workflow_chatbot.add_node("suggest_meal_node", suggest_meal_node)
    workflow_chatbot.add_node("generate_final_response", generate_final_response)
    workflow_chatbot.add_node("food_suggestion", food_suggestion)
    workflow_chatbot.add_node("select_food_plan", select_food_plan)
    workflow_chatbot.add_node("food_query", food_query)
    workflow_chatbot.add_node("select_food", select_food)
    workflow_chatbot.add_node("general_chat", general_chat)
    workflow_chatbot.add_node("policy", policy)

    workflow_chatbot.add_edge(START, "classify_topic")

    workflow_chatbot.add_conditional_edges(
        "classify_topic",
        route_by_topic,
        {
            "meal_identify": "meal_identify",
            "food_suggestion": "food_suggestion",
            "food_query": "food_query",
            "policy": "policy",
            "general_chat": "general_chat",
        }
    )

    workflow_chatbot.add_edge("meal_identify", "suggest_meal_node")
    workflow_chatbot.add_edge("suggest_meal_node", "generate_final_response")
    workflow_chatbot.add_edge("generate_final_response", END)

    workflow_chatbot.add_edge("food_suggestion", "select_food_plan")
    workflow_chatbot.add_edge("select_food_plan", END)

    workflow_chatbot.add_edge("food_query", "select_food")
    workflow_chatbot.add_edge("select_food", END)

    workflow_chatbot.add_edge("policy", END)
    workflow_chatbot.add_edge("general_chat", END)

    app = workflow_chatbot.compile()
    
    return app
