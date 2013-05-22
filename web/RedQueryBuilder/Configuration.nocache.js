/**
 * This is the root Configuration object to configure RedQueryBuilder.
 * 
 * @constructor
 */
function Configuration(meta) {
    /**
     * The description of the database.
     * @type Meta
     */
	this.meta = meta;

	/** 
	 * Notification of the SQL or argument values changing.
	 * @function 
	 * @param {string} sql the new SQL.
	 * @param {object[]} args the new argument values.*/
	this.onSqlChange = function(sql, args) {}
	
	/** 
	 * Notification of the set of tables changing.
	 * @function 
	 * @param {TableFilter[]} filters the latest TableFilters.*/
	this.onTableChange = function(filters) {}
	
	/** 
	 * Notification that widget is fully loaded.
	 * @function 
	 */
	this.onLoad = function() {}
	
	/** 
	 * Request from the Suggestion Oracle.
	 * @function
	 * @param {SuggestRequest} request details.
	 * @param {function} callback to return any suggestions.*/
	this.suggest = function(request, callback) {}
	
	/**
	 * Request from the Select editor etc.
	 * @function
	 * @param {EnumerateRequest} request request details.
	 * @param {function} callback to return any suggestions. Can be an array of strings or
	 * array of {Suggestion}s.
	 */
	this.enumerate = function(request, callback) {}
	
	/**
	 * Configuration of Editors.
	 * @type Editor[]
	 */
	this.editors = [];
}

/**
 * Database meta data.
 * 
 * @constructor
 */
function Meta() {
	/**
	 * @type Table[] 
	 */
	this.tables = [];
	/**
	 * @type Type[]
	 */
	this.types = [];
}

/**
 * Database table.
 * 
 * @constructor
 */
function Table(name, label, columns) {
    /**
     * Name to be used in the SQL.
     * @type string
     */
	this.name = name;
	
    /**
     * The text to display to the user.
     * @type string
     */
	this.label = label;

    /**
     * Table columns.
     * @type Column[]
     */
	this.columns = columns;
	
    /**
     * Optional set of foreign keys.
     * @type ForeignKey[]
     */
	this.fks = [];
}


/**
 * Database column.
 * 
 * @constructor
 */
function Column(name, label, type) {
    /**
     * The name to be used in the SQL.
     * @type string
     */
	this.name = name;
	
    /**
     * The text to display to the user.
     * @type string
     */
	this.label = label;
	
    /**
     * The type name that references a type defined in meta.types[].
     * @type string
     */
	this.type = type;
	
	/**
	 * Optional override of the Editor.
     * @type string
     */
    this.editor = null;
}

/**
 * Request to enumerate the applicable values.
 * 
 * @constructor
 */
function EnumerateRequest() {
    /**
     * SQL table name.
     * @type string
     */
	this.tableName = null;
	
	/**
     * Column name.
     * @type string
     */
	this.columnName = null;
	
	/**
     * Column Type name.
     * @type string
     */
	this.columnTypeName = null;
}

/**
 * A value in a Suggestion Request Reponse.
 * 
 * @constructor
 */
function Suggestion(value, label) {
    /**
     * Value to be used in the SQL query.
     * @type object
     */
	this.value = value;
	
	/**
     * Label to show to the user.
     * @type string
     */
	this.label = label;
}

/**
 * Database column type.
 * 
 * @constructor
 */
function Type(name, editor, operators){
    /**
     * Type identifier.
     * @type string
     */
	this.name = name;
	
    /**
     * An {@link Editor} name.
     * @type string
     */
	this.editor = editor;
	
    /**
     * Operators for this type.
     * @type Operator[]
     */
	this.operators = operators;
}

/**
 * A SQL operator.
 * 
 * @constructor
 */
function Operator(name, label, cardinality) {
    /**
     * The string to be used in the SQL.
     * @type string
     */
	this.name = name;
	
    /**
     * The text to display to the user rather than the actual SQL.
     * @type string
     */
	this.label = label;
	
    /**
     * The number of values. 'ZERO' such as "a IS NULL", 'ONE' such as "a = b" or 'MULTI' such as "a IN (1,2,3)"
     * @type string
     */
	this.cardinality = cardinality;
	
}



/**
 * A database foreign key. Used to generate joins.
 * 
 * @constructor
 */
function ForeignKey(name, pkColumnNames, fkTableName, fkColumnNames) {
    /**
     * Name for debugging purposes.
     * @type string
     */
	this.name = name;
	
    /**
     * The owning table's columns.
     * @type string[]
     */
	this.pkColumnNames = pkColumnNames;
	
    /**
     * The referenced table.
     * @type string
     */
	this.fkTableName = fkTableName;

	/**
     * Columns on the referenced table.
     * @type string[]
     */
	this.fkColumnNames = fkColumnNames;
	
    /**
     * Text to display to the user when going from owning table to referenced table.
     * @type string
     */
	this.label = label;

    /**
     * Text to display to the user when going from the referenced table to the owning table.
     * @type string
     */
	this.reverseLabel = reverseLabel;
}


/**
 * Request to make suggestions for a search oracle.
 * 
 * @constructor
 */
function SuggestRequest() {
    /**
     * SQL table name.
     * @type string
     */
	this.tableName = null;
	
	/**
     * Column name.
     * @type string
     */
	this.columnName = null;
	
	/**
     * Column Type name.
     * @type string
     */
	this.columnTypeName = null;
	
	/**
     * Partial text entered by the user.
     * @type string
     */
	this.query = null;
	
	/**
     * Maximum results to return.
     * @type number
     */
	this.limit = null;
}


/**
 * SQL combination of alias and tableName. 
 * The same table could be used more than once but the alias must be unique.
 * 
 * @constructor
 */
function TableFilter(tableName, alias) {
    /**
     * SQL table alias.
     * @type string
     */
	this.alias = alias;
	
	/**
     * Table name.
     * @type string
     */
	this.tableName = tableName;
}

/**
 * Editors inspired by HTML5 elements/attributes.
 * 
 * @constructor
 */
function Editor(name) {
    /**
     * Editor name.
     * @type string
     */
	this.name = name;
}

/** String editor 
 * @deprecated Since 0.2.0 please use TEXT.
 * */
Editor.STRING = 'STRING';

/** Text editor */
Editor.TEXT = 'TEXT';

/** Date editor 
 * Configuration attribute 'format' - see http://google-web-toolkit.googlecode.com/svn/javadoc/latest/com/google/gwt/i18n/client/DateTimeFormat.html */
Editor.DATE = 'DATE';

/** Select editor */
Editor.SELECT = 'SELECT';
