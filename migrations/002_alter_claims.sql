alter table claims
    add column if not exists username     varchar(40),
    add column if not exists processed_by uuid null,
    add constraint claims_processed_fkey foreign key (processed_by) references author (id);
alter table claims
    add column if not exists lock_id   bigint null,
    add column if not exists is_locked boolean default false;
create index if not exists ix_is_locked_claim on claims (is_locked);

alter type IncidentEnum add value if not exists 'username';
drop index if exists ix_phone_link_composed;
create index if not exists ix_source_composed on claims (phone, link, username);
