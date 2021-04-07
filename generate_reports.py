# generate_reports.py
#
# Description
# -----------
# This script will read the 'vacancy' and 'history' tables of the 'vacancies' 
# database in order to create a csv file detailing the history of all 
# vacancies applied for. Further manipulation of this csv files is also
# performed to create an xlsx format file with the same contents. This 
# utility is intended to provide evidence that jobs are actively being 
# applied for which is one of the conditions that need to be satisfied 
# in order to claim 'New Style JSA'. See the link below for further details 
# on 'New Style JSA'.
#
# https://www.gov.uk/how-to-claim-new-style-jsa
#
# This script also runs the sql query script 'queries.sql' which 
# generates further report data. The script 'queries.sql' must write
# any additional report data to file(s) in the directory
# C:\JOBSEARCH\2019\Co-Ordination\reports. All existing files in this 
# directory are removed before new report files are generated.
# 
# Usage
# -----
# This script requires no command line arguments and may be run as follows:
#
# python generate_report.py
#
# Data and configuration files
# ----------------------------
# The following data and configuration files are required by
# this script:
#
# .\Data\connect.data               -   Contains MySQL login details. 
# .\Data\application_history.docx   -   Document containing desciption
#                                       description of contents and hyper link
#                                       to ./Data/application_history.xlsx
# .\Data\queries.sql                -   An sql script which when run generates
#                                       additional metric data files.
#
# This script also requires the vitual basic script .\convert_workbook.vbs and the
# excel macros PERSONAL.XLSB!ReformatData and PERSONAL.XLSB!SaveAsXlsx to store
# application_history.csv in xlsx format.
#
# In my installation the macros are stored in the following file.
#
# C:\Users\<user name>\AppData\Roaming\Microsoft\Excel\XLSTART\PERSONAL.XLSB
#
# The macros have the following contents:
#
# Sub ReformatData()
# '
# ' ReformatData Macro
# ' Reformats csv data
# '
# ' Keyboard Shortcut: Ctrl+r
# '
#     Cells.Select
#     Selection.Columns.AutoFit
#     Selection.AutoFilter
# End Sub
#
# Sub SaveAsXlsx()
# '
# ' SaveAsXlsx Macro
# ' Save xlsx version of file
# '
# ' Keyboard Shortcut: Ctrl+s
# '
#     ChDir ActiveWorkbook.Path
#     ActiveWorkbook.SaveAs FileFormat:=xlOpenXMLWorkbook
#     ActiveWorkbook.Close
#    
# End Sub
#
# Report files
# ------------
# This script currently generates the following report files. 
#
# application_history.csv
# application_history.xlsx
# application_history_search.csv
# new_vacancies.csv
# new_vacancies_<n>.csv
# total_duplicates.csv
# total_in_state.csv
# total_vacancies.csv
#
# The format/contents of these files are as follows
#
# - application_history.csv/application_history.xlsx
#
# The first row of this file will consist of the following column headings:
#
# Company,Title,Location,Vacancy_url,New,Enhanced,Aapplied,Dropped,First,Second,Third,Offer,Rejected
#
# Subsequent rows of this file will contain job application data in the following format:
#
# <company name>,<job title>,<job location>,<job url>,<date and time application status changed to 'New'>,....,<date and time application status changed to 'Rejected'>
#
# - application_history_search.csv
# 
# Contains data on the number and timing of state changes for all applications made
#
# - new_vacancies.csv
#
# Contains data on The number of new vacancies detected per week
#
# - new_vacancies_<n>.csv
#
# Contains data on the number of new vacancies detected per week on a per engine basis.
#
# - total_duplicates.csv
# 
# Contains data on the total number of vacancies detected on a per engine basis
#
# - total_in_state.csv
#
# Contains data on the total number of duplicate vacancies detected on a per engine basis.
#
# - total_vacancies.csv
#
# Contains data on the number of vacancies currently in each possible state.
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
module = 'generate_reports'

# File names and modes
Currentdir = os.getcwd()
Datadir = Currentdir + '\\Data'
Errorfilename = Datadir + '\\' + 'log.txt'
Connectfilename = Datadir + '\\' + 'connect.csv'
Queriesfilename = Datadir + '\\' + 'queries.sql'
Metricsdir = 'C:\\JOBSEARCH\\2019\\Co-Ordination\\reports\\' 
Historyfilename = Metricsdir + 'application_history.csv'
Convertedhistoryfilename = Metricsdir + 'application_history.xlsx'
append = 'a'
read = 'r'
overwrite = 'w'

# Spreadsheet and script details
Spreadsheet = 'excel.exe'
ConversionScript = Currentdir + '\\convert_workbook.vbs'
ConversionWait = 6

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

# Progress message
Errormessage = 'Reading queries run file ' + Queriesfilename
File.Logerror(ErrorfileObject,module,Errormessage,info)

QueriesfileObject = File.Open(Queriesfilename,read,failure)
Errormessage = 'Could not open ' + Queriesfilename
if ( QueriesfileObject == failure ) : File.Logerror(ErrorfileObject,module,Errormessage,error)

QueriesfileData = File.Read(QueriesfileObject,empty)
Errormessage = 'No data in ' + Queriesfilename
if ( QueriesfileData != empty ) : 
    QueriesfileDataLines = QueriesfileData.split(';\n')
else: 
    File.Logerror(ErrorfileObject,module,Errormessage,error)
    
if ( File.Close(QueriesfileObject,failure) == failure ) : print ('Could not close %s' % Queriesfilename)

# Progress message
Errormessage = 'Removing old report files'
File.Logerror(ErrorfileObject,module,Errormessage,info)

# Remove old report files.
with os.scandir(Metricsdir) as files :
    for file in files :
        if file.is_file : 
            os.remove(file.path)
            Errormessage = 'File %s has been removed' % file.path
            File.Logerror(ErrorfileObject,module,Errormessage,info)

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
File.Logerror(ErrorfileObject,module,'Generating reports',info) 

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
    

# Generate other report data.
for QueriesfileLine in QueriesfileDataLines :
    SQLcommand = QueriesfileLine.replace(';','')
    SQLresponse = Db.SQLload(DbObject,DbCursor,SQLcommand,failure)
    Errormessage = 'SQLresponse error for SQL command ' + '\"' + SQLcommand + '\"'
    if ( (SQLresponse) == failure ): File.Logerror(ErrorfileObject,module,Errormessage,error)
    
# Disconnect from database.
Errormessage = 'Could not disconnect from database'
if ( Db.Disconnect(DbObject,failure) == failure ) : File.Logerror(ErrorfileObject,module,Errormessage,warning)

# Close export file
Errormessage = 'Could not close ' + Historyfilename
if ( File.Close(HistoryfileObject,failure) == failure ) : File.Logerror(ErrorfileObject,module,Errormessage,warning)

# Convert csv file to xlsx file
Interface.RunScript(ConversionScript,ConversionWait)

# View converted report file.
Interface.ViewSpeadsheet(Spreadsheet,Convertedhistoryfilename) 

# Log end of script
File.Logerror(ErrorfileObject,module,'Completed',info)

# Close error log file
Errormessage = 'Could not close ' + Errorfilename
if ( File.Close(ErrorfileObject,failure) == failure ) : File.Logerror(ErrorfileObject,module,Errormessage,warning)