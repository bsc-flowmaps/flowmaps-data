import json
import pandas as pd
from dateutil.parser import parse

from .utils import fetch_first, fetch_all_pages
from .data import geolayer, covid19, dataset, daily_mobility_matrix, population, zone_movements


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


def list_covid19():
    print('Listing consolidated ev:')
    filters = {
        'storedIn': 'layers.data.consolidated',
        'keywords.type': 'covid19', 
    }
    data = fetch_all_pages('provenance', filters, progress=False)
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
    filters = {
        'ev': ev,
        'type': 'covid19',
    }
    data = covid19(ev, start_date=start_date, end_date=end_date, fmt='records', print_url=True)
    if output_format == 'csv':
        df = pd.DataFrame(data)
        df.to_csv(output_file, index=False)
        print(f'{df.shape[0]} rows written to file:', output_file)
    elif output_format == 'json':
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        print('Saved to file:', output_file)
    else:
        print('Unrecognized output_format. Choose one from: csv, json')


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
    data = dataset(ev, start_date=start_date, end_date=end_date, fmt='records', print_url=True)
    if output_format == 'csv':
        df = pd.DataFrame(data)
        df.to_csv(output_file, index=False)
        print(f'{df.shape[0]} rows written to file:', output_file)
    elif output_format == 'json':
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        print('Saved to file:', output_file)
    else:
        print('Unrecognized output_format. Choose one from: csv, json')


def list_daily_mobility_matrix():
    print('Listing available mobility layers:')
    # filters = {
    #     'collection': 'mitma_mov.daily_mobility_matrix', 
    #     'field': 'source_layer',
    #     'query': {'date': '2020-10-10'},
    # }
    # data = fetch_all_pages('distinct', filters)
    # print("\n".join(data))

    pairs = [["mitma_mov", "mitma_mov"],
        ["cnig_provincias", "cnig_provincias"],
        ["cnig_ccaa", "cnig_ccaa"],
        ["abs_09", "abs_09"],
        ["zbs_15", "zbs_15"],
        ["zbs_07", "zbs_07"],
        ["oe_16", "oe_16"],
        ["zon_bas_13", "zon_bas_13"],
        ["cnig_provincias", "abs_09"],
        ["abs_09", "cnig_provincias"],
        ["cnig_provincias", "zbs_15"],
        ["zbs_15", "cnig_provincias"],
        ["cnig_provincias", "zbs_07"],
        ["zbs_07", "cnig_provincias"],
        ["cnig_provincias", "oe_16"],
        ["oe_16", "cnig_provincias"],
        ["cnig_provincias", "zon_bas_13"],
        ["zon_bas_13", "cnig_provincias"]]

    for source_layer, target_layer in pairs:
        print(json.dumps({"source_layer": source_layer, "target_layer": target_layer}))


def describe_daily_mobility_matrix(provenance=False):
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


def download_daily_mobility_matrix(source_layer, target_layer, output_file, start_date=None, end_date=None, output_format='csv', source=None, target=None):
    print(f'Dowloading mobility matrix for source_layer={source_layer} target_layer={target_layer}')
    data = daily_mobility_matrix(source_layer, target_layer, 
                                 start_date=start_date, end_date=end_date, 
                                 source=source, target=target,
                                 fmt='records', print_url=True)
    if output_format == 'csv':
        df = pd.DataFrame(data)
        df.to_csv(output_file, index=False)
        print(f'{df.shape[0]} rows written to file:', output_file)
    elif output_format == 'json':
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        print('Saved to file:', output_file)
    else:
        print('Unrecognized output_format. Choose one from: csv, json')


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
    data = population(layer, start_date=start_date, end_date=end_date, fmt='records', print_url=True)
    
    if output_format == 'csv':
        df = pd.DataFrame(data)
        df.to_csv(output_file, index=False)
        print(f'{df.shape[0]} rows written to file:', output_file)
    elif output_format == 'json':
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        print('Saved to file:', output_file)
    else:
        print('Unrecognized output_format. Choose one from: csv, json')


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
    data = zone_movements(layer, start_date=start_date, end_date=end_date, fmt='records', print_url=True)
    
    if output_format == 'csv':
        df = pd.DataFrame(data)
        df.to_csv(output_file, index=False)
        print(f'{df.shape[0]} rows written to file:', output_file)
    elif output_format == 'json':
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        print('Saved to file:', output_file)
    else:
        print('Unrecognized output_format. Choose one from: csv, json')
