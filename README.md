# Mati-Metsi: Community Resilience Platform

[![Live demo](https://img.shields.io/badge/live%20demo-GitHub%20Pages-0e7490)](https://ofentse66759.github.io/Mati-Metsi/)
![PWA](https://img.shields.io/badge/PWA-offline--first-22c55e)
![Backend](https://img.shields.io/badge/backend-Supabase-3ecf8e)

**Live demo:** https://ofentse66759.github.io/Mati-Metsi/

Mati-Metsi is a South African community resilience platform that helps households and neighbourhoods prepare for, coordinate during, and recover from disruptions to essential services: water, energy, transport, and food.

Built as an offline-first Progressive Web App (PWA), it bridges the gap between scattered community WhatsApp groups and formal municipal response.

<!-- Add screenshots here, e.g.
![Dashboard](docs/screenshots/dashboard.png)
![Prediction card](docs/screenshots/prediction.png)
![Offline mode](docs/screenshots/offline.png)
-->

## Core Features

- **Predictive Risk Engine:** A transparent, rule-based model that combines live Open-Meteo weather forecasts with recent community reports to predict localised risks (flooding, water shortage, heat stress).
- **Offline-First Architecture:** Service Worker plus local storage. Users can submit reports, browse the help board, and view their resilience plan without a connection. Data syncs to the cloud when connectivity returns.
- **Neighbour Help Board:** A community-driven board for offering or requesting essentials (water, transport, food parcels, charging stations).
- **Two-Sided Verification:** Community members submit reports; verified partners (municipalities, NGOs) can confirm reports and post official responses.
- **Accessibility & Inclusion:** Available in all 11 official South African languages (see [Languages](#languages)), with high-contrast mode, larger text and text-to-speech.
- **POPIA-minded privacy:** No third-party trackers, no GPS tracking, and user data export/deletion. See [Privacy](#privacy--popia).

## Technology Stack

| Layer | Technology |
| --- | --- |
| Frontend | Vanilla HTML5, CSS3, JavaScript (ES6+), PWA |
| Backend & database | Supabase (PostgreSQL) |
| Authentication | Supabase Auth (anonymous sign-ins) |
| File storage | Supabase Storage (report photos) |
| External APIs | Open-Meteo (weather and air quality) |
| Hosting | GitHub Pages |

## Project Structure

```
Mati-Metsi/
├── index.html        # App shell, UI, logic and translations
├── sw.js             # Service Worker (app-shell caching, offline routing)
├── manifest.json     # PWA manifest (Add to Home Screen)
├── icons/            # App icons
└── supabase/
    └── schema.sql    # Tables, RLS policies, trigger, storage policies
```

Adjust this tree to match your repository.

---

## Local Development Setup

### Requirements

- Any modern browser (Chrome, Edge, Firefox, Safari)
- Python 3 **or** Node.js, to serve the files locally

Service Workers only work on `http://localhost` or over HTTPS, so opening `index.html` by double-clicking (`file://`) will **not** register the Service Worker. Use a local server.

### Run it

1. Clone the repository:

   ```bash
   git clone https://github.com/ofentse66759/Mati-Metsi.git
   cd Mati-Metsi
   ```

2. Start a local server (pick one):

   ```bash
   # Python
   python3 -m http.server 8000

   # or Node.js
   npx serve .
   ```

3. Open <http://localhost:8000> in your browser.

### Test offline mode

1. Open DevTools → **Application** → **Service Workers** and confirm `sw.js` is registered.
2. Tick **Offline** (Network tab or Service Workers panel) and reload. The app shell should still load.
3. Submit a report while offline. It is queued in the outbox and synced when you go back online.

If you change `sw.js` or cached files and still see old content, use **Application → Storage → Clear site data**, or tick **Update on reload**.

### Install as an app

- **Android (Chrome):** menu → *Install app* / *Add to Home screen*.
- **iOS (Safari):** Share → *Add to Home Screen*.
- **Desktop (Chrome/Edge):** install icon in the address bar.

---

## Supabase Setup

The app works without a backend (everything stays in `localStorage`). To enable cross-device sync and shared community feeds, connect your own Supabase project.

### 1. Create the project

1. Create a free project at <https://supabase.com>.
2. In **Project Settings → API**, copy the **Project URL** and the **anon public key**.

### 2. Add your keys to the app

Set the values where the app configures Supabase (search for `SUPABASE_URL` in the source):

```js
const SUPABASE_URL = 'https://YOUR-PROJECT-ref.supabase.co';
const SUPABASE_ANON_KEY = 'YOUR-ANON-PUBLIC-KEY';
```

> **About keys:** the `anon` key is designed to be public in front-end code. Your data is protected by **Row Level Security (RLS)**, not by hiding this key. **Never** put the `service_role` key in this repository or in any front-end file.

### 3. Enable anonymous sign-ins

**Authentication → Providers → Anonymous Sign-Ins → Enable.** Every user then gets a stable `auth.uid()` with no sign-up friction.

### 4. Create the schema

Run the SQL below in the **SQL Editor** (save it as `supabase/schema.sql`).

> This is a **template**. Rename or add columns so they match what your app actually reads and writes.

```sql
-- ============ Tables ============
create table if not exists public.profiles (
  id          uuid primary key references auth.users(id) on delete cascade,
  display_name text,
  home_area   text,
  role        text not null default 'resident',   -- 'resident' | 'partner'
  created_at  timestamptz not null default now()
);

create table if not exists public.reports (
  id          uuid primary key default gen_random_uuid(),
  author_id   uuid not null default auth.uid() references public.profiles(id) on delete cascade,
  category    text not null check (category in ('water','energy','transport','food')),
  type        text,
  area        text not null,
  severity    text not null default 'medium'
              check (severity in ('low','medium','high','critical')),
  details     text,
  photo_path  text,
  status      text not null default 'open',
  created_at  timestamptz not null default now()
);

create table if not exists public.help_listings (
  id          uuid primary key default gen_random_uuid(),
  author_id   uuid not null default auth.uid() references public.profiles(id) on delete cascade,
  kind        text not null check (kind in ('offer','request')),
  category    text not null,
  area        text not null,
  details     text,
  status      text not null default 'active',
  created_at  timestamptz not null default now()
);

create table if not exists public.alerts (
  id          uuid primary key default gen_random_uuid(),
  area        text,
  category    text,
  level       text,
  message     text,
  created_at  timestamptz not null default now()
);

-- ============ Indexes ============
create index if not exists reports_author_idx  on public.reports (author_id);
create index if not exists reports_status_idx  on public.reports (status);
create index if not exists reports_area_idx    on public.reports (area);
create index if not exists listings_author_idx on public.help_listings (author_id);
create index if not exists listings_status_idx on public.help_listings (status);

-- ============ Auto-create a profile for each new (anonymous) user ============
create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
  insert into public.profiles (id) values (new.id) on conflict do nothing;
  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();

-- ============ Row Level Security ============
alter table public.profiles      enable row level security;
alter table public.reports       enable row level security;
alter table public.help_listings enable row level security;
alter table public.alerts        enable row level security;

-- Profiles: users manage only their own row
create policy "profiles_select_own" on public.profiles
  for select to authenticated using ((select auth.uid()) = id);
create policy "profiles_update_own" on public.profiles
  for update to authenticated using ((select auth.uid()) = id);

-- Reports: public read, owner-only write
create policy "reports_read_all" on public.reports
  for select using (true);
create policy "reports_insert_own" on public.reports
  for insert to authenticated with check ((select auth.uid()) = author_id);
create policy "reports_update_own" on public.reports
  for update to authenticated using ((select auth.uid()) = author_id);
create policy "reports_delete_own" on public.reports
  for delete to authenticated using ((select auth.uid()) = author_id);

-- Help listings: same pattern
create policy "listings_read_all" on public.help_listings
  for select using (true);
create policy "listings_insert_own" on public.help_listings
  for insert to authenticated with check ((select auth.uid()) = author_id);
create policy "listings_update_own" on public.help_listings
  for update to authenticated using ((select auth.uid()) = author_id);
create policy "listings_delete_own" on public.help_listings
  for delete to authenticated using ((select auth.uid()) = author_id);

-- Alerts: public read; writes only via the service role / dashboard
create policy "alerts_read_all" on public.alerts
  for select using (true);
```

### 5. Create the photo bucket

1. **Storage → New bucket** → name it `photos`, mark it **public** (public read).
2. Add policies so only signed-in users can upload, and only into their own folder:

```sql
create policy "photos_public_read" on storage.objects
  for select using (bucket_id = 'photos');

create policy "photos_owner_upload" on storage.objects
  for insert to authenticated
  with check (
    bucket_id = 'photos'
    and (storage.foldername(name))[1] = (select auth.uid())::text
  );

create policy "photos_owner_delete" on storage.objects
  for delete to authenticated
  using (
    bucket_id = 'photos'
    and (storage.foldername(name))[1] = (select auth.uid())::text
  );
```

Uploads should use the path `<user-id>/<filename>` so the folder rule matches.

### 6. Verify

- Open the app, submit a report, and confirm a row appears in **Table Editor → reports**.
- Open the app in a private window (a new anonymous user) and confirm the report is visible but cannot be edited.

---

## How the Risk Engine Works

The prediction is a transparent, additive score, not a black box. Each factor adds points and the app shows every factor under **"Why this prediction?"**

| Input | Source | Example effect |
| --- | --- | --- |
| Forecast rainfall | Open-Meteo | Raises flooding / transport risk |
| Max temperature | Open-Meteo | Raises heat-stress risk |
| Recent community reports | Supabase / local | Clusters of similar reports raise the risk for that service and area |
| Report severity and recency | Community | Newer, more severe reports weigh more |

Fill in your actual thresholds and point values here so contributors can audit them.

## Languages

Mati-Metsi supports the 11 official South African languages: English, isiZulu, isiXhosa, Afrikaans, Sepedi, Setswana, Sesotho, Xitsonga, siSwati, Tshivenda and isiNdebele.

> Translation coverage varies. Any string missing in a language falls back to English. Help finishing the remaining translations is very welcome. See [Contributing](#contributing).

## Privacy & POPIA

- **No GPS.** Only the town or suburb the user types is used.
- **No third-party trackers or analytics.**
- **Minimal public data.** Reports and listings show a name and suburb only, never a home address.
- **On-device by default.** Preferences, plan and alerts live in the browser's `localStorage`.
- **Your data, your control.** Users can export and delete their data, including what this device synced to Supabase.
- **Not an official channel.** Community reports are not municipal confirmations.

## Known Limitations

- Sample ("demo") reports, alerts and listings are shown so the app can be explored. They are not real events.
- Community reports are unverified unless confirmed by a verified partner.
- The risk model is rule-based and indicative, not an official forecast.
- Not an emergency service. In an emergency call **10111** (Police), **10177** (Ambulance) or **112** from any mobile.

## Roadmap

- [ ] Complete translations for all 11 languages
- [ ] Push notifications for local alerts
- [ ] Partner (municipality / NGO) onboarding and verification flow
- [ ] Moderation tools and abuse reporting
- [ ] Automated tests for the risk engine

## Project Development Timeline

<details>
<summary>Phases 1–6 (click to expand)</summary>

### Phase 1: Core Application Development
1. Built the single-page application using vanilla HTML, CSS and JavaScript.
2. Implemented the localization engine for 11 South African languages.
3. Integrated Open-Meteo for live weather, forecasts and air quality.
4. Developed the "Resilience Plan" and savings calculator (Rand, kWh and litres saved).
5. Built the client-side rule-based risk prediction engine.
6. Developed the local-first data layer using `localStorage` for reports, alerts and profiles.

### Phase 2: Progressive Web App & Offline Capabilities
1. Created and registered `sw.js` for app-shell caching and offline routing.
2. Implemented an offline outbox that queues reports submitted without internet.
3. Added `manifest.json` for installation on mobile devices.
4. Integrated connectivity detection (`navigator.onLine`).

### Phase 3: Cloud Backend & Security (Supabase)
1. Provisioned a Supabase PostgreSQL database.
2. Created tables: `profiles`, `reports`, `help_listings`, `alerts`.
3. Implemented Row Level Security so users can modify only their own data, with public read access to community feeds.
4. Added indexes on foreign keys and heavily queried columns (e.g. `author_id`, `status`).
5. Enabled Supabase Anonymous Authentication for a zero-friction `auth.uid()`.
6. Created the `handle_new_user` trigger to generate a profile for each new user.

### Phase 4: Cloud Storage & Synchronization
1. Provisioned the `photos` bucket with public read and owner-restricted uploads.
2. Migrated image handling from local Base64 to direct Storage uploads.
3. Implemented bi-directional sync:
   - **Push:** local creates, updates and deletes sync to Supabase (fire-and-forget).
   - **Pull:** on boot, the latest community data is fetched for cross-device visibility.
4. Updated the offline outbox to sync queued reports on reconnection.

### Phase 5: Performance Optimization
1. Memoized heavy `localStorage` reads (`getReports`, `getListings`).
2. Narrowed duplicate detection by category and area before text-similarity checks.
3. Throttled the auto-render interval.
4. Cached Risk Engine results when weather and report data are unchanged.

### Phase 6: Deployment
1. Configured the repository for GitHub Pages.
2. Used relative paths (`./`) for the Service Worker and manifest to support sub-directory hosting.
3. Ran cross-device and offline testing to verify PWA integrity.

</details>

## Contributing

Contributions are welcome, especially:

- **Translations:** find the dictionary for your language in the source, copy any missing keys from `en`, and translate the values. Keep placeholders like `{n}` and `{area}` and any HTML tags unchanged.
- **Bug reports and accessibility fixes:** open an issue with your device, browser and steps to reproduce.

Please do not commit secrets. Only the Supabase **anon** key belongs in the front-end.

## Acknowledgements

- Weather and air-quality data by [Open-Meteo](https://open-meteo.com/).
- Backend by [Supabase](https://supabase.com/).

## Licence

Add a licence (for example MIT) in a `LICENSE` file and name it here.

## Contact

Add a project contact email or issue-tracker link here.
