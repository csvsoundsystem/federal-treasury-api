var fs = require('fs')
var _ = require('underscore')
var request = require('request')
var verbose = true

var dsv = require('./dsv.js')

function nestItemDescs(json){
  var nest = {};
  _.each(json, function(item){
    if (!nest[item.table]) { nest[item.table] = {} };
    nest[item.table][item.item_name] = {}
    nest[item.table][item.item_name].description = item.description;
    nest[item.table][item.item_name].url = item.url;
  })
  return nest;
}

var item_desc      = fs.readFileSync('./schema-builder/TreasuryIO_ItemDescriptions.csv', 'utf-8'),
    item_desc_json = dsv.csv.parse(item_desc),
    item_desc_nest = nestItemDescs(item_desc_json);

var weekdays_arr = ['Friday', 'Thursday', 'Wednesday', 'Tuesday', 'Monday'], // This is in reverse order because it will be used to sort or weekday array by putting the days first going in order Friday to Monday.
    db_tables  = {
      "t1": {
        "label": "t1: Operating Cash Balance",
        "whitelisted_cols": ["date",],
        "type_parents": ["is_total"]
      },
      "t2": { 
        "label": "t2: Deposits and Withdrawals",
        "whitelisted_cols": ["date", "transaction_type", "item"],
        "type_parents": ["account", "transaction_type", "is_total", "parent_item"]
      },
      "t3a": { 
        "label": "t3a: Public Debt Transactions",
        "whitelisted_cols": ["date", "transaction_type"],
        "type_parents": ["transaction_type", "debt_type", "is_total", "parent_item"]
      },
      "t3b": { 
        "label": "t3b: Adjustment of Public Debt Transactions",
        "whitelisted_cols": ["date", "transaction_type"],
        "type_parents": ["transaction_type", "is_total", "parent_item"]
      },
      "t3c": { 
        "label": "t3c: Debt Subject to Limit",
        "whitelisted_cols": ["date", "item"],
        "type_parents": ["is_total", "parent_item"]
      },
      "t4": { 
        "label": "t4: Federal Tax Deposits",
        "whitelisted_cols": ["date", "classification"],
        "type_parents": ["type", "is_total"]
      },
        "t5": { 
        "label": "t5: Short-Term Cash Investments",
        "whitelisted_cols": ["date", "transaction_type"],
        "type_parents": ["transaction_type", "is_total"]
      },
      "t6": { 
        "label": "t6: Income Tax Refunds Issued",
        "whitelisted_cols": ["date", "refund_type"],
        "type_parents": ["refund_method"]
      }
     },
     db_schema = {
        "tables": { 
          "t1":  {},
          "t2":  {},
          "t3a": {},
          "t3b": {},
          "t3c": {},
          "t4":  {},
          "t5":  {},
          "t6":  {}
        }
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

function distinctWhere(list_obj, value){
  var vals = [],
      uniq_vals = [];
  _.each(list_obj, function(obj){
    var val = obj[value];
    vals.push(val);
  });
  uniq_vals = _.uniq(vals);
  return uniq_vals;
};

function getKeyByValue(object, value){
  var key_list = [];
  for( var prop in object ) {
    if( object.hasOwnProperty( prop ) ) {
      if( object[ prop ] === value )
        key_list.push(prop);
    };
  };
  return key_list;
};

function reportStatus(msgs){
  var msg;
  if (verbose == true){
    msg = msgs.join('---')
    console.log(msg);
  };
};

function grabAllCols(table_schema){
  var all_cols = [];
  _.each(table_schema, function(obj, index){

    /* 
    The PRAGMA command returns an object with a bunch of properties, we only want the name though
    */
    all_cols.push(obj.name)
  });

  // Move `url` to the last item in the array so that it displays nicer on the internets when we preview the query, it's also pretty ancillary info, so put it last
  var url_index = _.indexOf(all_cols, 'url');
  all_cols.move(url_index, all_cols.length - 1);

  return all_cols;
}

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
  reportStatus(['Writing file...']);
  fs.writeFileSync('./http/db_schema.js', JSON.stringify(db_schema));
};

/* var writeToFile_after = _.after(1, writeToFile); // Limit it to one table for test */
var writeToFile_after = _.after(_.size(db_tables), writeToFile); // Only invoked after all the tables have been processed

function treasuryIo(query, cb){
  var uid = _.uniqueId()
  var endpoint = 'http://premium.scraperwiki.com/cc7znvq/47d80ae900e04f2/sql/?q='
  request(endpoint + query, function (err, response, body) {
    if (err) {
      return cb(err)
    }
    cb(null, JSON.parse(body))
  })
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

  reportStatus(['Inserting', table_data.name, 'to db_schema']);
  writeToFile_after(db_schema);
};

function addDatatoColumnInfo(column_info, key, values){
  // Make sure they're sorted
  _.sortBy(values, function(val) { return val } );
  column_info[key] = values;
};

function addColumnInfoToAssociatedTable(table_obj, column_name, column_info, insertTableToDbSchema_after){
  reportStatus(['Inserting column', column_name, 'into', table_obj.name])
  table_obj.columns[column_name] = column_info;
  // After all of the columns in this table have been processed we'll add the table object to the db object
  insertTableToDbSchema_after(table_obj);
};

var dbTableIndex = 0
var tableNames = Object.keys(db_tables)

runTableInfo()
function runTableInfo () {
  var tableName = tableNames[dbTableIndex]
  if (tableName) {
    dbTableIndex++
    console.log('Getting...', tableName)
    getTableInfo(tableName, runTableInfo)
  }
}

function getTableInfo (table_name, cb) {
// for (var table_name in db_tables){
//   if (_.has(db_tables, table_name)){
    // if (table_name == 't2'){ // Limit it just to t2 for testing

    // Get a table scheme for each table, use a closure becaue it's done asynchronously and you need to know what table this ajax call refers to
    (function(table_name){
      treasuryIo('PRAGMA table_info(' + table_name +')', function(err, response){
          if (err) {
            return console.log(err)
          }

          var all_cols = grabAllCols(response);
          var table_obj = {
                "label": db_tables[table_name].label,
                "name" : table_name,
                "all_cols": all_cols,
                "columns": {}
              },
              column_infos = cleanPragmaObj(response, table_name),
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


              treasuryIo(query_text, function(err, response){
                  if (err) {
                    return console.log(err)
                  }
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
                      column_info.column_type = 'date';
                      var date_item_values = [
                        {
                          comparinator: '>',
                          value: values_with_blank[0]
                        },
                        {
                          comparinator: '<',
                          value: values_with_blank[1]
                        }
                      ];
                      addDatatoColumnInfo(column_info, 'item_values', date_item_values);
                      // The column now has all of its values added, so you can add that completed column information to the designated table
                      addColumnInfoToAssociatedTable(table_obj, column_info.name, column_info, insertTableToDbSchema_after);
                      cb()
                    }else{
                      var t = table_obj.name,
                          item_values = [];
                      if (t != 't2' && t != 't3'){
                        _.each(values_with_blank, function(value){
                          var val_obj = {
                            comparinator: '=',
                            value: value
                          };
                          item_values.push(val_obj);
                        });
                        addDatatoColumnInfo(column_info, 'item_values', item_values);
                        // The column now has all of its values added, so you can add that completed column information to the designated table
                        addColumnInfoToAssociatedTable(table_obj, column_info.name, column_info, insertTableToDbSchema_after);
                        cb()
                      }else if (t == 't3c'){
                       var date_item_values = [
                          {
                            comparinator: '=',
                            value: 'Total Public Debt Subject to Limit'
                          },
                          {
                            comparinator: '=',
                            value: 'Statutory Debt Limit'
                          }
                        ];     
                        addDatatoColumnInfo(column_info, 'item_values', item_values);
                        // The column now has all of its values added, so you can add that completed column information to the designated table
                        addColumnInfoToAssociatedTable(table_obj, column_info.name, column_info, insertTableToDbSchema_after);
                        cb()
                      }else if (t == 't2'){
                        if (column_info.name != 'item'){
                          _.each(values_with_blank, function(value){
                            var val_with_children = {
                              comparinator: '=',
                              value: value
                            };
                            item_values.push(val_with_children);
                            addDatatoColumnInfo(column_info, 'item_values', item_values);
                            addColumnInfoToAssociatedTable(table_obj, column_info.name, column_info, insertTableToDbSchema_after);
                            cb()
                          });
                        }else{
                          (function(column_info, table_obj){
                            var indexVal = 0
                            runBlankVal()
                            function runBlankVal () {
                              var value = values_with_blank[indexVal]
                              if (value) {
                                var parent_query = 'SELECT group_concat(DISTINCT transaction_type) as t_type_parents FROM t2 WHERE "item" = \'' + value + '\''
                                console.log('Getting...', value)
                                treasuryIo(parent_query, function(err, r){
                                  if (err) {
                                    return console.log(err)
                                  }
                                  var parent_t_types = r.t_type_parents ? r[0].t_type_parents.split(',') : r.t_type_parents
                                  var val_with_children = {
                                    comparinator: '=',
                                    value: value,
                                    parents: parent_t_types
                                  };

                                  if (item_desc_nest['t2'][value]){
                                    val_with_children.description = item_desc_nest['t2'][value].description
                                    val_with_children.url         = item_desc_nest['t2'][value].url
                                  }

                                  item_values.push(val_with_children);
                                  addDatatoColumnInfo(column_info, 'item_values', item_values);
                                  addColumnInfoToAssociatedTable(table_obj, column_info.name, column_info, insertTableToDbSchema_after);
                                  indexVal++
                                  runBlankVal()
                                })
                              }
                            }
                          })(column_info, table_obj)
                        }
                      }
                    };

                  }else{ // INTEGER or REAL
                    var int_real_vals = [];
                    if (column_info.name == 'is_total'){
                      column_info.column_type = 'is_total';
                      int_real_vals = [
                        {
                          value: values_with_blank[0]
                        },
                        {
                          value: values_with_blank[1]
                        }
                      ];
                    }else{
                      column_info.column_type = 'numeric';

                      int_real_vals = [
                        {
                          comparinator: '>',
                          value: values_with_blank[0]
                        },
                        {
                          comparinator: '<',
                          value: values_with_blank[1]
                        }
                      ];
                    };
                    addDatatoColumnInfo(column_info, 'item_values', int_real_vals);
                    // The column now has all of its values added, so you can add that completed column information to the designated table
                    addColumnInfoToAssociatedTable(table_obj, column_info.name, column_info, insertTableToDbSchema_after);
                    cb()
                  };


                });
            })(column_info, table_obj);
          });
        }); 
    })(table_name);
     // } // Limiting t2 if statement for testing 
}

