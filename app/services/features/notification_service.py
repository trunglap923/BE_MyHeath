from app.repositories.notification_repository import NotificationRepository
from app.schema.be_models import AddNotificationRequest
from app.core.notification import get_messaging, ADMIN_TOKEN
import logging

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self, notification_repository: NotificationRepository):
        self.notification_repository = notification_repository

    def insert_notification_to_db(self, notification: AddNotificationRequest):
        try:
            receiver_token = None
            if notification.receiverId == 0:
                receiver_token = ADMIN_TOKEN
            else:
                receiver_token = self.notification_repository.get_user_token(notification.receiverId)
                if not receiver_token:
                    return {"success": False, "error": "Receiver not found or has no token"}

            new_id = self.notification_repository.create_notification(notification)

            type_titles = {
                "ADD_DISH": "Người dùng thêm món ăn mới!",
                "ADD_INGREDIENT": "Người dùng thêm nguyên liệu mới!",
                "FEEDBACK": "Người dùng góp ý tới hệ thống!",
                "RESPOND": "Quản trị viên phản hồi tới bạn!"
            }
            title = type_titles.get(notification.type, type_titles["RESPOND"])

            try:
                messaging = get_messaging()
                message = messaging.Message(
                    notification=messaging.Notification(
                        title=title,
                        body=notification.content,
                    ),
                token=receiver_token,
                )
                messaging.send(message)
            except Exception as e:
                logger.error(f"Error sending firebase message: {e}")
                # Continue execution even if firebase fails, as DB insert was successful

            return {"success": True, "id": new_id}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_notifications_by_receiver_id(self, receiver_id: int):
        try:
            notifications = self.notification_repository.get_notifications_by_receiver(receiver_id)
            return {"success": True, "notifications": notifications}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def mark_notification_read(self, id: int):
        try:
            self.notification_repository.mark_read(id)
            return {"success": True, "message": "Updated successfully"}
        except Exception as e:
            return {"success": False, "error": str(e)}
