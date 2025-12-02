from langchain.prompts import PromptTemplate
import json
from pydantic import BaseModel, Field
from chatbot.agents.states.state import AgentState
from chatbot.models.llm_setup import llm
from typing import List
import logging

# --- Cấu hình logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MealIntent(BaseModel):
    meals_to_generate: List[str] = Field(
        description="Danh sách các bữa được người dùng muốn gợi ý: ['sáng', 'trưa', 'tối']."
    )
    
def meal_identify(state: AgentState):
    logger.info("---MEAL IDENTIFY---")

    llm_with_structure_op = llm.with_structured_output(MealIntent)

    # Lấy câu hỏi mới nhất từ lịch sử hội thoại
    messages = state["messages"]
    user_message = messages[-1].content if messages else state.question

    format_instructions = json.dumps(llm_with_structure_op.output_schema.model_json_schema(), ensure_ascii=False, indent=2)

    prompt = PromptTemplate(
        template="""
        Bạn là bộ phân tích yêu cầu gợi ý bữa ăn trong hệ thống chatbot dinh dưỡng.

        Dựa trên câu hỏi của người dùng, hãy xác định danh sách các bữa người dùng muốn gợi ý.

        - Các bữa người dùng có thể muốn gợi ý gồm: ["sáng", "trưa", "tối"].

        Câu hỏi người dùng: {question}

        Hãy xuất kết quả dưới dạng JSON theo schema sau:
        {format_instructions}
        """
    )

    chain = prompt | llm_with_structure_op

    result = chain.invoke({
        "question": user_message,
        "format_instructions": format_instructions
    })

    logger.info("Bữa cần gợi ý: " + ", ".join(result.meals_to_generate))

    return {
        "meals_to_generate": result.meals_to_generate,
    }
