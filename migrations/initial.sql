create extension if not exists pg_trgm;
create type IncidentEnum as enum ('link', 'phone');
create type StatusEnum as enum ('accepted', 'pending', 'review', 'resolved', 'declined');

create table author
(
    id         uuid primary key,
    full_name  varchar(255),
    tg_user_id varchar(40) -- id from TG as user_id --
);

create table claims
(
    id         serial primary key,
    created_at timestamptz    default now(),
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

create index ix_type_search on claims (type);
create index ix_status_search on claims (status);
create index ix_created_at_ordering on claims (created_at);
create index ix_phone_link_composed on claims (phone, link);

create table image
(
    id          uuid primary key,
    claim_id int references claims deferrable initially deferred,
    image       varchar(255) -- path to folder --
);
