
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from llm_service import generate_business_report, find_ticker_symbol
from fastapi.responses import JSONResponse

app = FastAPI()

# CORS (프론트엔드에서 요청 가능하게)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Prompt(BaseModel):
    text: str
    companyName: str


'''
예시
@app.post("/generate")
def generate(prompt: Prompt):
    report = test_generate_report(prompt.text)
    return JSONResponse(content={"report": report}, media_type="application/json; charset=utf-8")
'''
@app.post("/generate")
def generate(prompt: Prompt):
    ticker = find_ticker_symbol(prompt.companyName)
    data = {
        "companyName": prompt.companyName,
        "ticker": ticker,
        "csvData": "...",  # 필요하면 CSV 내용 전달
        "reportTemplate": "",
        "reportingPeriod": "2025-Q3",
        "industry": "Technology",
        "additionalRequests": prompt.text
    }
    report = generate_business_report(data)
    return report

@app.get("/")
def read_root():
    # 테스트용 GET route
    return {"report": "This is a test report. Use POST /generate for custom report."}


