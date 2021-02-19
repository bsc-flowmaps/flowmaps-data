import requests
import pytz
import json
from datetime import datetime, timedelta
from progress.bar import Bar

tz = pytz.timezone('Europe/Madrid')

API_URL = "https://flowmaps.life.bsc.es/api"


def date_rfc1123(dt):
    """Return a string representation of a date according to RFC 1123
    (HTTP/1.1).

    The supplied date must be in UTC.

    """
    weekday = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][dt.weekday()]
    month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep",
             "Oct", "Nov", "Dec"][dt.month - 1]
    return "%s, %02d %s %04d %02d:%02d:%02d GMT" % (weekday, dt.day, month,
        dt.year, dt.hour, dt.minute, dt.second)


def parse_date(date_str):
    return tz.localize(datetime.strptime(date_str, "%Y-%m-%d")) 


def clean_docs(docs):
    skip_fields = ['_links', '_created', '_updated', 'href', '_etag']
    for doc in docs:
        for field in skip_fields:
            if field in doc:
                del doc[field]
    return docs


def fetch_first(collection, query, projection={}):
    base_url = API_URL
    url = f"{base_url}/{collection}"
    params = {'where': json.dumps(query), 'max_results': 1, 'projection': json.dumps(projection)}
    # print(f"API url: {base_url}/{collection}?where={params['where']}&max_results={params['max_results']}&projection={params['projection']}")
    response = requests.get(url, params=params).json()
    if not response or not response.get('_items'):
        return None
    return response['_items'][0]


def fetch_all_pages(collection, query, batch_size=1000, projection={}, sort=None, progress=True, print_url=False):
    base_url = API_URL
    url = f"{base_url}/{collection}"
    params = {'where': json.dumps(query), 'max_results': batch_size, 'projection': json.dumps(projection)}
    if sort:
        params['sort'] = sort
    data = []
    if print_url:
        print(f"API request: {base_url}/{collection}?where={params['where']}")
    response = requests.get(url, params=params).json() # get first page
    data.extend(response['_items'])
    if '_links' not in response:
        return data
    num_docs = response['_meta']['total']
    if num_docs <= 0:
        return data
    if progress: bar = Bar('Dowloading documents', max=num_docs)
    while 'next' in response['_links']:
        if progress: bar.goto(len(data))
        url = f"{base_url}/{response['_links']['next']['href']}"
        response = requests.get(url).json()
        data.extend(response['_items'])
    if progress: bar.goto(len(data))
    if progress: bar.finish()
    return data


def save_df(df, output_file, output_format):
    if output_format == 'csv':
        df.to_csv(output_file, index=False)
        print(f'{df.shape[0]} rows written to file:', output_file)
    elif output_format == 'json':
        with open(output_file, 'w') as f:
            json.dump(df.to_dict('records'), f, indent=2)
        print('Saved to file:', output_file)
    elif output_format == 'parquet':
        df.to_parquet(output_file)
        print(f'{df.shape[0]} rows written to file:', output_file)
    else:
        print('Unrecognized output_format. Choose one from: csv, json, parquet')
