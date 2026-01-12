from app.core.database import get_connection
from app.schema.be_models import AddNotificationRequest
from app.core.notification import get_messaging, ADMIN_TOKEN
import logging

logger = logging.getLogger(__name__)

class NotificationService:
    def insert_notification_to_db(self, notification: AddNotificationRequest):
        conn = None
        try:
            conn = get_connection()
            cur = conn.cursor()

            receiver_token = None
            if notification.receiverId == 0:
                receiver_token = ADMIN_TOKEN
            else:
                cur.execute("SELECT token FROM public.userinfo WHERE id = %s;", (notification.receiverId,))
                token_row = cur.fetchone()
                if not token_row or not token_row[0]:
                    return {"success": False, "error": "Receiver not found or has no token"}
                receiver_token = token_row[0]

            insert_sql = """
                        INSERT INTO notification (senderId, receiverId, type, content, relatedId)
                        VALUES
                        (%s, %s, %s, %s, %s)
                        RETURNING id;
                    """
            values = (notification.senderId, notification.receiverId, notification.type, notification.content, notification.relatedId)

            cur.execute(insert_sql, values)
            new_id = cur.fetchone()[0]
            conn.commit()

            type_titles = {
                "ADD_DISH": "Người dùng thêm món ăn mới!",
                "ADD_INGREDIENT": "Người dùng thêm nguyên liệu mới!",
                "FEEDBACK": "Người dùng góp ý tới hệ thống!",
                "RESPOND": "Quản trị viên phản hồi tới bạn!"
            }
            title = type_titles.get(notification.type, type_titles["RESPOND"])

            messaging = get_messaging()
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=notification.content,
                ),
            token=receiver_token,
            )
            messaging.send(message)

            return {"success": True, "id": new_id}

        except Exception as e:
            if conn:
                conn.rollback()
            return {"success": False, "error": str(e)}
        finally:
            if conn:
                cur.close()
                conn.close()

    def get_notifications_by_receiver_id(self, receiver_id: int):
        conn = None
        try:
            conn = get_connection()
            cur = conn.cursor()

            sql = """
                SELECT
                  n.id,
                  u.fullname,
                  n.type,
                  n.content,
                  n.createdat,
                  n.status
                FROM public.notification n
                JOIN public.userinfo u ON n.senderid = u.id 
                WHERE n.receiverid = %s
                ORDER BY n.createdat DESC;
            """
            values = (receiver_id,)
            cur.execute(sql, values)
            rows = cur.fetchall()

            notifications = []
            for row in rows:
                notifications.append({
                    "id": row[0], 
                    "fullname": row[1],
                    "type": row[2],
                    "content": row[3],
                    "createAt": row[4],
                    "status": row[5]
                })

            return {"success": True, "notifications": notifications}

        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            if conn:
                cur.close()
                conn.close()

    def mark_notification_read(self, id: int):
        conn = None
        try:
            conn = get_connection()
            cur = conn.cursor()

            sql = "UPDATE public.notification SET status = 'READ' WHERE id = %s"
            values = (id,)
            
            cur.execute(sql, values)
            conn.commit()

            return {"success": True, "message": "Updated successfully"}

        except Exception as e:
            if conn: conn.rollback()
            return {"success": False, "error": str(e)}
        finally:
            if conn:
                cur.close()
                conn.close()
