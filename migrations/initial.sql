create extension if not exists pg_trgm;
create type IncidentEnum as enum ('link', 'phone');
create type StatusEnum as enum ('accepted', 'pending', 'review', 'resolved', 'declined');

create table if not exists author
(
    id         uuid primary key,
    full_name  varchar(255),
    tg_user_id varchar(40) -- id from TG as user_id --
);

create index if not exists ix_tg_user_id_search on author (tg_user_id);

create table if not exists claims
(
    id         serial primary key,
    created_at timestamptz default now(),
    type       IncidentEnum not null,
    status     StatusEnum   not null,
    -- platform claim, like instagram / lalafo / disel --
    platform   varchar(255) not null,
    -- id from TG as user_id --
    author     uuid         not null references author deferrable initially deferred,
    -- could content text with links to sources of another sites --
    decision   text,

    -- props fields --
    phone      varchar(20)  null,
    link       varchar(255) null
);

create index if not exists ix_type_search on claims (type);
create index if not exists ix_status_search on claims (status);
create index if not exists ix_created_at_ordering on claims (created_at);
create index if not exists ix_phone_link_composed on claims (phone, link);
create index if not exists ix_platform_trgm on claims using gist (platform gist_trgm_ops( siglen= 32));

create table if not exists image
(
    id       uuid primary key,
    claim_id int references claims deferrable initially deferred,
    image    varchar(255) -- path to folder --
);


create table if not exists malware
(
    id       uuid primary key,
    -- type of malware, like cryptographer/worm/joiner
    type     varchar(40),
    claim_id int not null references claims deferrable initially deferred
);

create index if not exists ix_malware_type_search on malware (type);
