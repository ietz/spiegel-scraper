import datetime as dt

import dateparser


def parse_date(date_string: str, relative_base: dt.datetime):
    return dateparser.parse(
        date_string=date_string,
        languages=['de'],
        settings={
            'RELATIVE_BASE': relative_base,
        },
    )
