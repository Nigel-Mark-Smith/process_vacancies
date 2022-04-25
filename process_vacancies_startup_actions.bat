@echo off
rem This batch file runs all utilities required on a day-to-day 
rem basis when applying for job vacancies.

rem Files and directories
set ReportFile=H:\administration\jobsearch\2019\Co-Ordination\reports\application_history.xlsx
set ScriptDir=%cd%

rem Remove report file
if exist %ReportFile% del /f /q %ReportFile%

rem Move to script directory
cd %ScriptDir%

rem Delay execution allowing Outlook to start
timeout /t 240 /nobreak

rem Run all utilities
parse_mail.py
remove_duplicates_using_priority.py
remove_duplicates_per_engine.py