from fastapi import APIRouter, HTTPException, Depends
from app.services.features.notification_service import NotificationService
from app.schema.be_models import AddNotificationRequest

router = APIRouter(prefix="/notification", tags=["Notification"])

def get_notification_service():
    return NotificationService()

@router.post("/send")
async def send_notification(notification: AddNotificationRequest, service: NotificationService = Depends(get_notification_service)):
    result = service.insert_notification_to_db(notification)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.get("/{receiver_id}")
async def get_notifications(receiver_id: int, service: NotificationService = Depends(get_notification_service)):
    result = service.get_notifications_by_receiver_id(receiver_id)
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@router.put("/read/{id}")
async def read_notification(id: int, service: NotificationService = Depends(get_notification_service)):
    result = service.mark_notification_read(id)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result
