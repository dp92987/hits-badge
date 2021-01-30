alter table repos drop column key;

alter table repos drop column url;

alter table repos alter column provider_id set not null;

alter table repos alter column internal_id set not null;

alter table repos alter column name set not null;

create unique index repos_provider_id_internal_id_uindex
	on repos (provider_id, internal_id);
