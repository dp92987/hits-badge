create table providers
(
	id serial not null,
	name varchar not null,
	url varchar not null,
	id_field_name varchar not null
);

create unique index providers_id_uindex
	on providers (id);

create unique index providers_name_uindex
	on providers (name);

alter table providers
	add constraint providers_pk
		primary key (id);

alter table hits rename column site_id to repo_id;

alter index hits_site_id_index rename to hits_repo_id_index;

alter index sites_id_uindex rename to repos_id_uindex;

alter index sites_key_uindex rename to repos_key_uindex;

alter index sites_pk rename to repos_pk;

alter table sites rename to repos;

alter table repos
	add provider_id int;

alter table repos
	add internal_id varchar;

alter table repos
	add name varchar;

create index repos_internal_id_index
	on repos (internal_id);

create index repos_provider_id_index
	on repos (provider_id);
