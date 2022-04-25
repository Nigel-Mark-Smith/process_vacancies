use vacancies;
select vacancy.company as company,vacancy.title as title,vacancy.location as location,history.vacancy_state as state,history.time_stamp as date_time from history join vacancy 
on ( history.vacancy_id = vacancy.vacancy_id and not field(vacancy.vacancy_state,'New','Enhanced','Dropped') ) order by title,company,date_time
into outfile 'H:\\administration\\jobsearch\\2019\\Co-Ordination\\reports\\application_history_search.csv' 
fields terminated by ',' optionally enclosed by '"' 
lines terminated by '\n';
select year(time_stamp) as year, week(time_stamp) as week_number, sum(found) as total from counter group by year, week_number
into outfile 'H:\\administration\\jobsearch\\2019\\Co-Ordination\\reports\\new_vacancies.csv'
fields terminated by ',' optionally enclosed by '"' 
lines terminated by '\n';
select year(time_stamp) as year, week(time_stamp) as week_number, sum(found) as total from counter where engine_id = 1 group by year, week_number
into outfile 'H:\\administration\\jobsearch\\2019\\Co-Ordination\\reports\\new_vacancies_1.csv' 
fields terminated by ',' optionally enclosed by '"' 
lines terminated by '\n';
select year(time_stamp) as year, week(time_stamp) as week_number, sum(found) as total from counter where engine_id = 2 group by year, week_number
into outfile 'H:\\administration\\jobsearch\\2019\\Co-Ordination\\reports\\new_vacancies_2.csv' 
fields terminated by ',' optionally enclosed by '"' 
lines terminated by '\n';
select year(time_stamp) as year, week(time_stamp) as week_number, sum(found) as total from counter where engine_id = 3 group by year, week_number
into outfile 'H:\\administration\\jobsearch\\2019\\Co-Ordination\\reports\\new_vacancies_3.csv' 
fields terminated by ',' optionally enclosed by '"' 
lines terminated by '\n';
select year(time_stamp) as year, week(time_stamp) as week_number, sum(found) as total from counter where engine_id = 4 group by year, week_number
into outfile 'H:\\administration\\jobsearch\\2019\\Co-Ordination\\reports\\new_vacancies_4.csv' 
fields terminated by ',' optionally enclosed by '"' 
lines terminated by '\n';
select year(time_stamp) as year, week(time_stamp) as week_number, sum(found) as total from counter where engine_id = 5 group by year, week_number
into outfile 'H:\\administration\\jobsearch\\2019\\Co-Ordination\\reports\\new_vacancies_5.csv' 
fields terminated by ',' optionally enclosed by '"' 
lines terminated by '\n';
select year(time_stamp) as year, week(time_stamp) as week_number, sum(found) as total from counter where engine_id = 6 group by year, week_number
into outfile 'H:\\administration\\jobsearch\\2019\\Co-Ordination\\reports\\new_vacancies_6.csv' 
fields terminated by ',' optionally enclosed by '"' 
lines terminated by '\n';
select engine.name as engine ,count(*) as total_vacancies from vacancy join engine on (vacancy.engine_id = engine.id) group by engine_id order by engine 
into outfile 'H:\\administration\\jobsearch\\2019\\Co-Ordination\\reports\\total_vacancies.csv' 
fields terminated by ',' optionally enclosed by '"' 
lines terminated by '\n';
select engine.name as engine ,sum(found) total_duplicates from duplicate join engine on (duplicate.engine_id = engine.id )group by engine_id order by engine
into outfile 'H:\\administration\\jobsearch\\2019\\Co-Ordination\\reports\\total_duplicates.csv' 
fields terminated by ',' optionally enclosed by '"' 
lines terminated by '\n';
select vacancy_state as state ,count(*) as total_in_state from vacancy group by state 
into outfile 'H:\\administration\\jobsearch\\2019\\Co-Ordination\\reports\\total_in_state.csv' 
fields terminated by ',' optionally enclosed by '"' 
lines terminated by '\n';