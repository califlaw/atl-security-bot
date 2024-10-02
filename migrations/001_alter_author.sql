-- add experience for each author
alter table author add column if not exists exp int not null default 0;
alter table author add column if not exists tg_username varchar(80) not null default '';
alter table author add column if not exists email varchar(80) null;
alter table author alter column tg_user_id type int using tg_user_id::int;
alter table author alter id set default gen_random_uuid();

alter table malware alter id set default gen_random_uuid();
