import argparse
from agents.vulnerability_agent import vulnerability_agent
from agents.ransomware_agent import ransomware_agent
from agents.cyber_security_event_agent import cyber_security_event_agent
from agents.cisa_agent import cisa_agent
from cybersecurity_research_assistant import graph

parser = argparse.ArgumentParser(description="Run cybersecurity research agents")
parser.add_argument(
    "agent",
    choices=["vulnerability", "ransomware", "events", "cisa", "full"],
    help="Which agent to run",
)
parser.add_argument("--month", default="September", help="Month to analyze")
parser.add_argument("--year", default="2024", help="Year to analyze")
args = parser.parse_args()

if args.agent == "vulnerability":
    response = vulnerability_agent.invoke(
        {
            "month": args.month,
            "year": args.year,
            "critical_vulnerabilities": "",
            "software_vulnerabilities": "",
            "network_device_vulnerabilities": "",
            "zero_day_vulnerabilities": "",
            "vulnerability_summary": "",
        }
    )
    print(response["vulnerability_summary"])

elif args.agent == "ransomware":
    response = ransomware_agent.invoke(
        {
            "month": args.month,
            "year": args.year,
            "active_groups": "",
            "ttps": "",
            "vulnerabilities": "",
            "raas_insights": "",
            "ransomware_summary": "",
        }
    )
    print(response["ransomware_summary"])

elif args.agent == "events":
    response = cyber_security_event_agent.invoke(
        {
            "month": args.month,
            "year": args.year,
            "industry_specific_attacks": "",
            "emerging_trends": "",
            "botnet_malware_activity": "",
            "cyber_security_events_summary": "",
        }
    )
    print(response["cyber_security_events_summary"])

elif args.agent == "cisa":
    response = cisa_agent.invoke({"cisa_summary": ""})
    print(response["cisa_summary"])

else:  # full report
    response = graph.invoke(
        {
            "month": args.month,
            "year": args.year,
            "vulnerability_summary": "",
            "ransomware_summary": "",
            "cyber_security_events_summary": "",
            "cisa_summary": "",
            "introduction": "",  # Introduction for the final report
            "content": "",  # Content for the final report
            "conclusion": "",  # Conclusion for the final report
            "final_report": "",  # Final report
        }
    )
    print(response["final_report"])
