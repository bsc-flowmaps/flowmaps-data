import pandas as pd
from datetime import datetime, timedelta

from .utils import fetch_first, fetch_all_pages, parse_date, date_rfc1123


def geolayer(layer, print_url=False):
    filters = {
        'layer': layer
    }
    data = fetch_all_pages('layers', filters, print_url=print_url)

    featureCollection = {
        "type": "FeatureCollection",
        "features": [{
            'id': doc['id'],
            'centroid': doc['centroid'],
            **doc['feat'],
        } for doc in data],
    }
    return featureCollection


def clean_docs(docs, drop_fields):
    for doc in docs:
        for field in drop_fields:
            del(doc[field])
    return docs


def covid19(ev, start_date=None, end_date=None, fmt='dataframe', print_url=False):
    filters = {
        'ev': ev,
        'type': 'covid19',
    }
    if start_date and end_date:
        filters['date'] = {'$gte': start_date, '$lte': end_date}
    elif start_date:
        filters['date'] = {'$gte': start_date}
    elif end_date:
        filters['date'] = {'$lte': end_date}
    data = fetch_all_pages('layers.data.consolidated', filters, print_url=print_url)
    data = clean_docs(data, ['d', 'c', 'updated_at', '_id', 'was_missing', 'type', 'ev'])
    if fmt == 'dataframe':
        return pd.DataFrame(data)
    return data


def dataset(ev, start_date=None, end_date=None, fmt='dataframe', print_url=False):
    filters = {
        'ev': ev,
    }
    if start_date and end_date:
        filters['evstart'] = {'$gte': date_rfc1123(parse_date(start_date)), '$lt': date_rfc1123(parse_date(end_date) + timedelta(days=1))}
    elif start_date:
        filters['evstart'] = {'$gte': date_rfc1123(parse_date(start_date))}
    elif end_date:
        filters['evstart'] = {'$lt': date_rfc1123(parse_date(end_date) + timedelta(days=1))}
    data = fetch_all_pages('layers.data', filters, print_url=print_url)
    if fmt == 'dataframe':
        return pd.DataFrame(data)
    return data


def daily_mobility(source_layer, target_layer, start_date=None, end_date=None, source=None, target=None, fmt='dataframe', print_url=False):
    filters = {
        'source_layer': source_layer,
        'target_layer': target_layer,
    }
    if start_date and end_date:
        filters['date'] = {'$gte': start_date, '$lte': end_date}
    elif start_date:
        filters['date'] = {'$gte': start_date}
    elif end_date:
        filters['date'] = {'$lte': end_date}
    if source:
        filters['source'] = source
    if target:
        filters['target'] = target
    data = fetch_all_pages('mitma_mov.daily_mobility_matrix', filters, print_url=print_url)
    if fmt == 'dataframe':
        return pd.DataFrame(data)
    return data


def population(layer, start_date=None, end_date=None, fmt='dataframe', print_url=False):
    filters = {
        'layer': layer,
        'type': 'population',
    }
    if start_date and end_date:
        filters['date'] = {'$gte': start_date, '$lte': end_date}
    elif start_date:
        filters['date'] = {'$gte': start_date}
    elif end_date:
        filters['date'] = {'$lte': end_date}
    data = fetch_all_pages('layers.data.consolidated', filters, print_url=print_url)
    if fmt == 'dataframe':
        return pd.DataFrame(data)
    return data


def zone_movements(layer, start_date=None, end_date=None, fmt='dataframe', print_url=False):
    filters = {
        'layer': layer,
        'type': 'zone_movements',
    }
    if start_date and end_date:
        filters['date'] = {'$gte': start_date, '$lte': end_date}
    elif start_date:
        filters['date'] = {'$gte': start_date}
    elif end_date:
        filters['date'] = {'$lte': end_date}
    data = fetch_all_pages('layers.data.consolidated', filters, print_url=print_url)
    if fmt == 'dataframe':
        return pd.DataFrame(data)
    return data
