CREATE TABLE _t2 (
  "table" TEXT NOT NULL,
  "date" TEXT NOT NULL,
  "day" TEXT NOT NULL,
  "account" TEXT NOT NULL,
  "type" TEXT NOT NULL,
  "subtype" TEXT NOT NULL,
  "item" TEXT NOT NULL,
  "is_total" TEXT NOT NULL,
  "today" INTEGER NOT NULL,
  "mtd" INTEGER NOT NULL,
  "fytd" INTEGER NOT NULL,
  "footnote"
);
.separator ','
.import '../data/lifetime_csv/table_2.csv' _t2
DROP TABLE IF EXISTS t2;
ALTER TABLE _t2 RENAME TO t2;
