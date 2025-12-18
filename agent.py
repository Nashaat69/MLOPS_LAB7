from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from state import AgentState
from nodes import supervisor_node, researcher_node, analyzer_node, remediator_node

# 1. Build the Graph
workflow = StateGraph(AgentState)

workflow.add_node("Supervisor", supervisor_node)
workflow.add_node("Researcher", researcher_node)
workflow.add_node("Analyzer", analyzer_node)
workflow.add_node("Remediator", remediator_node)

workflow.add_edge("Researcher", "Supervisor")
workflow.add_edge("Analyzer", "Supervisor")
workflow.add_edge("Remediator", "Supervisor")

workflow.add_conditional_edges(
    "Supervisor",
    lambda x: x["next_step"],
    {
        "Researcher": "Researcher",
        "Analyzer": "Analyzer",
        "Remediator": "Remediator",
        "FINISH": END,
    }
)

workflow.add_edge(START, "Supervisor")

# 2. Compile with Memory & Interrupt
checkpointer = MemorySaver()
graph = workflow.compile(
    checkpointer=checkpointer,
    interrupt_before=["Remediator"], # Pause to review analysis before recommending fixes
)

# 3. Execution Loop
if __name__ == "__main__":
    print("--- 🛡️ Threat Intel Swarm (Researcher -> Analyzer -> [PAUSE] -> Remediator) ---")
    
    user_input = input("\nEnter a vulnerability or CVE (e.g., 'CVE-2021-44228 Log4j'): ")
    config = {"configurable": {"thread_id": "security_audit_01"}}
    current_input = {"messages": [HumanMessage(content=user_input)]}
    
    while True:
        try:
            events = graph.stream(current_input, config=config, stream_mode="values")
            for event in events:
                if "messages" in event and event["messages"]:
                    last_msg = event["messages"][-1]
                    if last_msg.name == "Analyzer":
                        print(f"\n\033[91m[Threat Analysis]:\033[0m\n{event.get('threat_analysis')}")

            snapshot = graph.get_state(config)
            if snapshot.next:
                print(f"\n---- ⏸️  Interrupt: Review required before Remediation ----")
                approve = input("Analysis complete. Generate remediation plan? (yes/no): ")
                
                if approve.lower() == "yes":
                    current_input = None 
                else:
                    break
            else:
                final_state = snapshot.values
                if final_state.get("remediation_plan"):
                    print(f"\n\033[92m[Final Remediation Plan]:\033[0m\n{final_state.get('remediation_plan')}")
                    with open("security_remediation.txt", "w") as f:
                        f.write(final_state.get('remediation_plan'))
                break
        except Exception as e:
            print(f"Error: {e}")
            break