from typing import TypedDict
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END, START

from utils.utils import write_section
from utils.tools import WebTool

llm = ChatOpenAI(model="gpt-4o", temperature=0)


class RansomwareState(TypedDict):
    month: str
    year: str
    active_groups: str
    ttps: str
    vulnerabilities: str
    raas_insights: str
    ransomware_summary: str


class RansomwareOutputState(TypedDict):
    ransomware_summary: str


class RansomwareAgent:
    def __init__(self):
        self.graph = StateGraph(RansomwareState, output=RansomwareOutputState)
        self._setup_graph()
        self.web_tool = WebTool()

    def _setup_graph(self):
        self.graph.add_node("gather_active_groups", self.gather_active_groups)
        self.graph.add_node("identify_ttps", self.identify_ttps)
        self.graph.add_node(
            "find_exploited_vulnerabilities", self.find_exploited_vulnerabilities
        )
        self.graph.add_node("provide_raas_insights", self.provide_raas_insights)
        self.graph.add_node("summarize", self.summarize)

        self.graph.add_edge(START, "gather_active_groups")
        self.graph.add_edge("gather_active_groups", "summarize")

        self.graph.add_edge(START, "identify_ttps")
        self.graph.add_edge("identify_ttps", "summarize")

        self.graph.add_edge(START, "find_exploited_vulnerabilities")
        self.graph.add_edge("find_exploited_vulnerabilities", "summarize")

        self.graph.add_edge(START, "provide_raas_insights")
        self.graph.add_edge("provide_raas_insights", "summarize")

        self.graph.add_edge("summarize", END)

    def gather_active_groups(self, state: RansomwareState) -> RansomwareState:
        query = f"""Most active ransomware groups in the month {state['month']} {state['year']}, 
        targeted sectors (healthcare, finance, education), and recent ransomware attack trends
        """
        result = self.web_tool.search_web(query)
        return {"active_groups": result}

    def identify_ttps(self, state: RansomwareState) -> RansomwareState:
        query = f"""Common TTPs used by ransomware groups in the month {state['month']} {state['year']}, 
        methods for gaining initial access, exploitation of vulnerabilities, phishing, and social engineering techniques
        """
        result = self.web_tool.search_web(query)
        return {"ttps": result}

    def find_exploited_vulnerabilities(self, state: RansomwareState) -> RansomwareState:
        query = f"Vulnerabilities frequently abused by ransomware groups, specific software or systems targeted, and techniques for exploiting them in the month {state['month']} {state['year']}"
        result = self.web_tool.search_web(query)
        return {"vulnerabilities": result}

    def provide_raas_insights(self, state: RansomwareState) -> RansomwareState:
        query = f"Overview of the Ransomware-as-a-Service (RaaS) model, role in recent ransomware attacks, and contribution to the rise in ransomware incidents in the month {state['month']} {state['year']}"
        result = self.web_tool.search_web(query)
        return {"raas_insights": result}

    def summarize(self, state: RansomwareState) -> RansomwareOutputState:
        context = "\n".join(
            [
                state["active_groups"],
                state["ttps"],
                state["vulnerabilities"],
                state["raas_insights"],
            ]
        )
        summarized_text = write_section(llm, context, focus="Ransomware Threat")
        return {"ransomware_summary": summarized_text}


# Instantiate and compile the graph
ransomware_agent = RansomwareAgent().graph.compile()
