import os
import io
import uuid
import pandas as pd
import matplotlib.pyplot as plt
from typing import List, Dict
from datetime import datetime
import yfinance as yf
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain.tools import tool
from ydata_profiling import ProfileReport
from autoviz.AutoViz_Class import AutoViz_Class
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "outputs")
os.makedirs(OUT_DIR, exist_ok=True)

#Pandas DataFrame Agent Tool (데이터 분석)


#DataFrame 분석 Tool
#여기서 넣을 수 있는 분석할만한 요소를 우리가 미리지정한다면 더 좋지 않을까

@tool("dataframe_analysis")
def dataframe_analysis_tool(df, query: str) -> str:
    """Pandas DataFrame 기반 분석 질의"""
    llm = ChatOpenAI(model="gpt-4o-mini")
    agent = create_pandas_dataframe_agent(llm, df, verbose=False)
    return agent.run(query)

#DataFrame 기반 자동 EDA
@tool("eda_and_insight")
def eda_and_insight_tool(csv_path: str):
    df = pd.read_csv(csv_path)
    
    # 자동 EDA 리포트
    profile = ProfileReport(df, minimal=True)
    report_path = "/mnt/data/eda_report.html"
    profile.to_file(report_path)
    
    # LLM 기반 데이터 분석 질의 예시
    agent = create_pandas_dataframe_agent(llm, df)
    insight = agent.run("데이터셋에서 주요 인사이트 5가지 알려줘")
    
    return {
        "eda_report": report_path,
        "insight": insight
    }



#차트 생성 (PythonAstREPLTool)
from langchain_experimental.tools import PythonAstREPLTool

def create_python_chart_tool():
    python_tool = PythonAstREPLTool()

    return python_tool

#ticker 찾기
llm = ChatOpenAI(model="gpt-4o-mini")

@tool("find_ticker")
def find_ticker_tool(company_name: str):
    """
    회사 이름으로 미국/글로벌 증시의 티커를 추론한다.
    예: 'Apple' -> 'AAPL'
    """
    prompt = f"""
    아래 회사명의 주식 티커(symbol)를 알려줘.
    - 회사명: {company_name}
    - 티커만 한 단어로 출력해줘.
    """
    return llm.invoke(prompt).content.strip()

#yfinance 다운로드
@tool("fetch_financial_data")
def fetch_financial_data_tool(ticker: str):
    """
    Fetch stock price & financial fundamentals using yfinance.
    """
    stock = yf.Ticker(ticker)
    
    info = stock.info
    hist = stock.history(period="1y").reset_index().to_dict(orient="records")

    result = {
        "ticker": ticker,
        "longName": info.get("longName"),
        "sector": info.get("sector"),
        "industry": info.get("industry"),
        "marketCap": info.get("marketCap"),
        "financials": stock.financials.to_dict() if stock.financials is not None else {},
        "history": hist,
    }

    return result

#산업 동향 자동 웹검색
@tool("search_industry_news")
def search_industry_news(company: str) -> str:
    """Search industry trend news related to the company."""
    from serpapi import GoogleSearch

    search = GoogleSearch({
        "q": f"{company} industry trend",
        "api_key": "YOUR_SERPAPI_KEY"
    })
    results = search.get_dict()
    articles = results.get("news_results", [])

    text = ""
    for a in articles[:5]:
        text += f"- {a.get('title')} : {a.get('snippet')}\n"

    return text

#차트이미지생성
AV = AutoViz_Class()
OUT_DIR = "/mnt/data"

@tool("autoviz_tool")
def autoviz_tool(csv_path: str, dep_var: str = "") -> list:
    """
    CSV를 받아 AutoViz 차트 생성 후 이미지 파일 리스트 반환
    """
    df = pd.read_csv(csv_path)
    
    # AutoViz 실행 (차트 자동 생성)
    AV.AutoViz(filename=csv_path, depVar=dep_var, dfte=df, chart_format="png")
    
    # 결과 폴더에 저장된 png 파일 목록 반환
    import glob
    return glob.glob(f"{OUT_DIR}/*.png")