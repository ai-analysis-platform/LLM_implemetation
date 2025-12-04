from langgraph.graph import StateGraph
from typing import TypedDict, List, Optional
from .tools import create_pandas_tool,read_data_from_csv, simple_clean, generate_eda, generate_time_series_charts, save_markdown_report
from .agents import create_dataframe_agent, create_python_repl_tool
import pandas as pd
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
import os

BASE_DIR = os.path.dirname(__file__)
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

class ReportState(TypedDict):
    user_query: str
    csv_path: str
    df: Optional[pd.DataFrame]
    eda_summary: str
    charts: List[str]
    insights: str
    report_md: str
    report_path: str

def node_load_csv(state: ReportState):
    path = state.get("csv_path")
    df = read_data_from_csv(path)
    state["df"] = df
    return state

def node_clean(state: ReportState):
    df = state["df"]
    df = simple_clean(df)
    state["df"] = df
    return state

def node_eda(state: ReportState):
    df = state["df"]
    state["eda_summary"] = generate_eda(df)
    return state

def node_charts(state: ReportState):
    df = state["df"]
    charts = generate_time_series_charts(df)
    state["charts"] = charts
    return state

def node_insight_via_agent(state: ReportState):
    """
    간단한 패턴: Pandas agent에게 eda+차트에 대해 인사이트 생성 요구
    """
    df = state["df"]
    # LangChain pandas agent를 사용해서 요약/인사이트를 얻도록 시도
    try:
        agent = create_pandas_tool(df, verbose=False)
        prompt = f"데이터셋에 대한 간단한 인사이트(핵심 5개 항목)와 추천 조치 3가지를 한국어로 작성해줘.\n그리고 생성된 차트 파일개수는 {len(state.get('charts',[]))}개 입니다."
        res = agent.run(prompt)
    except Exception as e:
        print("agent failed:", e)
        # fallback: 단순 통계 기반 요약
        res = "자동 인사이트 생성에 실패했습니다. EDA 요약을 확인해 주세요."
    state["insights"] = res
    return state

def node_compose_report(state: ReportState):
    tpl = env.get_template("report.md.j2")
    md = tpl.render(
        title="자동 생성 비즈니스 리포트",
        generated_at=datetime.utcnow().isoformat(),
        user_query=state["user_query"],
        eda_summary=state["eda_summary"],
        insights=state["insights"],
        charts=[os.path.relpath(c) for c in state["charts"]],
        recommendations="(LLM 권장사항을 여기에 삽입)"
    )
    state["report_md"] = md
    rp = save_markdown_report(md)
    state["report_path"] = rp
    return state

def build_workflow():
    graph = StateGraph(ReportState)
    graph.add_node("load_csv", node_load_csv)
    graph.add_node("clean", node_clean)
    graph.add_node("eda", node_eda)
    graph.add_node("charts", node_charts)
    graph.add_node("insight", node_insight_via_agent)
    graph.add_node("compose", node_compose_report)
    graph.set_entry_point("load_csv")

    graph.add_edge("load_csv", "clean")
    graph.add_edge("clean", "eda")
    graph.add_edge("eda", "charts")
    graph.add_edge("charts", "insight")
    graph.add_edge("insight", "compose")

    app = graph.compile()
    return app