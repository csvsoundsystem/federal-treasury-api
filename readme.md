## Running
This one command downloads the (new) fixies and converts them to an SQLite3 database.

    ./run

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
