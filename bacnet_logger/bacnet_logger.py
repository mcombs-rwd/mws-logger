#!/usr/bin/env python3

import argparse
import csv
from datetime import datetime
import logging
from logging.config import dictConfig
import pathlib
import time

import BAC0
from ruamel.yaml import YAML

from bacnet_table import BacnetTable, request_dict
from bacnet_controllers import load_controllers

def load_csv(file_name):
    rows = []
    with open(file_name, 'r') as f:
        csv_reader = csv.reader(f)
        for row in csv_reader:
            rows.append(row)
    return rows

def write_csv(file_name, rows):
    with open(file_name, 'a', newline='') as data_file:
        data_writer = csv.writer(data_file)
        for row in rows:
            data_writer.writerow(row)

def setup(config_file, test_mode=False):
    """Return config, controllers. Init BBMD and files."""
    yaml = YAML(typ='safe')
    with open(config_file, 'r') as f:
        config_text = f.read()
        config = yaml.load(config_text)
    controllers = load_controllers(config['automation_servers'])
    logger.info(f"Loaded {len(controllers)} of"
        + f" {len(config['automation_servers'])} controllers.")

    logger.info("Registering to BBMD.")
    if test_mode:
        logger.info('...Mock bacnet bbmd registration')
        bacnet = None
    else:
        try:
            bacnet = BAC0.lite(ip=f"{config['network']['my_ip']}"
                        f"/{config['network']['my_ip_mask']}",
                        bbmdAddress=config['network']['bbmd_ip'])
            BAC0.log_level('error')
        except BAC0.core.io.IOExceptions.InitializationError:
            print(f"Error: The IP address provided"
                + f" ({config['network']['my_ip']}) is invalid.")
            print("Check if another software is using port 47808 on this"
                + " network interface."
                + " If YABE is running, try port 47809 for it."
                + " Find and stop other processes using port 47080 with"
                + " netstat, or currports.")
            exit()
        except KeyboardInterrupt:
            bacnet.disconnect()

    logger.info(f"Polling every {config['poll_interval']} minutes.")
    if config['wide_table'] and not pathlib.Path(config['wide_csv']).exists():
        write_csv(config['wide_csv'], [config['wide_headings']])
    if config['tall_table'] and not pathlib.Path(config['tall_csv']).exists():
        write_csv(config['tall_csv'], [config['tall_headings']])
    return (config, controllers, bacnet)

def poll(config, controllers, bacnet, test_mode=False):
    for controller_count, controller in enumerate(controllers):
        bacnet_results = BacnetTable(controller, config['wide_headings'])
        rd = request_dict(controller.ip, controller.objects)
        logger.debug(rd)
        if test_mode and controller_count == 0:
            logger.info("...loading test data")
            bacnet_results.load_table(load_csv(config['test_csv']))
        if not test_mode:
            logger.info(f"...polling {controller}")
            try:
                response = bacnet.readMultiple(controller.ip, request_dict=rd)
                logger.debug(response)
                if not response or response == ['']:
                    logger.info(f"...Error, no result")
                    continue
                bacnet_results.response = response
            except KeyboardInterrupt:
                bacnet.disconnect()
        if not test_mode and config['tall_table']:
            write_csv(config['tall_csv'], bacnet_results.tall_table())
        if config['wide_table']:
            write_csv(config['wide_csv'], bacnet_results.wide_table())

def main(config_file, test_mode=False):
    (config, controllers, bacnet) = setup(config_file, test_mode)
    while True:
        poll(config, controllers, bacnet, test_mode)
        if test_mode:
            break
        # TODO: Change to use schedule package
        print(f"{datetime.strftime(datetime.now(), '%m-%d %H:%M')}"
                f" Waiting to poll in {config['poll_interval']} minutes.")
        time.sleep(config['poll_interval'] * 60)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description="Logs data from BACnet HVAC devices")
    parser.add_argument("-c", "--config", 
            help="configuration file, default is config.yml", 
            default="config.yml")
    parser.add_argument('-t', '--test', 
            help="test mode doesn't require actual BACnet devices",
            action="store_true")
    args = parser.parse_args()

    yaml = YAML(typ='safe')
    with open('config-logging.yml', 'r') as f:
        logging_config_dict = yaml.load(f)
    dictConfig(logging_config_dict)
    logger = logging.getLogger(__name__)
    logger.info("Program started.")

    main(args.config, args.test)
