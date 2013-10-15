import flask
import json
from flask import request
import dataset
import StringIO
import csv

app = flask.Flask(__name__)
db = dataset.connect('sqlite:///data/treasury_data.db')


# csv ouput
def row2string(row):
    si = StringIO.StringIO()
    cw = csv.writer(si)
    cw.writerow(row)
    return si.getvalue().strip('\r\n')

@app.route("/")
def query():

  # parse args
  query = request.args.get('q', 'SELECT * FROM t2 LIMIT 100')
  format = request.args.get('format', 'json')
  
  results = [r for r in db.query(query)]

  if format == 'json':
    return json.dumps(results)
  elif format == 'csv':
    header = row2string(results[0].keys()) + "\n"
    data = "\n".join([row2string(r.values()) for r in results])
    return header + data
  
if __name__ == "__main__":
  app.debug = True
  app.run(host='0.0.0.0', port=5000)