# _just the_ Federal Treasury API
```
   ‹
   €     |    |     €€€€≤±‹€€€€≤±‹
   €    .| -- | -+
   €   ' |    |  |  €€€€≤±±≤€€€€€€€€€€€€≤±±≤€€€€€≤±
   €    `|    |
   €     |`.  |     €€€€≤±±≤€€€€€€€€€€€€≤±±≤€€€€€≤±
   €     |  `.|
   €     |    |`.   €€€€≤±±≤€€€€€€€€€€€€≤±±≤€€€€€≤±
   € +   |    |   '
   € | _ | __ | _'   €€€≤±±≤€€€€€€€€€€€€≤±±≤€€€€€≤±
   €     |    |
   €€€€€€€€€€€€€€€€€€€€€€≤±±≤€€€€€€€€€€€€≤±±≤€€€€€≤±
   €
   €€€€€€€€€€€€€€€€€€€€€€≤±±≤€€€€€€€€€€€€≤±±≤€€€€€≤±
   €
   €                      ﬂ±≤€€€€€€€€€€€€≤±±≤€€€€€≤±
   €                                      ﬂ±≤€€€€€≤±
   €
   €
```

`federal-treasury-api` is the first-ever electronically-searchable database of the Federal government's daily cash spending and borrowing. It updates daily and the data can be exported in various formats and loaded into various systems.


## ABOUT THIS BRANCH
the `just-the-api` branch of `federal-treasury-api` contains just the code needed to download the data locally and host a queryable api. `master` contains code specific to running on ScraperWiki.


## Dependencies

    pip install -r requirements.pip


## Obtaining the data
### POSIX
This one command downloads the (new) fixies and converts them to an SQLite3 database.

    ./run.sh

### Windows
Run everything

    cd parser
    python download_and_parse_fms_fixies.py

## Starting the API
First run this:

    python api.py

Now navigate to [http://localhost:5000/](http://localhost:5000/)


Run `crontab -e` to edit the schedule later.

### Testing

## Tables
There are eight tables.

* I. Operating Cash Balance (`t1`)
* II. Deposits and Withdrawals (`t2`)
* IIIa. Public Debt Transactions (`t3a`)
* IIIb. Adjustment of Public Dept Transactions to Cash Basis (`t3b`)
* IIIc. Debt Subject to Limit (`t3c`)
* IV. Federal Tax Deposits (`t4`)
* V. Short-term Cash Investments (`t5`)
* VI. Incom Tax Refunds Issued (`t6`)

