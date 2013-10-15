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

## About the data
There are eight tables.

* I. Operating Cash Balance (`t1`)
* II. Deposits and Withdrawals (`t2`)
* IIIa. Public Debt Transactions (`t3a`)
* IIIb. Adjustment of Public Dept Transactions to Cash Basis (`t3b`)
* IIIc. Debt Subject to Limit (`t3c`)
* IV. Federal Tax Deposits (`t4`)
* V. Short-term Cash Investments (`t5`)
* VI. Incom Tax Refunds Issued (`t6`)

Check out our comprehensive [data dictionary](https://github.com/csvsoundsystem/federal-treasury-api/wiki/Treasury.io-Data-Dictionary) and [treasury.io](http://treasury.io) for more information.


## ABOUT THIS BRANCH
the `just-the-api` branch of `federal-treasury-api` contains just the code needed to download the data locally and host a queryable api. `master` contains code specific to running on ScraperWiki.


## Dependencies

    pip install -r requirements.pip


## Obtaining the data
### POSIX / MAC OSX
This one command downloads the (new) fixies and converts them to an SQLite3 database.

    ./run.sh

_Warning_: this will take a while... ~10-15 minutes on my laptop.

### Windows
Run everything

    cd parser
    python download_and_parse_fms_fixies.py

## Starting the API
First run this:

    python api.py

Now navigate to [http://localhost:5000/](http://localhost:5000/)

## Querying the API
parameters:

  - `q`= A url-encoded SQL query
  - `format` = `json` or `csv`

example:

[http://localhost:5000/?q=SELECT * FROM t2 LIMIT 10](http://localhost:5000/?q=SELECT%20*%20FROM%20t2%20LIMIT%2010)

## Testing the data
This one command tests whether the data is up-to-date, what values are null, if any, and if there are any new line items in the data that we're not yet aware of. 

```
./test.sh
```
`test.sh` is also run with `run.sh`

####Optional emails:
If you'd like these tests to be emailed every day, you can register a free app at [http://postmarkapp.com](http://postmarkapp.com).  You'll then want to to configure `postmark.yml` with your credentials:

```
from: mypostmarkemail@domain.com
to: mypersonalgmail+federal-treasury-api-tests@gmail.com
api_key: dfasfdsdga-dgasg-gdsag-dgasgd-dgasdg
```

## Cron
Run everything each day around 4:30 - right after the data has been released.

```
30 16 * * * cd path/to/federal-treasury-api && ./run.sh
```

####Optional: set up logging
```
30 16 * * * cd path/to/federal-treasury-api && ./run.sh >> run.log 2>> err.log
```

