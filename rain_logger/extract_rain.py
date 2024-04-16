#!/usr/bin/env python3
# """Download rain gauge data from SFTP server, extract data for a rain gauge."""
import rain_logger.config as config
import csv
import dataclasses
from pathlib import Path
import pysftp


# @dataclasses
# class rainfall:

#     def __init__(self) -> None:
#         name = self.name

def download_rain_file(server, filename, cache_filepath):
    """Connect to SFTP server, get file and store it locally."""
    remote_filepath = Path(server["path"]) / Path(filename)
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    # connect to server, change to path
    with pysftp.Connection(host=server["url"],
            username=server["user"], password=["password"],
            cnopts=cnopts) as sftp:
        print(f"Connected to {server}")
    # get file, store in cache folder
        sftp.get(remote_filepath, cache_filepath)
        print(f"Downloaded {remote_filepath} to {cache_filepath}")
    return


def load_rain_csv(filepath):
    """Load rain CSV"""
    data = []
    with open(filepath, mode="r", encoding="utf-8-sig") as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for observation in csv_reader:
            data.append(observation)
    # print(f"Loaded CSV: {filepath}")
    # print(data[0])
    # print(data[1])
    return data


def prior_24hour_rain(csv, rain_gauge, date):
    """Get total of rain in specified day

    csv has: SampleDate, SampleTime, GaugeName, SampleValue
    output has: inches * 100
    """
    print("Totalling rainfall")
    rain = 0
    # Scan all lines for rain_gauge and date match
    # Add rain to total
    for observation in csv:
        if (observation["GaugeName"] == rain_gauge
                and observation["SampleDate"] == date):
            # print(rain_gauge, observation)
            rain = rain + observation["SampleValue"] * 100
    return rain


def main():
    date_to_total = "12-6-2022"
    CACHE_PATH = Path(config.rain_logger["cache_path"])
    # Download files into cache
    files = []
    for server in config.rain_logger["servers"]:
        for file in server["files"]:
            if False:
                download_rain_file(server, file["filename"], CACHE_PATH)
            files.append(file)
    # Process each file in cache
    rain_gauges = []
    for file in files:
        csv = load_rain_csv(Path(CACHE_PATH) / Path(file["filename"]))
        for rain_gauge in file["rain_gauges"]:
            rain_24h = prior_24hour_rain(csv, rain_gauge["name"], 
                    date_to_total)
            rain_gauges.append(rain_24h)
        print(rain_gauge["name"], date_to_total, rain_24h)


if __name__ == "__main__":
    main()
