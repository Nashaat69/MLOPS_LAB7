from typing import Annotated, List, TypedDict
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    messages: Annotated[List, add_messages]
    vulnerability_details: str  # Raw data from Researcher
    threat_analysis: str       # Impact assessment from Analyzer
    remediation_plan: str      # Final fix from Remediation Writer
    next_step: str             # Supervisor's routing decision