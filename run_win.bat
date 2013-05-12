cd C:\Users\User\Documents\GitHub\fms_parser\code
download_and_parse_fms_fixies.py
echo "Downloaded and parsed fixies"

sqlite3  ../data/fms.db < to_sqlite3.sql
echo "Imported to SQLite3"

pause 