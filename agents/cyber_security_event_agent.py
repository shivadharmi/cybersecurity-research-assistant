from typing import TypedDict
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END, START

from utils.utils import write_section
from utils.tools import WebTool

llm = ChatOpenAI(model="gpt-4o", temperature=0)


class CyberSecurityEventState(TypedDict):
    month: str
    year: str
    industry_specific_attacks: str
    emerging_trends: str
    botnet_malware_activity: str
    cyber_security_events_summary: str


class CyberSecurityEventOutputState(TypedDict):
    cyber_security_events_summary: str


class CyberSecurityEventAgent:
    def __init__(self):
        self.graph = StateGraph(
            CyberSecurityEventState, output=CyberSecurityEventOutputState
        )
        self._setup_graph()
        self.web_tool = WebTool()

    def _setup_graph(self):
        self.graph.add_node(
            "gather_industry_specific_attacks", self.gather_industry_specific_attacks
        )
        self.graph.add_node("identify_emerging_trends", self.identify_emerging_trends)
        self.graph.add_node(
            "find_botnet_malware_activity", self.find_botnet_malware_activity
        )
        self.graph.add_node("summarize", self.summarize)

        self.graph.add_edge(START, "gather_industry_specific_attacks")
        self.graph.add_edge("gather_industry_specific_attacks", "summarize")

        self.graph.add_edge(START, "identify_emerging_trends")
        self.graph.add_edge("identify_emerging_trends", "summarize")

        self.graph.add_edge(START, "find_botnet_malware_activity")
        self.graph.add_edge("find_botnet_malware_activity", "summarize")

        self.graph.add_edge("summarize", END)

    def gather_industry_specific_attacks(
        self, state: CyberSecurityEventState
    ) -> CyberSecurityEventState:
        query = f"""Cyberattacks targeting specific industries like healthcare, finance, education, and government in {state['month']} {state['year']}, including the techniques and vulnerabilities exploited."""
        result = self.web_tool.search_web(query)
        return {"industry_specific_attacks": result}

    def identify_emerging_trends(
        self, state: CyberSecurityEventState
    ) -> CyberSecurityEventState:
        query = f"""Emerging cybersecurity trends and threats in {state['month']} {state['year']}, including new attack vectors, techniques used by attackers, and vulnerabilities being exploited."""
        result = self.web_tool.search_web(query)
        return {"emerging_trends": result}

    def find_botnet_malware_activity(
        self, state: CyberSecurityEventState
    ) -> CyberSecurityEventState:
        query = f"""Recent botnet or malware campaigns targeting critical systems or network infrastructure in {state['month']} {state['year']}, including details on affected systems and methods of compromise."""
        result = self.web_tool.search_web(query)
        return {"botnet_malware_activity": result}

    def summarize(
        self, state: CyberSecurityEventState
    ) -> CyberSecurityEventOutputState:
        context = "\n".join(
            [
                state["industry_specific_attacks"],
                state["emerging_trends"],
                state["botnet_malware_activity"],
            ]
        )
        summarized_text = write_section(llm, context, focus="Cyber Security Events")
        return {"cyber_security_events_summary": summarized_text}

    def compile(self):
        return self.graph.compile()


cyber_security_event_agent = CyberSecurityEventAgent().compile()
