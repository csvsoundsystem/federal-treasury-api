## Scheduling
Run this to schedule the thingy to download and parse daily.

    ./crontab.sh | crontab

Run `crontab -e` to edit the schedule later.

## Converting to SQLite
If we want to convert to SQLite, we should write a schema and then use
`.import`. Hmm. Actually, we could also do it within Python with Pandas
or DumpTruck or just sqlite.
