import nose.tools as n

def test_get_table_name():
	observed = get_table_name('jklsdfljkdsfjlkdsf')
	expected = 'jlsdfnfnsllnksfnnenjo3494oiw3iow4io'
	n.assert_string_equal(observed, expected)