from fastapi import APIRouter, Request, BackgroundTasks, Depends, Form
from core.security import get_current_user
from app.services.honeypot_service import HoneypotService
from app.services.session_service import SessionService
import ipaddress

router = APIRouter(prefix="/api", tags=["honeypot"])

@router.post("/login")
async def bait_login(
    request: Request,
    background_tasks: BackgroundTasks,
    username: str = Form(...),
    password: str = Form(...),
    honeypot: str = Form(""),
    honeypot_svc: HoneypotService = Depends(lambda: honeypot_svc)  # Dependency injection later
):
    ip = request.client.host
    data = {"ip": ip, "path": "/api/login", "body": {"username": username, "password": password}}
    if honeypot:
        data["attack_type"] = "honeypot_fill"
    
    fake_resp = await honeypot_svc.handle_request(data, background_tasks)
    return fake_resp

@router.post("/signup")
async def bait_signup(request: Request, background_tasks: BackgroundTasks, username: str = Form(...), email: str = Form(...), password: str = Form(...)):
    ip = request.client.host
    data = {"ip": ip, "path": "/api/signup", "body": {"username": username, "email": email}}
    fake_resp = await honeypot_svc.handle_request(data, background_tasks)
    return fake_resp

@router.post("/checkout")
async def bait_checkout(request: Request, background_tasks: BackgroundTasks, card_number: str = Form(...), cvv: str = Form(...)):
    ip = request.client.host
    data = {"ip": ip, "path": "/api/checkout", "body": {"card_number": card_number, "cvv": cvv}}
    fake_resp = await honeypot_svc.handle_request(data, background_tasks)
    return {"status": "processing"}

@router.get("/query")
async def bait_query(request: Request, background_tasks: BackgroundTasks, q: str = ""):
    ip = request.client.host
    data = {"ip": ip, "path": "/api/query", "query": q}
    fake_resp = await honeypot_svc.handle_request(data, background_tasks)
    return fake_resp

@router.route("/admin/dashboard", methods=["GET"])
@router.route("/admin/logs", methods=["GET"])
@router.route("/admin/products", methods=["POST"])
async def bait_admin(request: Request, background_tasks: BackgroundTasks):
    ip = request.client.host
    data = {"ip": ip, "path": request.url.path, "method": request.method}
    fake_resp = await honeypot_svc.handle_request(data, background_tasks)
    return {"dashboard": "fake_data", "logs": []}

