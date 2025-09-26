import json
from os import getenv
from textwrap import dedent

from dotenv import load_dotenv
from openai import OpenAI

from .website import Website

_ = load_dotenv()

MODEL = "gpt-4o-mini"

openai_client = OpenAI(api_key=getenv("OPENAI_API_KEY"))


class RelevantLinksAgent:
    system_prompt = dedent("""You are provided with a list of links found on a webpage.
    You are able to decide which of the links would be most relevant to include in a brochure about the company,
    such as links to an About page, or a Company page, or Careers/Jobs pages.
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

    def get_relevant_links(self, url: str) -> list[dict[str, str]]:
        website = Website(url)
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
        result = "Landing page:\n"
        result += Website(url).get_contents()
        links = self.get_relevant_links(url)
        print("Found links:", links)
        for link in links["links"]:
            result += f"\n\n{link['type']}\n"
            result += Website(link["url"]).get_contents()
        return result


class CompanyResearchAgent:
    system_prompt = dedent("""
    You are an assistant that analyzes the contents of several relevant pages from a company website \
    and creates a short brochure about the company for prospective customers, investors and recruits. Respond in markdown.\
    Include details of company culture, customers and careers/jobs if you have the information.
    """)

    def __init__(self, links_agent: RelevantLinksAgent, model: str = MODEL):
        self.links_agent = links_agent
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
{self.links_agent.get_all_details(url)}"""
        user_prompt = user_prompt[:5_000]  # Truncate if more than 5,000 characters
        return dedent(user_prompt)


if __name__ == "__main__":
    company_name = "HelloFresh"
    url = "https://www.hellofresh.com.au"
    links_agent = RelevantLinksAgent()
    brochure_agent = CompanyResearchAgent(links_agent)
    res = brochure_agent.create_brochure(company_name, url)
    print(res)
