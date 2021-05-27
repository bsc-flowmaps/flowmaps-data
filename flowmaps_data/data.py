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


def covid19(ev, start_date=None, end_date=None, print_url=False):
    # fetch covid cases
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

    cursor = fetch_all_pages('layers.data.consolidated', filters, print_url=print_url)
    cursor = clean_docs(cursor, ['d', 'c', 'updated_at', '_id', 'was_missing', 'type', 'ev'])
    df = pd.DataFrame(cursor)
    return df


def dataset(ev, start_date=None, end_date=None, print_url=False):
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
    return pd.DataFrame(data)


def daily_mobility(source_layer, target_layer, start_date=None, end_date=None, source=None, target=None, print_url=False):
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
    data = clean_docs(data, ['source_layer', 'target_layer', '_id', 'updated_at'])
    return pd.DataFrame(data)


def population(layer, start_date=None, end_date=None, print_url=False):
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
    data = clean_docs(data, ['_id', 'type', 'layer', 'updated_at'])
    return pd.DataFrame(data)


def zone_movements(layer, start_date=None, end_date=None, print_url=False):
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
    return pd.DataFrame(data)


def risk(source_layer, target_layer, ev, date):
    filters = {
        'source_layer': source_layer,
        'target_layer': target_layer,
        'date': date
    }
    mobility = fetch_all_pages('mitma_mov.daily_mobility_matrix', filters, print_url=False)
    mobility = pd.DataFrame(mobility)

    filters = {
        'type': 'covid19',
        'ev': ev,
        'date': date
    }
    cases = fetch_all_pages('layers.data.consolidated', filters, print_url=False)
    cases = pd.DataFrame(cases)

    filters = {
        'type': 'population',
        'layer': source_layer,
        'date': date
    }
    population = fetch_all_pages('layers.data.consolidated', filters, print_url=False)
    population = pd.DataFrame(population)

    df = pd.merge(mobility, cases, left_on='source', right_on='id', how='inner')
    df = pd.merge(df, population, left_on='source', right_on='id', how='inner')
    df = df.rename(columns={'population': 'source_population', 'active_cases_14': 'source_cases_last_14_days', 'active_cases_7': 'source_cases_last_7_days', 'new_cases': 'source_cases'})
    df = df[['source_layer', 'target_layer', 'date', 'source', 'target', 'trips', 'source_population', 'source_cases_last_14_days', 'source_cases_last_7_days', 'source_cases', 'ev']]
    df['source_cases_by_100k_last_14_days'] = 100000 * df['source_cases_last_14_days'] / df['source_population']
    df['risk'] = df['trips'] * df['source_cases_last_14_days'] / df['source_population']
    return df
