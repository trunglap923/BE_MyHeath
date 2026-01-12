from fastapi import APIRouter, HTTPException, Depends
from app.services.features.user_service import UserService
from app.schema.be_models import RegisterRequest, LoginRequest, UserInfoRequest
from app.core.container import Container

router = APIRouter(prefix="/user", tags=["User"])

def get_user_service():
    return UserService()

@router.post("/register")
async def register(data: RegisterRequest, service: UserService = Depends(get_user_service)):
    result = service.register_account(data.userName, data.passWord)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.post("/login")
async def login(data: LoginRequest, service: UserService = Depends(get_user_service)):
    result = service.login_account(data.userName, data.passWord)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.post("/info/create")
async def create_user_info(data: UserInfoRequest, service: UserService = Depends(get_user_service)):
    result = service.insert_userinfo_to_db(data)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.put("/info/update/{id}")
async def update_user_info(id: int, data: UserInfoRequest, service: UserService = Depends(get_user_service)):
    result = service.update_userinfo_in_db(id, data)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.get("/info/{id}")
async def get_user_info(id: int, service: UserService = Depends(get_user_service)):
    result = service.get_user_info_by_id(id)
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@router.get("/required-index/{id}")
async def get_required_index(id: int, service: UserService = Depends(get_user_service)):
    result = service.get_required_index_by_id(id)
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])
    return result
