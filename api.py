# REST API that calculates the distance from vertical and horizontal distances.
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from math import sqrt

from starlette.responses import Response
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("distanceCalculator")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://berke.dev"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response

@app.middleware("http")
async def custom_cors_middleware(request, call_next):
    origin = request.headers.get("origin")
    allowed = False
    if origin:
        if origin.startswith("http://localhost") or origin.startswith("https://localhost"):
            allowed = True
        elif origin.startswith("https://berke.dev"):
            allowed = True
    response = await call_next(request)
    if origin and allowed:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "*"
    elif origin:
        return Response("CORS origin forbidden", status_code=403)
    return response

@app.middleware("http")
async def add_request_logging(request, call_next):
    logger.info(f"Request: {request.method} {request.url} - Headers: {dict(request.headers)}")
    response = await call_next(request)
    logger.info(f"Response: {response.status_code} - Headers: {dict(response.headers)}")
    return response

class DistanceRequest(BaseModel):
    vertical: float
    horizontal: float

@app.post("/calculate_distance")
async def calculate_distance(request: DistanceRequest):
    if request.vertical < 0 or request.horizontal < 0:
        raise HTTPException(status_code=400, detail="Distance cannot be negative.")

    distance = sqrt(request.vertical ** 2 + request.horizontal ** 2)
    return {"distance": round(distance, 2)}

@app.get("/")
def read_root():
    return {"message": "Welcome to the Distance Calculator API! Use POST /calculate_distance to calculate distance."}
@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Distance Calculator API is running."}
@app.get("/version")
def get_version():
    return {"version": "1.0.0", "description": "Distance Calculator API version 1.0.0"}
@app.get("/docs")
def get_docs():
    if os.environ.get("ENV", "development") == "production":
        raise HTTPException(status_code=404, detail="Not found")
    return {"message": "API documentation is available at /docs"}