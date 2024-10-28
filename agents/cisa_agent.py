from typing import TypedDict
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END, START

from utils.utils import write_section
from utils.tools import CisaTool

llm = ChatOpenAI(model="gpt-4o", temperature=0)


class CISAState(TypedDict):
    cisa_summary: str
    formatted_docs: str


class CISAAgent:
    def __init__(self):
        self.graph = StateGraph(CISAState)
        self._setup_graph()
        self.cisa_tool = CisaTool()

    def _setup_graph(self):
        self.graph.add_node("fetch_cisa_info", self.fetch_cisa_info)
        self.graph.add_node("summarize", self.summarize)

        self.graph.add_edge(START, "fetch_cisa_info")
        self.graph.add_edge("fetch_cisa_info", "summarize")
        self.graph.add_edge("summarize", END)

    def fetch_cisa_info(self, state: CISAState) -> CISAState:
        formatted_docs = self.cisa_tool.fetch_cisa_info()
        return {"formatted_docs": formatted_docs}

    def summarize(self, state: CISAState) -> CISAState:
        context = state["formatted_docs"]
        summarized_text = write_section(llm, context, focus="CISA Advisory summary")
        return {"cisa_summary": summarized_text}

    def compile(self):
        return self.graph.compile()


cisa_agent = CISAAgent().compile()
