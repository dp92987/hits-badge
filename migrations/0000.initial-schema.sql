create table sites
(
    id serial not null,
    key varchar not null,
    url varchar not null,
    initial_hits int default 0 not null
);

create unique index sites_id_uindex
    on sites (id);

create unique index sites_key_uindex
    on sites (key);

alter table sites
    add constraint sites_pk
        primary key (id);


create table hits
(
    id serial not null,
    timestamp timestamptz default now() not null,
    site_id int not null
        constraint hits_sites_id_fk
            references sites (id)
                on delete cascade,
    remote_addr varchar not null
);

create unique index hits_id_uindex
    on hits (id);

create index hits_site_id_index
    on hits (site_id);

alter table hits
    add constraint hits_pk
        primary key (id);
