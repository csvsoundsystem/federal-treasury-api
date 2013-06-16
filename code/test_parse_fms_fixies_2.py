from parse_fms_fixies_2 import strip_table_name
from test_helpers import check_parse

def test_strip_clean_table_name():
    observed = strip_table_name(u'TABLE I Operating Cash Balance')
    assert observed == u'TABLE I Operating Cash Balance'

def test_strip_dirty_table_name():
    observed = strip_table_name(u'TABLE I Operating Cash Balance \xb3')
    assert observed == u'TABLE I Operating Cash Balance'

def test_table4_text_format():
#   check_parse('06073100')
    check_parse('13020500')
