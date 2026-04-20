import os
import redis

class Config:
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev_secret_key')
    PORT = int(os.getenv('FLASK_PORT', 5000))
    FASTAPI_INTERNAL_URL = os.getenv('FASTAPI_INTERNAL_URL', 'http://localhost:8000')
    FASTAPI_SERVICE_TOKEN = os.getenv('FASTAPI_SERVICE_TOKEN', 'dummy_token')
    
    # Server-side sessions using Redis
    SESSION_TYPE = 'redis'
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    
    redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
    SESSION_REDIS = redis.from_url(redis_url)
