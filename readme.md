# Federal Treasury API
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

federal-treasury-api` is the first-ever electronically-searchable database of the Federal government's daily cash spending and borrowing. It updates daily and the data can be exported in various formats and loaded into various systems.


### Deploying to ScraperWiki
You can run this on any number of servers, but we happen to be using ScraperWiki.
You can check out their documentation [here](https://beta.scraperwiki.com/help/developer/)

#### SSH
To use ScraperWiki, log in [here](https://beta.scraperwiki.com/login),
make a project, click the "SSH in" link, add your SSH key and SSH in.
Then you can SSH to the box like so.

    ssh cc7znvq@premium.scraperwiki.com

Or add this to your `~/.ssh/config`

    Host fms
    HostName premium.scraperwiki.com
    User cc7znvq

and just run

    ssh fms

#### What this ScraperWiki account is
Some notes about how ScraperWiki works:

* We have a user account in a chroot jail.
* We don't have root, so we install Python packages in a virtualenv.
* Files in `/home/http` get served on the web.
* The database `/home/scraperwiki.sqlite` gets served from the SQLite web API.
    - NOTE: the `home/scraperwiki.sqlite` is simply a symbolic link to `data/treasury_data.db` generated by this command:
    ```ln -s data/treasury_data.db scraperwiki.sqlite```

The directions below still apply for any other service, of course.

## Running
Optionally set up a virtualenv. (You need this on ScraperWiki.)
Run this from the root of the current repository.

    virtualenv env

Install dependencies.

    pip install -r requirements.pip

### POSIX
This one command downloads the (new) fixies and converts them to an SQLite3 database.

    ./run.sh

### Windows
Run everything

    cd parser
    python download_and_parser_fms_fixies.py

## Scheduling

Run `crontab -e` to edit the schedule later.

### Testing

### Parser unit tests
To unit test parser functions, write tests in `tests/parse_fms_fixies.py`,
and then run them with nose.

    cd tests
    nosetests

You might want to write some tests to make sure that a specific table
is perfectly parsed. In order to do that, copy the source fixie and the
intended csv to the `fixtures` directory. (Name them as they would be
named in the `data` folder.) A test will be generated for each of these.

To make sure that the script is still running on ScraperWiki, run

    python tests/is_it_running.py

### Data integrity tests
To make sure that results are reasonable, run the integrity tests.

    cd tests
    python integrity_tests.py

Results will appear in `tests/test_output/%Y-%m-%d.csv`, named after today's
date.

### Monitoring
If you prefix a command with `./monitor.sh` and the command fails, the output
of the command will be sent wherever you specify. In order to use this, you
need to create a `~/.smtpcli.conf`.

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

## Downloaders
`examples` contains some example downloader functions.
[csv/json](https://github.com/csv/json) is a website that serves the data as csv.

## Reseting the database.
If (and only if) you change the parsing engine, you can reset the data by running `reset_data.sh`.  This function will attempt to delete `data/daily_csv`, `data/lifetime_csv`, `data/treasury_data.db`, and then run `python parser/download_and_parse_fms_fixies.py`

## Troubleshooting
If you have a strange error, try deleting the parser output and updating the code
to the latest `master`. You can do this by running `./reset_data.sh`.
