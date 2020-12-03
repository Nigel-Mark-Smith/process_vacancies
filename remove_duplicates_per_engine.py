# remove_duplicates_per_engine.py
#
# Description
# -----------
# This script will parse all 'New' vacancies in the 'vacancy' table of
# the 'vacancies' database and determine if any of these vacancies are
# duplicates of each other or of vacancies that are currently being pursued
# or have been recently 'Dropped'. These duplicates are then removed.
# The search for duplicates is done using the following criteria:
#
# - Duplicate vacancies in the 'vacancy' table have the same non NULL values for:
#    
#   engine_id
#   company
#   title
#   location
#
# Prior to performing duplicate searches this script will scrape 'company'
# 'title' and 'location' data for all 'New' vacancies from the web 
# and update the relevant record in the 'vacancy' table.
#
# Usage
# -----
# This script requires no command line arguments and may be run as follows:
#
# python remove_duplicates_per_engine.py
#
# Data and configuration files
# ----------------------------
# 
# The following data and configuration files are required by
# this script:
#
# ./Data/connect.data       -   Contains MySQL login details. 
#
# Logging
# -------
# This script logs progress and error information in:
#
# ./Data/log.txt

import Db
import File
import Interface
import Web
import os
import re
import requests
import sys
import json

# Function return values
invalid = failure = 0
empty = ''
success = 1

# Error levels
error = 'ERROR'
warning = 'WARNING'
info = 'INFO'
module = 'remove_duplicates_per_engine.py'

# File names and modes
Currentdir = os.getcwd()
Datadir = Currentdir + '\\Data'
Errorfilename = Datadir + '\\' + 'log.txt'
Connectfilename = Datadir + '\\' + 'connect.csv'
append = 'a'
read = 'r'
overwrite = 'w'

# Database and tables
DbName = 'vacancies'
VacancyTable = DbName + '.' + 'vacancy'
HistoryTable = DbName + '.' + 'history'
DuplicateTable = DbName + '.' + 'duplicate'

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

# Read fields in table 'vacancy'
SQLcommand = 'show columns from %s' % VacancyTable 
SQLresponse = ( Db.SQLload(DbObject,DbCursor,SQLcommand,failure) )
Errormessage = 'SQLresponse error for SQL command ' + '\"' + SQLcommand + '\"'
if ( (SQLresponse) == failure ): File.Logerror(ErrorfileObject,module,Errormessage,error)
VacancyFields = Db.Fielddefs(SQLresponse)

# Progress update
File.Logerror(ErrorfileObject,module,'Read vacancy table field definitions',info)

# Read fields in table 'history'
SQLcommand = 'show columns from %s' % HistoryTable 
SQLresponse = Db.SQLload(DbObject,DbCursor,SQLcommand,failure)
Errormessage = 'SQLresponse error for SQL command ' + '\"' + SQLcommand + '\"'
if ( (SQLresponse) == failure ): File.Logerror(ErrorfileObject,module,Errormessage,error)
HistoryFields = Db.Fielddefs(SQLresponse)

# Progress update
File.Logerror(ErrorfileObject,module,'Read history table field definitions',info)

# Read fields in table 'Duplicate'
SQLcommand = 'show columns from %s' % DuplicateTable 
SQLresponse = Db.SQLload(DbObject,DbCursor,SQLcommand,failure)
Errormessage = 'SQLresponse error for SQL command ' + '\"' + SQLcommand + '\"'
if ( (SQLresponse) == failure ): File.Logerror(ErrorfileObject,module,Errormessage,error)
DuplicateFields = Db.Fielddefs(SQLresponse)

# Progress update
File.Logerror(ErrorfileObject,module,'Read duplicate table field definitions',info)

# Select all new vacancies.
SQLcommand  = 'select * from %s where vacancy_state = \'%s\'' % (VacancyTable,'New')
SQLresponse = Db.SQLload(DbObject,DbCursor,SQLcommand,failure)
Errormessage = 'SQLresponse error for SQL command ' + '\"' + SQLcommand + '\"'
if ( (SQLresponse) == failure ): File.Logerror(ErrorfileObject,module,Errormessage,error)

# Progress update
File.Logerror(ErrorfileObject,module,'Updating all new vacancies with data scraped from vacancy urls',info)

# Update all 'New' vacancy records.
for VacancyRow in SQLresponse :

    # Populate 'vacancy' values dictionary
    VacancyValues = {}
    FieldIndex = 0
    VacancyValuesIncomplete = False
    
    # This code includes a check to see if some vacancy values have not
    # been defined.
    for VacancyField in VacancyFields.keys() :
        if ((VacancyRow[FieldIndex])) is None : VacancyValuesIncomplete = True    
        VacancyValues[VacancyField] = (VacancyRow[FieldIndex])
        FieldIndex += 1
   
    # If vacancy already complete move to next one.
    if not (VacancyValuesIncomplete) : continue
    
    # Scrape web data.
    VacancyUpdate = {}
    Engine_Id = VacancyValues['engine_id']
    Vacancy_Url = VacancyValues['vacancy_url']
    
    if ( Engine_Id == 1 ) : VacancyUpdate = Web.ScrapeCVLibrary(Vacancy_Url)    
    if ( Engine_Id == 2 ) : VacancyUpdate = Web.ScrapeLinkedIn(Vacancy_Url)  
    if ( Engine_Id == 3 ) : VacancyUpdate = Web.ScrapeReed(Vacancy_Url)
    # This process doesn't work for Indeed vacancies.
    if ( Engine_Id == 4 ) : continue
    if ( Engine_Id == 5 ) : VacancyUpdate = Web.ScrapeTotalJobs(Vacancy_Url) 
    if ( Engine_Id == 6 ) : VacancyUpdate = Web.ScrapeFindAJob(Vacancy_Url)

    # General protection against scraping failure
    # !!!! NOTE !!!! Needs a better solution.    
    if (len(VacancyUpdate) == 0 ) :     
        if ( Engine_Id == 2 ) or ( Engine_Id == 3 ) or ( Engine_Id == 5 ) or ( Engine_Id == 6 ): 
            VacancyUpdate['vacancy_state'] = 'Dropped'
        else :
           continue
    
    # Populate primary field values dictionary
    PrimaryValues = {}
    PrimaryValues['engine_id'] = VacancyValues['engine_id']
    PrimaryValues['vacancy_id'] = VacancyValues['vacancy_id']
    
    # Execute database updates
    SQLcommand = Db.GenSQLupdate(VacancyTable,VacancyUpdate,VacancyFields,PrimaryValues)
    SQLresponse = Db.SQLload(DbObject,DbCursor,SQLcommand,failure)
    Errormessage = 'SQLresponse error for SQL command ' + '\"' + SQLcommand + '\"'
    if ( (SQLresponse) == failure ): File.Logerror(ErrorfileObject,module,Errormessage,error)
    
    
# Progress update
File.Logerror(ErrorfileObject,module,'Updated \'New\' vacancies with data scraped from vacancy urls ',info)

# Select all new vacancies.
SQLcommand  = 'select * from %s where vacancy_state = \'%s\'' % (VacancyTable,'New')
SQLresponse = Db.SQLload(DbObject,DbCursor,SQLcommand,failure)
Errormessage = 'SQLresponse error for SQL command ' + '\"' + SQLcommand + '\"'
if ( (SQLresponse) == failure ): File.Logerror(ErrorfileObject,module,Errormessage,error)

# Iterate through all 'New' vacancies to find duplicates. Store duplicate
# information in a list of lists.
DuplicateLists = []

for VacancyRow in SQLresponse :

    # Populate 'vacancy' values dictionary
    VacancyValues = {}
    FieldIndex = 0
    
    for VacancyField in VacancyFields.keys() :
        VacancyValues[VacancyField] = VacancyRow[FieldIndex]
        FieldIndex += 1  
        
    # Exclude Indeed vacancies.
    Engine_Id = VacancyValues['engine_id']
    if ( Engine_Id == 4 ) : continue

    # Build and execute select statement for duplicate vacancies.
    SelectFields = ('engine_id','vacancy_id','vacancy_url','vacancy_state')
    WhereFields = ('engine_id','company','title','location')

    SQLcommand = 'select ' + (  Db.GenSelectList(SelectFields) )    
    SQLcommand = SQLcommand + ( ' from %s where ' % VacancyTable )
    SQLcommand = SQLcommand + ( Db.GenWhereList(WhereFields,VacancyValues,VacancyFields) )
    
        
    SQLresponse = Db.SQLload(DbObject,DbCursor,SQLcommand,failure)
    Errormessage = 'SQLresponse error for SQL command ' + '\"' + SQLcommand + '\"'
    if ( (SQLresponse) == failure ): File.Logerror(ErrorfileObject,module,Errormessage,error)

    
    # Update the duplicates list of lists.
    DuplicatesList = SQLresponse
    if ( len(DuplicatesList) > 1 ) : DuplicateLists.append(DuplicatesList)

# Progress update
if ( len(DuplicateLists) > 0 ) : File.Logerror(ErrorfileObject,module,'Detected duplicate vacancies',info)

# Iterate through sets of duplicates logging duplicate information and creating an
# ActionLists structure with latest vacancy status information.
ActionLists = []

for DuplicateList in DuplicateLists :  
    Errormessage = 'The following set of duplicates have been detected  -> '
    File.Logerror(ErrorfileObject,module,Errormessage,info)
    
    ActionList = []
    
    for Duplicate in DuplicateList :
    
        # Build and execute select statement to determine latest vacancy state and timestamp
        SQLcommand = 'select time_stamp,vacancy_state from %s where engine_id = %s and vacancy_id = \'%s\'' % (HistoryTable,str(Duplicate[0]),Duplicate[1])
        SQLresponse = Db.SQLload(DbObject,DbCursor,SQLcommand,failure)
        Errormessage = 'SQLresponse error for SQL command ' + '\"' + SQLcommand + '\"'
        if ( (SQLresponse) == failure ): File.Logerror(ErrorfileObject,module,Errormessage,error)
      
        # Extract latest state information for vacancy
        LatestStatusData = SQLresponse[len(SQLresponse) - 1]
        LatestTimeStamp = LatestStatusData[0]
        LatestState = LatestStatusData[1] 
        
        # Log duplicate information
        Errormessage = 'Vacancy ID %s Vacancy URL %s changed to state %s on %s ' % (Duplicate[1],Duplicate[2],LatestState,str(LatestTimeStamp))
        File.Logerror(ErrorfileObject,module,Errormessage,info)

        # Add to action list structure if vacancy is new
        if ( LatestState == 'New' ) :
            EnhancedDuplicate = list(Duplicate)
            NewFields = [LatestState,LatestTimeStamp]
            EnhancedDuplicate.extend(NewFields)
            ActionList.append(EnhancedDuplicate)
        
    if (len(ActionList) != 0) : ActionLists.append(ActionList)   

# Iterate through ActionLists structure creating duplicate (counter) entries and removing
# duplicate vacancies.
DuplicateCount  = 0

for ActionList in ActionLists :

    # Add a duplicate counter value
    Fieldnames = ['engine_id','found']
    Fieldvalues = [str(Duplicate[0]),str(len(ActionList))]
    SQLcommand =  Db.GenSQLinsert(DuplicateTable,Fieldnames,DuplicateFields,Fieldvalues)
    SQLresponse = ( Db.SQLload(DbObject,DbCursor,SQLcommand,failure) )
    Errormessage = 'SQLresponse error for SQL command ' + '\"' + SQLcommand + '\"'
    if ( (SQLresponse) == failure ): File.Logerror(ErrorfileObject,module,Errormessage,warning)
    
    # Remove all but latest 'New' vacancy    
    for DuplicateIndex in range(0,(len(ActionList) - 1)) :
    
        Engine_Id = str(ActionList[DuplicateIndex][0])
        Vacancy_Id = str(ActionList[DuplicateIndex][1])
        Vacancy_Url = str(ActionList[DuplicateIndex][2])
    
        # Change state of duplicate vacancy to 'Dropped'
        PrimaryValues = {}
        VacancyUpdate = {}
        PrimaryValues['engine_id'] = Engine_Id
        PrimaryValues['vacancy_id'] = Vacancy_Id

        VacancyUpdate['vacancy_state'] = 'Dropped' 
        SQLcommand = Db.GenSQLupdate(VacancyTable,VacancyUpdate,VacancyFields,PrimaryValues)
        SQLresponse = Db.SQLload(DbObject,DbCursor,SQLcommand,failure)
        Errormessage = 'SQLresponse error for SQL command ' + '\"' + SQLcommand + '\"'
        if ( (SQLresponse) == failure ): File.Logerror(ErrorfileObject,module,Errormessage,error)
           
        # Add entry in table 'history' to reflect the change in state of the vacancy.
        Fieldnames = ['engine_id','vacancy_id','vacancy_state']
        Fieldvalues = [Engine_Id,Vacancy_Id,'Dropped']
        SQLcommand =  Db.GenSQLinsert(HistoryTable,Fieldnames,HistoryFields,Fieldvalues)
        SQLresponse = ( Db.SQLload(DbObject,DbCursor,SQLcommand,failure) )
        Errormessage = 'SQLresponse error for SQL command ' + '\"' + SQLcommand + '\"'
        if ( (SQLresponse) == failure ): File.Logerror(ErrorfileObject,module,Errormessage,warning)
       
        Errormessage = 'Vacancy ID %s Vacancy URL %s has been \'Dropped\'' % (Vacancy_Id,Vacancy_Url)
        File.Logerror(ErrorfileObject,module,Errormessage,info)
        
        DuplicateCount += 1
  
# Progress update
if ( DuplicateCount > 0 ) :
    Errormessage = 'Removed %d duplicate vacancies' % DuplicateCount
    File.Logerror(ErrorfileObject,module,Errormessage,info)

# Disconnect from database.
Errormessage = 'Could not disconnect from database'
if ( Db.Disconnect(DbObject,failure) == failure ) : File.Logerror(ErrorfileObject,module,Errormessage,warning)

# Log end of script
File.Logerror(ErrorfileObject,module,'Completed',info)

# Close error log file
Errormessage = 'Could not close ' + Errorfilename
if ( File.Close(ErrorfileObject,failure) == failure ) : File.Logerror(ErrorfileObject,module,Errormessage,warning)

