# Minter.io Export

Simple python script to export [Minter.io](https://minter.io/) data

## Requirements

    pip -r requirements.txt

## Usage
```
usage: export.py [-h] --api-token API_TOKEN --report-id REPORT_ID --api-method
                 API_METHOD [--date-from DATE_FROM] [--to_date TO_DATE]
                 [--unit {day,week,month}] [--export-file EXPORT_FILE_PATH]

optional arguments:
  -h, --help            show this help message and exit
  --api-token API_TOKEN
                        Minter.io API token. You can get your API token here:
                        https://minter.io/#!/developer/apps/
  --report-id REPORT_ID
                        Minter.io report_id. You can get a report_id from API
                        or web.
  --api-method API_METHOD
                        Minter.io API methods. Full list of API methods here:
                        https://developers.minter.io/reference. Example:
                        "total_followers".
  --date-from DATE_FROM
                        The start of the date range. Format: YYYY-MM-DD.
                        Default: 2010-01-01.
  --to_date TO_DATE     The end of the date range. Format: YYYY-MM-DD.
                        Default: Current date.
  --unit {day,week,month}
                        The level of granularity of the data. Default: "day".
  --export-file EXPORT_FILE_PATH
                        Output file path. Default: "minterio_export.csv"
```

## License

MIT