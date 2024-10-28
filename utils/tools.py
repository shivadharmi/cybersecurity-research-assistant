from langchain_community.tools.tavily_search import TavilySearchResults
from utils.cisa_scraper import CisaScraper


class WebTool:
    def __init__(self):
        self.tavily_search = TavilySearchResults(max_results=3)

    def search_web(self, prompt: str) -> str:
        """Retrieve docs from web search based on provided prompt"""
        search_docs = self.tavily_search.invoke(prompt)
        formatted_search_docs = "\n\n---\n\n".join(
            [
                f'<Document href="{doc["url"]}"/>\n{doc["content"]}\n</Document>'
                for doc in search_docs
            ]
        )
        return formatted_search_docs


class CisaTool:
    def __init__(self):
        self.scraper = CisaScraper(9, 2024)

    def fetch_cisa_info(self) -> str:
        self.scraper.load_or_scrape_advisories()
        self.scraper.fetch_all_advisory_content()
        formatted_cisa_docs = "\n\n---\n\n".join(
            [
                f'<Document href="{doc["link"]}"/>\n{doc["content"]["main"]}\n</Document>'
                for doc in self.scraper.advisory_list
            ]
        )
        return formatted_cisa_docs
