from langgraph.graph import StateGraph
from schemas.state_schema import GraphState
from agents.rq_agent import rq_agent_node

def build_graph():
    graph = StateGraph(GraphState)

    graph.add_node("rq_agent", rq_agent_node)
    #graph.add_node("analysis_agent", analysis_agent_node)
    #graph.add_node("report_agent", report_agent_node)

    graph.set_entry_point("rq_agent")
    #graph.add_edge("rq_agent", "analysis_agent")
    #graph.add_edge("analysis_agent", "report_agent")

    return graph.compile()
