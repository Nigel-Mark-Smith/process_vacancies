/*
queries.sql

This sql script will generate export files containing
data relating to the following:

- The number and timeing of state changes for all applications made.
- The number of new vacancies detected on each execution of 'parase_mail.py'
  on a per engine basis.
- The total number of vacancies detected on a per engine basis.
- The total number of duplicate vacancies detected on a per engine basis.
- The number of vacancies current in each possible state.

This script file is executed from the MySQL prompt using

source X:/GitHub/process_vacancies/Data/queries.sql;
*/
use vacancies;
/*
Generate application history file
*/
select vacancy.company as company,vacancy.title as title,vacancy.location as location,history.vacancy_state as state,history.time_stamp as date_time from history join vacancy \
on ( history.vacancy_id = vacancy.vacancy_id and vacancy.vacancy_state = 'Applied' ) order by vacancy.company,history.time_stamp DESC \
into outfile 'X:\\GitHub\\process_vacancies\\Data\\application_history.csv' \
fields terminated by ',' optionally enclosed by '"' \
lines terminated by '\n';
/*
Generate vacancy geeneration rate per engine data.
*/
select time_stamp as raised_on, found as new_vacancies from counter where engine_id = 1 order by time_stamp DESC \
into outfile 'X:\\GitHub\\process_vacancies\\Data\\new_vacancies_1.csv' \
fields terminated by ',' optionally enclosed by '"' \
lines terminated by '\n';
select time_stamp as raised_on, found as new_vacancies from counter where engine_id = 2 order by time_stamp DESC \
into outfile 'X:\\GitHub\\process_vacancies\\Data\\new_vacancies_2.csv' \
fields terminated by ',' optionally enclosed by '"' \
lines terminated by '\n';
select time_stamp as raised_on, found as new_vacancies from counter where engine_id = 3 order by time_stamp DESC \
into outfile 'X:\\GitHub\\process_vacancies\\Data\\new_vacancies_3.csv' \
fields terminated by ',' optionally enclosed by '"' \
lines terminated by '\n';
select time_stamp as raised_on, found as new_vacancies from counter where engine_id = 4 order by time_stamp DESC \
into outfile 'X:\\GitHub\\process_vacancies\\Data\\new_vacancies_4.csv' \
fields terminated by ',' optionally enclosed by '"' \
lines terminated by '\n';
select time_stamp as raised_on, found as new_vacancies from counter where engine_id = 5 order by time_stamp DESC \
into outfile 'X:\\GitHub\\process_vacancies\\Data\\new_vacancies_5.csv' \
fields terminated by ',' optionally enclosed by '"' \
lines terminated by '\n';
select time_stamp as raised_on, found as new_vacancies from counter where engine_id = 6 order by time_stamp DESC \
into outfile 'X:\\GitHub\\process_vacancies\\Data\\new_vacancies_6.csv' \
fields terminated by ',' optionally enclosed by '"' \
lines terminated by '\n';
/*
Generate total vacancy count per engine data
*/ 
select engine.name as engine ,count(*) as total_vacancies from vacancy join engine on (vacancy.engine_id = engine.id) group by engine_id order by engine.name \
into outfile 'X:\\GitHub\\process_vacancies\\Data\\total_vacancies.csv' \
fields terminated by ',' optionally enclosed by '"' \
lines terminated by '\n';
/*
Generate total duplicate vacancy count per engine data
*/
select engine.name as engine ,sum(found) total_duplicates from duplicate join engine on (duplicate.engine_id = engine.id )group by engine_id order by engine.name \
into outfile 'X:\\GitHub\\process_vacancies\\Data\\total_duplicates.csv' \
fields terminated by ',' optionally enclosed by '"' \
lines terminated by '\n';
/*
Generate total of vacancies per state data
*/
select vacancy_state as state ,count(*) as total_in_state from vacancy group by vacancy_state \
into outfile 'X:\\GitHub\\process_vacancies\\Data\\total_in_state.csv' \
fields terminated by ',' optionally enclosed by '"' \
lines terminated by '\n';

