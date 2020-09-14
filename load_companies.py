# load_companies.py
#
# This script loads the data contained in the './Data/companies.csv' file 
# into the 'company' table of database 'vacancies'. This script has been
# written to allow bulk updates.
#
# Data and configuration files
# ----------------------------
# 
# The following data and configuration files are required by
# this script:
#
# ./Data/companies.csv     -   Contains company data provided by
#                              companies house.
# ./Data/connect.csv       -   Contains MySQL login details.
#
# Logging
# -------
# This script logs progress and error information in:
#
# ./Data/log.txt
#
# A progress message is also displayed every 100 lines of data processed from
# input file ./Data/companies.csv

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
Connectfilename = Datadir + '\\' + 'connect.csv'
Companyfilename = Datadir + '\\' + 'companies.csv'
append = 'a'
read = 'r'

# Database and tables
DbName = 'vacancies'
Companytable = '%s.%s' % (DbName,'company')

# Function return values
invalid = failure = 0
empty = ''

# Error levels
error = 'ERROR'
warning = 'WARNING'
info = 'INFO'
module = 'load_companies.py'

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

# Verify 'company' table is defined and read field definitions
SQLcommand = 'show columns from %s.%s' % (DbName,'company') 
SQLresponse = ( Db.SQLload(DbObject,DbCursor,SQLcommand,failure) )
Errormessage = 'SQLresponse error for SQL command ' + '\"' + SQLcommand + '\"'
if ( (SQLresponse) == failure ): File.Logerror(ErrorfileObject,module,Errormessage,error)
Companyfields = Db.Fielddefs(SQLresponse)
   
# Progress update
File.Logerror(ErrorfileObject,module,'Verified that table company is defined',info)

# Load company data from 'companies.data' file
CompanyfileObject = File.Open(Companyfilename,read,failure)
Errormessage = 'Could not open ' + Companyfilename
if ( CompanyfileObject == failure ) : File.Logerror(ErrorfileObject,module,Errormessage,error)

CompanyfileData = File.Readline(CompanyfileObject,empty)
Errormessage = 'No data in ' + Companyfilename
if ( CompanyfileData == empty ) : File.Logerror(ErrorfileObject,module,Errormessage,error)

# Progress update
Errormessage = 'Loading data from file $s' % Companyfilename
File.Logerror(ErrorfileObject,module,Errormessage,info)

DataCount = 0
DataInserted = 0
while ( CompanyfileData != empty ) :
    SQLcommand = Db.Geninsert(Companytable,Companyfields,CompanyfileData) 
    SQLresponse = ( Db.SQLload(DbObject,DbCursor,SQLcommand,failure) )
    Errormessage = 'SQLresponse error for SQL command ' + '\"' + SQLcommand + '\"'
    if ( (SQLresponse) == failure ): 
        File.Logerror(ErrorfileObject,module,Errormessage,warning)
    else :
        DataInserted += 1
        
    CompanyfileData = File.Readline(CompanyfileObject,empty)
    
    # Increment counter and display progress message. 
    DataCount += 1
    if ( DataCount%100 == 0 ) : print ('%d lines processed' % DataCount)

# Progress update
Errormessage = 'Populated \'company\' table with %i of a possible %i entries' % (DataInserted,DataCount)
File.Logerror(ErrorfileObject,module,Errormessage,info)

Errormessage = 'Could not close ' + Companyfilename
if ( File.Close(CompanyfileObject,failure) == failure ) : File.Logerror(ErrorfileObject,module,Errormessage,warning)

# Disconnect from database.
Errormessage = 'Could not disconnect from database'
if ( Db.Disconnect(DbObject,failure) == failure ) : File.Logerror(ErrorfileObject,module,Errormessage,warning)

# Log end of script
File.Logerror(ErrorfileObject,module,'Completed',info)

# Close error log file
Errormessage = 'Could not close ' + Errorfilename
if ( File.Close(ErrorfileObject,failure) == failure ) : File.Logerror(ErrorfileObject,module,Errormessage,warning)



    
