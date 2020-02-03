import json
import re

import lxml.html
import requests


def by_url(article_url: str):
    html = html_by_url(article_url)
    return scrape_html(html)


def html_by_url(article_url: str):
    return requests.get(article_url).text


def scrape_html(article_html: str):
    doc = lxml.html.fromstring(article_html)

    ld_content = doc.xpath('string(//script[@type="application/ld+json"]/text())')
    ld = json.loads(ld_content)
    ld_by_type = {ld_entry['@type']: ld_entry for ld_entry in ld}
    news_ld = ld_by_type['NewsArticle']

    settings = json.loads(doc.xpath('string(//script[@type="application/settings+json"]/text())'))
    info = settings['editorial']['info']

    text_node_selector = \
        'main .word-wrap > p,'  \
        'main .word-wrap > h3, ' \
        'main .word-wrap > ul > li, ' \
        'main .word-wrap > ol > li'
    text_nodes = doc.cssselect(text_node_selector)
    text = re.sub(r'\n+', '\n', '\n'.join([node.text_content() for node in text_nodes])).strip()

    return {
        'url': doc.xpath('string(//link[@rel="canonical"]/@href)'),
        'id': info['article_id'],
        'channel': info['channel'],
        'subchannel': info['subchannel'],
        'headline': {
            'main': info['headline'],
            'social': info['headline_social']
        },
        'intro': info['intro'],
        'text': text,
        'topics': info['topics'],
        'author': settings['editorial']['author'],
        'comments_enabled': settings['editorial']['attributes']['is_comments_enabled'],
        'date_created': news_ld['dateCreated'],
        'date_modified': news_ld['dateModified'],
        'date_published': news_ld['datePublished'],
        'breadcrumbs': [breadcrumb['item']['name'] for breadcrumb in ld_by_type['BreadcrumbList']['itemListElement']],
    }

