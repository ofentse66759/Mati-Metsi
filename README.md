# Mati-Metsi: Community Resilience Platform

[![Live demo](https://img.shields.io/badge/live%20demo-GitHub%20Pages-0e7490)](https://ofentse66759.github.io/Mati-Metsi/)
![PWA](https://img.shields.io/badge/PWA-offline--first-22c55e)
![Backend](https://img.shields.io/badge/backend-Supabase-3ecf8e)

**Live demo:** https://ofentse66759.github.io/Mati-Metsi/

Mati-Metsi is a South African community resilience platform that helps households and neighbourhoods prepare for, coordinate during, and recover from disruptions to essential services: water, energy, transport, and food.

Built as an offline-first Progressive Web App (PWA), it bridges the gap between scattered community WhatsApp groups and formal municipal response.

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
├──  # Images used in this README
├── icons/            # icon-192.png, icon-512.png
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

Open **SQL Editor**, paste the contents of [`supabase/schema.sql`](supabase/schema.sql) and click **Run**. It creates the `reports` and `help_listings` tables, their indexes and the Row Level Security policies. It is safe to re-run.

The app generates its own text IDs (for example `r-lq3k2-ab12c`), so the `id` columns are `text`, not `uuid`.

### 5. Photo storage (optional)

The current build does not upload photos to Storage yet. When you add it, create a public `photos` bucket and use the commented storage policies at the bottom of `schema.sql`.

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
- **Minimal public data.** Reports and listings show a name, surname and suburb only, never a home address. Email and cell number (used to sign in) are never shown to other residents.
- **Optional map pin.** A pin on a report is rounded to about 110 m before it is saved. The live street map loads only when the user taps "Load live map" and the map provider can then see their IP address.
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

MIT. See the `LICENSE` file.

## Contact

ofentserasekhula8@gmail.com
