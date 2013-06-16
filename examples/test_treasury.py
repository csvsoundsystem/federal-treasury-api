import nose.tools as n
from pandas import DataFrame
from treasury import treasury

n.assert_equal(
  treasury('''SELECT * FROM "t1" WHERE "date" = '2013-05-22';'''),
  DataFrame(
    {u'account': {0: u'Federal Reserve Account',
      1: u'Supplementary Financing Program Account',
      2: u'Short Term Cash Investments Table V',
      3: u'Total Operating Balance'},
     u'close_today': {0: 25206, 1: 0, 2: 0, 3: 25206},
     u'date': {0: u'2013-05-22',
      1: u'2013-05-22',
      2: u'2013-05-22',
      3: u'2013-05-22'},
     u'day': {0: u'Wednesday', 1: u'Wednesday', 2: u'Wednesday', 3: u'Wednesday'},
     u'footnote': {0: None, 1: None, 2: None, 3: None},
     u'is_total': {0: 0, 1: 0, 2: 0, 3: 1},
     u'open_fy': {0: 85446, 1: 0, 2: 0, 3: 85446},
     u'open_mo': {0: 213863, 1: 0, 2: 0, 3: 213863},
     u'open_today': {0: 31246, 1: 0, 2: 0, 3: 31246},
     u'table': {0: u'TABLE I Operating Cash Balance',
      1: u'TABLE I Operating Cash Balance',
      2: u'TABLE I Operating Cash Balance',
      3: u'TABLE I Operating Cash Balance'}}
  ),
  msg = 'The May 22 table 1 should be correct.'
)

nose.tools.assert_raises(
  ValueError, lambda: treasury('SELECT aoeu'),
  msg = 'Invalid SQL should raise an error.'
)
