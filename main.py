from graph.graph_builder import build_graph

graph = build_graph()

#하윤 수정해줘
initial_state = {
    "input_data": {
        "companyName": "삼성전자",
        "reportingPeriod": "2025-Q3",
        "industry": "Manufacturing",
        "internal_data_list": "1. 손익계산서(매출, 매출원가, 영업이익, 세전이익, 당기순이익 등) 분기 및 연간 (원 단위). 2. 재무상태표(유동자산, 비유동자산, 부채, 자본 등). 3. 현금흐름표(영업/투자/재무활동).",
        "additionalRequests": "요즘 실적이 왜 이렇게 나빠?",
        "report_type": "Financial Snapshot Report"
    },
    "research_questions": [], #rq agent 결과
    
    "analysis_results": {}, #
    "final_report": ""
}

if __name__ == "__main__":
    result = graph.invoke(initial_state)
    