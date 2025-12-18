from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage

# Initialize models
llm = ChatOllama(model="qwen3:0.6b", temperature=0)

def supervisor_node(state):
    """Orchestrates the security workflow"""
    if not state.get("vulnerability_details"):
        return {"next_step": "Researcher"}
    
    if state.get("vulnerability_details") and not state.get("threat_analysis"):
        return {"next_step": "Analyzer"}
    
    if state.get("threat_analysis") and not state.get("remediation_plan"):
        return {"next_step": "Remediator"}
    
    return {"next_step": "FINISH"}

def researcher_node(state):
    """Agent 1: Scans/Researches the vulnerability (CVE)"""
    topic = state['messages'][0].content
    print(f"--- 🛡️ Researching Vulnerability: {topic} ---")
    
    prompt = f"Provide a technical summary of the security vulnerability: {topic}. Include CVSS score and affected versions."
    response = llm.invoke([SystemMessage(content=prompt)])
    return {
        "messages": [HumanMessage(content="Research Complete", name="Researcher")],
        "vulnerability_details": response.content
    }

def analyzer_node(state):
    """Agent 2: Performs impact and threat analysis"""
    print("--- 🔍 Analyzing Threat Impact ---")
    details = state['vulnerability_details']
    
    prompt = f"Based on these details: {details}, analyze the potential exploit scenarios and the impact on enterprise infrastructure."
    response = llm.invoke([SystemMessage(content=prompt)])
    return {
        "messages": [HumanMessage(content=response.content, name="Analyzer")],
        "threat_analysis": response.content
    }

def remediator_node(state):
    """Agent 3: Writes the final remediation/patching guide"""
    print("--- 🛠️ Generating Remediation Plan ---")
    analysis = state['threat_analysis']
    
    prompt = f"Given this threat analysis: {analysis}, write a step-by-step remediation plan including configuration changes or patching instructions."
    response = llm.invoke([SystemMessage(content=prompt)])
    return {
        "messages": [HumanMessage(content="Remediation Plan Generated", name="Remediator")],
        "remediation_plan": response.content
    }