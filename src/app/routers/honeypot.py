from fastapi import APIRouter, Request, BackgroundTasks, Depends, Form
from core.security import get_current_user
from app.services.honeypot_service import HoneypotService
from app.services.session_service import SessionService
from app.services.honeypot_service import HoneypotService, get_honeypot_service
from app.middleware.rate_limit import limiter
import ipaddress

router = APIRouter(prefix="/api", tags=["honeypot"])

@router.post("/login")
@limiter.limit("100/hour")
async def bait_login(
    request: Request,
    background_tasks: BackgroundTasks,
    username: str = Form(...),
    password: str = Form(...),
    honeypot: str = Form(""),
    honeypot_svc: HoneypotService = Depends(get_honeypot_service)
):
    ip = request.client.host
    data = {"ip": ip, "path": "/api/login", "body": {"username": username, "password": password}}
    if honeypot:
        data["attack_type"] = "honeypot_fill"
    
    fake_resp = await honeypot_svc.handle_request(data, background_tasks)
    return fake_resp

@router.post("/signup")
@limiter.limit("100/hour")
async def bait_signup(request: Request, background_tasks: BackgroundTasks, username: str = Form(...), email: str = Form(...), password: str = Form(...), honeypot_svc: HoneypotService = Depends(get_honeypot_service)):
    ip = request.client.host
    data = {"ip": ip, "path": "/api/signup", "body": {"username": username, "email": email}}
    fake_resp = await honeypot_svc.handle_request(data, background_tasks)
    return fake_resp

@router.post("/checkout")
@limiter.limit("100/hour")
async def bait_checkout(request: Request, background_tasks: BackgroundTasks, card_number: str = Form(...), cvv: str = Form(...), honeypot_svc: HoneypotService = Depends(get_honeypot_service)):
    ip = request.client.host
    data = {"ip": ip, "path": "/api/checkout", "body": {"card_number": card_number, "cvv": cvv}}
    fake_resp = await honeypot_svc.handle_request(data, background_tasks)
    return {"status": "processing"}

@router.get("/query")
@limiter.limit("100/hour")
async def bait_query(request: Request, background_tasks: BackgroundTasks, q: str = "", honeypot_svc: HoneypotService = Depends(get_honeypot_service)):
    ip = request.client.host
    data = {"ip": ip, "path": "/api/query", "query": q}
    fake_resp = await honeypot_svc.handle_request(data, background_tasks)
    return fake_resp

@router.get("/admin/dashboard")
@router.get("/admin/logs")
@router.post("/admin/products")
@limiter.limit("100/hour")
async def bait_admin(request: Request, background_tasks: BackgroundTasks, honeypot_svc: HoneypotService = Depends(get_honeypot_service)):
    ip = request.client.host
    data = {"ip": ip, "path": request.url.path, "method": request.method}
    fake_resp = await honeypot_svc.handle_request(data, background_tasks)
    return {"dashboard": "fake_data", "logs": []}

