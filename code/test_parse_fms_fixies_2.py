from parse_fms_fixies_2 import strip_table_name

def test_strip_clean_table_name():
    observed = strip_table_name(u'TABLE I Operating Cash Balance')
    assert observed == u'TABLE I Operating Cash Balance'

def test_strip_dirty_table_name():
    observed = strip_table_name(u'TABLE I Operating Cash Balance \xb3')
    assert observed == u'TABLE I Operating Cash Balance'

