# generate_report.py
#
# Description
# -----------
# This script will read the 'vacancy' and 'history' tables of the 'vacancies' 
# database in order to create a csv file detailing the history of all 
# vacancies applied for. Further manual manipulation of this csv files is required
# to create an xlsx format file. This utility is intended to provide 
# evidence that jobs are actively being applied for which is one of the
# the conditions that need to be satisfied in order to claim 'New Style JSA'. 
# See the link below for further details on 'New Style JSA'.
#
# https://www.gov.uk/how-to-claim-new-style-jsa
#
# Data and configuration files
# ----------------------------
# 
# The following data and configuration files are required by
# this script:
#
# .\Data\connect.data               -   Contains MySQL login details. 
# .\Data\application_history.docx   -   Document containing desciption
#                                       description of contents and hyper link
#                                       to ./Data/application_history.xlsx
#
# Export file
# -----------
#
# This script will create an export file in the C:\JOBSEARCH\2019\Co-Ordination directory
# with the following file name format:
#
# application_history.csv
#
# The first row of this file will consist of the following column headings:
#
# Company,Title,Location,Vacancy_url,New,Enhanced,Aapplied,Dropped,First,Second,Third,Offer,Rejected
#
# Subsequent rows of this file will contain job application data in the following format:
#
# <company name>,<job title>,<job location>,<job url>,<date and time application status changed to 'New'>,....,<date and time application status changed to 'Rejected'>
#
# Logging
# -------
# This script logs progress and error information in:
#
# ./Data/log.txt

import Db
import File
import Interface
import os
import subprocess
import sys

# Function return values
invalid = failure = 0
empty = ''
success = 1

# Error levels
error = 'ERROR'
warning = 'WARNING'
info = 'INFO'
module = 'genrate_report'

# File names and modes
Currentdir = os.getcwd()
Datadir = Currentdir + '\\Data'
Errorfilename = Datadir + '\\' + 'log.txt'
Connectfilename = Datadir + '\\' + 'connect.csv'
Historyfilename = 'C:\\JOBSEARCH\\2019\\Co-Ordination\\' + 'application_history.csv'
append = 'a'
read = 'r'
overwrite = 'w'

# Broswer
Spreadsheet = 'excel.exe'

# Database and tables
DbName = 'vacancies'
VacancyTable = DbName + '.' + 'vacancy'
HistoryTable = DbName + '.' + 'history'

# CSV file columns
CSVColumns = ('company','title','location','vacancy_url','New','Enhanced','Applied','Dropped','First','Second','Third','Offer','Rejected')

# Create/open log file
ErrorfileObject = File.Open(Errorfilename,append,failure)
Errormessage = 'Could not open ' + Errorfilename
if ( ErrorfileObject == failure ) : File.Logerror(ErrorfileObject,module,Errormessage,error)

# Log start of script
File.Logerror(ErrorfileObject,module,'Started',info)

# Open export file
HistoryfileObject = File.Open(Historyfilename,overwrite,failure)
Errormessage = 'Could not open ' + Historyfilename
if ( ErrorfileObject == failure ) : File.Logerror(ErrorfileObject,module,Errormessage,error)

# Progress message
Errormessage = 'Openned export file ' + Historyfilename
File.Logerror(ErrorfileObject,module,Errormessage,info)

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

# List all vacancy id's that have been applied for.
SQLcommand  = 'select engine_id,vacancy_id from %s where vacancy_state = \'%s\'' % (HistoryTable,'Applied')
SQLresponse = Db.SQLload(DbObject,DbCursor,SQLcommand,failure)
Errormessage = 'SQLresponse error for SQL command ' + '\"' + SQLcommand + '\"'
if ( (SQLresponse) == failure ): File.Logerror(ErrorfileObject,module,Errormessage,error)

# Progress update
File.Logerror(ErrorfileObject,module,'Generating report',info) 

# Write column headers to export file
OutputLine = ''
for CSVColumn in CSVColumns :
    OutputLine = OutputLine + CSVColumn.capitalize()  + ','

OutputLine = OutputLine.rstrip(',')
OutputLine = OutputLine + '\n'
File.Writeline(HistoryfileObject,OutputLine,failure)

# Iterate through all vacancies where an application has been made:
for VacancyHistory in SQLresponse :
    
    EngineID = VacancyHistory[0]
    VacancyID = VacancyHistory[1]
    
    # Intialise row output
    CSVRow = {}
    for CSVcolumn in CSVColumns : 
        CSVRow[CSVcolumn] = ''
    
    # Determine vacancy details
    SQLcommand  = 'select company,title,location,vacancy_url from %s where engine_id = %s and vacancy_id = \'%s\'' % (VacancyTable,EngineID,VacancyID)
    SQLresponse = Db.SQLload(DbObject,DbCursor,SQLcommand,failure)
    Errormessage = 'SQLresponse error for SQL command ' + '\"' + SQLcommand + '\"'
    if ( (SQLresponse) == failure ): File.Logerror(ErrorfileObject,module,Errormessage,error)
    
    for VacancyData in SQLresponse :
        CSVRow['company'] = VacancyData[0]
        CSVRow['title'] = VacancyData[1]
        CSVRow['location'] = VacancyData[2]
        CSVRow['vacancy_url'] = VacancyData[3]
    
    # Determine vacancy state change information
    SQLcommand  = 'select vacancy_state,time_stamp from %s where engine_id = %s and vacancy_id = \'%s\'' % (HistoryTable,EngineID,VacancyID)
    SQLresponse = Db.SQLload(DbObject,DbCursor,SQLcommand,failure)
    Errormessage = 'SQLresponse error for SQL command ' + '\"' + SQLcommand + '\"'
    if ( (SQLresponse) == failure ): File.Logerror(ErrorfileObject,module,Errormessage,error)
    
    for StateChangeData in SQLresponse :
        CSVRow[StateChangeData[0]] = StateChangeData[1]
      
    # Print vacancy data
    OutputLine = ''
    for RowValue in CSVRow.values() :
        OutputLine = OutputLine + '\"' + str(RowValue) +'\"' + ','
       
    OutputLine = OutputLine.rstrip(',')
    OutputLine = OutputLine + '\n'
    File.Writeline(HistoryfileObject,OutputLine,failure)

# Disconnect from database.
Errormessage = 'Could not disconnect from database'
if ( Db.Disconnect(DbObject,failure) == failure ) : File.Logerror(ErrorfileObject,module,Errormessage,warning)

# Close export file
Errormessage = 'Could not close ' + Historyfilename
if ( File.Close(HistoryfileObject,failure) == failure ) : File.Logerror(ErrorfileObject,module,Errormessage,warning)

# Display manual step message and launch Excel
Errormessage = 'Please convert %s to xlsx format' % Historyfilename
File.Logerror(ErrorfileObject,module,Errormessage,warning)

Interface.ViewSpeadsheet(Spreadsheet,Historyfilename) 

# Log end of script
File.Logerror(ErrorfileObject,module,'Completed',info)


# Close error log file
Errormessage = 'Could not close ' + Errorfilename
if ( File.Close(ErrorfileObject,failure) == failure ) : File.Logerror(ErrorfileObject,module,Errormessage,warning)