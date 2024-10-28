import requests
from bs4 import BeautifulSoup
from datetime import datetime
import logging
import time
import json
import os


class CisaScraper:
    def __init__(self, month: int, year: int):
        # Set up logging configuration
        self.logger = logging.getLogger()
        self.base_url = "https://www.cisa.gov"
        self.current_month = month
        self.current_year = year
        self.advisory_list = []

    def scrape_page(self, url, page_number):
        try:
            self.logger.info(f"Scraping page: {url}")
            response = requests.get(url, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            self.logger.error(f"Request failed for {url}: {e}")
            return None

        soup = BeautifulSoup(response.content, "html.parser")
        advisories = soup.find_all(
            "article", class_="is-promoted c-teaser c-teaser--horizontal"
        )

        if not advisories:
            self.logger.warning(f"No advisories found on page: {url}")

        for advisory in advisories:
            try:
                date_str = advisory.find("time")[
                    "datetime"
                ]  # Example: "2024-10-17T12:00:00Z"
                advisory_date = datetime.fromisoformat(
                    date_str.replace("Z", "")
                )  # Convert ISO datetime to Python datetime object

                if (
                    advisory_date.year == self.current_year
                    and advisory_date.month == self.current_month
                ):
                    title = advisory.find("h3", class_="c-teaser__title").get_text(
                        strip=True
                    )
                    link = advisory.find("a")["href"]
                    full_link = f"{self.base_url}{link}"

                    self.advisory_list.append(
                        {
                            "title": title,
                            "date": advisory_date.strftime("%Y-%m-%d"),
                            "page_number": page_number,
                            "link": full_link,
                        }
                    )

                    self.logger.info(
                        f"Advisory found: {title} ({advisory_date.strftime('%Y-%m-%d')}) - {full_link}"
                    )
                else:
                    self.logger.info(
                        f"Encountered an advisory from a previous month ({advisory_date.strftime('%Y-%m-%d')}). Skipping."
                    )
            except (AttributeError, TypeError) as e:
                self.logger.error(f"Error extracting advisory details: {e}")

        next_page_link = soup.find("a", class_="c-pager__link c-pager__link--next")
        if next_page_link:
            next_page_url = self.base_url + next_page_link["href"]
            self.logger.debug(f"Next page URL found: {next_page_url}")
            return next_page_url
        else:
            self.logger.info("No more pages to scrape.")
            return None

    def scrape_advisories(self):
        initial_page_url = f"{self.base_url}/news-events/cybersecurity-advisories"
        current_page_url = initial_page_url
        page_number = 1

        while current_page_url:
            current_page_url = self.scrape_page(current_page_url, page_number)
            page_number += 1
            time.sleep(1)  # Rate limiting to avoid overwhelming the server

        self.logger.info("Scraping completed.")

    def load_or_scrape_advisories(self):
        if (
            os.path.exists("../data/advisories.json")
            and os.path.getsize("advisories.json") > 0
        ):
            self.logger.info("Loading existing advisories from JSON file.")
            with open("advisories.json", "r") as json_file:
                self.advisory_list = json.load(json_file)
        else:
            self.scrape_advisories()

    def get_advisory_content(self, advisory):
        try:
            self.logger.info(f"Fetching content for advisory: {advisory['title']}")
            response = requests.get(advisory["link"], timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")
            header_tag = soup.find("h1", class_="c-page-title__title")
            main_content_tag = soup.find("div", class_="l-full__main")

            header = (
                header_tag.get_text(strip=True)
                if header_tag
                else "Header not available"
            )
            main_content = (
                main_content_tag.get_text(strip=True)
                if main_content_tag
                else "Main content not available"
            )

            advisory["content"] = {"header": header, "main": main_content}
            self.logger.info(
                f"Successfully fetched content for advisory: {advisory['title']}"
            )
        except requests.RequestException as e:
            self.logger.error(f"Request failed for {advisory['link']}: {e}")
            advisory["content"] = "Content not available"
        except AttributeError as e:
            self.logger.error(f"Error extracting content for {advisory['link']}: {e}")
            advisory["content"] = "Content not available"

    def fetch_all_advisory_content(self):
        for advisory in self.advisory_list:
            self.get_advisory_content(advisory)
            time.sleep(1)  # Rate limiting to avoid overwhelming the server

    def save_advisories_to_file(self):
        with open("advisories.json", "w") as json_file:
            json.dump(self.advisory_list, json_file, indent=4)

    def print_advisories(self):
        for advisory in self.advisory_list:
            print(advisory)


if __name__ == "__main__":
    scraper = CisaScraper(9, 2024)
    scraper.fetch_all_advisory_content()
    scraper.save_advisories_to_file()
    scraper.print_advisories()
