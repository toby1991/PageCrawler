# -*-coding:utf-8-*-
__author__ = 'Toby'

from pyquery import PyQuery as pq  # pyquery
import pycurl  # curl
from io import BytesIO  # 字节处理
import os  # 系统
import re  # 正则

# crawl page
def crawl(page_name, base_url, first_page, retry_times = 3):
    page_crawled = []
    js_crawed = []
    css_crawed = []
    img_crawed = []

    result = crawlPage(page_name, base_url, [first_page], page_crawled, retry_times, js_crawed, css_crawed, img_crawed)
    if result == []:
        print('抓取结束, 感谢使用!')
        return True
    else:
        return False
    

def main():
    theme_name = 'materialism'
    base_url = 'http://www.theme-guys.com/materialism/html/'
    #base_url = 'http://themes.krzysztof-furtak.pl/themes/malpha2/malpha2/'
    page = 'index.html'
    page_crawled = []
    retry_times = 3
    js_crawed = []
    css_crawed = []
    img_crawed = []

    result = crawlPage(theme_name, base_url, [page], page_crawled, retry_times, js_crawed, css_crawed, img_crawed)
    if result == []:
        print('抓取结束, 感谢使用!')


def crawlPage(theme_name, base_url, page_arr_new_new, page_crawled, retry_times, js_crawed, css_crawed, img_crawed):
    for page in page_arr_new_new:
        if page not in page_crawled:
            craw_page_obj = crawler(theme_name, base_url, base_url, page, 'page')
            # 重试
            retry = 0
            while craw_page_obj.is_ok != True and retry < retry_times:
                craw_page_obj = crawler(theme_name, base_url, base_url, page, 'page')
                retry += 1
                print('重试抓取:'+base_url+page+' '+str(retry)+'次')

            if craw_page_obj.is_ok:
                # js
                js_arr = craw_page_obj.getJSs()
                for js in js_arr:
                    if js not in js_crawed:
                        url = craw_page_obj.formatLink(js, base_url)
                        if craw_page_obj.curlGetHTML(url, 'js'):
                            js_crawed.append(js)

                # css
                css_arr = craw_page_obj.getCSSs()
                for css in css_arr:
                    if css not in css_crawed:
                        url = craw_page_obj.formatLink(css, base_url)
                        if craw_page_obj.curlGetHTML(url, 'css'):
                            css_crawed.append(css)
                            # css文件里有可能出现图片链接
                            css_base_url = url[0:-len(url[url.rfind('/'):])] + '/'
                            craw_css_obj = crawler(theme_name, base_url, css_base_url, css, 'css')

                            # 重试
                            retry = 0
                            while craw_css_obj.is_ok != True and retry < retry_times:
                                craw_css_obj = crawler(theme_name, base_url, css_base_url, css, 'css')
                                retry += 1

                            if craw_css_obj.is_ok:
                                img_arr = craw_css_obj.getCSSIMGs()
                                for img in img_arr:
                                    if img not in img_crawed:
                                        url = craw_css_obj.formatLink(img, css_base_url)
                                        if craw_css_obj.curlGetHTML(url, 'img'):
                                            img_crawed.append(img)

                # img
                img_arr = craw_page_obj.getIMGs()
                for img in img_arr:
                    if img not in img_crawed:
                        url = craw_page_obj.formatLink(img, base_url)
                        if craw_page_obj.curlGetHTML(url, 'img'):
                            img_crawed.append(img)

                page_arr_new = craw_page_obj.getPages()

                # 记录已经爬过的页面
                page_crawled.append(page)

                # 把新爬出结果中, 已经爬过的页面删除
                for page_tmp in page_arr_new:
                    if page_tmp in page_crawled:
                        page_arr_new.remove(page_tmp)

                page_arr_new_new += page_arr_new
            else:
                print(page + ' 该页面无法处理!系统已自动跳过')
                page_arr_new_new.remove(page)

            page_arr_new_new = list(set(page_arr_new_new))  # 排重
            # 得到剩余没有爬的页面
            for page_tmp in page_crawled:
                if page_tmp in page_arr_new_new:
                    page_arr_new_new.remove(page_tmp)

    if len(page_arr_new_new) == 0:
        return []
    else:
        crawlPage(theme_name, base_url, page_arr_new_new, page_crawled, retry_times, js_crawed, css_crawed, img_crawed)


class crawler:
    # 初始化
    def __init__(self, theme_name, theme_url, base_url, page, url_type):
        self.theme_name = theme_name
        self.theme_url = theme_url
        self.base_url = base_url
        self.page = page
        self.type = url_type
        if self.page.find('//') == -1:
            url = self.base_url + self.page
        else:
            if self.page[0:2] == '//':
                url = 'http:'+self.page
            else:
                url = self.page
        self.is_ok = self.curlGetHTML(url, url_type)
        # self.html = ''
        # self.d = pq(self.html)
        self.page_arr = []
        self.js_arr = []
        self.css_arr = []
        self.img_arr = []

    # 获取页面列表
    def getPages(self):
        self.d('a[href]').each(self.getAHref)
        return self.page_arr

    # 获取A标签地址回调
    def getAHref(self, i, val):
        href = self.d(val).attr('href')
        href_exception = ['sms://', 'tel:', 'mailto:', 'javascript:', '#', '.png', '.jpg', '.jpeg', '.ico']
        if len(href) > 0:
            find_exception = False
            for ex in href_exception:
                if href.find(ex) != -1:
                    find_exception = True
                    break
            if href[-1] != '/' and href != self.base_url and find_exception == False:
                href = self.formatLink(href, self.base_url)
                self.page_arr.append(href)

    # 获取Js标签列表
    def getJSs(self):
        self.d('script[src]').each(self.getJSSrc)
        return self.js_arr

    # 获取Js标签地址回调
    def getJSSrc(self, i, val):
        src = self.d(val).attr('src')
        if src.find('.js') != -1:
            src = self.formatLink(src, self.base_url)
            self.js_arr.append(src)

    # 获取CSS标签列表
    def getCSSs(self):
        self.d('link[href]').each(self.getCSSHref)
        return self.css_arr

    # 获取CSS标签地址回调
    def getCSSHref(self, i, val):
        href = self.d(val).attr('href')
        if href.find('.css') != -1:
            href = self.formatLink(href, self.base_url)
            self.css_arr.append(href)

    # 获取CSS中图片列表
    def getCSSIMGs(self):
        i = 0
        for val in re.findall('url\\((.*?)\\)', self.css):
            self.getCSSIMGUrl(i, val)
            i += 1
        return self.img_arr

    # 获取CSS中图片列表回调
    def getCSSIMGUrl(self, i, val):
        if val.find('data:image') == -1:
            if val[0] == '"' or val[0] == '\'':
                val = val[1:]
            if val[-1] == '"' or val[-1] == '\'':
                val = val[0:-1]
            val = self.formatLink(val, self.base_url)
            self.img_arr.append(val)

    # 获取IMG标签列表
    def getIMGs(self):
        self.d('img[src]').each(self.getIMGSrc)
        return self.img_arr

    # 获取IMG标签地址回调
    def getIMGSrc(self, i, val):
        src = self.d(val).attr('src')
        if src.find('data:image') == -1 or src.rfind('.png') != -1 or src.rfind('.jpg') != -1 or src.rfind(
                '.jpeg') != -1 or src.rfind('.ico') != -1:
            src = self.formatLink(src, self.base_url)
            self.img_arr.append(src)

    # 链接转换为绝对路径
    def formatLink(self, link, base_url):
        if link.rfind('#') != -1:
            link = link[0:link.rfind('#')]
        if link.rfind('?') != -1:
            link = link[0:link.rfind('?')]
        if link.find('//') != -1:
            # 绝对路径
            if link.find(base_url):
                # 站内链接
                pass
            else:
                # 站外链接
                pass
        else:
            # 相对路径
            if link.find('../') != -1:
                while link[0:3] == '../':
                    base_url = base_url[0:base_url[0:-1].rfind('/')] + '/'
                    link = link[3:]
            link = base_url+link
        return link

    # curl获取网页源码
    def curlGetHTML(self, url, url_type):
        print(url)
        try:
            buffer = BytesIO()

            c = pycurl.Curl()
            c.setopt(c.URL, url)
            c.setopt(c.WRITEDATA, buffer)
            c.setopt(c.CONNECTTIMEOUT, 60)
            c.setopt(c.TIMEOUT, 60)
            # c.setopt(c.PROXY, 'http://inthemiddle.com:8080')
            c.perform()

            buffer_data = buffer.getvalue()
            buffer.close()

            file_name = url[url.rfind('/') + 1:]
            if file_name != '':
                if url.find(self.theme_url) != -1:
                    # 本站的文件
                    dir_path = url[len(self.theme_url):-len(file_name)]
                else:
                    # 外站的文件
                    dir_path = url.replace('://', '/')
                    dir_path = dir_path[0:-len(file_name)]

                if url_type == 'page':
                    self.html = buffer_data.decode('utf-8')
                    self.d = pq(self.html)

                    dir = os.getcwd() + '/' + self.theme_name
                elif url_type == 'js':
                    dir = os.getcwd() + '/' + self.theme_name + '/' + dir_path
                elif url_type == 'css':
                    self.css = buffer_data.decode('utf-8')

                    dir = os.getcwd() + '/' + self.theme_name + '/' + dir_path
                elif url_type == 'img':
                    dir = os.getcwd() + '/' + self.theme_name + '/' + dir_path

                if os.path.exists(dir) == False:
                    os.makedirs(dir)
                file_handle = open(dir + '/' + file_name, 'wb')
                file_handle.write(buffer_data)
                file_handle.close()

                return True
            else:
                print('文件名为空! 地址:' + url)

                return False


        except Exception as e:
            print(e)
            return False


if __name__ == '__main__':
    main()
