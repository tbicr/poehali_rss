import lxml.etree
import lxml.html
import requests


def parse_list():
    url = 'http://forum.poehali.net/index.php?board=12'
    page = lxml.html.fromstring(requests.get(url).content)
    results = []
    for row in page.xpath('//table//table//table//table//tr')[2:]:
        link = row.xpath('.//td[3]//a')[0]
        results.append((link.attrib['href'], link.text_content().strip()))
    return results


def parse_page(url):
    page = lxml.html.fromstring(requests.get(url).content)
    post = page.xpath('//table//table//table//table//tr')[0].xpath('./td[2]')
    return lxml.etree.tostring(post)