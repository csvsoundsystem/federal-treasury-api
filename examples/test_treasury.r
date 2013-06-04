library(testthat)
source('treasury.r')
load('test_treasury.RData') # Load may.22

test_that('treasury(sql) function', {
  expect_that(treasury('SELECT * FROM "t1" WHERE "date" = \'2013-05-22\';'), equals(may.22))
  expect_that(treasury('SELEC-nhaoesaoeuhasouesnaouhsaoe2013-05-22\';'), throws_error())
})
