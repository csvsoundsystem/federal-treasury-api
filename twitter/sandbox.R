#!/usr/bin/env Rscript
library(plyr)
library(utils)
library(RJSONIO)
library(RCurl)

treasury <- function(sql) {
  url = paste('https://premium.scraperwiki.com/cc7znvq/47d80ae900e04f2/sql/?q=', URLencode(sql), sep = '')
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

sql = "SELECT * FROM t2 WHERE item='Medicare' ORDER BY date DESC LIMIT 90"
medicare <- treasury(sql)
x <- sqrt(as.numeric(medicare$today))
medicare[80:84,]
z <- (x - mean(x)) / sd(x)
plot(z, type="l")

setwd("~/Dropbox/code/fms_parser/data/lifetime_csv")

d <- read.csv("table_ii.csv")
head(d)

