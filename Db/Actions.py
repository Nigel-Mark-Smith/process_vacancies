import pymysql

# Connect to database

def Connect (server,user,password,database,failure):
    
    "Connects to database"

    try:
        db = pymysql.connect(server,user,password,database,autocommit=True)
    except:
        return failure
    else:
        return db
 
        
# Disconnect from server

def Disconnect (db,failure):
   
    "Disconnects from database"

    try:
        db.close() 
    except:
        return failure
        
# Initiate DB cursor    
  
def Initcursor (db,failure):
    
    "Initiates DB cursor"

    try:
        cursor = db.cursor() 
    except:
        return failure
    else:
        return cursor
        
# Execute an SQL command.

def SQLexecute (cursor,command,failure):
    
    "Executes an SQL command"

    try:
        cursor.execute(command)
    except:
        return failure
        
# Returns SQL command result

def SQLresponse (cursor,failure):
   
    "Returns SQL command result"

    try:
        output = cursor.fetchall()
    except:
        return failure
    else:
        return output
        
# Execute SQL command and return response

def SQLload (db,cursor,command,failure):
   
    "Execute an SQL command and return response"

    try:
        cursor.execute(command)
        try:
            output = cursor.fetchall()
            db.commit()
        except:
            return failure
        else:
            return output
    except:
        return failure  
        
# Return dictionary of field definitions from SQL response
# 
# Note the argument to this function must be the response from
# SQL command of format 'show columns <table name>'

def Fielddefs (response):

     "Return dictionary of field definitions from SQL response"
      
     definition = {}
     fieldnumber = 0
     
     while ( fieldnumber < len(response) ) :
        line = response[fieldnumber]
        definition[line[0]] = line[1]
        # print ( 'Key is %s and value is %s' % ( line[0],line[1] ) )
        fieldnumber = fieldnumber + 1
     
     return definition
     
# Generate an SQL insert command using table name, field definitions and 
# data from data file.

def Geninsert (table,definition,data):

    "Return SQL insert command"
    
    data = data.strip()
    values = data.split(',')
    start = 'insert into %s(' % table
    end = ') ' + 'values ('
    
    # iterate through fields and data
    
    datum = 0
    iteration = iter(definition)
    
    for field in iteration : 
        start = start + field + ','
        value = values[datum]
        if ( definition[field].find('int(') == -1 ) : value = '\"' + value + '\"'   
        # The following string manipulation is required as
        # we may store '\' characters in the joburl for engines
        value = value.replace('\\','\\\\')
        
        # The following string manipulation is required to cope
        # with company names containing a single quote e.g. ONLINE PA'S LIMITED
        value = value.replace('\'','\\\'')
        value = value.replace('\"','\'')
        
        end = end + value + ','
        datum =  datum + 1
        
    end = end + ')'    
    command = start + end
    
    # remove superfluous ','
    command = command.replace(',)',')')
    
    return command
    
# Determines if all the fields in 'fieldlist' exist as
# key values in 'fielddefinitions'. 
def FieldsExist (fieldlist,fielddefinitions,failure,success):
    
    "Determines if all the fields in 'fieldlist' exist as key values in 'fielddefinitions'"
    
    result = success
    
    for field in fieldlist :
        if ( field in fielddefinitions ) : 
            continue
        else :
            result = failure
            break
    
    return result
    
# Generate an SQL insert command using table name, field list, field definitions and 
# field values from data file.
def GenSQLinsert (table,fieldlist,fielddefinitions,fieldvalues):

    "Generate an SQL insert command using table name, field list, field definitions and field values from data file"
    
    start = 'insert into %s(' % table
    end = ') ' + 'values ('
    
    # Iterate through fields present
    index = 0
    
    for field in fieldlist :
    
        start = start + field + ','
        value = fieldvalues[index]
        
        # Enclose value in quotation marks if the field is not and integer
        if ( fielddefinitions[field].find('int(') == -1 ) : value = '\"' + value + '\"' 
        
        # The following string manipulation is required to cope
        # with company names containing a single quote e.g. ONLINE PA'S LIMITED
        value = value.replace('\'','\\\'')
        value = value.replace('\"','\'')
        
        # The following string manipulation is required as
        # we may store '\' characters in the joburl for engines
        value = value.replace('\\','\\\\')
        
        end = end + value + ','
        
        index += 1
    
    # Complete command string creation
    end = end + ')'    
    command = start + end
    command = command.replace(',)',')')
        
    return command       
    
# Return the row count from a SQL select statement reponse.
def GetSQLrowcount (response):

    "Return the row count from a SQL select statement reponse"
    
    return response[0][0]
    
# Generate an SQL command table name, and select criteria
def GenSQLselect (table,condition):

    "Generate an SQL command table name, and select criteria"
    
    command = 'select count(*) from %s where ' % table
    command = command + condition
    return command
    
# Returns a list of the possible values of an enumerated MySQL field.
def GetENUMvalues (definition) :

    "Returns possible values of an enumerated MySQL field"
    
    result = definition.replace('enum(','')
    result = result.replace(')','')
    result = result.replace('\'','')
    result = result.split(',')
    
    return result

# Generate an SQL update command using table name, field values ,field definitions, 
# and field value pairs that should determine a unique record in the table.
def GenSQLupdate (table,fieldvalues,fielddefinitions,primaryfieldvalues):

    "Generate an SQL update command using table name, field values ,field definitions, and field value pairs that should determine a unique record in the table"
    
    start = 'update %s set ' % table
    
    # Iterate through fields present  
    seperator = ' , '
    
    for fieldname in fieldvalues :
        
        value = fieldvalues[fieldname]  
        # Enclose value in quotation marks if the field is not an integer
        if ( fielddefinitions[fieldname].find('int(') == -1 ) : 
            value = '\"' + value + '\"' 
            
            # The following string manipulation is required to cope
            # with company names containing a single quote e.g. ONLINE PA'S LIMITED
            value = value.replace('\'','\\\'')
            value = value.replace('\"','\'')
                   
        else :
            value = str(value)
        
        start = start + fieldname + ' = ' + value + seperator
    
    start = start.rstrip(seperator)
    
    end = ' where '
    
    # Iterate through primary fields  
    seperator = ' and '
    
    for primaryfieldname in primaryfieldvalues :
   
        value =  primaryfieldvalues[primaryfieldname]
        # Enclose value in quotation marks if the field is not an integer
        if ( fielddefinitions[primaryfieldname].find('int(') == -1 ) : 
            value = '\'' + value + '\'' 
        else :
            value = str(value)
            
        end = end + primaryfieldname + ' = ' + value + seperator
     
    end = end.rstrip(seperator)
    
    command = start + end
    command = command.replace(',)',')')
        
    return command       

# Generate a comma seperated list of fields for inclusion in an SQL select statement
def GenSelectList (fieldlist) :

    "Generate a list of fields for inclusion in an SQL select statement"

    seperator = ','
    list = ''
    
    for field in fieldlist : 
        list = list + field + seperator
        
    list = list.rstrip(seperator)
   
    return list
    
# Generate a list of where conditions for inclusion in an SQL select statement
def GenWhereList (fieldlist,fieldvalues,fielddefinitions) :

    "Generate a list of where conditions for inclusion in an SQL select statement"

    seperator = ' and '
    list = ''
    
    for field in fieldlist : 
        fieldvalue = str(fieldvalues[field])
        if ( fielddefinitions[field].find('int(') == -1 ) :  
            fieldvalue = '\"' + fieldvalue + '\"'
            
            # The following string manipulation is required to cope
            # with company names containing a single quote e.g. ONLINE PA'S LIMITED
            fieldvalue = fieldvalue.replace('\'','\\\'')
            fieldvalue = fieldvalue.replace('\"','\'')
            
        list = list + field + ' = ' + fieldvalue + seperator
    
    list = list.rstrip(seperator)
   
    return list

    
    
