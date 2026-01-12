from app.services.core.llm_service import LLMService
from app.services.core.retrieval_service import RetrievalService
from app.services.core.optimization_service import OptimizationService
from app.services.workflows.meal_suggestion_workflow import MealSuggestionWorkflowService
from app.services.workflows.chatbot_workflow import ChatbotWorkflowService
from app.services.workflows.food_similarity_workflow import FoodSimilarityWorkflowService
from app.services.features.food_management_service import FoodManagementService
from app.services.features.user_service import UserService
from app.services.features.food_service import FoodService
from app.services.features.tracking_service import TrackingService
from app.services.features.notification_service import NotificationService
from app.repositories.user_repository import UserRepository
from app.repositories.food_repository import FoodRepository
from app.repositories.notification_repository import NotificationRepository
from app.repositories.tracking_repository import TrackingRepository

class Container:
    _instance = None

    def __init__(self):
        # Repositories
        self.user_repository = UserRepository()
        self.food_repository = FoodRepository()
        self.tracking_repository = TrackingRepository()
        self.notification_repository = NotificationRepository()

        self.llm_service = LLMService()
        self.retrieval_service = RetrievalService(self.llm_service)
        self.optimization_service = OptimizationService()
        
        self.meal_workflow_service = MealSuggestionWorkflowService(
            self.llm_service,
            self.retrieval_service,
            self.optimization_service
        )
        
        self.chatbot_workflow_service = ChatbotWorkflowService(
            self.llm_service,
            self.retrieval_service,
            self.meal_workflow_service
        )
        
        self.food_similarity_service = FoodSimilarityWorkflowService(self.llm_service, self.retrieval_service, self.meal_workflow_service)
        
        self.food_management_service = FoodManagementService(self.retrieval_service)
        self.user_service = UserService(self.user_repository)
        self.food_service = FoodService(self.food_repository)
        self.tracking_service = TrackingService(self.tracking_repository)
        self.notification_service = NotificationService(self.notification_repository)

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

# Global instance
container = Container.get_instance()
