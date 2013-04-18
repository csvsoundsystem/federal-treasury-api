-- Missing data is modeled as the empty string.
==> ../data/lifetime_csv/table_1.csv <==
CREATE TABLE _t2 (
  "table" TEXT NOT NULL,
  "date" TEXT NOT NULL,
  "day" TEXT NOT NULL,
  "account" TEXT NOT NULL,
is_total,close_today,open_today,open_mo,open_fy,footnote
  "type" TEXT NOT NULL,
  "subtype" TEXT NOT NULL,
  "item" TEXT NOT NULL,
  "is_total" TEXT NOT NULL,
  "today" FLOAT NOT NULL,
  "mtd" FLOAT NOT NULL,
  "fytd" FLOAT NOT NULL,
  "footnote"
);

==> ../data/lifetime_csv/table_2.csv <==
table,date,day,account,type,subtype,item,is_total,today,mtd,fytd,footnote
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

==> ../data/lifetime_csv/table_3.csv <==
table,date,day,account,type,subtype,item,is_total,today,mtd,fytd,footnote

==> ../data/lifetime_csv/table_4.csv <==
table,date,day,surtype,type,subtype,item,is_total,today,mtd,fytd,footnote

==> ../data/lifetime_csv/table_5.csv <==
table,date,day,surtype,type,subtype,item,is_total,today,mtd,fytd,footnote

==> ../data/lifetime_csv/table_6.csv <==
table,date,day,type,item,is_total,close_today,open_today,open_mo,open_fy,footnote

==> ../data/lifetime_csv/table_7.csv <==
table,date,day,type,classification,is_total,today,mtd,fytd,footnote

==> ../data/lifetime_csv/table_8.csv <==
table,date,day,type,classification,is_total,today,mtd,fytd,footnote
.separator ','


.import '../data/lifetime_csv/table_2.csv' _t2
DROP TABLE IF EXISTS t2;
ALTER TABLE _t2 RENAME TO t2;
