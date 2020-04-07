# parse_mail.py
#
# This script will read the contents of job alert e-mails
# (in Outloook) to extract urls which directly display 
# the details of individual job vacancies. The script will then 
# add additional records in tables 'vacancy' and 'history' 
# in the MySQL database 'vacancies' relating to these vacancy urls. 
# The 'vacancies' database is created by script 'initialize_database.py' 
# which must be run (once) before this script can be run.
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

import win32com.client
import win32com
import sys
import os
import re
import requests
import Db
import File
import Email
import Interface
import Web
from datetime import date, datetime, timedelta

# Function return values
invalid = failure = 0
empty = ''

# Error levels
error = 'ERROR'
warning = 'WARNING'
info = 'INFO'
module = 'parse_mail'

# Age limit for e-mail 
# set to '7' days in seconds
limit = 7
limit = limit*24*60*60

# File names and modes
Currentdir = os.getcwd()
Datadir = Currentdir + '\\Data'
Errorfilename = Datadir + '\\' + 'log.txt'
Connectfilename = Datadir + '\\' + 'connect.data'
append = 'a'
read = 'r'
overwrite = 'w'

# Database and tables
DbName = 'vacancies'
EngineTable = DbName + '.' + 'engine'
VacancyTable = DbName + '.' + 'vacancy'
HistoryTable = DbName + '.' + 'history'
CounterTable = DbName + '.' + 'counter'

# Mail client detsils.
Outlook = 'OUTLOOK.EXE'
Delay = 7

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

# Killing outlook process if it exists.
Interface.KillProcess (Outlook,Delay,empty) 

# Progress update
Errormessage = 'Killed any existing instance of %s' % Outlook
File.Logerror(ErrorfileObject,module,Errormessage,info)

# Connect to Outlook
OutlookObj = Email.Mailconnect(invalid)
Errormessage = 'Unable to connect to Outlook'
if ( OutlookObj == invalid ) : File.Logerror(ErrorfileObject,module,Errormessage,error)

# Progress update
File.Logerror(ErrorfileObject,module,'Connected to Outlook',info)

# Get Outlook account information
OutlookAccounts = Email.Mailaccounts(failure)
Errormessage = 'Unable to get Outlook accounts detail'
if ( OutlookAccounts == failure ) : File.Logerror(ErrorfileObject,module,Errormessage,error)

# Read fields in table 'vacancy'
SQLcommand = 'show columns from %s' % VacancyTable 
SQLresponse = Db.SQLload(DbObject,DbCursor,SQLcommand,failure)
Errormessage = 'SQLresponse error for SQL command ' + '\"' + SQLcommand + '\"'
if ( (SQLresponse) == failure ): File.Logerror(ErrorfileObject,module,Errormessage,error)
Vacancyfields = Db.Fielddefs(SQLresponse)

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

# Read fields in table 'counter'
SQLcommand = 'show columns from %s' % CounterTable 
SQLresponse = Db.SQLload(DbObject,DbCursor,SQLcommand,failure)
Errormessage = 'SQLresponse error for SQL command ' + '\"' + SQLcommand + '\"'
if ( (SQLresponse) == failure ): File.Logerror(ErrorfileObject,module,Errormessage,error)
Counterfields = Db.Fielddefs(SQLresponse)

# Progress update
File.Logerror(ErrorfileObject,module,'Read Counter table field definitions',info)

# Read job engine data.
SQLcommand = 'select * from %s' % EngineTable
SQLresponse = Db.SQLload(DbObject,DbCursor,SQLcommand,failure)
Errormessage = 'SQLresponse error for SQL command ' + '\"' + SQLcommand + '\"'
if ( (SQLresponse) == failure ): File.Logerror(ErrorfileObject,module,Errormessage,error)

# Progress update
File.Logerror(ErrorfileObject,module,'Read Outlook mail folder detail',info)

# Build required lists.
EngineIDList = []
EngineNameList = []
MailfolderList = []
JobUrlreList = []
UrllenList = []
IDlenList = []
PrioritiesList = []
ExclusionsList = []
InclusionsList = []
JoburlLists = {}

for EngineDetails in SQLresponse :
    EngineIDList.append(EngineDetails[0])
    EngineNameList.append(EngineDetails[1])
    MailfolderList.append(EngineDetails[2])
    JobUrlreList.append(EngineDetails[3])
    UrllenList.append(EngineDetails[4])
    IDlenList.append(EngineDetails[5])
    PrioritiesList.append(EngineDetails[6])
    ExclusionsList.append(EngineDetails[7])
    InclusionsList.append(EngineDetails[8])
    
# Progress update
File.Logerror(ErrorfileObject,module,'Built mail folder list',info)

# Iterate through mail folders for each CV engine.
EngineIndex = 0

while ( EngineIndex < len(MailfolderList) ) :
    EngineName = EngineNameList[EngineIndex]
    FolderDetails = MailfolderList[EngineIndex].split(':')
    AccountName = FolderDetails[0]
    SubfolderDetails = FolderDetails[1].split('/')
    JobUrlRe = JobUrlreList[EngineIndex]
    Urllen = UrllenList[EngineIndex]
    IDlen = IDlenList[EngineIndex]
    
    # Verify if Outlook account exists
    OutlookAccount = Email.Findaccount(OutlookAccounts,AccountName,failure)
    Errormessage = 'Unable to find Outlook account ' + AccountName
    if ( OutlookAccount == failure ) : File.Logerror(ErrorfileObject,module,Errormessage,error)
    
    # Find top level folder
    OutlookFolder = Email.Topfolder(OutlookObj,OutlookAccount,failure)
    Errormessage = 'Unable to find top level folder for ' + AccountName
    if ( OutlookFolder == failure ) : File.Logerror(ErrorfileObject,module,Errormessage,error)
    
    # Find sub folder for engine's e-mail alerts.
    for subfolderdetail in SubfolderDetails :
        OutlookFolder = Email.Subfolder(OutlookFolder.Folders,subfolderdetail,failure)
        Errormessage = 'Unable to find sub folder ' + subfolderdetail
        if ( OutlookFolder == failure ) : File.Logerror(ErrorfileObject,module,Errormessage,error)
      
    # Progress update
    Errormessage = 'Processing sub-folder ' + OutlookFolder.name
    File.Logerror(ErrorfileObject,module,Errormessage,info)
    
    # ReedEngine = False
    
    # Determine if engine is 'Reed'  
    if ( EngineName == 'Reed' ) : 
        ReedEngine = True
    else :
        ReedEngine = False
    
    # Determine if there are exclusions and/or inclusions defined
    if ( len(ExclusionsList[EngineIndex]) != 0 ) : 
        Exclusions = ExclusionsList[EngineIndex].split(':')
        ExclusionsApply = True
        Errormessage = 'Exclusions will apply for mail in ' + OutlookFolder.name
        File.Logerror(ErrorfileObject,module,Errormessage,info)
    else:
        ExclusionsApply = False
        
    if ( len(InclusionsList[EngineIndex]) != 0  ) : 
        Inclusions = InclusionsList[EngineIndex].split(':')
        InclusionsApply = True
        Errormessage = 'Inclusions will apply for mail in ' + OutlookFolder.name
        File.Logerror(ErrorfileObject,module,Errormessage,info)
    else:
        InclusionsApply = False
    
    JoburlList = []
    
    # Iterate through messages in sub-folder
    Mailnumber = len(OutlookFolder.Items) - 1
    
    while ( Mailnumber >= 0 ) :
        Message = OutlookFolder.Items[Mailnumber]
        if ( Email.Isrecent(str(Message.ReceivedTime),limit,failure) != failure ) :
            MessageLines = Message.Body.split('\n')
            for messageLine in MessageLines :
                
                if ( ExclusionsApply ) : 
                    if ( Email.ExcludeLine(messageLine,Exclusions) ) : continue
                if ( InclusionsApply ) : 
                    if not ( Email.IncludeLine(messageLine,Inclusions) ) : continue 
                    
                MatchObj = re.search(JobUrlRe, messageLine)
                if MatchObj : 
                    if ( len(MatchObj.group()) > Urllen ) : 
                        if not ( ReedEngine ) : 
                            JoburlList.append(MatchObj.group()[0:Urllen])
                        else:
                        
                            # For Reed information must be scraped from vacancy
                            JobUrlRe = 'https://www.reed.co.uk/jobs/(.*?)/(\d+)'
                            Reedurl = Email.FindReedID((MatchObj.group()[0:Urllen]),JobUrlRe)
                            JoburlList.append(Reedurl)
                            Urllen = 27
                            IDlen = 8    
      
        # Move the parsed e-mail to deleted items folder.
        Message.delete()
        Mailnumber -= 1
    
    # Remove duplicate items from the list.    
    JoburlSet = set(JoburlList)
    JoburlList = list(JoburlSet)
    JoburlLists[EngineName] = JoburlList
    
    # Output job urls to csv file.
    urlcount = 0
        
    for Joburl in JoburlList : 
             
        Jobid = Joburl[len(Joburl)-IDlen:]
        
        # Determine if there is already an entry in table 'vacancy' for this job url.
        SelectCriteria = 'engine_id = %s and vacancy_id = \'%s\'' % (str(EngineIDList[EngineIndex]),Jobid)
        SQLcommand = Db.GenSQLselect(VacancyTable,SelectCriteria)
        SQLresponse = Db.SQLload(DbObject,DbCursor,SQLcommand,failure)
        Errormessage = 'SQLresponse error for SQL command ' + '\"' + SQLcommand + '\"'
        if ( (SQLresponse) == failure ): File.Logerror(ErrorfileObject,module,Errormessage,warning)
        if ( Db.GetSQLrowcount(SQLresponse) == 1 ) : continue
        
        urlcount += 1
        
        # Add entry in table 'vacancy'.
        Fieldnames = ['engine_id','vacancy_id','vacancy_url','vacancy_state']
        Fieldvalues = [str(EngineIDList[EngineIndex]),Jobid,Joburl,'New']
        SQLcommand =  Db.GenSQLinsert(VacancyTable,Fieldnames,Vacancyfields,Fieldvalues)
        SQLresponse = ( Db.SQLload(DbObject,DbCursor,SQLcommand,failure) )
        Errormessage = 'SQLresponse error for SQL command ' + '\"' + SQLcommand + '\"'
        if ( (SQLresponse) == failure ): File.Logerror(ErrorfileObject,module,Errormessage,warning)
     
        # Add entry in table 'history' to reflect the change in state of the vacancy.
        Fieldnames = ['engine_id','vacancy_id','vacancy_state']
        Fieldvalues = [str(EngineIDList[EngineIndex]),Jobid,'New']
        SQLcommand =  Db.GenSQLinsert(HistoryTable,Fieldnames,Historyfields,Fieldvalues)
        SQLresponse = ( Db.SQLload(DbObject,DbCursor,SQLcommand,failure) )
        Errormessage = 'SQLresponse error for SQL command ' + '\"' + SQLcommand + '\"'
        if ( (SQLresponse) == failure ): File.Logerror(ErrorfileObject,module,Errormessage,warning)
            
    # Progress update
    if ( urlcount > 0 ) :
        Errormessage = str(urlcount) + ' job urls found in ' + OutlookFolder.name
        File.Logerror(ErrorfileObject,module,Errormessage,info)
        
        # Add entry in table 'counter' to reflect the change in state of the vacancy.
        Fieldnames = ['engine_id','found']
        Fieldvalues = [str(EngineIDList[EngineIndex]),str(urlcount)]
        SQLcommand =  Db.GenSQLinsert(CounterTable,Fieldnames,Counterfields,Fieldvalues)
        SQLresponse = ( Db.SQLload(DbObject,DbCursor,SQLcommand,failure) )
        Errormessage = 'SQLresponse error for SQL command ' + '\"' + SQLcommand + '\"'
        if ( (SQLresponse) == failure ): File.Logerror(ErrorfileObject,module,Errormessage,warning)
        
    else :
        Errormessage = 'No job urls found in ' + OutlookFolder.name
        File.Logerror(ErrorfileObject,module,Errormessage,warning)
          
    EngineIndex += 1

# Progress update
File.Logerror(ErrorfileObject,module,'Displayed mail folder information',info)

# Disconnect from database.
Errormessage = 'Could not disconnect from database'
if ( Db.Disconnect(DbObject,failure) == failure ) : File.Logerror(ErrorfileObject,module,Errormessage,warning)

# Log end of script
File.Logerror(ErrorfileObject,module,'Completed',info)

# Close error log file
Errormessage = 'Could not close ' + Errorfilename
if ( File.Close(ErrorfileObject,failure) == failure ) : File.Logerror(ErrorfileObject,module,Errormessage,warning)


    