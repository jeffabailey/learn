do
$do$
begin
create extension if not exists pg_stat_statements;
if not exists (
  select 1
  from information_schema.schemata
  where catalog_name = 'learnsignalfx'
) then
  create user learnsignalfx with encrypted password 'learnsignalfx';
  alter database learnsignalfx owner to learnsignalfx;
  alter user learnsignalfx with superuser;
end if;
end;
$do$
