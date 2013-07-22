var _          = require('underscore'),
		$          = require('jquery'),
		fs 				 = require('fs');

var weekdays_arr = ['Friday', 'Thursday', 'Wednesday', 'Tuesday', 'Monday'], // This is in reverse order because it will be used to sort or weekday array by putting the days first going in order Friday to Monday.
  table_names = {
  	't1': "t1: Operating Cash Balance",
    't2': "t2: Deposits and Withdrawals",
    't3a': "t3a: Public Debt Transactions",
    't3b': "t3b: Adjustment of Public Debt Transactions",
    't3c': "t3c: Debt Subject to Limit",
    't4': "t4: Federal Tax Deposits",
    't5': "t5: Short-Term Cash Investments",
    't6': "t6: Income Tax Refunds Issued"
   },
   table_schema = {
      "tables":{ 
        "t1": {},
        "t2": {},
        "t3": {},
        "t3a": {},
        "t3b": {},
        "t3c": {},
        "t4": {},
        "t5": {},
        "t6": {},
      },
      "types":[
        {
          "name":"TEXT",
          "operators":[
            {
              "name":"=",
              "label":"is",
            },
            {
              "name":"<>",
              "label":"is not",
            }
          ]
        },
        {
          "name":"DATE",
          "operators":[
            {
              "name":"=",
              "label":"is",
            },
            {
              "name":"<>",
              "label":"is not",
            },
            {
              "name":"<",
              "label":"is before",
            },
            {
              "name":">",
              "label":"is after",
            }
          ]
        },
        {
          "name":"INTEGER",
          "operators":[
            {
              "name":"=",
              "label":"is",
            },
            {
              "name":"<>",
              "label":"is not",
            },
            {
              "name":"<",
              "label":"less than",
            },
            {
              "name":">",
              "label":"greater than",
            }
          ]
        }
      ]
    },
    tables = [];


String.prototype.contains = function(it) { return this.indexOf(it) != -1; };

Array.prototype.move = function (old_index, new_index) {
    while (old_index < 0) {
        old_index += this.length;
    }
    while (new_index < 0) {
        new_index += this.length;
    }
    if (new_index >= this.length) {
        var k = new_index - this.length;
        while ((k--) + 1) {
            this.push(undefined);
        }
    }
    this.splice(new_index, 0, this.splice(old_index, 1)[0]);
    /* return this; // for testing purposes */
};


function cleanPragmaObj(json){
	var clean_json = [];
	_.each(json, function(obj, index){
		delete obj.cid;
		delete obj.notnull;
		delete obj.dflt_value;
		delete obj.pk;

		// Remove certain columns 
		if (obj.name != 'url' && obj.name != 'table' && obj.name != 'footnote' && obj.name.contains('raw') == false){
			clean_json.push(obj);
		};
	});

	return clean_json;
};

function writeToFile(table_schema){
  console.log('Writing file...');
  // var sorted_tables_arr = _.sortBy(tables_arr, function(table) { return table.name}); // Sort the final json so the tables are in order
  // table_schema.tables = sorted_tables_arr;

	fs.writeFileSync('table_schema.json', JSON.stringify(table_schema) );
};

var writeToFile_after = _.after(_.size(table_names), writeToFile); // Only invoked after all the tables have been processed

function treasuryIo(query){
  return $.ajax({
    url: 'https://premium.scraperwiki.com/cc7znvq/47d80ae900e04f2/sql/?q='+query
  });
};


function addValuesToColumn(obj_to_push){
  var table_name = obj_to_push.name;
  table_schema.tables[table_name] = obj_to_push;

  console.log('Adding', obj_to_push.name);
  writeToFile_after(table_schema);
};


for (var table_name in table_names){
	if (_.has(table_names, table_name)){

    // Get a table scheme for each table, use a closure becaue it's done asynchronously and you need to know what table this ajax call refers to
		(function(table_name){
			treasuryIo('PRAGMA table_info(' + table_name +')')
				.done( function(response){

				  var name_types = cleanPragmaObj(response),
				      table_obj = {
				      	"label": table_names[table_name],
				      	"name" : table_name,
                "columns": {}
				      };

          var addValuesToColumn_after = _.after(_.size(name_types), addValuesToColumn); // Only invoked after all of the columns in a given table are processed

          // Loop through each item that was returned from PRAGMA, again using a closure so it knows what column it's acting on
          _.each(name_types, function(name_type){
            (function(name_type, table_obj){
              var query_text;

              // We don't want every single integer, so if it's numeric, find the range instead of the DISTINCT values
              if (name_type.type == 'TEXT' && (name_type.name != 'date' && name_type.name != 'year_month')){
                query_text = 'SELECT DISTINCT "' + name_type.name + '" FROM ' + table_obj.name;
              }else{
                query_text = 'SELECT min("' + name_type.name + '") as min, max("' + name_type.name + '") as max FROM ' + table_obj.name;
              };

              treasuryIo(query_text)
                .done( function(response){

                  // Process the json response into a single flat, ascending sorted array of values
					  			var values = _.flatten(_.map(response, function(value){return _.values(value)})),
                      values_with_blank = _.map(values, function(val) { return ((val != null) ?  val :  '(blank)' )} ),
                      sorted_values_with_blank = _.sortBy(values_with_blank, function(val) {  return val  } );

                  // If there's a blank value, make it the last item in the array
                  var blank_index = _.indexOf(sorted_values_with_blank, '(blank)');
                  if (blank_index != -1){
                    sorted_values_with_blank.move(blank_index, (sorted_values_with_blank.length - 1) );
                  };

                  // If we're adding weekdays, make it so that they're sorted Monday - Friday, even if all the days aren't present
                  if (name_type.name == 'weekday'){
                    _.each(weekdays_arr, function(weekday){
                      var weekday_indx = _.indexOf(sorted_values_with_blank, weekday);
                      if (weekday_indx != -1){
                        sorted_values_with_blank.move(weekday_indx, 0);
                      }; 
                    });
                  };

					  			name_type['values'] = sorted_values_with_blank
					  			table_obj.columns[name_type.name] = name_type;
                  addValuesToColumn_after(table_obj);

                });
            })(name_type, table_obj);
          });
				}); 
		})(table_name)
	};
};

