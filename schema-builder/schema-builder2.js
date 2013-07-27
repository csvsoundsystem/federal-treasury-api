var _          = require('underscore'),
    $          = require('jquery'),
    fs         = require('fs');

var weekdays_arr = ['Friday', 'Thursday', 'Wednesday', 'Tuesday', 'Monday'], // This is in reverse order because it will be used to sort or weekday array by putting the days first going in order Friday to Monday.
    db_tables  = {
      "t1": {
        "label": "t1: Operating Cash Balance",
        "type_parents": null
      },
      "t2": { 
        "label": "t2: Deposits and Withdrawals",
        "whitelisted_cols": ["date", "account", "type", "item", "today", "mtd", "fytd"],
        "type_parents": ["account", "type"]
      },
      "t3a": { 
        "label": "t3a: Public Debt Transactions",
        "type_parents": null
      },
      "t3b": { 
        "label": "t3b: Adjustment of Public Debt Transactions",
        "type_parents": null
      },
      "t3c": { 
        "label": "t3c: Debt Subject to Limit",
        "type_parents": null
      },
      "t4": { 
        "label": "t4: Federal Tax Deposits",
        "type_parents": null
      },
        "t5": { 
        "label": "t5: Short-Term Cash Investments",
        "type_parents": null
      },
      "t6": { 
        "label": "t6: Income Tax Refunds Issued",
        "type_parents": null
      }
     },
     table_schema = {
        "tables": { 
          "t1":  {},
          "t2":  {},
          "t3":  {},
          "t3a": {},
          "t3b": {},
          "t3c": {},
          "t4":  {},
          "t5":  {},
          "t6":  {},
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


function cleanPragmaObj(json, table_name){
  var clean_json = [];
  _.each(json, function(obj, index){

    /* 
    The PRAGMA command returns an object with a bunch of properties, we only want the name and type though 
    */
    var clean_obj = {
      name: obj.name,
      type: obj.type
    };

    /* 
    Only include the whitelisted columns for each table.
    We don't need to include columns such as "url" beause you're not going to do a WHERE query on the url.
    Nor do we need "year_month" because we'll have a datepicker
    */
    if (_.indexOf(db_tables[table_name].whitelisted_cols, clean_obj.name) != -1 ){
      clean_json.push(clean_obj);
    };
  });

  return clean_json;
};

function writeToFile(table_schema){
  console.log('Writing file...');
  fs.writeFileSync('table_schema2.json', JSON.stringify(table_schema) );
};

var writeToFile_after = _.after(1, writeToFile); // Limit it to one table for test
// var writeToFile_after = _.after(_.size(db_tables), writeToFile); // Only invoked after all the tables have been processed

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


for (var table_name in db_tables){
  if (_.has(db_tables, table_name)){
    if (table_name == 't2'){ // Limit it just to t2 for testing

    // Get a table scheme for each table, use a closure becaue it's done asynchronously and you need to know what table this ajax call refers to
    (function(table_name){
      treasuryIo('PRAGMA table_info(' + table_name +')')
        .done( function(response){

          var name_types = cleanPragmaObj(response, table_name),
              table_obj = {
                "label": db_tables[table_name].label,
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
                  var values = _.flatten(_.map(response, function(value){ return _.values(value)})),
                      values_with_blank = _.map(values, function(val) { return ((val != null) ? val : '(blank)' )} ),
                      sorted_values_with_blank = _.sortBy(values_with_blank, function(val) { return val } );

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

                  if (name_type.type == 'TEXT'){
                    if (name_type.name == 'date'){
                      name_type['date_range'] = sorted_values_with_blank;
                    }else{
                      /* Get information for each value such as name, date range, its limiting parents or if it is a parent */
                      _.each(sorted_values_with_blank, function(value){
                        (function(value, name_type, table_obj){
                          var value_obj = {},
                              query_string;

                          if (_.indexOf(db_tables[table_obj.name].type_parents, name_type.name) != -1){
                            /* If the column we're on is not a designated parent item column */
                            query_string = 'SELECT min("date") as min, max("date") as max FROM ' + table_obj.name + ' WHERE "' + name_type.name + '" ' + ((value == '(blank)') ? 'IS NULL' : ("= '" + value + "'") )
                            value_obj.is_parent = true;
                          }else{
                            /* If the column we're on is not a designated parent item column the it's child and we therefore need to query what parents it exists under */
                            query_string = 'SELECT min("date") as min, max("date") as max, ' + _.map(db_tables[table_obj.name].type_parents, function(col){ return '"' + col + '"'}).join(', ') + ' FROM ' + table_obj.name + ' WHERE "' + name_type.name + '" = \'' + value + '\''
                            value_obj.is_parent = false;
                          };

                          treasuryIo(query_string)
                            .done( function(date_range_response){
                              // console.log(date_range_response);
                              value_obj.date_range = [date_range_response[0].min, date_range_response[0].max];


                              if (date_range_response.parent_item){
                                value_obj.parent_item = date_range_response[0].parent_item
                              };

                              // After deleting the min and max and parent_item, the remaining object will have the parent_type limiters 
                              delete date_range_response[0].min;
                              delete date_range_response[0].max;
                              // delete date_range_response[0].parent_item;
                              if (!value_obj.is_parent){
                                value_obj.type_parents = _.values(date_range_response[0]);
                              };

                              console.log(value_obj);


                              /* TODO, add field definition link when that is done and made into a JSON object */
                            });

                        })(value, name_type, table_obj);
                      });
                      
                    }
                  }else{
                    name_type['values'] = sorted_values_with_blank;
                  };

                  table_obj.columns[name_type.name] = name_type;


                  addValuesToColumn_after(table_obj);

                });
            })(name_type, table_obj);
          });
        }); 
    })(table_name);
    } // Limiting t2 if statement for testing
  };
};

