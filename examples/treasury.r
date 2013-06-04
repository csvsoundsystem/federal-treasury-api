library(plyr)
library(RJSONIO)

treasury <- function(sql) {
  url = 'https://box.scraperwiki.com/cc7znvq/47d80ae900e04f2/sql/'
  query_string = urlencode({'q':sql})
  ldply(
    fromJSON(url + '?' + query_string),
    function(row) {as.data.frame(t(row))}
  )
}
