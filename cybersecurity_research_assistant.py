from typing import TypedDict

from langgraph.graph import START, END, StateGraph
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI

from agents.vulnerability_agent import vulnerability_agent
from agents.ransomware_agent import ransomware_agent
from agents.cyber_security_event_agent import cyber_security_event_agent
from agents.cisa_agent import cisa_agent

### LLM
llm = ChatOpenAI(model="gpt-4o", temperature=0)

### Schema


class ResearchGraphState(TypedDict):
    month: str
    year: str
    vulnerability_summary: str
    ransomware_summary: str
    cyber_security_events_summary: str
    cisa_summary: str
    executive_summary: str  # Introduction for the final report
    content: str  # Content for the final report
    conclusion: str  # Conclusion for the final report
    final_report: str  # Final report


class ReportWriter:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0)
        self.report_writer_instructions = """You are a technical writer creating a report on this overall topic: 

        {topic}
            
        Your task: 

        1. You will be given a collection of memos.
        2. Think carefully about the insights from each memo.
        3. Consolidate these into a crisp overall Executive summary that ties together the central ideas from all of the memos. 
        4. Summarize the central points in each memo into a cohesive single narrative.

        Add following sections and following section specific instructions:
            Executive Summary:
                Objective: Summarize the major events of the reporting period with a focus on critical vulnerabilities, key ransomware activities, and targeted sectors
                Details:
                    - Write an executive summary that highlights the key cybersecurity events of {month}, focusing on the rise of critical vulnerabilities, notable ransomware attacks, and which sectors were most targeted. Include the number of vulnerabilities added to the CISA KEV list and name specific software or platforms that faced the most significant threats.
            
            Vulnerability Breakdown Table:
                Objective: Present a table that lists the critical vulnerabilities detected during the reporting period, their severity, associated software, and the extent of exploitation
                Details:
                    - Create a detailed table listing the most critical vulnerabilities discovered in {month}. For each vulnerability, include its CVE ID, the affected product, the severity (High, Medium, or Critical), a brief description, whether it's a zero-day exploit, if it's actively exploited, and whether malware has abused the vulnerability.
            
            Ransomware Insights:
                Objective: Provide a summary of ransomware activity for the period, detailing the number of affected organizations, targeted industries, and the vulnerabilities that were most commonly abused
                Details:
                    - Generate a summary of ransomware insights for {month}, identifying the key ransomware groups active during the period, their methods of attack, the number of organizations affected, the industries targeted, and the specific vulnerabilities they exploited. Include a brief description of each ransomware group's tactics and targets.

            Key Vulnerabilities Exploited by Malware:
                Objective: Focus on the vulnerabilities that were actively abused by malware during the reporting period
                Details:
                    - List the most critical vulnerabilities that were actively exploited by malware during {month}. For each vulnerability, provide the CVE ID, a brief description, the type of malware exploiting it, and whether it has been added to the CISA Known Exploited Vulnerabilities (KEV) list.
            
            Botnet Activity:
                Objective: Analyze the impact and activity of botnets during the reporting period, focusing on their targets and methods
                Details:
                    - Analyze the activity of significant botnets for {month}, with an emphasis on their targets and the methods used to exploit vulnerabilities. Mention specific botnets, such as Mirai, and highlight the devices or software they targeted (e.g., routers, IoT devices).

            Conclusion & Recommendations:
                Objective: Provide a conclusion summarizing the cybersecurity landscape for the month, offering general recommendations for organizations
                Details:
                    - Summarize the overall cybersecurity landscape for {month}, emphasizing the major threats posed by newly discovered vulnerabilities and active ransomware campaigns. Provide general recommendations for organizations on how to strengthen their defenses, focusing on patch management, vulnerability scanning, and network security.

        To format your report:
         
        1. Use markdown formatting. 
        2. Include no pre-amble for the report.
        3. Use no sub-heading. 
        4. Start your report with a single title header: ## Insights
        5. Preserve any citations in the memos, which will be annotated in brackets, for example [1] or [2].
        6. Create a final, consolidated list of sources and add to a Sources section with the `## Sources` header.
        7. List your sources in order and do not repeat.
        8. Use markdown table in sections that had been specified create tables

        [1] Source 1
        [2] Source 2

        Here are the memos to build your report from: 

        {context}"""

    def write_report(self, state: ResearchGraphState):
        """Node to write the final report body"""
        vulnerability_summary = state["vulnerability_summary"]
        ransomware_summary = state["ransomware_summary"]
        cyber_security_events_summary = state["cyber_security_events_summary"]
        cisa_summary = state["cisa_summary"]

        topic = "Threat and Vulnerabilities"
        formatted_str_sections = "\n\n".join(
            [
                vulnerability_summary,
                ransomware_summary,
                cyber_security_events_summary,
                cisa_summary,
            ]
        )
        system_message = self.report_writer_instructions.format(
            topic=topic, context=formatted_str_sections, month=state["month"]
        )
        report = self.llm.invoke(
            [SystemMessage(content=system_message)]
            + [HumanMessage(content="Write a report based upon these memos.")]
        )
        return {"content": report.content}


class ExecutiveSummaryOrConclusionWriter:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0)
        self.instructions = """You are a technical writer finishing a report on {topic}

        You will be given all of the sections of the report.

        You job is to write a crisp and compelling Executive summary or conclusion section.

        The user will instruct you whether to write the Executive summary or conclusion.

        Include no pre-amble for either section.

        Target around 300 words, crisply previewing (for Executive summary) or recapping (for conclusion) all of the sections of the report.

        Use markdown formatting. 

        For your Executive summary, create a compelling title and use the # header for the title.

        For your Executive summary, use ## Executive Summary as the section header. 

        For your conclusion, use ## Conclusion as the section header.

        Here are the sections to reflect on for writing: {formatted_str_sections}"""

    def write_executive_summary(self, state: ResearchGraphState):
        """Node to write the executive introduction"""
        vulnerability_summary = state["vulnerability_summary"]
        ransomware_summary = state["ransomware_summary"]
        cyber_security_events_summary = state["cyber_security_events_summary"]
        cisa_summary = state["cisa_summary"]

        topic = "Threat and Vulnerabilities"
        formatted_str_sections = "\n\n".join(
            [
                vulnerability_summary,
                ransomware_summary,
                cyber_security_events_summary,
                cisa_summary,
            ]
        )
        instructions = self.instructions.format(
            topic=topic, formatted_str_sections=formatted_str_sections
        )
        intro = self.llm.invoke(
            [instructions] + [HumanMessage(content="Write the report introduction")]
        )
        return {"executive_summary": intro.content}

    def write_conclusion(self, state: ResearchGraphState):
        """Node to write the conclusion"""
        vulnerability_summary = state["vulnerability_summary"]
        ransomware_summary = state["ransomware_summary"]
        cyber_security_events_summary = state["cyber_security_events_summary"]
        cisa_summary = state["cisa_summary"]

        topic = "Threat and Vulnerabilities"
        formatted_str_sections = "\n\n".join(
            [
                vulnerability_summary,
                ransomware_summary,
                cyber_security_events_summary,
                cisa_summary,
            ]
        )
        instructions = self.instructions.format(
            topic=topic, formatted_str_sections=formatted_str_sections
        )
        conclusion = self.llm.invoke(
            [instructions] + [HumanMessage(content="Write the report conclusion")]
        )
        return {"conclusion": conclusion.content}


class ReportFinalizer:
    def finalize_report(self, state: ResearchGraphState):
        """The is the "reduce" step where we gather all the sections, combine them, and reflect on them to write the intro/conclusion"""
        content = state["content"]
        if content.startswith("## Insights"):
            content = content.strip("## Insights")
        if "## Sources" in content:
            try:
                content, sources = content.split("\n## Sources\n")
            except Exception:  # Specify the exception type
                sources = None
        else:
            sources = None

        final_report = (
            state["executive_summary"]
            + "\n\n---\n\n"
            + content
            + "\n\n---\n\n"
            + state["conclusion"]
        )
        if sources is not None:
            final_report += "\n\n## Sources\n" + sources
        return {"final_report": final_report}


class ResearchGraphBuilder:
    def __init__(self):
        self.builder = StateGraph(ResearchGraphState)
        self._add_nodes()
        self._add_edges()

    def _add_nodes(self):
        self.builder.add_node("vulnerability_agent", vulnerability_agent)
        self.builder.add_node("ransomware_agent", ransomware_agent)
        self.builder.add_node("cyber_security_event_agent", cyber_security_event_agent)
        self.builder.add_node("cisa_agent", cisa_agent)

        report_writer = ReportWriter()
        executive_summary_or_conclusion_writer = ExecutiveSummaryOrConclusionWriter()
        report_finalizer = ReportFinalizer()

        self.builder.add_node("write_report", report_writer.write_report)
        self.builder.add_node(
            "write_executive_summary",
            executive_summary_or_conclusion_writer.write_executive_summary,
        )
        self.builder.add_node(
            "write_conclusion", executive_summary_or_conclusion_writer.write_conclusion
        )
        self.builder.add_node("finalize_report", report_finalizer.finalize_report)

    def _add_edges(self):
        self.builder.add_edge(START, "vulnerability_agent")
        self.builder.add_edge(START, "ransomware_agent")
        self.builder.add_edge(START, "cyber_security_event_agent")
        self.builder.add_edge(START, "cisa_agent")
        self.builder.add_edge(
            [
                "vulnerability_agent",
                "ransomware_agent",
                "cyber_security_event_agent",
                "cisa_agent",
            ],
            "write_report",
        )
        self.builder.add_edge("write_report", "write_executive_summary")
        self.builder.add_edge("write_report", "write_conclusion")
        self.builder.add_edge(
            ["write_conclusion", "write_report", "write_executive_summary"],
            "finalize_report",
        )
        self.builder.add_edge("finalize_report", END)

    def compile(self):
        return self.builder.compile()


# Instantiate and compile the graph
graph_builder = ResearchGraphBuilder()
graph = graph_builder.compile()
