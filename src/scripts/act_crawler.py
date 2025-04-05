import sys
from processing.crawlers.act_crawler import ActCrawler, ActType

if len(sys.argv) == 1:
    raise Exception("Year argument not provided")
if not sys.argv[1]:
    raise Exception("Year argument not provided")

year = sys.argv[1]
crawler = ActCrawler()
crawler.download(year=year, act_type=ActType.USTAWA)
