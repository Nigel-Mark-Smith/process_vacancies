# process_vacancies

This repository delivers python utility scripts 'initialize_database.py', 'parse_mail.py', remove_duplicates_per_engine.py, 
remove_duplicates_using_priority.py, 'update_vacancies.py','load_companies.py' and 'generate_report.py'. These scripts support 
the processing of job alert e-mails which can be received from a number of popular CV/Job engines. The scripts both implement 
and rely on a database called 'vacancies' defined on a local instance of 'MySQL'. They also require that the job alert e-mails 
received are stored in separate mail folders in a local instance of 'Outlook'. 'Chrome' must also be installed so that details 
of any vacancy can be displayed using a unique vacancy url.

These scripts together streamline the processes of reviewing job alert e-mails received and allow the user to track the progress of 
a particular application by changing the state of the associated 'vacancy' stored in the 'vacancies' database. The scripts will
reduce effort by ensuring that details of any vacancy advertised are only processed by the user once. The implementation of the 
'vacancies' database also allows the following reports and metrics to be produced by script generate_reports.py.

- Vacancy history ( for vacancies applied for ).
- Report on proportion of vacancies dropped or pursued.
- Weekly rate at which new vacancies are raised.
- Weekly rate at which new vacancies are raised by each engine.
- Cumulative vacancy counts per engine.
- Cumulative duplicate vacancy counts per engine.

The entirety of the functionality provided by these scripts relies on the following assumptions being correct:

- The job alert e-mails contain unique urls relating to each job vacancy advertised on that engine.
- That accessing these urls will result in the display of all the advertised vacancies details ( without
  being logged in ).
- If the job alert e-mails do not contain unique job urls, that these can be obtained by scraping the delivered web content
  when clicking on a link in those e-mails ( Reed ).
- The unique vacancy urls themselves contain a unique alpha/numeric identifier within the unique url.
- The CV/Job engines continue to deliver alert e-mails in the same format.

Deliverables
------------
To implement the functionality discussed above the following scripts and configuration files are delivered:

File | File Contents
------------- | -------------
initialize_database.py | Configures and checks the MySQL 'vacancies' database and associated tables.
parse_mail.py | Parses Outlook mail and adds details of new vacancies to MySQL
remove_duplicates_per_engine.py | Detects any duplicate vacancies in state 'New' ( per engine ) and removes all but the latest. 
remove_duplicates_using_priority.py | Detects any duplicate vacancies in state 'New' or 'Enhanced'and removes all but one based on age and engine priority.
update_vacancies.py | Interacts with the user allowing them to change details ( including the state ) of individual vacancies. 
load_companies.py | Provides bulk loading of comapny data from companies.csv file.
generate_reports.py | Generates reports containing the history of all vacancies applied for or other vacancy metrics
companies.data | An extract of Companies House data containing known recruitment agencies.
connect.data | Information required to connect to local MySQL instance
definition.sql | All SQL statements required to define the 'vacancies' database and associated tables.
engines.data | CV engine specific data including location of Outlook mail folders and format of unique vacancy urls.
queries.sql | Generates export files containing metrics data.
test_mail.py | Test utility which allows users to determine the per engine data that requires to be specified in file ..\Data\engines.csv
test_scraping.py | Test utility which tests scraping functionality  provided in the 'Web' module
process_vacancies.bat | Runs all utilities required on a day-to-day basis when applying for job vacancies. 
convert_workbook.vbs | Converts a csv file containing application history into an Excel spreadsheet.  

As well as the above scripts and data files the following supporting documentation is also provided:

Document File | File Contents
------------- | -------------
process_vacancies_installation.txt | Installation instructions
process_vacancies_usage.txt | Script usage information
process_vacancies_testing.txt | Script testing information
ReformatData.txt | Source of Excel macro required by convert_workbook.vbs
SaveAsXlsx.txt | Source of Excel macro required by convert_workbook.vbs


Future Developments
-------------------
The following additional functionality is planned:

- Detection/removal of vacancies raised by agencies.
- Automatic backup of the contents of the 'vacancies' database.


