#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import csv
import datetime
import logging
import time

import requests

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def valid_date(s):
    try:
        return datetime.strptime(s, '%Y-%m-%d')
    except ValueError:
        raise argparse.ArgumentTypeError(
            '{} is not valid date.'.format(s)
        )


class MinterioExporter(object):

    def __init__(self):
        self.api_base = 'https://api.minter.io/v1.0/reports'

    def format_value(self, value):
        if value == 'null':
            return ''
        return value

    def format_data(self, data):
        formatted_data = []
        if 'values' in data:
            keys = list(data['values'].keys())
            head = [''] + keys
            formatted_data.append(head)
            for date in data['series']:
                line = [date]
                for key in keys:
                    line.append(
                        self.format_value(
                            data['values'][key].get(date)
                        )
                    )
                formatted_data.append(line)
        if 'values' not in data and 'categories' in data and 'series' in data:
            idx = 0
            for value in data['series'][0]['data']:
                formatted_data.append(
                    [data['categories'][idx], self.format_value(value)]
                )
                idx += 1
        if 'values' not in data and 'categories' not in data and 'series' in data:
            for value in data['series']:
                formatted_data.append(
                    [value['name'], self.format_value(value['y'])]
                )
        if isinstance(data, list):
            head = []
            keys = data[0].keys()
            for key in keys:
                if isinstance(data[0].get(key), dict):
                    for nested_key in data[0].get(key).keys():
                        head.append('{}__{}'.format(key, nested_key))
                else:
                    head.append(key)
            formatted_data.append(head)
            for obj in data:
                line = []
                for key in keys:
                    if isinstance(obj.get(key), dict):
                        for nested_key in obj.get(key).keys():
                            line.append(
                                self.format_value(
                                    obj.get(key).get(nested_key)
                                )
                            )
                    else:
                        line.append(
                            self.format_value(obj.get(key))
                        )
                formatted_data.append(line)
        return formatted_data

    def _request(self, url, params, iterable=False):
        data = []
        headers = {
            'User-Agent': 'MinterioExporter 1.0'
        }
        while True:
            try:
                response = requests.get(url, params=params, headers=headers, timeout=600)
                if response.status_code == 404:
                    raise Exception('Error. Data not found. Check your `report_id` and `api_method` params')
                if response.status_code == 400:
                    raise Exception('Error. {}'.format(response.json()['error']['message']))
                if response.status_code in [500, 502]:
                    time.sleep(10)
                else:
                    result = response.json()['data']
                    if iterable:
                        if result:
                            params.update({
                                'skip': params['skip'] + 1
                            })
                            data += result
                            logger.info('Fetched {} objects.'.format(len(data)))
                        else:
                            return data
                    else:
                        data = result
                        return data
            except requests.exceptions.RequestException as ex:
                logger.error(ex)
                time.sleep(10)

    def get_data(self, api_token, report_id, api_method, date_from, to_date, unit, iterable=False):
        if api_method in ('followers_online', 'best_time', 'best_time_engagement'):
            raise Exception('This script does not support this method.')
        if api_method in ('top_followers_list', 'top_unfollowers_list', 'top_posts_list'):
            iterable = True
        url = '{api_url}/{report_id}/{api_method}'.format(
            api_url=self.api_base,
            report_id=report_id,
            api_method=api_method
        )
        params = {
            'date_from': date_from,
            'to_date': to_date,
            'unit': unit,
            'access_token': api_token
        }
        if iterable:
            params.update({
                'skip': 0,
                'count': 10000
            })

        data = self._request(url, params, iterable)
        return self.format_data(data)

    def save_data(self, data, export_file_path):
        with open(export_file_path, 'w') as csvfile:
            w = csv.writer(csvfile)
            w.writerows(data)
        logger.info('Done. Lines: {}. File: `{}`.'.format(len(data), export_file_path))
        return True

    def export(self, api_token, report_id, api_method, date_from, to_date, unit, export_file_path):
        if not date_from:
            date_from = '2010-01-01'
        if not to_date:
            now = datetime.datetime.utcnow()
            to_date = now.strftime('%Y-%m-%d')

        data = self.get_data(api_token, report_id, api_method, date_from, to_date, unit)
        return self.save_data(data, export_file_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Export Minter.io data')
    parser.add_argument(
        '--api-token',
        dest='api_token',
        required=True,
        type=str,
        help='Minter.io API token. You can get your API token here: https://minter.io/#!/developer/apps/'
    )
    parser.add_argument(
        '--report-id',
        dest='report_id',
        required=True,
        type=str,
        help='Minter.io report_id. You can get a report_id from API or web.'
    )
    parser.add_argument(
        '--api-method',
        dest='api_method',
        required=True,
        default='top_posts_list',
        type=str,
        help='Minter.io API methods. Full list of API methods here: https://developers.minter.io/reference. '
             'Example: "total_followers".'
    )
    parser.add_argument(
        '--date-from',
        dest='date_from',
        type=valid_date,
        help='The start of the date range. Format: YYYY-MM-DD. Default: 2010-01-01.'
    )
    parser.add_argument(
        '--to_date',
        dest='to_date',
        type=valid_date,
        help='The end of the date range. Format: YYYY-MM-DD. Default: Current date.'
    )
    parser.add_argument(
        '--unit',
        dest='unit',
        default='day',
        choices=['day', 'week', 'month'],
        help='The level of granularity of the data. Default: "%(default)s".'
    )
    parser.add_argument(
        '--export-file',
        dest='export_file_path',
        type=str,
        default='minterio_export.csv',
        help='Output file path. Default: "%(default)s"'
    )
    args = parser.parse_args()
    export = MinterioExporter()
    export.export(**vars(parser.parse_args()))
