from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from app.routers import root, public, profile, stocks
from app.users import get_user_by_username, verify_password
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from app.models import User, StockMetadata, StockPrice, UserWatchlist, TickerConfig
from app.auth import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from app.services.scheduler import job_scheduler
from app.services.scheduler.registry import register_all_jobs

app = FastAPI()

@app.on_event("startup")
async def app_init():
    # Initialize MongoDB
    client = AsyncIOMotorClient("mongodb://mongodb:27017")
    await init_beanie(
        database=client.kuberan, 
        document_models=[User, StockMetadata, StockPrice, UserWatchlist, TickerConfig]
    )
    
    # Register and start all scheduled jobs
    register_all_jobs()
    job_scheduler.start()
    print("✓ Application started successfully")

@app.on_event("shutdown")
async def app_shutdown():
    # Stop all scheduled jobs
    job_scheduler.stop()
    print("✓ Application shutdown complete")

app.include_router(root.router)
app.include_router(public.router)
app.include_router(profile.router)
app.include_router(stocks.router)

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await get_user_by_username(form_data.username)
    if not user or not await verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.username}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": access_token, "token_type": "bearer"}

