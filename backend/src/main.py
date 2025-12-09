from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.model.Token import ScanResult,Request
from src.scanner import scan_source

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/test')
def index():
    return {"server listining on port 8000"}

@app.post("/scan", response_model=ScanResult)
async def scan_code(request: Request):
    return scan_source(request.code)