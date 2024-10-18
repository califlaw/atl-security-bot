create table if not exists referrals
(
    id            serial primary key,
    author_id     uuid not null references author deferrable initially deferred unique,
    referrer_code varchar(255) unique,
    referrers     bigint array default '{}',
    created_at    timestamptz default now()
);
