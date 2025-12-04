from graph.graph_builder import build_graph

graph = build_graph()

initial_state = {
    "input_data": {
        "companyName": "삼성전자",
        "csvData": "...",
        "reportTemplate": "",
        "reportingPeriod": "2025-Q3",
        "industry": "Manufacturing",
        "additionalRequests": "요즘 실적이 왜 이렇게 나빠?",
        "report_type": "Financial Snapshot Report"
    },
    "research_questions": [],
    "analysis_results": {},
    "final_report": ""
}

if __name__ == "__main__":
    result = graph.invoke(initial_state)
    print(result)