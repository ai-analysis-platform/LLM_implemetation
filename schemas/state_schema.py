from typing import TypedDict, Dict, Any, List

class GraphState(TypedDict):
    input_data: Dict[str, Any]
    research_questions: List[Dict[str, Any]]
    analysis_results: Dict[str, Any]
    final_report: str