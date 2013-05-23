/**
 * A helper class to construct and manage RedQueryBuilder instances.
 * 
 * Use RedQueryBuilderFactory.create rather than the constructor.
 * 
 * @constructor
 */
function RedQueryBuilderFactory(config, sql, args) {
    /**
     * The description of the database.
     * @type Configuration
     */
	this.config = config;
	
    /**
     * Initial SQL.
     * @type string
     */
	this.sql = sql;
	
    /**
     * Initial arguments.
     * @type string[]
     */
	this.args = args;
}

RedQueryBuilderFactory.create = function(config, sql, args) {
  var x = new RedQueryBuilderFactory(config, sql, args);
  x.waitForLoad();
}

RedQueryBuilderFactory.prototype.waitForLoad = function() {
  var rqb = this;
  var fn = function() {
    if (!window.redQueryBuilder) {
      setTimeout(fn, 50);
    } else {
      rqb.ready();
    }
  }
  fn();
}

RedQueryBuilderFactory.prototype.ready = function() {
  window.redQueryBuilder(this.config, this.sql, this.args);
  if (this.config.onLoad) {
	  this.config.onLoad();
  }
}