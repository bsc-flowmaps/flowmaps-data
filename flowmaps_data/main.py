#!/usr/bin/env python3

import sys
import argparse

from . import commands


CONFIG = {
    "layers": {
        "subcommands": {
            "list": {
                "fn": commands.list_layers,
                "argparse": {},
            },
            "describe": {
                "fn": commands.describe_layer,
                "argparse": {
                    "--layer": {"required": True, "type": str, "help": "", },
                    "--provenance": {"required": False, "default": False, "action": "store_true", "help": "show provenance", },
                    "--plot": {"required": False, "default": False, "action": "store_true", "help": "", },
                },
            },
            "download": {
                "fn": commands.download_layer,
                "argparse": {
                    "--layer": {"required": True, "type": str, "help": "", },
                    "--output-file": {"required": False,"dest": "output_file",  "default": None, "type": str, "help": "", },
                    "--plot": {"required": False, "default": False, "action": "store_true", "help": "", },
                    "--no_save": {"required": False, "default": False, "action": "store_true", "help": "", },
                },
            },
        },
    },
    "covid19": {
        "subcommands": {
            "list": {
                "fn": commands.list_covid19,
                "argparse": {
                    "--only-ids": {"dest": "only_ids", "required": False, "default": False, "action": "store_true", "help": "", },
                },
            },
            "describe": {
                "fn": commands.describe_covid19,
                "argparse": {
                    "--ev": {"required": True, "type": str, "help": "", },
                    "--provenance": {"required": False, "default": False, "action": "store_true", "help": "show provenance", },
                },
            },
            "download": {
                "fn": commands.download_covid19,
                "argparse": {
                    "--ev": {"required": True, "type": str, "help": "", },
                    "--output-file": {"required": True, "dest": "output_file", "type": str, "help": "", },
                    "--output-format": {"required": False, "dest": "output_format", "default": "csv", "type": str, "help": "", },
                    "--start-date": {"dest": "start_date", "required": False, "type": str, "help": "", },
                    "--end-date": {"dest": "end_date", "required": False, "type": str, "help": "", },
                },
            },
        },
    },
    "datasets": {
        "subcommands": {
            "list": {
                "fn": commands.list_data,
                "argparse": {},
            },
            "describe": {
                "fn": commands.describe_data,
                "argparse": {
                    "--ev": {"required": True, "type": str, "help": "", },
                    "--provenance": {"required": False, "default": False, "action": "store_true", "help": "show provenance", },
                },
            },
            "download": {
                "fn": commands.download_data,
                "argparse": {
                    "--ev": {"required": True, "type": str, "help": "", },
                    "--output-file": {"required": True, "dest": "output_file", "type": str, "help": "", },
                    "--output-format": {"required": False, "dest": "output_format", "default": "csv", "type": str, "help": "", },
                    "--start-date": {"dest": "start_date", "required": False, "type": str, "help": "", },
                    "--end-date": {"dest": "end_date", "required": False, "type": str, "help": "", },
                },
            },
        },
    },
    "hourly_mobility": {
        "subcommands": {
            "list": {
                "fn": commands.list_hourly_mobility,
                "argparse": {
                    "--only-urls": {"dest": "only_urls", "required": False, "default": False, "action": "store_true", "help": "", },
                },
            },
            "list-dates": {
                "fn": commands.list_hourly_mobility_dates,
                "argparse": {},
            },
            "describe": {
                "fn": commands.describe_hourly_mobility,
                "argparse": {
                    "--date": {"dest": "date", "required": True, "type": str, "help": "", },
                    "--only-url": {"dest": "only_url", "required": False, "default": False, "action": "store_true", "help": "", },
                },
            },
        },
    },
    "daily_mobility": {
        "subcommands": {
            "list": {
                "fn": commands.list_daily_mobility,
                "argparse": {},
            },
            "list-dates": {
                "fn": commands.list_daily_mobility_dates,
                "argparse": {},
            },
            "describe": {
                "fn": commands.describe_daily_mobility,
                "argparse": {
                    "--provenance": {"required": False, "default": False, "action": "store_true", "help": "show provenance", },
                },
            },
            "download": {
                "fn": commands.download_daily_mobility,
                "argparse": {
                    "--source-layer": {"required": True, "dest": "source_layer", "type": str, "help": "", },
                    "--target-layer": {"required": True, "dest": "target_layer", "type": str, "help": "", },
                    "--source": {"required": False, "type": str, "help": "", },
                    "--target": {"required": False, "type": str, "help": "", },
                    "--output-file": {"required": True, "dest": "output_file", "type": str, "help": "", },
                    "--output-format": {"required": False, "dest": "output_format", "default": "csv", "type": str, "help": "", },
                    "--start-date": {"dest": "start_date", "required": False, "type": str, "help": "", },
                    "--end-date": {"dest": "end_date", "required": False, "type": str, "help": "", },
                },
            },
        },
    },
    "zone_movements": {
        "subcommands": {
            "list": {
                "fn": commands.list_zone_movements,
                "argparse": {},
            },
            "describe": {
                "fn": commands.describe_zone_movements,
                "argparse": {
                    "--provenance": {"required": False, "default": False, "action": "store_true", "help": "show provenance", },
                },
            },
            "download": {
                "fn": commands.download_zone_movements,
                "argparse": {
                    "--layer": {"required": True, "type": str, "help": "", },
                    "--output-file": {"required": True, "dest": "output_file", "type": str, "help": "", },
                    "--output-format": {"required": False, "dest": "output_format", "default": "csv", "type": str, "help": "", },
                    "--start-date": {"dest": "start_date", "required": False, "type": str, "help": "", },
                    "--end-date": {"dest": "end_date", "required": False, "type": str, "help": "", },
                },
            },
        },
    },
    "population": {
        "subcommands": {
            "list": {
                "fn": commands.list_population_layers,
                "argparse": {},
            },
            "describe": {
                "fn": commands.describe_population,
                "argparse": {
                    "--layer": {"required": True, "type": str, "help": "", },
                    "--provenance": {"required": False, "default": False, "action": "store_true", "help": "show provenance", },
                },
            },
            "download": {
                "fn": commands.download_population,
                "argparse": {
                    "--layer": {"required": True, "type": str, "help": "", },
                    "--output-file": {"required": True, "dest": "output_file", "type": str, "help": "", },
                    "--output-format": {"required": False, "dest": "output_format", "default": "csv", "type": str, "help": "", },
                    "--start-date": {"dest": "start_date", "required": False, "type": str, "help": "", },
                    "--end-date": {"dest": "end_date", "required": False, "type": str, "help": "", },
                },
            },
        },
    },
    "risk": {
        "subcommands": {
            "list": {
                "fn": commands.list_risk,
                "argparse": {},
            },
            "list-dates": {
                "fn": commands.list_risk_dates,
                "argparse": {
                    "--ev": {"dest": "ev", "required": True, "type": str, "help": "", },
                },
            },
            "download": {
                "fn": commands.download_risk,
                "argparse": {
                    "--source-layer": {"dest": "source_layer", "required": True, "type": str, "help": "", },
                    "--target-layer": {"dest": "target_layer", "required": True, "type": str, "help": "", },
                    "--ev": {"dest": "ev", "required": True, "type": str, "help": "", },
                    "--date": {"dest": "date", "required": True, "type": str, "help": "", },
                    "--output-file": {"required": True, "dest": "output_file", "type": str, "help": "", },
                    "--output-format": {"required": False, "dest": "output_format", "default": "csv", "type": str, "help": "", },
                },
            },
        },
    },
}


usage_str = '''
usage: flowmaps-data [-h] COLLECTION [list describe download]

examples: 

    # Geojson layers
    flowmaps-data layers list
    flowmaps-data layers describe --layer cnig_provincias --provenance
    flowmaps-data layers describe --layer cnig_provincias --plot
    flowmaps-data layers download --layer cnig_provincias

    # Consolidated COVID-19 data
    flowmaps-data covid19 list
    flowmaps-data covid19 describe --ev ES.covid_cpro
    flowmaps-data covid19 download --ev ES.covid_cpro --output-file out.csv --output-format csv

    # Population
    flowmaps-data population list
    flowmaps-data population describe --layer cnig_provincias
    flowmaps-data population download --layer zbs_15 --output-file out.csv

    # Origin-destination daily mobility (from MITMA)
    flowmaps-data daily_mobility list
    flowmaps-data daily_mobility list-dates
    flowmaps-data daily_mobility describe
    flowmaps-data daily_mobility download --source-layer cnig_provincias --target-layer cnig_provincias --start-date 2020-10-10 --end-date 2020-10-16 --output-file out.csv

    # Daily zone movements (from MITMA)
    flowmaps-data zone_movements list
    flowmaps-data zone_movements describe
    flowmaps-data zone_movements download --layer cnig_provincias --output-file out.csv --start-date 2020-10-10 --end-date 2020-10-10

    # Raw datasets
    flowmaps-data datasets list
    flowmaps-data datasets describe --ev ES.covid_cpro
    flowmaps-data datasets download --ev ES.covid_cpro --output-file out.csv --output-format csv

    # Mobility Associated Risk
    flowmaps-data risk list
    flowmaps-data risk list-dates
    flowmaps-data risk download --source-layer cnig_provincias --target-layer cnig_provincias --ev ES.covid_cpro --date 2020-10-10 --output-file out.csv --output-format csv
'''

def print_usage():
    print(usage_str)


def execute_command(fn, argparse_spec, commandline):
    parser = argparse.ArgumentParser(description='')
    for arg, options in argparse_spec.items():
        parser.add_argument(arg, **options)
    args = parser.parse_args(commandline)
    fn(**vars(args))


def parse_commandline(config, commandline):
    subcmd = config
    for i, word in enumerate(commandline):
        if word in subcmd:
            subcmd = subcmd[word]
        
        if 'fn' in subcmd:
            # print('calling fn', subcmd['fn'], subcmd['argparse'], commandline[i+1:])
            return execute_command(subcmd['fn'], subcmd['argparse'], commandline[i+1:])
        elif 'subcommands' in subcmd:
            subcmd = subcmd['subcommands']
        else:
            print_usage()
            print(f"Unknown command '{word}'. Available options are: {', '.join(subcmd.keys())}")
            return

    print_usage()
    print(f"Available options are: {', '.join(subcmd.keys())}")


def main():
    commandline = sys.argv[1:]
    parse_commandline(CONFIG, commandline)


if __name__ == '__main__':
    main()
