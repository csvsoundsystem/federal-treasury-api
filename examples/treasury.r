library(plyr)
library(utils)
library(RJSONIO)

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

print(treasury('SELECT * FROM "t1" WHERE "date" = \'2013-05-22\';'))
print(treasury('SELEC-nhaoesaoeuhasouesnaouhsaoe2013-05-22\';'))
