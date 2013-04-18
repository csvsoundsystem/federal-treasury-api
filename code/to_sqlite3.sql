-- Missing data is modeled as the empty string.
CREATE TABLE _t2 (
  "table" TEXT NOT NULL,
  "date" TEXT NOT NULL,
  "day" TEXT NOT NULL,
  "account" TEXT NOT NULL,
  "type" TEXT NOT NULL,
  "subtype" TEXT NOT NULL,
  "item" TEXT NOT NULL,
  "is_total" TEXT NOT NULL,
  "today" FLOAT NOT NULL,
  "mtd" FLOAT NOT NULL,
  "fytd" FLOAT NOT NULL,
  "footnote"
);
.separator ','
.import '../data/lifetime_csv/table_2.csv' _t2
DROP TABLE IF EXISTS t2;
ALTER TABLE _t2 RENAME TO t2;
