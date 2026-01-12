from app.repositories.base_repository import BaseRepository
from app.schema.be_models import AddNotificationRequest
import logging

logger = logging.getLogger(__name__)

class NotificationRepository(BaseRepository):
    def get_user_token(self, user_id: int):
        with self.get_cursor() as cur:
            cur.execute("SELECT token FROM public.userinfo WHERE id = %s;", (user_id,))
            row = cur.fetchone()
            return row[0] if row else None

    def create_notification(self, notification: AddNotificationRequest) -> int:
        with self.get_cursor() as cur:
            insert_sql = """
                INSERT INTO notification (senderId, receiverId, type, content, relatedId)
                VALUES
                (%s, %s, %s, %s, %s)
                RETURNING id;
            """
            values = (notification.senderId, notification.receiverId, notification.type, notification.content, notification.relatedId)
            cur.execute(insert_sql, values)
            return cur.fetchone()[0]

    def get_notifications_by_receiver(self, receiver_id: int):
        with self.get_cursor() as cur:
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
            cur.execute(sql, (receiver_id,))
            rows = cur.fetchall()
            return [
                {
                    "id": row[0], 
                    "fullname": row[1],
                    "type": row[2],
                    "content": row[3],
                    "createAt": row[4],
                    "status": row[5]
                }
                for row in rows
            ]

    def mark_read(self, id: int):
        with self.get_cursor() as cur:
            sql = "UPDATE public.notification SET status = 'READ' WHERE id = %s"
            cur.execute(sql, (id,))
