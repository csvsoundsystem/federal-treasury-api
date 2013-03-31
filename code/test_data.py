from foo import parse_fixie

def test(datestamp):
	observed = parse_fixie('data/fixies/' + datestamp)
	expected = pandas.read_csv('data/fixtures/' + datestamp)
	assert observed == expected, datestamp

for fixture in os.listdir('fixtures'):
	test(fixture)