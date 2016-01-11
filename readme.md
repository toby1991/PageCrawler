##PageCrawler
###0x01 DESCRIPTION
***
For html page crawling.  
Written by Python 3.5  
###0x02 NEEDLE
***
* pyquery
* pycurl
* BytesIO
* os
* re
  
####Attention: Packages all above are for python3!  
###0x03 HOW TO USE
***
```Python
import crawler
page_name = 'xxx' 
base_url = 'http://xxx/themes/xxx/'
first_page = 'index.html'
retry_times = 3
result = crawler.crawl(page_name, base_url, first_page, retry_times)
if result == True:
    print('oh yeah.')
```
after these codes, the pages will appear in the folder named variable `page_name`, in this example, folder named `xxx`
###0x04 WHAT CANNOT DONE
***
In currently version, it can just crawl for html page, pages that written by angularjs would cannot be crawled.
