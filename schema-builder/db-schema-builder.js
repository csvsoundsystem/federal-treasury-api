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
     db_schema = {
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


function cleanPragmaObj(table_schema, table_name){
  var whitelisted_schema = [];
  _.each(table_schema, function(obj, index){

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
      whitelisted_schema.push(clean_obj);
    };
  });

  return whitelisted_schema;
};

function writeToFile(db_schema){
  console.log('Writing file...');
  fs.writeFileSync('db_schema.json', JSON.stringify(db_schema) );
};

var writeToFile_after = _.after(1, writeToFile); // Limit it to one table for test
// var writeToFile_after = _.after(_.size(db_tables), writeToFile); // Only invoked after all the tables have been processed

function treasuryIo(query){
  return $.ajax({
    url: 'https://premium.scraperwiki.com/cc7znvq/47d80ae900e04f2/sql/?q='+query
  });
};

function createDbSchemaColumnOrder(table_obj, columns_info){
  /* 
  This function adds the names of each column as keys in the `columns` key of the db_schema.
  This would happen automatically in `addColumnInfoToAssociatedTable` but since the column data is fetched asynchronously, the order won't be what we set it to up top.
  By allowing to be in order, the UI might be a bit nicer. Terrible to set the UI positioning on an object's keys because objects are by their nature unordered.
  But go with me here...
  */
  _.each(columns_info, function(column_info){
    table_obj.columns[column_info.name] = null;
  });

  return table_obj;
}


function insertTableToDbSchema(table_data){
  var table_name = table_data.name;
  db_schema.tables[table_name] = table_data;

  console.log('Adding', table_data.name);
  writeToFile_after(db_schema);
};

function addDatatoColumnInfo(column_info, key, values){
  // Make sure they're sorted
  sorted_values = _.sortBy(values, function(val) { return val } );
  column_info[key] = values;
};

function addColumnInfoToAssociatedTable(table_obj, column_name, column_info, insertTableToDbSchema_after){
  console.log('Inserting column', column_name, 'in', table_obj.name)
  table_obj.columns[column_name] = column_info;
  // After all of the columns in this table have been processed we'll add the table object to the db object
  insertTableToDbSchema_after(table_obj);
};


for (var table_name in db_tables){
  if (_.has(db_tables, table_name)){
    if (table_name == 't2'){ // Limit it just to t2 for testing

    // Get a table scheme for each table, use a closure becaue it's done asynchronously and you need to know what table this ajax call refers to
    (function(table_name){
      treasuryIo('PRAGMA table_info(' + table_name +')')
        .done( function(response){

          var column_infos = cleanPragmaObj(response, table_name),
              table_obj = {
                "label": db_tables[table_name].label,
                "name" : table_name,
                "columns": {}
              },
              insertTableToDbSchema_after = _.after(_.size(column_infos), insertTableToDbSchema); // Only invoked after all of the columns in a given table are processed

          // Make the keys for the `columns` key in what will be `db_schema.tables[table_name].columns`, currently `table_obj.columns`, to the order they're given in the config array.
          table_obj = createDbSchemaColumnOrder(table_obj, column_infos);

          // Loop through each column object, which contains a name and a type, that was returned from PRAGMA, again using a closure so it knows what column it's acting on
          _.each(column_infos, function(column_info){
            (function(column_info, table_obj){
              var query_text;

              // We don't want every single integer, so if it's numeric, find the range instead of the DISTINCT values
              if (column_info.type == 'TEXT' && (column_info.name != 'date' && column_info.name != 'year_month')){
                query_text = 'SELECT DISTINCT "' + column_info.name + '" FROM ' + table_obj.name;
              }else{
                query_text = 'SELECT min("' + column_info.name + '") as min, max("' + column_info.name + '") as max FROM ' + table_obj.name;
              };

              treasuryIo(query_text)
                .done( function(response){

                  // Process the json response into a single flat, ascending sorted array of values
                  var values = _.flatten(_.map(response, function(value){ return _.values(value)})),
                      values_with_blank = _.map(values, function(val) { return ((val != null) ? val : '(blank)' )} );

                  // If there's a blank value, make it the last item in the array
                  var blank_index = _.indexOf(values_with_blank, '(blank)');
                  if (blank_index != -1){
                    values_with_blank.move(blank_index, (values_with_blank.length - 1) );
                  };

                  // If we're adding weekdays, make it so that they're sorted Monday - Friday, even if all the days aren't present
                  if (column_info.name == 'weekday'){
                    _.each(weekdays_arr, function(weekday){
                      var weekday_indx = _.indexOf(values_with_blank, weekday);
                      if (weekday_indx != -1){
                        values_with_blank.move(weekday_indx, 0);
                      }; 
                    });
                  };

                  if (column_info.type == 'TEXT'){
                    if (column_info.name == 'date'){
                      addDatatoColumnInfo(column_info, 'date_range', values_with_blank);
                      // The column now has all of its values added, so you can add that completed column information to the designated table
                      addColumnInfoToAssociatedTable(table_obj, column_info.name, column_info, insertTableToDbSchema_after);

                    }else{
                      var addDatatoColumnInfo_after            = _.after(values_with_blank.length, addDatatoColumnInfo),
                          addColumnInfoToAssociatedTable_after = _.after(values_with_blank.length, addColumnInfoToAssociatedTable),
                          column_values                        = [];

                      /* Get information for each value such as name, date range, its limiting parents or if it is a parent */
                      _.each(values_with_blank, function(value){
                        (function(value, column_info, table_obj){
                          var value_obj = {},
                              query_string;

                          if (_.indexOf(db_tables[table_obj.name].type_parents, column_info.name) != -1){
                            /* If the column we're on is not a designated parent item column */
                            query_string = 'SELECT min("date") as min, max("date") as max FROM ' + table_obj.name + ' WHERE "' + column_info.name + '" ' + ((value == '(blank)') ? 'IS NULL' : ("= '" + value + "'") )
                            value_obj.is_parent = true;
                          }else{
                            /* If the column we're on is not a designated parent item column the it's child and we therefore need to query what parents it exists under */
                            query_string = 'SELECT min("date") as min, max("date") as max, ' + _.map(db_tables[table_obj.name].type_parents, function(col){ return '"' + col + '"'}).join(', ') + ' FROM ' + table_obj.name + ' WHERE "' + column_info.name + '" = \'' + value + '\''
                            value_obj.is_parent = false;
                          };

                          treasuryIo(query_string)
                            .done( function(date_range_response){
                              // console.log(date_range_response);
                              value_obj.name       = value;
                              value_obj.date_range = [date_range_response[0].min, date_range_response[0].max];


                              if (date_range_response.parent_item){
                                value_obj.parent_item = date_range_response[0].parent_item;
                              };/* else{
                                value_obj.parent_item = null;
                              }; 
                              This might be useful to add a null field, or it might be easier to just omit it entirely.
                              */

                              // After deleting the min and max and parent_item from the sql response, the remaining object will have the parent_type limiters 
                              delete date_range_response[0].min;
                              delete date_range_response[0].max;
                              // delete date_range_response[0].parent_item;
                              if (!value_obj.is_parent){
                                value_obj.type_parents = _.values(date_range_response[0]);
                              };

                              column_values.push(value_obj);
                              console.log('Processed', value, 'in', column_info.name, 'in', table_obj.name);

                              addDatatoColumnInfo_after(column_info, 'values', column_values);
                              // The column now has all of its values added, so you can add that completed column information to the designated table
                              addColumnInfoToAssociatedTable_after(table_obj, column_info.name, column_info, insertTableToDbSchema_after);

                              /* TODO, add field definition link when that is done and made into a JSON object */
                            });

                        })(value, column_info, table_obj);
                      });
                      
                    };
                  }else{
                    addDatatoColumnInfo(column_info, 'values', values_with_blank);
                    // The column now has all of its values added, so you can add that completed column information to the designated table
                    addColumnInfoToAssociatedTable(table_obj, column_info.name, column_info, insertTableToDbSchema_after);
                  };


                });
            })(column_info, table_obj);
          });
        }); 
    })(table_name);
    } // Limiting t2 if statement for testing
  };
};

