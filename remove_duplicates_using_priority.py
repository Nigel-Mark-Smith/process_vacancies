# remove_duplicates_using_priority.py
#
# Description
# -----------
# This script will parse all 'New' vacancies in the 'vacancy' table of
# the 'vacancies' database and determine if any of these vacancies are
# duplicates of each other or of vacancies that are about to be 
# applied for. These duplicates are then removed. The search for a 
# duplicate vacancy is done using the following criteria:
#
# - Duplicate vacancy's 'state' is either 'New' of 'Enhanced'.
# - Duplicate vacancy has the same value for 'title' as new vacancy.
# - The first first part of duplicate vacancy's 'company' value matches the first 
#   word of the new vacancy's 'company' value.  
# - The duplicate vacancy's 'location' conatins the first word of the the new vacancy's
#   'location' value
# - Any non 0 values of duplicate vacancy's 'salary_min' and 'salary_max'
#   match those of the new vacancy.
#
# As duplicates vacancies are detected across engines the vacancy or
# vacancies selected for removal are selected based on the age of the vacancy 
# ( oldest ) and the 'priority' associated with the engine on which the
# the vacancy was advertised.
#
# Prior to performing duplicate searches this script will scrape 'company'
# 'title' and 'location' data for all 'New' vacancies from the web 
# and update the relevant record in the 'vacancy' table.
#
# Usage
# -----
# This script requires no command line arguments and may be run as follows:
#
# python detect_duplicates.py
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
module = 'remove_duplicates_using_priority.py'

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
EngineTable = DbName + '.' + 'engine'

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

# Read fields in table 'duplicate'
SQLcommand = 'show columns from %s' % DuplicateTable 
SQLresponse = Db.SQLload(DbObject,DbCursor,SQLcommand,failure)
Errormessage = 'SQLresponse error for SQL command ' + '\"' + SQLcommand + '\"'
if ( (SQLresponse) == failure ): File.Logerror(ErrorfileObject,module,Errormessage,error)
DuplicateFields = Db.Fielddefs(SQLresponse)

# Progress update
File.Logerror(ErrorfileObject,module,'Read duplicate table field definitions',info)

# Read fields in table 'engine'
SQLcommand = 'show columns from %s' % EngineTable 
SQLresponse = Db.SQLload(DbObject,DbCursor,SQLcommand,failure)
Errormessage = 'SQLresponse error for SQL command ' + '\"' + SQLcommand + '\"'
if ( (SQLresponse) == failure ): File.Logerror(ErrorfileObject,module,Errormessage,error)
EngineFields = Db.Fielddefs(SQLresponse)

# Progress update
File.Logerror(ErrorfileObject,module,'Read engine table field definitions',info)

# Read engine data.
SQLcommand  = 'select * from %s' % EngineTable
SQLresponse = Db.SQLload(DbObject,DbCursor,SQLcommand,failure)
Errormessage = 'SQLresponse error for SQL command ' + '\"' + SQLcommand + '\"'
if ( (SQLresponse) == failure ): File.Logerror(ErrorfileObject,module,Errormessage,error)

EngineData = SQLresponse

# Progress update
File.Logerror(ErrorfileObject,module,'Read engine table data',info)

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
        if ( Engine_Id != 4 ) : 
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
    
    Vacancy_Id = VacancyValues['vacancy_id']
    
    # Use first part of company name
    Company = VacancyValues['company']
    CompanyMatch = re.search('(\A\w*)',Company)
    if CompanyMatch : Company = CompanyMatch.group(1)
    
    Title = VacancyValues['title']
    
    # Use first part of location
    Location = VacancyValues['location']
    LocationMatch = re.search('(\A\w*)',Location)
    if LocationMatch : Location = LocationMatch.group(1)
    
    MinSalary = VacancyValues['salary_min']
    MaxSalary = VacancyValues['salary_max']
  
    # Build and execute select statement for duplicate vacancies.
    SQLcommand = 'select * from %s where title = \'%s\' and (vacancy_state = \'New\' or vacancy_state = \'Enhanced\' )' % (VacancyTable,Title)
    SQLresponse = Db.SQLload(DbObject,DbCursor,SQLcommand,failure)
    Errormessage = 'SQLresponse error for SQL command ' + '\"' + SQLcommand + '\"'
    if ( (SQLresponse) == failure ): File.Logerror(ErrorfileObject,module,Errormessage,error)
    
    # Remove 'unlikely' duplicates
    SelectList = SQLresponse
    DuplicatesList = []
    
    for Selection in SelectList :
    
        # Load duplicate candidate data for comparison
        FieldIndex = 0
        SelectValues = {}
        
        for SelectField in VacancyFields.keys() :
            SelectValues[SelectField] = Selection[FieldIndex]
            FieldIndex += 1
        
        # Filter out non 'duplicates'       
        # if not ( SelectValues['location'].startswith(Location) ) : continue 
        if not ( SelectValues['location'].find(Location) >= 0 ) : continue
        if ( MinSalary > 0 ) and ( SelectValues['salary_min'] > 0 ) and ( SelectValues['salary_min'] != MinSalary ) : continue
        if ( MaxSalary > 0 ) and ( SelectValues['salary_max'] > 0 ) and ( SelectValues['salary_max'] != MaxSalary ) : continue
        if not ( SelectValues['company'].startswith(Company) ) : continue
        
        # Add 'duplicate' to duplicates action list
        DuplicatesList.append(Selection)
        
    # Update the duplicates list of lists.
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
        
        # Extract engine priority value
        Engine_Id = str(Duplicate[0])
        EnginePriority  = int(EngineData[int(Engine_Id)-1][6])
        
        # Set duplicate for deletion
        SaveDuplicate = False

        # Add to action list structure
        EnhancedDuplicate = list(Duplicate)
        NewFields = [LatestState,LatestTimeStamp,EnginePriority,SaveDuplicate]
        EnhancedDuplicate.extend(NewFields)
        ActionList.append(EnhancedDuplicate)
        
    if (len(ActionList) > 1) : ActionLists.append(ActionList) 
    
# Determine which duplicate(s) need(s) to be removed
RemoveList = []
RemoveIDs = []
    
for ActionList in ActionLists :
    
    # Determine index of highest priority vacancy to save  
    SavedPriority = 0  
    SavedIndex = 0    
    
    for DuplicateIndex in range(0,len(ActionList)) :
    
        Engine_Id = str(ActionList[DuplicateIndex][0])
        Vacancy_Id = str(ActionList[DuplicateIndex][1])
        Vacancy_Url = str(ActionList[DuplicateIndex][2])
        Priority  = int(EngineData[int(Engine_Id)-1][6])
        
        # Look for highest priority vacancy to save. 
        if ( Priority >= SavedPriority ) :
            SavedPriority = Priority
            SavedIndex = DuplicateIndex
                  
    # Mark duplicate for saving.
    ActionList[SavedIndex][12] = True
    
    # Create a list of duplicates to remove.       
    for DuplicateIndex in range(0,len(ActionList)) :
    
        if not ( ActionList[DuplicateIndex][12] ) :

            # Populate remove lists
            Engine_Id = str(ActionList[DuplicateIndex][0])
            Vacancy_Id = str(ActionList[DuplicateIndex][1])
            Vacancy_Url = str(ActionList[DuplicateIndex][2])
            
            if not ( Vacancy_Id in RemoveIDs ) : 
                RemoveIDs.append(Vacancy_Id)
                RemoveDuplicate = {'engine_id':Engine_Id,'vacancy_id':Vacancy_Id,'vacancy_url':Vacancy_Url}
                RemoveList.append(RemoveDuplicate)
            
# Remove duplicates
DuplicateCount  = 0

for Duplicate in RemoveList : 

    # Change state of duplicate vacancy to 'Dropped'
    PrimaryValues = {}
    VacancyUpdate = {}
    PrimaryValues['engine_id'] = Duplicate['engine_id']
    PrimaryValues['vacancy_id'] = Duplicate['vacancy_id']

    VacancyUpdate['vacancy_state'] = 'Dropped' 
    SQLcommand = Db.GenSQLupdate(VacancyTable,VacancyUpdate,VacancyFields,PrimaryValues)
    SQLresponse = Db.SQLload(DbObject,DbCursor,SQLcommand,failure)
    Errormessage = 'SQLresponse error for SQL command ' + '\"' + SQLcommand + '\"'
    if ( (SQLresponse) == failure ): File.Logerror(ErrorfileObject,module,Errormessage,error)  
    
    # Add entry in table 'history' to reflect the change in state of the vacancy.
    Fieldnames = ['engine_id','vacancy_id','vacancy_state']
    Fieldvalues = [Duplicate['engine_id'],Duplicate['vacancy_id'],'Dropped']
    SQLcommand =  Db.GenSQLinsert(HistoryTable,Fieldnames,HistoryFields,Fieldvalues)
    SQLresponse = ( Db.SQLload(DbObject,DbCursor,SQLcommand,failure) )
    Errormessage = 'SQLresponse error for SQL command ' + '\"' + SQLcommand + '\"'
    if ( (SQLresponse) == failure ): File.Logerror(ErrorfileObject,module,Errormessage,warning)
       
    Errormessage = 'Vacancy ID %s Vacancy URL %s has been \'Dropped\'' % (Duplicate['vacancy_id'],Duplicate['vacancy_url'])
    File.Logerror(ErrorfileObject,module,Errormessage,info)
    
    DuplicateCount += 1
    
    
# Progress update
if ( len(RemoveList) > 0 ) :
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