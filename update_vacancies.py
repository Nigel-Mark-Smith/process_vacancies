# update_vacancies.py
#
# Description
# -----------
# This script will read the 'vacancy' table of the 'vacancies' database
# in order to display both new vacancies and vacancies that are currently 
# being pursued. Following the display of a vacancy ( by Chrome ) the user
# is prompted to add additional detail and/or change the state of the vacancy.
# New vacancies are imported into the MySQL database via the script 'parse_mail.py'.
# The 'vacancies' database is created by script 'initialize_database.py' which 
# must be run (once) before this script can be run.
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

import re
import requests
import sys
import os
import Db
import File
import Email
import Interface
import Web
import subprocess
import json


# Function return values
invalid = failure = 0
empty = ''
success = 1

# Error levels
error = 'ERROR'
warning = 'WARNING'
info = 'INFO'
module = 'update_vacancies'

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

# Broswer
Browser = 'chrome.exe'
Killdelay = 1

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
Vacanyfields = Db.Fielddefs(SQLresponse)

# Progress update
File.Logerror(ErrorfileObject,module,'Read vacancy table field definitions',info)

# Read fields in table 'history'
SQLcommand = 'show columns from %s' % HistoryTable 
SQLresponse = Db.SQLload(DbObject,DbCursor,SQLcommand,failure)
Errormessage = 'SQLresponse error for SQL command ' + '\"' + SQLcommand + '\"'
if ( (SQLresponse) == failure ): File.Logerror(ErrorfileObject,module,Errormessage,error)
Historyfields = Db.Fielddefs(SQLresponse)

# Progress update
File.Logerror(ErrorfileObject,module,'Read history table field definitions',info)

# Select all new vacancies.
SQLcommand  = 'select * from %s where vacancy_state = \'%s\'' % (VacancyTable,'New')
SQLresponse = Db.SQLload(DbObject,DbCursor,SQLcommand,failure)
Errormessage = 'SQLresponse error for SQL command ' + '\"' + SQLcommand + '\"'
if ( (SQLresponse) == failure ): File.Logerror(ErrorfileObject,module,Errormessage,error)

# Iterate through the new vacancies
VacancyTotal = len(SQLresponse)
VacancyNumber = 1

for Vacancy in SQLresponse :

    # Progress update
    print('******** Processing New vacancy %s of %s ********' % ( str(VacancyNumber),str(VacancyTotal) ) )
    
    EngineID = Vacancy[0]
    JobID = Vacancy[1]
    Joburl = Vacancy[2]
    
    # Create the primary fields dictionary of values.
    Primary = {}
    Primary['vacancy_id'] = JobID
    Primary['engine_id'] = EngineID
    
    # Display to true
    Display = True

    # Populate updates. This involves scraping web content.
    VacancyUpdate = {}
    if ( EngineID == 1 ) : 
        VacancyUpdate = Web.ScrapeCVLibrary(Joburl)
        if not 'title' in VacancyUpdate : 
            Display = False
            Errormessage = 'Vacancy %s for CV-Libaray has expired' % JobID
            File.Logerror(ErrorfileObject,module,Errormessage,info)   
            
    if ( EngineID == 2 ) : 
        VacancyUpdate = Web.ScrapeLinkedIn(Joburl)
        # Job alerts can contain expired vacancies
        if not 'title' in VacancyUpdate : 
            Display = False
            Errormessage = 'Vacancy %s for LinkedIn has expired' % JobID
            File.Logerror(ErrorfileObject,module,Errormessage,info)
            
    if ( EngineID == 3 ) : 
        VacancyUpdate = Web.ScrapeReed(Joburl)
        # Job alerts can contain expired vacancies
        if not 'title' in VacancyUpdate : 
            Display = False
            Errormessage = 'Vacancy %s for Reed has expired' % JobID
            File.Logerror(ErrorfileObject,module,Errormessage,info)
            
    if ( EngineID == 4 ) : VacancyUpdate = Web.ScrapeIndeed(Joburl)
    if ( EngineID == 5 ) : 
        VacancyUpdate = Web.ScrapeTotalJobs(Joburl)
        # Job alerts can contain expired vacancies
        if not 'title' in VacancyUpdate : 
            Display = False
            Errormessage = 'Vacancy %s for TotalJobs has expired' % JobID
            File.Logerror(ErrorfileObject,module,Errormessage,info)
            
    if ( EngineID == 6 ) : 
        VacancyUpdate = Web.ScrapeFindAJob(Joburl)
        # Job alerts can contain expired vacancies
        if not 'title' in VacancyUpdate : 
            Display = False
            Errormessage = 'Vacancy %s for FindAJob has expired' % JobID
            File.Logerror(ErrorfileObject,module,Errormessage,info)
            
    HistoryUpdate = {}
    
    if ( Display ) :
    
        # Display vacancy.
        if ( EngineID == 5 ) :
            Interface.ViewVacancyByBatch(Browser,Joburl)
        else:
            Interface.ViewVacancy(Browser,Joburl)
    
        # Display standard job details.
        Interface.DisplayDetails(VacancyUpdate)
   
        # Enter if further action is required.
        Choices = ['y','n','skip']
        Prompt = 'Do you wish to pursue vacancy %s %s : ' % ( JobID , str(Choices) )
        Choice = Interface.GetChoice(Prompt,Choices,count = 2)  

    else:
    
        Choice = 'n' 
    
    # Set vacancy to correct state and fill in further details if available
    if ( Choice == 'y' ) :
    
        ReSelect = False
  
        while True :
        
            # Enhance database updates
            VacancyUpdate['vacancy_state'] = 'Enhanced'    

            if ( ( len(VacancyUpdate['company']) == 0 ) or ReSelect ) :
                Prompt = 'Please enter the name of the company where the vacancy is : '
                VacancyUpdate['company'] = Interface.GetStrinput(Prompt)
        
            if ( ( len(VacancyUpdate['title']) == 0 ) or ReSelect ) :
                Prompt = 'Please enter the name of the title of the vacancy : '
                VacancyUpdate['title'] = Interface.GetStrinput(Prompt)
                
            if ( ( len(VacancyUpdate['location']) == 0 ) or ReSelect ) :
                Prompt = 'Please enter the name of the location of the vacancy : '
                VacancyUpdate['location'] = Interface.GetStrinput(Prompt)
        
            if ( ( VacancyUpdate['salary_min'] == 0 ) or ReSelect ) :
                Prompt = 'Please enter the minimum salary for the vacancy : '
                VacancyUpdate['salary_min'] = str(Interface.GetIntinput(Prompt))
                
            if ( ( VacancyUpdate['salary_max'] == 0 ) or ReSelect ):
                Prompt = 'Please enter the maximum salary for the vacancy : '
                VacancyUpdate['salary_max'] = str(Interface.GetIntinput(Prompt))

            # Confirm if the details to be entered are correct. If not
            # re-enter.
            Choices = ['y','n']
            Prompt = 'Are the values entered correct %s : ' % str(Choices)
            Choice = Interface.GetChoice(Prompt,Choices,count = 2)
            
            if ( Choice == 'y' ) : 
                break
            else : 
                ReSelect = True
        
        # Execute database updates
        SQLcommand = Db.GenSQLupdate(VacancyTable,VacancyUpdate,Vacanyfields,Primary)
        SQLresponse = Db.SQLload(DbObject,DbCursor,SQLcommand,failure)
        Errormessage = 'SQLresponse error for SQL command ' + '\"' + SQLcommand + '\"'
        if ( (SQLresponse) == failure ): File.Logerror(ErrorfileObject,module,Errormessage,error)
        
        # Create and execute database inserts 
        Fieldnames = ['engine_id','vacancy_id','vacancy_state']
        Fieldvalues = [str(EngineID),JobID,'Enhanced']
        SQLcommand =  Db.GenSQLinsert(HistoryTable,Fieldnames,Historyfields,Fieldvalues)
        SQLresponse = ( Db.SQLload(DbObject,DbCursor,SQLcommand,failure) )
        Errormessage = 'SQLresponse error for SQL command ' + '\"' + SQLcommand + '\"'
        if ( (SQLresponse) == failure ): File.Logerror(ErrorfileObject,module,Errormessage,warning)
        
    elif ( Choice == 'skip' ) : break
        
    else:
    
        # Create and execute database updates       
        VacancyUpdate['vacancy_state'] = 'Dropped' 
        SQLcommand = Db.GenSQLupdate(VacancyTable,VacancyUpdate,Vacanyfields,Primary)
        SQLresponse = Db.SQLload(DbObject,DbCursor,SQLcommand,failure)
        Errormessage = 'SQLresponse error for SQL command ' + '\"' + SQLcommand + '\"'
        if ( (SQLresponse) == failure ): File.Logerror(ErrorfileObject,module,Errormessage,error)
        
        # Create and execute database inserts
        Fieldnames = ['engine_id','vacancy_id','vacancy_state']
        Fieldvalues = [str(EngineID),JobID,'Dropped']
        SQLcommand =  Db.GenSQLinsert(HistoryTable,Fieldnames,Historyfields,Fieldvalues)
        SQLresponse = ( Db.SQLload(DbObject,DbCursor,SQLcommand,failure) )
        Errormessage = 'SQLresponse error for SQL command ' + '\"' + SQLcommand + '\"'
        if ( (SQLresponse) == failure ): File.Logerror(ErrorfileObject,module,Errormessage,warning)
    
    # Remove vacancy from view
    VacancyNumber += 1
    Interface.KillProcess(Browser,Killdelay,empty)
    
    
# Select all vacancies in progress.
SQLcommand  = 'select * from %s where vacancy_state != \'New\' and vacancy_state != \'Dropped\' and vacancy_state != \'Rejected\'' % VacancyTable
SQLresponse = Db.SQLload(DbObject,DbCursor,SQLcommand,failure)
Errormessage = 'SQLresponse error for SQL command ' + '\"' + SQLcommand + '\"'
if ( (SQLresponse) == failure ): File.Logerror(ErrorfileObject,module,Errormessage,error)

# Iterate through the ongoing vacancies
VacancyTotal = len(SQLresponse)
VacancyNumber = 1

for Vacancy in SQLresponse :


    # Progress update
    print('******** Processing On-going vacancy %s of %s ********' % ( str(VacancyNumber),str(VacancyTotal) ) )
    
    EngineID = Vacancy[0]
    JobID = Vacancy[1]
    Joburl = Vacancy[2]
    Vacancystate = Vacancy[3]
    
    VacancyDetails = {}
    VacancyDetails['company'] =  Vacancy[4]
    VacancyDetails['title'] =  Vacancy[5]
    VacancyDetails['location'] =  Vacancy[6]
    VacancyDetails['salary_min'] = Vacancy[7]
    VacancyDetails['salary_max'] = Vacancy[8]
    
    # Create the primary fields dictionary of values.
    Primary = {}
    Primary['vacancy_id'] = JobID
    Primary['engine_id'] = EngineID

    # Initialize updates
    VacancyUpdate = {}
    HistoryUpdate = {}
    
    # It may be that the CV-Library vacancy has expired.
    if ( EngineID == 1 ) : 
        VacancyUpdate = Web.ScrapeCVLibrary(Joburl)
        if not 'title' in VacancyUpdate : 
            Errormessage = 'Vacancy %s for CV-Library has expired and will be Dropped' % JobID
            File.Logerror(ErrorfileObject,module,Errormessage,info)
            
            VacancyUpdate['vacancy_state'] = 'Dropped'
            
            # Create and execute database updates        
            SQLcommand = Db.GenSQLupdate(VacancyTable,VacancyUpdate,Vacanyfields,Primary)
            SQLresponse = Db.SQLload(DbObject,DbCursor,SQLcommand,failure)
            Errormessage = 'SQLresponse error for SQL command ' + '\"' + SQLcommand + '\"'
            if ( (SQLresponse) == failure ): File.Logerror(ErrorfileObject,module,Errormessage,error)
        
            # Create and execute database inserts
            Fieldnames = ['engine_id','vacancy_id','vacancy_state']
            Fieldvalues = [str(EngineID),JobID,VacancyUpdate['vacancy_state']]
            SQLcommand =  Db.GenSQLinsert(HistoryTable,Fieldnames,Historyfields,Fieldvalues)
            SQLresponse = ( Db.SQLload(DbObject,DbCursor,SQLcommand,failure) )
            Errormessage = 'SQLresponse error for SQL command ' + '\"' + SQLcommand + '\"'
            if ( (SQLresponse) == failure ): File.Logerror(ErrorfileObject,module,Errormessage,warning)
            
            VacancyNumber += 1
            continue
    
    # It may be that the LinkedIn vacancy has expired.
    if ( EngineID == 2 ) : 
        VacancyUpdate = Web.ScrapeLinkedIn(Joburl)
        if not 'title' in VacancyUpdate : 
            Errormessage = 'Vacancy %s for LinkedIn has expired and will be Dropped' % JobID
            File.Logerror(ErrorfileObject,module,Errormessage,info)
            
            VacancyUpdate['vacancy_state'] = 'Dropped'
            
            # Create and execute database updates        
            SQLcommand = Db.GenSQLupdate(VacancyTable,VacancyUpdate,Vacanyfields,Primary)
            SQLresponse = Db.SQLload(DbObject,DbCursor,SQLcommand,failure)
            Errormessage = 'SQLresponse error for SQL command ' + '\"' + SQLcommand + '\"'
            if ( (SQLresponse) == failure ): File.Logerror(ErrorfileObject,module,Errormessage,error)
        
            # Create and execute database inserts
            Fieldnames = ['engine_id','vacancy_id','vacancy_state']
            Fieldvalues = [str(EngineID),JobID,VacancyUpdate['vacancy_state']]
            SQLcommand =  Db.GenSQLinsert(HistoryTable,Fieldnames,Historyfields,Fieldvalues)
            SQLresponse = ( Db.SQLload(DbObject,DbCursor,SQLcommand,failure) )
            Errormessage = 'SQLresponse error for SQL command ' + '\"' + SQLcommand + '\"'
            if ( (SQLresponse) == failure ): File.Logerror(ErrorfileObject,module,Errormessage,warning)
            
            VacancyNumber += 1
            continue
    
    # It may be that the Reed vacancy has expired.    
    if ( EngineID == 3 ) : 
        VacancyUpdate = Web.ScrapeReed(Joburl)
        if not 'title' in VacancyUpdate : 
            Errormessage = 'Vacancy %s for Reed has expired and will be Dropped' % JobID
            File.Logerror(ErrorfileObject,module,Errormessage,info)
            
            VacancyUpdate['vacancy_state'] = 'Dropped'
            
            # Create and execute database updates        
            SQLcommand = Db.GenSQLupdate(VacancyTable,VacancyUpdate,Vacanyfields,Primary)
            SQLresponse = Db.SQLload(DbObject,DbCursor,SQLcommand,failure)
            Errormessage = 'SQLresponse error for SQL command ' + '\"' + SQLcommand + '\"'
            if ( (SQLresponse) == failure ): File.Logerror(ErrorfileObject,module,Errormessage,error)
        
            # Create and execute database inserts
            Fieldnames = ['engine_id','vacancy_id','vacancy_state']
            Fieldvalues = [str(EngineID),JobID,VacancyUpdate['vacancy_state']]
            SQLcommand =  Db.GenSQLinsert(HistoryTable,Fieldnames,Historyfields,Fieldvalues)
            SQLresponse = ( Db.SQLload(DbObject,DbCursor,SQLcommand,failure) )
            Errormessage = 'SQLresponse error for SQL command ' + '\"' + SQLcommand + '\"'
            if ( (SQLresponse) == failure ): File.Logerror(ErrorfileObject,module,Errormessage,warning)
            
            VacancyNumber += 1
            continue
            
    # It may be that the Indeed vacancy has expired.    
    if ( EngineID == 4 ) : 
        VacancyUpdate = Web.ScrapeIndeed(Joburl)
        if not 'title' in VacancyUpdate : 
            Errormessage = 'Vacancy %s for Indeed has expired and will be Dropped' % JobID
            File.Logerror(ErrorfileObject,module,Errormessage,info)
            
            VacancyUpdate['vacancy_state'] = 'Dropped'
            
            # Create and execute database updates        
            SQLcommand = Db.GenSQLupdate(VacancyTable,VacancyUpdate,Vacanyfields,Primary)
            SQLresponse = Db.SQLload(DbObject,DbCursor,SQLcommand,failure)
            Errormessage = 'SQLresponse error for SQL command ' + '\"' + SQLcommand + '\"'
            if ( (SQLresponse) == failure ): File.Logerror(ErrorfileObject,module,Errormessage,error)
        
            # Create and execute database inserts
            Fieldnames = ['engine_id','vacancy_id','vacancy_state']
            Fieldvalues = [str(EngineID),JobID,VacancyUpdate['vacancy_state']]
            SQLcommand =  Db.GenSQLinsert(HistoryTable,Fieldnames,Historyfields,Fieldvalues)
            SQLresponse = ( Db.SQLload(DbObject,DbCursor,SQLcommand,failure) )
            Errormessage = 'SQLresponse error for SQL command ' + '\"' + SQLcommand + '\"'
            if ( (SQLresponse) == failure ): File.Logerror(ErrorfileObject,module,Errormessage,warning)
            
            VacancyNumber += 1
            continue
        
           
    # It may be that the TotalJobs vacancy has expired.
    if ( EngineID == 5 ) : 
        VacancyUpdate = Web.ScrapeTotalJobs(Joburl)
        if not 'title' in VacancyUpdate : 
            Errormessage = 'Vacancy %s for Totaljobs has expired and will be Dropped' % JobID
            File.Logerror(ErrorfileObject,module,Errormessage,info)
            
            VacancyUpdate['vacancy_state'] = 'Dropped'
            
            # Create and execute database updates        
            SQLcommand = Db.GenSQLupdate(VacancyTable,VacancyUpdate,Vacanyfields,Primary)
            SQLresponse = Db.SQLload(DbObject,DbCursor,SQLcommand,failure)
            Errormessage = 'SQLresponse error for SQL command ' + '\"' + SQLcommand + '\"'
            if ( (SQLresponse) == failure ): File.Logerror(ErrorfileObject,module,Errormessage,error)
        
            # Create and execute database inserts
            Fieldnames = ['engine_id','vacancy_id','vacancy_state']
            Fieldvalues = [str(EngineID),JobID,VacancyUpdate['vacancy_state']]
            SQLcommand =  Db.GenSQLinsert(HistoryTable,Fieldnames,Historyfields,Fieldvalues)
            SQLresponse = ( Db.SQLload(DbObject,DbCursor,SQLcommand,failure) )
            Errormessage = 'SQLresponse error for SQL command ' + '\"' + SQLcommand + '\"'
            if ( (SQLresponse) == failure ): File.Logerror(ErrorfileObject,module,Errormessage,warning)
            
            VacancyNumber += 1
            continue
    
    # It may be that the FindAJob vacancy has expired.
    if ( EngineID == 6 ) : 
        VacancyUpdate = Web.ScrapeFindAJob(Joburl)
        if not 'title' in VacancyUpdate : 
            Errormessage = 'Vacancy %s for FindAJob has expired and will be Dropped' % JobID
            File.Logerror(ErrorfileObject,module,Errormessage,info)
            
            VacancyUpdate['vacancy_state'] = 'Dropped'
            
            # Create and execute database updates        
            SQLcommand = Db.GenSQLupdate(VacancyTable,VacancyUpdate,Vacanyfields,Primary)
            SQLresponse = Db.SQLload(DbObject,DbCursor,SQLcommand,failure)
            Errormessage = 'SQLresponse error for SQL command ' + '\"' + SQLcommand + '\"'
            if ( (SQLresponse) == failure ): File.Logerror(ErrorfileObject,module,Errormessage,error)
        
            # Create and execute database inserts
            Fieldnames = ['engine_id','vacancy_id','vacancy_state']
            Fieldvalues = [str(EngineID),JobID,VacancyUpdate['vacancy_state']]
            SQLcommand =  Db.GenSQLinsert(HistoryTable,Fieldnames,Historyfields,Fieldvalues)
            SQLresponse = ( Db.SQLload(DbObject,DbCursor,SQLcommand,failure) )
            Errormessage = 'SQLresponse error for SQL command ' + '\"' + SQLcommand + '\"'
            if ( (SQLresponse) == failure ): File.Logerror(ErrorfileObject,module,Errormessage,warning)
            
            VacancyNumber += 1
            continue
    
    # Display vacancy.
    if ( EngineID == 5 ) :
        Interface.ViewVacancyByBatch(Browser,Joburl)
    else:
        Interface.ViewVacancy(Browser,Joburl)
    
    # Display standard job details.
    Interface.DisplayDetails(VacancyDetails)
    
    # Enter if further action is required.
    Choices = ['y','n','exit']
    Prompt = 'Do you wish to change the state of vacancy %s from %s %s : ' % ( JobID ,Vacancystate, str(Choices) )
    Choice = Interface.GetChoice(Prompt,Choices,count = 2)
    
    if ( Choice == 'y' ) :
  
        while True :
        
            # Create select of new possible states
            if ( Vacancystate == 'Enhanced' ) : Choices = ['Applied','Dropped','First','Second','Third','Offer','Rejected']
            if ( Vacancystate == 'Applied' ) : Choices = ['Dropped','First','Rejected']
            if ( Vacancystate == 'First' ) : Choices = ['Dropped','Second','Offer','Rejected']
            if ( Vacancystate == 'Second' ) : Choices = ['Dropped','Third','Offer','Rejected']
            if ( Vacancystate == 'Third' ) : Choices = ['Dropped','Offer','Rejected']
            Prompt = 'Please enter one of the following states %s : ' % str(Choices)
            VacancyUpdate['vacancy_state']  = Interface.GetChoice(Prompt,Choices,count = 2)
            
            # Confirm the change
            Choices = ['y','n']
            Prompt = 'Do you wish to change the state of vacancy %s to %s %s : ' % ( JobID ,VacancyUpdate['vacancy_state'], str(Choices) )
            Choice = Interface.GetChoice(Prompt,Choices,count = 2)  
            
            if ( Choice == 'y' ) : break
            
        
        # Create and execute database updates        
        SQLcommand = Db.GenSQLupdate(VacancyTable,VacancyUpdate,Vacanyfields,Primary)
        SQLresponse = Db.SQLload(DbObject,DbCursor,SQLcommand,failure)
        Errormessage = 'SQLresponse error for SQL command ' + '\"' + SQLcommand + '\"'
        if ( (SQLresponse) == failure ): File.Logerror(ErrorfileObject,module,Errormessage,error)
        
        # Create and execute database inserts
        Fieldnames = ['engine_id','vacancy_id','vacancy_state']
        Fieldvalues = [str(EngineID),JobID,VacancyUpdate['vacancy_state']]
        SQLcommand =  Db.GenSQLinsert(HistoryTable,Fieldnames,Historyfields,Fieldvalues)
        SQLresponse = ( Db.SQLload(DbObject,DbCursor,SQLcommand,failure) )
        Errormessage = 'SQLresponse error for SQL command ' + '\"' + SQLcommand + '\"'
        if ( (SQLresponse) == failure ): File.Logerror(ErrorfileObject,module,Errormessage,warning)
    
    VacancyNumber += 1
    Interface.KillProcess(Browser,Killdelay,empty)
    
    if ( Choice == 'exit' ) : break
        
# Disconnect from database.
Errormessage = 'Could not disconnect from database'
if ( Db.Disconnect(DbObject,failure) == failure ) : File.Logerror(ErrorfileObject,module,Errormessage,warning)

# Log end of script
File.Logerror(ErrorfileObject,module,'Completed',info)

# Close error log file
Errormessage = 'Could not close ' + Errorfilename
if ( File.Close(ErrorfileObject,failure) == failure ) : File.Logerror(ErrorfileObject,module,Errormessage,warning)