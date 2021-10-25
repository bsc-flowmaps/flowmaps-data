import pandas as pd
from datetime import datetime, timedelta

from .utils import fetch_first, fetch_all_pages, parse_date, date_rfc1123, tz


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


def _zone_movements_mitma_mov(start_date=None, end_date=None, print_url=False):
    filters = {}
    if start_date and end_date:
        filters['evstart'] = {'$gte': date_rfc1123(parse_date(start_date)), '$lt': date_rfc1123(parse_date(end_date) + timedelta(days=1))}
    elif start_date:
        filters['evstart'] = {'$gte': date_rfc1123(parse_date(start_date))}
    elif end_date:
        filters['evstart'] = {'$lt': date_rfc1123(parse_date(end_date) + timedelta(days=1))}
    data = fetch_all_pages('mitma_mov.zone_movements', filters, print_url=print_url)
    df = pd.DataFrame(data)

    # add a date string column
    df['evstart'] = pd.to_datetime(df['evstart'])
    df['evstart'] = df['evstart'].dt.tz_convert(tz)
    df['date'] = df['evstart'].dt.strftime('%Y-%m-%d')

    # replace 'inf' with 3
    df['viajes'] = df['viajes'].map(lambda x: 3 if x == float('inf') else x)

    columns = ['id', 'date', 'viajes', 'personas']
    return df[columns]


def zone_movements(layer, start_date=None, end_date=None, print_url=False):
    if layer == 'mitma_mov':
        return _zone_movements_mitma_mov(start_date, end_date, print_url)

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
    columns = ['id', 'date', 'viajes', 'personas']
    return pd.DataFrame(data)[columns]


def risk(source_layer, target_layer, ev, date):
    filters = {
        'source_layer': source_layer,
        'target_layer': target_layer,
        'date': date
    }
    mobility = fetch_all_pages('mitma_mov.daily_mobility_matrix', filters, print_url=False)
    if not mobility:
        raise Exception(f'Missing mobility data matching: {filters}')
    mobility = pd.DataFrame(mobility)
    mobility = mobility[['source', 'target', 'source_layer', 'target_layer', 'trips']]

    filters = {
        'type': 'covid19',
        'ev': ev,
        'date': date
    }
    cases = fetch_all_pages('layers.data.consolidated', filters, print_url=False)
    if not cases:
        raise Exception(f'Missing Covid19 data matching: {filters}')
    cases = pd.DataFrame(cases)

    df = pd.merge(mobility, cases, left_on='source', right_on='id', how='inner')

    if 'population' not in cases.columns: 
        filters = {
            'type': 'population',
            'layer': source_layer,
            'date': date
        }
        population = fetch_all_pages('layers.data.consolidated', filters, print_url=False)
        population = pd.DataFrame(population)
        if not population:
            raise Exception(f'Missing population data matching: {filters}')
        df = pd.merge(df, population, left_on='source', right_on='id', how='inner')

    df = df.rename(columns={'population': 'source_population', 'active_cases_14': 'source_cases_last_14_days', 'active_cases_7': 'source_cases_last_7_days', 'new_cases': 'source_cases'})
    df = df[['source_layer', 'target_layer', 'date', 'source', 'target', 'trips', 'source_population', 'source_cases_last_14_days', 'source_cases_last_7_days', 'source_cases', 'ev']]
    df['source_cases_by_100k_last_14_days'] = 100000 * df['source_cases_last_14_days'] / df['source_population']
    df['risk'] = df['trips'] * df['source_cases_last_14_days'] / df['source_population']
    return df


def deceased(ev, start_date=None, end_date=None, print_url=False):
    # deceased datasets are no consolidated, so they can just be downloaded as any other dataset
    return dataset(ev, start_date=start_date, end_date=end_date, print_url=print_url)
