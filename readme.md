## Running
Install dependencies.

    pip install -r requirements.pip

This one command downloads the (new) fixies and converts them to an SQLite3 database.

    ./run

Then serve the web api like so.

    ./api.py

## Scheduling
Run this to schedule the above script to run daily.

    crontab -l > /tmp/crontab
    ./crontab.sh >> /tmp/crontab
    cat /tmp/crontab | crontab
    rm /tmp/crontab

Run `crontab -e` to edit the schedule later.

## Results
Resulting files go in the `data` directory, to which the `http` directory
is linked (for ScraperWiki compatibility). `fixie` contains the original files,
`daily_csv` contains corresponding csv files, one per table per day, and
`lifetime` contains eight csv files, one per table, with all of the days
stacked (unioned) on top of each other.

## Tables
There are eight tables.

* I. Operating Cash Balance (`t1`)
* II. Deposits (`t2a`) and Withdrawals (`t2b`)
* IIIa. Public Debt Transactions (`t3a`)
* IIIb. Adjustment of Public Dept Transactions to Cash Basis (`t3b`)
* IIIc. Debt Subject to Limit (`t3c`)
* IV. Federal Tax Deposits (first half of `t4_t5`)
* V. Short-term Cash Investments (second half of `t4_t5`)
* VI. Incom Tax Refunds Issued (`t6`)
