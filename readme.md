## Scheduling
Run this to schedule the thingy to download and parse daily.

    ./crontab.sh | crontab

Run `crontab -e` to edit the schedule later.

## Converting to SQLite
If we want to convert to SQLite, we should write a schema and then use
`.import`. Hmm. Actually, we could also do it within Python with Pandas
or DumpTruck or just sqlite.

## Results
Resulting files go in the `data` directory, to which the `http` directory
is linked (for ScraperWiki compatibility). `fixie` contains the original files,
`daily_csv` contains corresponding csv files, one per table per day, and
`lifetime` contains eight csv files, one per table, with all of the days
stacked (unioned) on top of each other.
