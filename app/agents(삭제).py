import os
from openai import OpenAI
from langchain import OpenAI as LC_OpenAI  # 또는 langchain.chat_models
from langchain.agents import create_csv_agent
from langchain_experimental.tools import PythonAstREPLTool
from langchain.agents.agent_toolkits import create_pandas_dataframe_agent
import pandas as pd

# 환경변수 OPENAI_API_KEY 필요
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise EnvironmentError("OPENAI_API_KEY 환경 변수를 설정하세요.")

# OpenAI client wrapper (LangChain용)
llm = LC_OpenAI(model="gpt-4o-mini", temperature=0.0, openai_api_key=OPENAI_API_KEY)

def create_dataframe_agent_from_df(df: pd.DataFrame, verbose: bool=False):
    """
    Pandas agent: LLM이 DataFrame을 직접 탐색하고, 코드 실행으로 차트/분석까지 시도.
    """
    agent = create_pandas_dataframe_agent(llm, df, verbose=verbose)
    return agent

def create_python_repl_tool():
    # PythonAstREPLTool: LLM이 안전하게 python 코드를 실행 (표준 LangChain 제공 도구)
    tool = PythonAstREPLTool()
    return tool