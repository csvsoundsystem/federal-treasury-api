#!/usr/bin/env Rscript
library(plyr)
library(utils)
library(RJSONIO)
library(RCurl)

treasury <- function(sql) {
  url = paste('https://box.scraperwiki.com/cc7znvq/47d80ae900e04f2/sql/?q=', URLencode(sql), sep = '')
  handle <- getCurlHandle()
  body <- getURL(url, curl = handle)
  if (200 == getCurlInfo(handle)$response.code) {
    ldply(
      fromJSON(body),
      function(row) {as.data.frame(t(row))}
    )
  } else {
    stop(body)
  }
}

if (!interactive()) {
  print('Operating cash balances for May 22, 2013')
  print(treasury('SELECT * FROM "t1" WHERE "date" = \'2013-05-22\';'))
}
