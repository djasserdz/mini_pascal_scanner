from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.model.Token import ScanRequest,ScanResult
from src.scanner import scan_source

app = FastAPI()

app.middleware(CORSMiddleware(
    app,
    allow_origins=['*'],
    allow_headers=['*'],
    allow_methods=['*']
))

@app.get('/test')
def index():
    return {"server listining on port 8000"}

@app.post("/scan", response_model=ScanResult)
async def scan_code(request: ScanRequest):
    return scan_source(request.code)