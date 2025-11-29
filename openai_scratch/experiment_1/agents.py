import json
import re
from collections import deque
from os import getenv
from textwrap import dedent
from venv import logger

from dotenv import load_dotenv
from openai import OpenAI

from .prompts import CompanyResearch, PageSummarization, WebCrawling
from .website import Website

_ = load_dotenv()

regex = r"^(https?://)?([a-zA-Z0-9.-]+(?:\.[a-zA-Z]{2,})?)(:[0-9]+)?(/.*)?$"
MODEL = getenv("OPENAI_MODEL") or "gpt-4o-mini"

openai_client = OpenAI(api_key=getenv("OPENAI_API_KEY"))


class CrawlerAgent:
    def __init__(self, *, model: str = MODEL, max_hops: int = 1) -> None:
        self.model = model
        self.max_hops = max_hops

    def get_relevant_links(self, website: Website) -> list[dict[str, str]]:
        response = openai_client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": WebCrawling.system_prompt},
                {"role": "user", "content": WebCrawling.user_prompt(website)},
            ],
            response_format={"type": "json_object"},
        )
        result = response.choices[0].message.content
        return json.loads(result)

    def crawl_pages(self, url: str) -> list[tuple[str, str]]:
        result = []

        site = Website("Landing Page", url)
        visited = set()
        queue = deque([(0, site)])

        while queue:
            distance, site = queue.popleft()

            if site.url in visited:
                continue

            print(f"Crawling {site.url}...")
            result.append((site.url, site.get_contents()))

            if distance < self.max_hops:
                links = self.get_relevant_links(site)

                for link in links["links"]:
                    if link["url"] not in visited and self.is_valid_link(link["url"]):
                        try:
                            print(
                                f"Adding {link['url']} to queue. Distance={distance + 1}"
                            )
                            queue.append(
                                (distance + 1, Website(link["type"], link["url"]))
                            )
                        except:
                            logger.warning(f"Unable to resolve {link['url']}")
                            continue

            visited.add(site.url)

        print(f"A total of {len(result)} pages were crawled. Visited={visited}")
        return result

    def get_all_details(self, url: str):
        result = self.crawl_pages(url)

        text = "\n".join(
            [f"**URL**: {url}\n**CONTENT**: {content}" for url, content in result]
        )
        return text

    def is_valid_link(self, link: str) -> bool:
        return re.match(regex, link) is not None


class PageSummarizerAgent:
    def __init__(self, model: str = MODEL) -> None:
        self.model = MODEL

    def summarize(self, page_name: str, content: str):
        print(f"Summarizing content for {page_name}")
        response = openai_client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": PageSummarization.system_prompt},
                {
                    "role": "user",
                    "content": PageSummarization.user_prompt(page_name, content),
                },
            ],
        )
        result = response.choices[0].message.content
        return result


class CompanyResearchAgent:
    def __init__(self, *, crawler_agent: CrawlerAgent, model: str = MODEL):
        self.summarizer = PageSummarizerAgent()
        self.crawler_agent = crawler_agent
        self.model = model

    def create_brochure(self, company_name: str, url: str):
        response = openai_client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": CompanyResearch.system_prompt},
                {
                    "role": "user",
                    "content": self._get_brochure_user_prompt_v2(company_name, url),
                },
            ],
        )
        result = response.choices[0].message.content
        return result

    def _get_brochure_user_prompt(self, company_name: str, url: str):
        user_prompt = f"""You are looking at a company called: {company_name}
Here are the contents of its landing page and other relevant pages; use this information to build a short brochure of the company in markdown.
{self.crawler_agent.get_all_details(url)}"""

        user_prompt = user_prompt[:5_000]  # Truncate if more than 5,000 characters
        return dedent(user_prompt)

    def _get_brochure_user_prompt_v2(self, company_name: str, url: str):
        summary = ""

        for link, content in self.crawler_agent.crawl_pages(url):
            summary += f"{self.summarizer.summarize(link, content)}\n"

        return CompanyResearch.user_prompt(company_name, summary)
