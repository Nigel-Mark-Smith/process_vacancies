drop database if exists vacancies;
create database vacancies;
use vacancies;
create table engine (
id int not null, 
name varchar(40),
mailbox varchar(100),
joburlre varchar(200),
url_len int,
id_len int,
priority int,
exclusions varchar(200),
inclusions varchar(200),
primary key (id)
);
create table company (
id varchar(8),
name varchar(160),
status varchar(70),
SICCode varchar(170),
url varchar(100),
primary key (id)
);
create table vacancy (
engine_id int,
vacancy_id varchar(160),
vacancy_url varchar(160),
vacancy_state enum ('New','Enhanced','Applied','Dropped','First','Second','Third','Offer','Rejected'),
company varchar(160),
title varchar(200),
location varchar(160),
salary_min int,
salary_max int,
primary key (vacancy_id)
);
create table history(
id int not null auto_increment, 
time_stamp timestamp default current_timestamp on update current_timestamp,
engine_id int,
vacancy_id varchar(160),
vacancy_state enum ('New','Enhanced','Applied','Dropped','First','Second','Third','Offer','Rejected'),
history_comment varchar(160),
primary key (id)
);
create table counter(
id int not null auto_increment, 
time_stamp timestamp default current_timestamp on update current_timestamp,
engine_id int,
found int,
primary key (id)
);
create table duplicate(
id int not null auto_increment, 
time_stamp timestamp default current_timestamp on update current_timestamp,
engine_id int,
found int,
primary key (id)
);