@echo off
rem This batch file runs all utilities required on a day-to-day 
rem basis when applying for job vacancies.

rem Files and directories
set ScriptDir=%cd%

rem Move to script directory
cd %ScriptDir%

rem Run all utilities
parse_mail.py
remove_duplicates_using_priority.py
remove_duplicates_per_engine.py
update_vacancies.py
generate_reports.py