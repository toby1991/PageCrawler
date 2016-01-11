import crawler
page_name = 'xxx'
base_url = 'http://aqvatarius.com/themes/intuitive/'
first_page = 'index.html'
retry_times = 3
result = crawler.crawl(page_name, base_url, first_page, retry_times)
if result == True:
    print('oh yeah.')
