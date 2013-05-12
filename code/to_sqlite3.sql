-- Import the lifetime CSV files to sqlite

-- CSV
.separator ','

-- Missing data is modeled as the empty string.

CREATE TABLE _t1 (
  "table" TEXT NOT NULL,
  "date" TEXT NOT NULL,
  "day" TEXT NOT NULL,
  "account" TEXT NOT NULL,
  "is_total" TEXT NOT NULL,
  "close_today" FLOAT NOT NULL,
  "open_today" FLOAT NOT NULL,
  "open_mo" FLOAT NOT NULL,
  "open_fy" FLOAT NOT NULL,
  "footnote"
);

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

CREATE TABLE _t3 (
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

CREATE TABLE _t4 (
  "table" TEXT NOT NULL,
  "date" TEXT NOT NULL,
  "day" TEXT NOT NULL,
  "surtype" TEXT NOT NULL,
  "type" TEXT NOT NULL,
  "subtype" TEXT NOT NULL,
  "item" TEXT NOT NULL,
  "is_total" TEXT NOT NULL,
  "today" FLOAT NOT NULL,
  "mtd" FLOAT NOT NULL,
  "fytd" FLOAT NOT NULL,
  "footnote"
);

CREATE TABLE _t5 (
  "table" TEXT NOT NULL,
  "date" TEXT NOT NULL,
  "day" TEXT NOT NULL,
  "surtype" TEXT NOT NULL,
  "type" TEXT NOT NULL,
  "subtype" TEXT NOT NULL,
  "item" TEXT NOT NULL,
  "is_total" TEXT NOT NULL,
  "today" FLOAT NOT NULL,
  "mtd" FLOAT NOT NULL,
  "fytd" FLOAT NOT NULL,
  "footnote"
);

CREATE TABLE _t6 (
  "table" TEXT NOT NULL,
  "date" TEXT NOT NULL,
  "day" TEXT NOT NULL,
  "type" TEXT NOT NULL,
  "item" TEXT NOT NULL,
  "is_total" TEXT NOT NULL,
  "close_today" FLOAT NOT NULL,
  "open_today" FLOAT NOT NULL,
  "open_mo" FLOAT NOT NULL,
  "open_fy" FLOAT NOT NULL,
  "footnote"
);

CREATE TABLE _t7 (
  "table" TEXT NOT NULL,
  "date" TEXT NOT NULL,
  "day" TEXT NOT NULL,
  "type" TEXT NOT NULL,
  "classification" TEXT NOT NULL,
  "is_total" TEXT NOT NULL,
  "today" FLOAT NOT NULL,
  "mtd" FLOAT NOT NULL,
  "fytd" FLOAT NOT NULL,
  "footnote"
);

CREATE TABLE _t8 (
  "table" TEXT NOT NULL,
  "date" TEXT NOT NULL,
  "day" TEXT NOT NULL,
  "type" TEXT NOT NULL,
  "classification" TEXT NOT NULL,
  "is_total" TEXT NOT NULL,
  "today" FLOAT NOT NULL,
  "mtd" FLOAT NOT NULL,
  "fytd" FLOAT NOT NULL,
  "footnote"
);

.import '../data/lifetime_csv/table_1.csv' _t1
DROP TABLE IF EXISTS t1;
ALTER TABLE _t1 RENAME TO t1;

.import '../data/lifetime_csv/table_2.csv' _t2
DROP TABLE IF EXISTS t2;
ALTER TABLE _t2 RENAME TO t2;

.import '../data/lifetime_csv/table_3.csv' _t3
DROP TABLE IF EXISTS t3a;
ALTER TABLE _t3 RENAME TO t3a;

.import '../data/lifetime_csv/table_4.csv' _t4
DROP TABLE IF EXISTS t3b;
ALTER TABLE _t4 RENAME TO t3b;

.import '../data/lifetime_csv/table_5.csv' _t5
DROP TABLE IF EXISTS t3c;
ALTER TABLE _t5 RENAME TO t3c;

.import '../data/lifetime_csv/table_6.csv' _t6
DROP TABLE IF EXISTS t4;
ALTER TABLE _t6 RENAME TO t4;

.import '../data/lifetime_csv/table_7.csv' _t7
DROP TABLE IF EXISTS t5;
ALTER TABLE _t7 RENAME TO t5;

.import '../data/lifetime_csv/table_8.csv' _t8
DROP TABLE IF EXISTS t6;
ALTER TABLE _t8 RENAME TO t6;
