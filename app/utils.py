import os
import io
import uuid
import pandas as pd
import matplotlib.pyplot as plt
from typing import List, Dict
from datetime import datetime
import yaml
from google.genai import Client


OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "outputs")
os.makedirs(OUT_DIR, exist_ok=True)

def read_data_from_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    return df


def simple_clean(df: pd.DataFrame) -> pd.DataFrame:
    # 기본 전처리: 결측치 제거(혹은 전략 확장 가능)
    df = df.copy()
    df = df.dropna(axis=0, how='any')
    return df

def generate_eda(df: pd.DataFrame) -> str:
    desc = df.describe(include='all').transpose()
    # 간단한 상관계수 및 null info 추가
    corr = df.corr().round(3)
    nulls = df.isna().sum()
    s = f"DESCRIBE:\n{desc.to_string()}\n\nCORR:\n{corr.to_string()}\n\nNULLS:\n{nulls.to_string()}"
    return s

def generate_time_series_charts(df: pd.DataFrame, candidate_columns: List[str]=None) -> List[str]:
    """
    전달받은 컬럼에 대해 자동으로 차트를 생성.
    - candidate_columns 가 None이면 수치형 컬럼 상위 3개 선택
    """
    if candidate_columns is None:
        num_cols = df.select_dtypes(include="number").columns.tolist()
        candidate_columns = num_cols[:3]

    saved = []
    for col in candidate_columns:
        try:
            fig, ax = plt.subplots(figsize=(8,4))
            if pd.api.types.is_datetime64_any_dtype(df.index):
                df[col].plot(ax=ax)
            else:
                # x축이 명시적 시간형이 아닌 경우 인덱스를 사용
                df[col].reset_index(drop=True).plot(ax=ax)
            ax.set_title(f"{col} Trend")
            ax.set_xlabel("index")
            ax.set_ylabel(col)
            fname = f"{uuid.uuid4().hex}_{col}.png"
            path = os.path.join(OUT_DIR, fname)
            fig.tight_layout()
            fig.savefig(path)
            plt.close(fig)
            saved.append(path)
        except Exception as e:
            print("chart error", col, e)
    return saved

def save_markdown_report(md_content: str, out_name: str=None) -> str:
    out_name = out_name or f"report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.md"
    out_path = os.path.join(OUT_DIR, out_name)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    return out_path







def load_yaml_prompt(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
    
def get_genai_client():
    #api_key = os.getenv("GEMINI_API_KEY")
    api_key ="AIzaSyBBjLYmk0uCNebCvHl_C1zjuhjYpzY_BIg"
    if not api_key:
        raise ValueError("GEMINI_API_KEY 환경 변수가 설정되지 않았습니다.")

    return Client(api_key=api_key)
genai_client = get_genai_client()