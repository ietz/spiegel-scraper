import datetime as dt
import re

import dateparser
import requests
import lxml.html
import tldextract


def by_date(date: dt.date):
    html = html_by_date(date)
    return scrape_html(html)


def html_by_date(date: dt.date):
    archive_url = f'https://www.spiegel.de/nachrichtenarchiv/artikel-{date.strftime("%d.%m.%Y")}.html'
    resp = requests.get(archive_url)
    return resp.text


def scrape_html(html: str):
    doc = lxml.html.fromstring(html)
    url = doc.xpath('string(//link[@rel="canonical"]/@href)')
    date_string = re.search(r'/artikel-(\d{2}\.\d{2}\.\d{4})\.html$', url)[1]
    timestamp = dt.datetime.strptime(date_string, '%d.%m.%Y')

    articles = []
    for article in doc.xpath('//article'):
        url = article.xpath('string(.//a/@href)')

        # omit external layouts such as Bento and Manager Magazin
        if tldextract.extract(url).registered_domain != 'spiegel.de':
            continue

        articles.append({
            'url': url,
            'headline': article.xpath('string(.//a/@title)'),
            'is_paid': article.xpath('boolean(.//svg/title[text()="Icon: Spiegel Plus"])'),
            'date_published': parse_date(article.xpath('string(./footer/span[1])'), relative_base=timestamp),
            'channel': article.xpath('string(./footer/span[3])'),
        })

    return articles


def parse_date(date_string: str, relative_base: dt.datetime):
    return dateparser.parse(
        date_string=date_string,
        languages=['de'],
        settings={
            'RELATIVE_BASE': relative_base,
        },
    )
