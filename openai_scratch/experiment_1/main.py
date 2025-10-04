from .agents import CompanyResearchAgent, CrawlerAgent, PageSummarizerAgent


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
    main1()
    # main2()
    # main3()
