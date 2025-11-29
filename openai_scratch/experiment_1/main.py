from .agents import CompanyResearchAgent, CrawlerAgent, PageSummarizerAgent


def main1(company_name, url):
    crawler_agent = CrawlerAgent()
    details = crawler_agent.get_all_details(company_name, url)
    print(details)


def main2(company_name, url):
    crawler_agent = CrawlerAgent(max_hops=0)
    result = crawler_agent.crawl_pages(company_name, url)
    summarizer = PageSummarizerAgent()
    details = summarizer.summarize(result[0][0], result[0][1])
    print(details)


def main3(company_name, url):
    crawler_agent = CrawlerAgent(max_hops=1)
    brochure_agent = CompanyResearchAgent(crawler_agent=crawler_agent)
    res = brochure_agent.create_brochure(company_name, url)
    print(res)


if __name__ == "__main__":
    company_name, url = "HelloFresh", "https://www.hellofresh.com.au"
    # main1(company_name, url)
    # main2(company_name, url)
    main3(company_name, url)
