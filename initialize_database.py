# initialize_database.py
#
# This script defines the MySQL 'vacancies' database tables used by scripts 'process_vacancies'
# and 'update_vacancies.py' and loads some initial data. This script also checks 
# that all the requisite database tables have been defined but does not verify 
# the definition of individual table fields.
#
# Data and configuration files
# ----------------------------
# 
# The following data and configuration files are required by
# this script:
#
# ./Data/companies.data     -   Contains company data provided by
#                               companies house.
# ./Data/connect.data       -   Contains MySQL login details.
# ./Data/definition.sql     -   Contains SQL statements required
#                               to definie database 'vacancies' 
#                               and it's tables.
# ./Data/engines.data       -   Contains information relating to
#                               ehe locations of job-alert e-mails
#                               and the format ( using regular expressions) 
#                               of single vacancy urls conatined in these 
#                               e-mails. Invidual job sites delivering
#                               job-alert e-mails are referred to as engines.
#
# Logging
# -------
# This script logs progress and error information in:
#
# ./Data/log.txt

import re
import requests
import os
import sys
import File
import Db
import Web

# File names and modes
Currentdir = os.getcwd()
Datadir = Currentdir + '\\Data'
Errorfilename = Datadir + '\\' + 'log.txt'
SQLfilename = Datadir + '\\' + 'definition.sql'
Connectfilename = Datadir + '\\' + 'connect.csv'
Companyfilename = Datadir + '\\' + 'companies.csv'
Enginefilename = Datadir + '\\' + 'engines.csv'
append = 'a'
read = 'r'

# Database and tables
# DbName = 'test'
DbName = 'vacancies'
DbTable = ('company','engine','vacancy','history','counter','duplicate')

# Function return values
invalid = failure = 0
empty = ''

# Error levels
error = 'ERROR'
warning = 'WARNING'
info = 'INFO'
module = 'initialize_database'

# Create/open log file
ErrorfileObject = File.Open(Errorfilename,append,failure)
Errormessage = 'Could not open ' + Errorfilename
if ( ErrorfileObject == failure ) : File.Logerror(ErrorfileObject,module,Errormessage,error)

# Log start of script
File.Logerror(ErrorfileObject,module,'Started',info)

# Read database connection data file
ConnectfileObject = File.Open(Connectfilename,read,failure)
Errormessage = 'Could not open ' + Connectfilename
if ( ConnectfileObject == failure ) : File.Logerror(ErrorfileObject,module,Errormessage,error)

ConnectfileData = File.Read(ConnectfileObject,empty)
if ( ConnectfileData != empty ) : 
    ConnectfileDataList = ConnectfileData.split(',')
else:
    Errormessage = 'No data in ' + Connectfilename
    File.Logerror(ErrorfileObject,module,Errormessage,error)

Errormessage = 'Could not close' + Connectfilename
if ( File.Close(ConnectfileObject,failure) == failure ) : File.Logerror(ErrorfileObject,module,Errormessage,error)

# Progress update
File.Logerror(ErrorfileObject,module,'Read database connection data',info)

# Read SQL data file
SQLfileObject = File.Open(SQLfilename,read,failure)
Errormessage = 'Could not open ' + SQLfilename
if ( SQLfileObject == failure ) : File.Logerror(ErrorfileObject,module,Errormessage,error)

SQLfileData = File.Read(SQLfileObject,empty)
Errormessage = 'No data in ' + SQLfilename
if ( SQLfileData != empty ) : 
    SQLfileDataList = SQLfileData.split(';\n')
else: 
    File.Logerror(ErrorfileObject,module,Errormessage,error)
    
if ( File.Close(SQLfileObject,failure) == failure ) : print ('Could not close %s' % SQLfilename)

# Progress update
File.Logerror(ErrorfileObject,module,'Read database table definition data',info)

# Open database connection.
DbObject = Db.Connect(ConnectfileDataList[0],ConnectfileDataList[1],ConnectfileDataList[2],ConnectfileDataList[3],invalid)
Errormessage = 'Could not connect to database'
if ( DbObject == invalid ) : File.Logerror(ErrorfileObject,module,Errormessage,error)

# Prepare a database cursor object.
DbCursor = Db.Initcursor(DbObject,invalid)
Errormessage = 'Unable to create database cursor'
if ( DbCursor == invalid ) : File.Logerror(ErrorfileObject,module,Errormessage,error)

# Progress update
File.Logerror(ErrorfileObject,module,'Connected to database',info) 

# Load SQL data file
for SQLline in SQLfileDataList :
    SQLcommand = SQLline.replace(';',' ')
    SQLresponse = Db.SQLload(DbObject,DbCursor,SQLcommand,failure)
    Errormessage = 'SQLresponse error for SQL command ' + '\"' + SQLcommand + '\"'
    if ( (SQLresponse) == failure ): File.Logerror(ErrorfileObject,module,Errormessage,error)

# Progress update
File.Logerror(ErrorfileObject,module,'Loaded database table definition data',info)

# Verify all required tables have been defined.
for table in DbTable :

    # Generate SQL command
    
    SQLcommand = 'show columns from %s.%s' % (DbName,table) 
    SQLresponse = ( Db.SQLload(DbObject,DbCursor,SQLcommand,failure) )
    Errormessage = 'SQLresponse error for SQL command ' + '\"' + SQLcommand + '\"'
    if ( (SQLresponse) == failure ): File.Logerror(ErrorfileObject,module,Errormessage,error)
    
    # Determine field definitions for tables 'company' and engine
    if ( table == 'company' ) : Companyfields = Db.Fielddefs(SQLresponse)
    if ( table == 'engine' ) : Enginefields = Db.Fielddefs(SQLresponse)
    
# Progress update
File.Logerror(ErrorfileObject,module,'Verified that all required tables have been defined',info)

# Load company data from 'companies.data' file
CompanyfileObject = File.Open(Companyfilename,read,failure)
Errormessage = 'Could not open ' + Companyfilename
if ( CompanyfileObject == failure ) : File.Logerror(ErrorfileObject,module,Errormessage,error)

CompanyfileData = File.Readline(CompanyfileObject,empty)
Errormessage = 'No data in ' + Companyfilename
if ( CompanyfileData == empty ) : File.Logerror(ErrorfileObject,module,Errormessage,error)

while ( CompanyfileData != empty ) :
    SQLcommand = Db.Geninsert('company',Companyfields,CompanyfileData) 
    SQLresponse = ( Db.SQLload(DbObject,DbCursor,SQLcommand,failure) )
    Errormessage = 'SQLresponse error for SQL command ' + '\"' + SQLcommand + '\"'
    if ( (SQLresponse) == failure ): File.Logerror(ErrorfileObject,module,Errormessage,warning)
    CompanyfileData = File.Readline(CompanyfileObject,empty)

# Progress update
File.Logerror(ErrorfileObject,module,'Populated \'company\' table ',info)

Errormessage = 'Could not close ' + Companyfilename
if ( File.Close(CompanyfileObject,failure) == failure ) : File.Logerror(ErrorfileObject,module,Errormessage,warning)

# Load engine data from 'engines.data' file
EnginefileObject = File.Open(Enginefilename,read,failure)
Errormessage = 'Could not open ' + Enginefilename
if ( EnginefileObject == failure ) : File.Logerror(ErrorfileObject,module,Errormessage,error)

EnginefileData = File.Readline(EnginefileObject,empty)
Errormessage = 'No data in ' + Enginefilename
if ( EnginefileData == empty ) : File.Logerror(ErrorfileObject,module,Errormessage,error)

while ( EnginefileData != empty ) :
    SQLcommand = Db.Geninsert('engine',Enginefields,EnginefileData) 
    SQLresponse = ( Db.SQLload(DbObject,DbCursor,SQLcommand,failure) )
    Errormessage = 'SQLresponse error for SQL command ' + '\"' + SQLcommand + '\"'
    if ( (SQLresponse) == failure ): File.Logerror(ErrorfileObject,module,Errormessage,error)
    EnginefileData = File.Readline(EnginefileObject,empty)    
    
# Progress update
File.Logerror(ErrorfileObject,module,'Populated \'engine\' table ',info)

Errormessage = 'Could not close ' + Enginefilename
if ( File.Close(EnginefileObject,failure) == failure ) : File.Logerror(ErrorfileObject,module,Errormessage,warning)
 
# Disconnect from database.
Errormessage = 'Could not disconnect from database'
if ( Db.Disconnect(DbObject,failure) == failure ) : File.Logerror(ErrorfileObject,module,Errormessage,warning)

# Log end of script
File.Logerror(ErrorfileObject,module,'Completed',info)

# Close error log file
Errormessage = 'Could not close ' + Errorfilename
if ( File.Close(ErrorfileObject,failure) == failure ) : File.Logerror(ErrorfileObject,module,Errormessage,warning)



    
