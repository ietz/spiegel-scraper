import datetime as dt

import dateparser
import requests
import lxml.html
import tldextract


def articles_by_date(date: dt.date):
    timestamp = dt.datetime(date.year, date.month, date.day)
    archive_url = f'https://www.spiegel.de/nachrichtenarchiv/artikel-{date.strftime("%d.%m.%Y")}.html'
    resp = requests.get(archive_url)
    doc = lxml.html.fromstring(resp.content)

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
