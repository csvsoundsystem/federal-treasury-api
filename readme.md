## Git branches

We develop on `master`, and we deploy to `gh-pages`.

## Running
Optionally set up a virtualenv. (You need this on ScraperWiki.)
Run this from the root of the current repository.

    virtualenv env

Install dependencies.

    pip install -r requirements.pip

### POSIX
This one command downloads the (new) fixies and converts them to an SQLite3 database.

    ./run.sh

Then serve the web api like so.

    ./api.py

### Windows
Run everything

    run.bat

Serve the API locally.

    python api.py

## Scheduling

### POSIX
Run this to schedule the above script to run daily.

    crontab -l > /tmp/crontab
    ./crontab.sh >> /tmp/crontab
    cat /tmp/crontab | crontab
    rm /tmp/crontab

Run `crontab -e` to edit the schedule later.

### Windows
In the Task Scheduler, set `run.bat` to run every day at 5 pm.

### Testing
To make sure that the script is still running on ScraperWiki, run

    ./is_it_running.py

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
* IV. Federal Tax Deposits (`t4`)
* V. Short-term Cash Investments (`t5`)
* VI. Incom Tax Refunds Issued (`t6`)

## Frontend
    python -m SimpleHTTPServer

then visit http://localhost:8000

## Downloaders
`examples` contains some example downloader functions.
[csv/json](https://github.com/csv/json) is a website that serves the data as csv.
