import json
import pandas as pd
from dateutil.parser import parse
from datetime import timedelta

from .utils import fetch_first, fetch_all_pages, date_rfc1123, parse_date, tz, save_df
from .data import geolayer, covid19, dataset, daily_mobility, population, zone_movements, risk


def list_layers():
    print('Listing layers:')
    filters = {
        'storedIn': 'layers', 
    }
    data = fetch_all_pages('provenance', filters, progress=False)
    for doc in data:
        print(f"{doc['keywords']['layer']}:  \t{doc['keywords']['layerDesc']}, {doc['numEntries']} polygons")


def describe_layer(layer, provenance=False, plot=False):
    print(f'Describing layer={layer}')
    filters = {
        'storedIn': 'layers',
        'keywords.layer': layer,
    }
    doc = fetch_first('provenance', filters)
    if not doc:
        print(f"No data for layer={layer}")
        return
    print(f"Description: {doc.get('keywords', {}).get('layerDesc')}")
    print(f"Layer in geojson format (https://en.wikipedia.org/wiki/GeoJSON)")
    print(f"Number of polygons: {doc.get('numEntries', '')}")

    if provenance:
        print(f"Full provenance: {json.dumps(doc, indent=4)}")

    if plot:
        download_layer(layer, None, plot=True, no_save=True)


def download_layer(layer, output_file, plot=False, no_save=False):
    if output_file is None:
        output_file = layer+'.geojson'

    print(f'Dowloading layer {layer}')
    featureCollection = geolayer(layer, print_url=True)

    if not no_save:
        print(f'Saving layer to file: {output_file}')
        with open(output_file, 'w') as f:
            json.dump(featureCollection, f, indent=2)

    if plot:
        try:
            import geopandas as gpd
            import descartes
            import matplotlib.pylab as plt
            gpd.GeoDataFrame.from_features(featureCollection['features']).plot()
            plt.show()
        except ImportError as e:
            # import traceback
            # traceback.print_exc()
            print(f"\n\n  WARN: {e}. \n  To use the --plot option you need to install the following packages: geopandas, descartes, matplotlib. \n  For example, use:  pip install geopandas descartes matplotlib")


def list_covid19(only_ids=False):
    filters = {
        'storedIn': 'layers.data.consolidated',
        'keywords.type': 'covid19', 
    }
    data = fetch_all_pages('provenance', filters, progress=False)
    if only_ids:
        for doc in data:
            print(doc['keywords']['ev'])
    else:
        print('Listing consolidated ev:')
        for doc in data:
            print(f"{doc['keywords']['ev']}\n\tDescription: {doc.get('processedFrom', [{}])[0].get('keywords', {}).get('evDesc')}\n\tNumber of entries: {doc['numEntries']}\n\tlayer: {doc['keywords']['layer']}\n")


def describe_covid19(ev, provenance=False):
    print(f'Describing consolidated ev={ev}')
    filters = {
        'storedIn': 'layers.data.consolidated',
        'keywords.ev': ev,
    }
    prov = fetch_first('provenance', filters)
    print(f"Description: {prov.get('processedFrom', [{}])[0].get('keywords', {}).get('evDesc')}")
    print(f"Original data url: {[x.get('from') for x in prov.get('processedFrom', [{}])[0].get('fetched', [{}])]}")
    print(f"Original data downloaded at: {prov.get('processedFrom', [{}])[0].get('storedAt')}")
    print(f"Processed at: {prov.get('storedAt')}")
    print(f"Number of entries: {prov.get('numEntries', '')}")
    filters = {
        'collection': 'layers.data.consolidated', 
        'field': 'date',
        'query': {'type': 'covid19', 'ev': ev},
    }
    data = fetch_all_pages('distinct', filters, progress=False)
    print(f"Available dates: min={min(data)}, max={max(data)}")

    example = fetch_first('layers.data.consolidated', {'type': 'covid19', 'ev': ev})
    print("Example document:\n"+json.dumps(example, indent=4))

    if provenance:
        print(f"Full provenance: {json.dumps(prov, indent=4)}")


def download_covid19(ev, output_file, output_format='csv', start_date=None, end_date=None):
    print(f'Dowloading consolidated health data for ev={ev}')
    df = covid19(ev, start_date=start_date, end_date=end_date, print_url=True)
    save_df(df, output_file, output_format)


def list_data():
    print('Listing ev:')
    filters = {
        'storedIn': 'layers.data',
    }
    data = fetch_all_pages('provenance', filters, progress=False)
    for doc in data:
        print(f"{doc['keywords']['ev']}\n\tDescription: {doc['keywords'].get('evDesc', '')}\n\tlayer: {doc['keywords'].get('layer')}\n")


def describe_data(ev, provenance=False):
    print(f'Describing ev={ev}')
    filters = {
        'storedIn': 'layers.data',
        'keywords.ev': ev,
    }
    prov = fetch_first('provenance', filters)
    print(f"Description: {prov.get('keywords', {}).get('evDesc')}")
    print(f"Original data url: {[x.get('from') for x in prov.get('fetched', [{}])]}")
    print(f"Last downloaded at: {prov.get('storedAt')}")
    print(f"Data associated to layer: {prov.get('keywords').get('layer')}")
    # print(f"Number of entries: {prov.get('numEntries', '')}")
    filters = {
        'collection': 'layers.data', 
        'field': 'evstart',
        'query': {'ev': ev},
    }
    dates = fetch_all_pages('distinct', filters, progress=False)
    dates = [parse(date) for date in dates]
    print(f"Available dates: min={min(dates)}, max={max(dates)}")
    if provenance:
        print(f"Full provenance: {json.dumps(prov, indent=4)}")

    example = fetch_first('layers.data', {'ev': ev})
    print("Example document:\n"+json.dumps(example, indent=4))


def download_data(ev, output_file, output_format='csv', start_date=None, end_date=None):
    print(f'Dowloading data for ev={ev}')
    df = dataset(ev, start_date=start_date, end_date=end_date, print_url=True)
    save_df(df, output_file, output_format)


def list_hourly_mobility(only_urls=False):
    filters = {
        'storedIn': 'mitma_mov.movements_raw',
    }
    data = fetch_all_pages('provenance', filters, progress=False)
    for doc in data:
        if only_urls:
            print(doc['fetched'][0]['from'])
        else:
            print(f"{doc['keywords']['ev']}\n\tDescription: {doc['keywords'].get('evDesc', '')}\n\tlayer: {doc['keywords'].get('layer')}\n\tdate: {doc['keywords'].get('evday')}\n\turl: {doc['fetched'][0].get('from')}\n")


def list_hourly_mobility_dates():
    filters = {
        'storedIn': 'mitma_mov.movements_raw',
        'numEntries': {'$gt': 0},
    }
    prov = fetch_all_pages('provenance', filters, sort='keywords.evday', progress=False)
    for doc in prov:
        print(parse(doc['keywords']['evday']).strftime('%Y-%m-%d'))


def describe_hourly_mobility(date, only_url=False):
    filters = {
        'storedIn': 'mitma_mov.movements_raw',
        'keywords.evday': {'$gte': date_rfc1123(parse_date(date)), '$lt': date_rfc1123(parse_date(date) + timedelta(days=1))}
    }
    data = fetch_all_pages('provenance', filters, progress=False)
    for doc in data:
        if only_url:
            print(doc['fetched'][0]['from'])
        else:
            print(f"Description: {doc['keywords'].get('evDesc', '')}")
            print(f"ev: {doc['keywords']['ev']}")
            print(f"layer: {doc['keywords'].get('layer')}")
            print(f"date: {doc['keywords'].get('evday')}")
            print(f"url: {doc['fetched'][0].get('from')}\n")
            print(f"Full provenance: {json.dumps(data, indent=4)}")


def list_daily_mobility():
    print('Listing available mobility layers:')
    filters = {
        'storedIn': 'mitma_mov.daily_mobility_matrix', 
        'keywords.layer_pairs': {'$ne': None},
    }
    data = fetch_all_pages('provenance', filters, progress=False)[0]
    pairs = data['keywords']['layer_pairs']
    for source_layer, target_layer in pairs:
        print(json.dumps({"source_layer": source_layer, "target_layer": target_layer}))


def list_daily_mobility_dates():
    filters = {
        'storedIn': 'mitma_mov.daily_mobility_matrix',
        'numEntries': {'$gt': 0},
    }
    prov = fetch_all_pages('provenance', filters, sort='keywords.date', progress=False)
    for doc in prov:
        print(doc['keywords']['date'])


def describe_daily_mobility(provenance=False):
    print(f'Describing daily mobility matrix')
    print(f"Description: Daily Origin-Destination matrix, based on anonymized mobile phone records from MITMA dataset (https://www.mitma.gob.es/ministerio/covid-19/evolucion-movilidad-big-data).")
    filters = {
        'storedIn': 'mitma_mov.daily_mobility_matrix',
        'numEntries': {'$gt': 0},
    }
    prov = fetch_all_pages('provenance', filters, sort='keywords.date', progress=False)
    print(f"Original data url: {[x.get('from') for x in prov[-1].get('processedFrom', [{}])[0].get('fetched', [{}])]}")
    print(f"Original data downloaded at: {prov[-1].get('processedFrom', [{}])[0].get('storedAt')}")
    print(f"Processed at: {prov[-1]['storedAt']}")
    print(f"Available dates: min={prov[0]['keywords']['date']}, max={prov[-1]['keywords']['date']}")
    
    if provenance:
        print(f"Full provenance: {json.dumps(prov, indent=4)}")
    
    example = fetch_first('mitma_mov.daily_mobility_matrix', {'source_layer': 'cnig_provincias', 'target_layer': 'cnig_provincias'})
    print("Example document:\n"+json.dumps(example, indent=4))


def download_daily_mobility(source_layer, target_layer, output_file, start_date=None, end_date=None, output_format='csv', source=None, target=None):
    print(f'Dowloading mobility matrix for source_layer={source_layer} target_layer={target_layer}')
    df = daily_mobility(source_layer, target_layer, 
                        start_date=start_date, end_date=end_date, 
                        source=source, target=target,
                        print_url=True)
    save_df(df, output_file, output_format)


def list_population_layers():
    print('Listing available population layers:')
    filters = {
        'collection': 'layers.data.consolidated', 
        'field': 'layer',
        'query': {'type': 'population'},
    }
    data = fetch_all_pages('distinct', filters)
    print("\n".join(data))


def describe_population(layer, provenance=False):
    print(f'Describing population data for layer={layer}')
    filters = {
        'storedIn': 'layers.data.consolidated',
        'keywords.layer': layer,
    }
    prov = fetch_first('provenance', filters)
    print(f"Description: population calculated based on anonymized mobile phone records from MITMA dataset (https://www.mitma.gob.es/ministerio/covid-19/evolucion-movilidad-big-data).")
    print(f"Original data url: {[x.get('from') for x in prov.get('processedFrom', [{}])[0].get('fetched', [{}])]}")
    print(f"Original data downloaded at: {prov.get('processedFrom', [{}])[0].get('storedAt')}")
    print(f"Processed at: {prov.get('storedAt')}")
    print(f"Number of entries: {prov.get('numEntries', '')}")
    filters = {
        'collection': 'layers.data.consolidated', 
        'field': 'date',
        'query': {'type': 'population', 'layer': layer},
    }
    data = fetch_all_pages('distinct', filters, progress=False)
    print(f"Available dates: min={min(data)}, max={max(data)}")

    example = fetch_first('layers.data.consolidated', {'type': 'population', 'layer': layer})
    print("Example document:\n"+json.dumps(example, indent=4))

    if provenance:
        print(f"Full provenance: {json.dumps(prov, indent=4)}")


def download_population(layer, output_file, output_format='csv', start_date=None, end_date=None):
    print(f'Dowloading population for layer={layer}')
    df = population(layer, start_date=start_date, end_date=end_date, print_url=True)
    save_df(df, output_file, output_format)


def list_zone_movements():
    print('Listing available zone_movements layers:')
    filters = {
        'collection': 'layers.data.consolidated', 
        'field': 'layer',
        'query': {'type': 'zone_movements'},
    }
    data = fetch_all_pages('distinct', filters)
    print("\n".join(data))


def describe_zone_movements(provenance=False):
    print(f'Describing zone_movements')
    filters = {
        'storedIn': 'layers.data.consolidated',
        'keywords.type': 'zone_movements',
        'numEntries': {'$gt': 0},
    }
    provs = fetch_all_pages('provenance', filters, sort='keywords.date', progress=False)
    prov = provs[-1]

    print(f"Description: mobility data from MITMA dataset (https://www.mitma.gob.es/ministerio/covid-19/evolucion-movilidad-big-data), aggregated at different layers. Original data is based on anonymized mobile phone records. It contains the number of people in each geographical area that has done 0,1,2,3+ trips. NOTE: 3 or more trips are encoded as '-1'.")
    print(f"Original data url: {[x.get('from') for x in prov.get('processedFrom', [{}])[0].get('fetched', [{}])]}")
    print(f"Original data downloaded at: {prov.get('processedFrom', [{}])[0].get('storedAt')}")
    print(f"Processed at: {prov.get('storedAt')}")
    print(f"Number of entries: {prov.get('numEntries', '')}")
    filters = {
        'collection': 'layers.data.consolidated', 
        'field': 'date',
        'query': {'type': 'zone_movements'},
    }
    data = fetch_all_pages('distinct', filters, progress=False)
    print(f"Available dates: min={min(data)}, max={max(data)}")

    example = fetch_first('layers.data.consolidated', {'type': 'zone_movements'})
    print("Example document:\n"+json.dumps(example, indent=4))

    if provenance:
        print(f"Full provenance: {json.dumps(provs, indent=4)}")


def download_zone_movements(layer, output_file, output_format='csv', start_date=None, end_date=None):
    print(f'Dowloading population for layer={layer}')
    df = zone_movements(layer, start_date=start_date, end_date=end_date, print_url=True)
    save_df(df, output_file, output_format)


def list_risk():
    filters = {
        'storedIn': 'mitma_mov.daily_mobility_matrix', 
        'keywords.layer_pairs': {'$ne': None},
    }
    data = fetch_all_pages('provenance', filters, progress=False)[0]
    pairs = data['keywords']['layer_pairs']

    filters = {
        'storedIn': 'layers.data.consolidated',
        'keywords.type': 'covid19', 
    }
    data = fetch_all_pages('provenance', filters, progress=False)
    print('Risk available for the following combinations of source layer, target layer and covid19 dataset:')
    for doc in data:
        ev = doc['keywords']['ev']
        layer = doc['keywords']['layer']
        for pair in pairs:
            if pair[0] == layer:
                print(json.dumps({'source_layer': pair[0], 'target_layer': pair[1], 'ev': ev}))


def list_risk_dates(ev):
    filters = {
        'storedIn': 'mitma_mov.daily_mobility_matrix',
        'numEntries': {'$gt': 0},
    }
    docs = fetch_all_pages('provenance', filters, sort='keywords.evday', progress=False)
    mobility_dates = [doc['keywords']['date'] for doc in docs]

    filters = {
        'collection': 'layers.data.consolidated', 
        'field': 'date',
        'query': {'type': 'covid19', 'ev': ev},
    }
    covid_dates = fetch_all_pages('distinct', filters, progress=False)
    
    dates = sorted(set(mobility_dates).intersection(covid_dates))
    print('\n'.join(dates))


def download_risk(source_layer, target_layer, ev, date, output_file, output_format='csv'):
    print(f'Dowloading risk for source_layer={source_layer}, target_layer={target_layer}')
    df = risk(source_layer, target_layer, ev, date)
    save_df(df, output_file, output_format)

