
create table if not exists public.reports (
  id           text primary key,
  author_id    uuid not null references auth.users (id) on delete cascade,
  author_name  text,
  category     text not null check (category in ('water','energy','transport','food')),
  type         text,
  area         text not null,
  severity     text not null default 'medium'
               check (severity in ('low','medium','high','critical')),
  description  text,
  status       text not null default 'open',
  source       text not null default 'community',
  org          text,
  votes        jsonb not null default '[]'::jsonb,      
  history      jsonb not null default '[]'::jsonb,
  responses    jsonb not null default '[]'::jsonb,
  demo         boolean not null default false,
  lat          double precision,
  lng          double precision,
  photo_path   text,
  created_at   timestamptz not null default now()
);

create table if not exists public.help_listings (
  id             text primary key,
  author_id      uuid not null references auth.users (id) on delete cascade,
  author_name    text,
  kind           text not null check (kind in ('offer','request')),
  category       text not null,
  title          text not null,
  description    text,
  area           text not null,
  quantity       text,
  until_at       text,
  contact        text,
  contact_value  text,                                   
  status         text not null default 'active',
  claimed_by     uuid references auth.users (id) on delete set null,
  messages       jsonb not null default '[]'::jsonb,
  demo           boolean not null default false,
  created_at     timestamptz not null default now()
);

-- ---------- Indexes (foreign keys and common filters) ----------

create index if not exists reports_author_idx       on public.reports (author_id);
create index if not exists reports_status_idx       on public.reports (status);
create index if not exists reports_area_idx         on public.reports (area);
create index if not exists reports_created_idx      on public.reports (created_at desc);
create index if not exists listings_author_idx      on public.help_listings (author_id);
create index if not exists listings_claimed_by_idx  on public.help_listings (claimed_by);
create index if not exists listings_status_idx      on public.help_listings (status);

-- ---------- Row Level Security ----------

alter table public.reports       enable row level security;
alter table public.help_listings enable row level security;

-- Reports: public read, owner-only write
drop policy if exists "reports_read_all"   on public.reports;
drop policy if exists "reports_insert_own" on public.reports;
drop policy if exists "reports_update_own" on public.reports;
drop policy if exists "reports_delete_own" on public.reports;

create policy "reports_read_all" on public.reports
  for select using (true);
create policy "reports_insert_own" on public.reports
  for insert to authenticated
  with check ((select auth.uid()) = author_id);
create policy "reports_update_own" on public.reports
  for update to authenticated
  using ((select auth.uid()) = author_id)
  with check ((select auth.uid()) = author_id);
create policy "reports_delete_own" on public.reports
  for delete to authenticated
  using ((select auth.uid()) = author_id);

-- Help listings: public read, owner-only write
drop policy if exists "listings_read_all"   on public.help_listings;
drop policy if exists "listings_insert_own" on public.help_listings;
drop policy if exists "listings_update_own" on public.help_listings;
drop policy if exists "listings_delete_own" on public.help_listings;

create policy "listings_read_all" on public.help_listings
  for select using (true);
create policy "listings_insert_own" on public.help_listings
  for insert to authenticated
  with check ((select auth.uid()) = author_id);
create policy "listings_update_own" on public.help_listings
  for update to authenticated
  using ((select auth.uid()) = author_id)
  with check ((select auth.uid()) = author_id);
create policy "listings_delete_own" on public.help_listings
  for delete to authenticated
  using ((select auth.uid()) = author_id);
