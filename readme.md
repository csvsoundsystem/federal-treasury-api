## Scheduling
Run this to schedule the thingy to download and parse daily.

    ./crontab.sh | crontab

Run `crontab -e` to edit the schedule later.

## Converting to SQLite
    
    cd code
    sqlite3 ../data/fms.db < to_sqlite3.sql

## Results
Resulting files go in the `data` directory, to which the `http` directory
is linked (for ScraperWiki compatibility). `fixie` contains the original files,
`daily_csv` contains corresponding csv files, one per table per day, and
`lifetime` contains eight csv files, one per table, with all of the days
stacked (unioned) on top of each other.
