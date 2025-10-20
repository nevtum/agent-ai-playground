from textwrap import dedent


class CrawlerPrompts:
    system = dedent("""You are provided with a list of links found on a webpage.
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

    user = dedent("""Here is the list of links on the website of {url} -
    please decide which of these are relevant web links for a brochure about the company, respond with the full https URL in JSON format.
    Do not include Terms of Service, Privacy, email links.

    Links (some might be relative links):
    {links}""")


class CompanyResearchPrompts:
    system = dedent("""
    You are an assistant that analyzes the contents of several relevant pages from a company website \
    and creates a short brochure about the company for prospective customers, investors and recruits. Respond in markdown.\
    Include details of company culture, customers and careers/jobs if you have the information.
    """)

    user = dedent("""You are looking at a company called: {company_name} \
    Here are the contents of its landing page and other relevant pages; \
    use this information to build a short brochure of the company in markdown.
    {summary}""")


class PageSummarizerPrompts:
    system = dedent("""You are an assistant that analyzes the contents of a website \
    and provides a short summary, ignoring text that might be navigation related. \
    Respond in markdown.
    """)

    user = dedent("""
    You are looking at a page '{page_name}'. \
    The contents from this page is as follows;
    {content} \n\n
    please summarize this page in markdown. \
    If it includes news or announcements, then summarize these too.\n\n

    You should respond with the results like this example:
    ---
    # Page: {page_name}
    # Content:
    summary goes here...
    """)
