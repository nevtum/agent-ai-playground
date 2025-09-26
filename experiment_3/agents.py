import json
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

    def __init__(self, model: str = MODEL) -> None:
        self.model = model

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

    def get_all_details(self, url: str):
        result = []
        site = Website(url)
        result.append((site.url, site.get_contents()))

        links = self.get_relevant_links(site)
        print(f"{site.url} found links: {links}")
        for link in links["links"]:
            link_site = Website(link["url"])
            result.append((link_site.url, link_site.get_contents()))

        text = "\n".join(
            [f"**URL**: {url}\n**CONTENT**: {content}" for url, content in result]
        )
        return text


class CompanyResearchAgent:
    system_prompt = dedent("""
    You are an assistant that analyzes the contents of several relevant pages from a company website \
    and creates a short brochure about the company for prospective customers, investors and recruits. Respond in markdown.\
    Include details of company culture, customers and careers/jobs if you have the information.
    """)

    def __init__(self, crawler_agent: CrawlerAgent, model: str = MODEL):
        self.crawler_agent = crawler_agent
        self.model = model

    def create_brochure(self, company_name: str, url: str):
        response = openai_client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {
                    "role": "user",
                    "content": self._get_brochure_user_prompt(company_name, url),
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


def main1():
    crawler_agent = CrawlerAgent()
    details = crawler_agent.get_all_details("https://www.hellofresh.com.au")
    print(details)


def main2():
    company_name = "HelloFresh"
    url = "https://www.hellofresh.com.au"
    crawler_agent = CrawlerAgent()
    brochure_agent = CompanyResearchAgent(crawler_agent)
    res = brochure_agent.create_brochure(company_name, url)
    print(res)


if __name__ == "__main__":
    main2()
