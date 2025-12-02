from langchain.prompts import PromptTemplate
import json
from pydantic import BaseModel, Field
from chatbot.agents.states.state import AgentState
from chatbot.models.llm_setup import llm
import logging

# --- Cấu hình logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Topic(BaseModel):
    name: str = Field(
        description=(
            "Tên chủ đề mà người dùng đang hỏi. "
            "Các giá trị hợp lệ: 'meal_suggestion', 'food_suggestion', food_query, 'policy', 'general_chat'."
        )
    )

def classify_topic(state: AgentState):
    logger.info("---CLASSIFY TOPIC---")
    llm_with_structure_op = llm.with_structured_output(Topic)

    prompt = PromptTemplate(
        template="""
        Bạn là bộ phân loại chủ đề câu hỏi người dùng trong hệ thống chatbot dinh dưỡng.

        Nhiệm vụ:
        - Phân loại câu hỏi vào một trong các nhóm:
            1. "meal_suggestion": khi người dùng yêu cầu gợi ý thực đơn cho cả một bữa ăn hoặc trong cả một ngày (chỉ cho bữa ăn, không cho món ăn đơn lẻ).
            2. "food_suggestion": khi người dùng yêu cầu tìm kiếm hoặc gợi ý một món ăn duy nhất (có thể của một bữa nào đó).
            3. "food_query": khi người dùng muốn tìm kiếm thông tin về một món ăn như tên, thành phần, dinh dưỡng, cách chế biến
            4. "policy": khi người dùng muốn biết các thông tin liên quan đến app.
            5. "general_chat": khi người dùng muốn hỏi đáp các câu hỏi chung liên quan đến sức khỏe, chất dinh dưỡng.

        Câu hỏi người dùng: {question}

        Hãy trả lời dưới dạng JSON phù hợp với schema sau:
        {format_instructions}
        """
    )

    messages = state["messages"]
    user_message = messages[-1].content if messages else state.question

    format_instructions = json.dumps(llm_with_structure_op.output_schema.model_json_schema(), ensure_ascii=False, indent=2)

    chain = prompt | llm_with_structure_op

    topic_result = chain.invoke({
        "question": user_message,
        "format_instructions": format_instructions
    })

    logger.info(f"Topic: {topic_result.name}")

    return {"topic": topic_result.name}

def route_by_topic(state: AgentState):
    topic = state["topic"]
    if topic == "meal_suggestion":
        return "meal_identify"
    elif topic == "food_suggestion":
        return "food_suggestion"
    elif topic == "food_query":
        return "food_query"
    elif topic == "policy":
        return "policy"
    else:
        return "general_chat"
    