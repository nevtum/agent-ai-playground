import json
from collections import deque
from os import getenv
from textwrap import dedent

from dotenv import load_dotenv
from openai import OpenAI

from .website import Website

_ = load_dotenv()

MODEL = "gpt-4o-mini"

openai_client = OpenAI(api_key=getenv("OPENAI_API_KEY"))


class CrawlerAgent:
    system_prompt = dedent("""You are provided with a list of links found on a webpage.
    You are able to decide which of the links would be most relevant to include in market research about the company,
    such as links to an About page, News/Events, a Company page, or Careers/Jobs pages.
    You should respond in JSON as in this example:
    {
        "links": [
            {"type": "about page", "url": "https://full.url/goes/here/about"},
            {"type": "careers page", "url": "https://another.full.url/careers"}
        ]
    }
    """)

    def __init__(self, *, model: str = MODEL, max_hops: int = 1) -> None:
        self.model = model
        self.max_hops = max_hops

    def get_relevant_links(self, website: Website) -> list[dict[str, str]]:
        response = openai_client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": self._get_links_user_prompt(website)},
            ],
            response_format={"type": "json_object"},
        )
        result = response.choices[0].message.content
        return json.loads(result)

    def _get_links_user_prompt(self, website: Website) -> str:
        user_prompt = f"""Here is the list of links on the website of {website.url} -
        please decide which of these are relevant web links for a brochure about the company, respond with the full https URL in JSON format.
        Do not include Terms of Service, Privacy, email links.

        Links (some might be relative links):
        {"\n".join(map(str, website.links))}"""
        return dedent(user_prompt)

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
                    if link["url"] not in visited:
                        print(f"Adding {link['url']} to queue. Distance={distance + 1}")
                        queue.append((distance + 1, Website(link["type"], link["url"])))

            visited.add(site.url)

        print(f"A total of {len(result)} pages were crawled. Visited={visited}")
        return result

    def get_all_details(self, url: str):
        result = self.crawl_pages(url)

        text = "\n".join(
            [f"**URL**: {url}\n**CONTENT**: {content}" for url, content in result]
        )
        return text


class PageSummarizerAgent:
    system_prompt = dedent("""You are an assistant that analyzes the contents of a website \
    and provides a short summary, ignoring text that might be navigation related. \
    Respond in markdown.
    """)

    def __init__(self, model: str = MODEL) -> None:
        self.model = MODEL

    def summarize(self, page_name: str, content: str):
        print(f"Summarizing content for {page_name}")
        response = openai_client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {
                    "role": "user",
                    "content": self._user_prompt(page_name, content),
                },
            ],
        )
        result = response.choices[0].message.content
        return result

    def _user_prompt(self, page_name: str, content: str) -> str:
        prompt = f"""
        You are looking at a page '{page_name}'. \
        The contents from this page is as follows;
        {content} \n\n
        please summarize this page in markdown. \
        If it includes news or announcements, then summarize these too.\n\n

        You should respond with the results like this example:
        ===
        # Page: {page_name}
        # Content:
        summary goes here...
        """
        return dedent(prompt)


class CompanyResearchAgent:
    system_prompt = dedent("""
    You are an assistant that analyzes the contents of several relevant pages from a company website \
    and creates a short brochure about the company for prospective customers, investors and recruits. Respond in markdown.\
    Include details of company culture, customers and careers/jobs if you have the information.
    """)

    def __init__(self, *, crawler_agent: CrawlerAgent, model: str = MODEL):
        self.summarizer = PageSummarizerAgent()
        self.crawler_agent = crawler_agent
        self.model = model

    def create_brochure(self, company_name: str, url: str):
        response = openai_client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
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

        user_prompt = dedent(f"""You are looking at a company called: {company_name} \
        Here are the contents of its landing page and other relevant pages; \
        use this information to build a short brochure of the company in markdown.
        {summary}""")
        return user_prompt


def main1():
    crawler_agent = CrawlerAgent()
    details = crawler_agent.get_all_details("https://www.hellofresh.com.au")
    print(details)


def main2():
    crawler_agent = CrawlerAgent(max_hops=0)
    result = crawler_agent.crawl_pages("https://www.hellofresh.com.au")
    summarizer = PageSummarizerAgent()
    details = summarizer.summarize(result[0][0], result[0][1])
    print(details)


def main3():
    company_name = "HelloFresh"
    url = "https://www.hellofresh.com.au"
    crawler_agent = CrawlerAgent(max_hops=2)
    brochure_agent = CompanyResearchAgent(crawler_agent=crawler_agent)
    res = brochure_agent.create_brochure(company_name, url)
    print(res)


if __name__ == "__main__":
    main3()
