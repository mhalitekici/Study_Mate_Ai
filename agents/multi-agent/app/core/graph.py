from langgraph.graph import StateGraph, END
from app.core.state import AgentState
from app.agents.planner_agent import planner_agent
from app.agents.retrieval_agent import retrieval_agent
from app.agents.tutor_agent import tutor_agent
from app.agents.critic_agent import critic_agent

def should_retry(state: AgentState) -> str:
    if state.get("needs_retry", False):
        print("[Graph] Low quality answer, retrying...")
        return "retry"
    return "done"

def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("planner", planner_agent)
    graph.add_node("retrieval", retrieval_agent)
    graph.add_node("tutor", tutor_agent)
    graph.add_node("critic", critic_agent)

    graph.set_entry_point("planner")
    graph.add_edge("planner", "retrieval")
    graph.add_edge("retrieval", "tutor")
    graph.add_edge("tutor", "critic")

    graph.add_conditional_edges(
        "critic",
        should_retry,
        {
            "retry": "tutor",
            "done": END
        }
    )

    return graph.compile()

agent_graph = build_graph()