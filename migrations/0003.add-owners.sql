-- alter providers

alter table providers drop column id_field_name;

alter table providers
	add field_names jsonb;

UPDATE public.providers SET field_names = '{"id": "id", "owner": "owner", "owner_id": "id", "owner_name": "login"}' WHERE id = 3;
UPDATE public.providers SET field_names = '{"id": "id", "owner": "namespace", "owner_id": "id", "owner_name": "path"}' WHERE id = 4;
UPDATE public.providers SET field_names = '{"id": "uuid", "owner": "workspace", "owner_id": "uuid", "owner_name": "slug"}' WHERE id = 5;

-- create owners

create table owners
(
	id serial not null,
	provider_id int not null
		constraint owners_providers_id_fk
			references providers
				on delete restrict,
	internal_id varchar not null,
	name varchar not null
);

create unique index owners_id_uindex
	on owners (id);

create unique index owners_provider_id_internal_id_uindex
	on owners (provider_id, internal_id);

create index owners_internal_id_index
	on owners (internal_id);

create index owners_provider_id_index
	on owners (provider_id);

alter table owners
	add constraint owners_pk
		primary key (id);

-- alter repos

alter table repos
	add owner_id int;

alter table repos
	add constraint repos_owners_id_fk
		foreign key (owner_id) references owners
			on delete restrict;
