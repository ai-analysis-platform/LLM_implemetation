import pandas as pd
import os
from google.genai import Client  # pip install google-genai, 예시 import
from typing import Optional

from typing import Dict, List, Any
import os


def test_generate_report(prompt: str):
    """
    prompt 기반으로 데이터를 분석해서 간단한 리포트 생성
    실제 LLM 대신 데모용으로 '리포트 템플릿'만 제공
    """

    df = pd.read_csv("backend/sample_data.csv")

    latest = df.iloc[0]
    prev = df.iloc[1]

    revenue_growth = latest["revenue"] - prev["revenue"]
    profit_growth = latest["profit"] - prev["profit"]

    report = f"""
    자동 생성 리포트

    요청 프롬프트: {prompt}

    최신 분기 매출: {latest['revenue']:,}
    이전 분기 매출: {prev['revenue']:,}
    매출 증감: {revenue_growth:,}

    최신 분기 이익: {latest['profit']:,}
    이전 분기 이익: {prev['profit']:,}
    이익 증감: {profit_growth:,}

    결론:
    매출과 이익이 모두 성장한 긍정적 분기였습니다.
    """

    return report

genai_client = Client(api_key="AIzaSyDof7GowCRnak7-XjcOmK7BK5riVr5b1Zw")
#openai.api_key = os.getenv("OPENAI_API_KEY")

def find_ticker_symbol(company_name: str) -> str:
    """
    회사 이름을 받아서 Yahoo Finance 형식의 티커 심볼 반환
    """
    prompt = f"""
    Find the stock ticker symbol for "{company_name}".
    Prefer Yahoo Finance ticker format (e.g., 005930.KS for Samsung Electronics, AAPL for Apple).
    Return ONLY the ticker symbol as a string, nothing else.
    """
    
    try:
    
        result = genai_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        
        # 4️⃣ 결과에서 텍스트 추출
        text = getattr(result, "text", "")
        return text.strip() if text else ""
    
    except Exception as e:
        print("Failed to find ticker:", e)
        return ""


FinancialData = Dict[str, Any]
GroundingChunk = Dict[str, Any]
ChartConfig = Dict[str, Any]

def generate_business_report(data: FinancialData) -> Dict[str, Any]:
    """
    TypeScript generateBusinessReport를 Python으로 변환.
    LLM을 호출해 재무 데이터 기반 Equity Research Report 생성.
    """

    # 1️⃣ 프롬프트 구성
    prompt = f"""
You are a Chief Equity Analyst at a top-tier investment bank (like Goldman Sachs or Morgan Stanley).
Your task is to write a professional "Equity Research Report" for the company: "{data.get('companyName')}" (Ticker: {data.get('ticker', 'N/A')}).
The report must be based on the provided internal financial data (CSV) and real-time market data sourced via Google Search.

**Input Data:**
- Company: {data.get('companyName')}
- Industry: {data.get('industry')}
- Reporting Period: {data.get('reportingPeriod')}
- Internal CSV Data: 
{data.get('csvData', '')[:5000]}
- User Request: {data.get('additionalRequests', 'None')}
- Report Template: {data.get('reportTemplate', '')}

**Virtual Python Environment Instructions (Simulation):**
Imagine you have access to Python libraries `yfinance` and `FinanceDataReader`. 
Since you cannot actually run code, use Google Search to FIND the specific data points that these libraries would provide.

**Report Structure (Strictly follow this structure):**
1. Header Section: Investment Rating, Target Price, Current Price, Market Cap, 52-week Range
2. Investment Summary: 3-4 bullet points
3. Earnings Review: Consensus vs Actual
4. Segment Breakdown
5. Valuation: P/E, P/B ratios
6. ESG & Risks

**Chart Generation Instructions:**
Generate 2-3 charts: Price Trend, Segment Performance, Valuation/Growth

**Output Format:**
[REPORT_START]
(Write the full Markdown report here.)
[REPORT_END]

[CHARTS_START]
(Provide a valid JSON array of ChartConfig objects here.)
[CHARTS_END]
"""
    
    print(prompt)

    try:

        result = genai_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        
        # 4️⃣ 결과에서 텍스트 추출
        text = getattr(result, "text", "")

        
        # 2️⃣ LLM 호출
        response = genai_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        # 3️⃣ 결과 추출
        text = getattr(response, "text", "")

        # 4️⃣ REPORT / CHARTS 분리
        report_start = "[REPORT_START]"
        report_end = "[REPORT_END]"
        charts_start = "[CHARTS_START]"
        charts_end = "[CHARTS_END]"

        if report_start in text and report_end in text:
            report_text = text.split(report_start)[1].split(report_end)[0].strip()

        if charts_start in text and charts_end in text:
            import json
            charts_str = text.split(charts_start)[1].split(charts_end)[0].strip()
            try:
                charts = json.loads(charts_str)
            except json.JSONDecodeError:
                charts = []

        return {"reportText": report_text, "charts": charts, "sources": []}

    except Exception as e:
        print("Failed to generate report:", e)
        return {"reportText": "", "charts": [], "sources": []}
    

