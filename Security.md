# Security Policy

## Supported versions

| Version | Supported |
| ------- | --------- |
| v8.3 (current demo) | ✅ |
| Earlier versions | ❌ |

## Reporting a vulnerability

Mati-Metsi is a hackathon demonstration. If you find a security problem, please email **security@mati-metsi.org**.

- **Do not open a public issue** for security concerns.
- Include what you found, the steps to reproduce it, and the browser/device you used.
- For personal-data or POPIA matters, contact the Data Protection Officer at **privacy@mati-metsi.org**.

---

# Security Assessment

This project followed a Secure System Development Life Cycle (SSDLC). This document covers the risk assessment, STRIDE threat model, secure-coding practices, testing performed, known limitations and the integration plan. It describes the build as it exists today.

## 1. Architecture at a glance

Mati-Metsi is a single-file, offline-first Progressive Web App that runs in the browser.

- **On the device (`localStorage`):** accounts, session, reports, help listings, alert subscriptions, resilience-plan progress, drafts, preferences and the offline outbox.
- **Supabase (PostgreSQL, Auth, Storage):** reports and help listings you submit are also synced to Supabase so neighbours can see them across devices. Access is controlled by Row Level Security. Deleting your account also removes what your device synced.
- **Service Worker (`sw.js`):** caches the app shell for offline use.
- **External services:** WeatherAPI.com (weather and geocoding, with an Open-Meteo fallback) and Open-Meteo (air quality). They receive only the suburb or place name a user types, never GPS coordinates or personal identifiers.
- **Never used:** `navigator.geolocation`, third-party analytics, advertising or session-replay scripts.

**Trust boundaries.** The device is the trust boundary for local data: `localStorage` is not encrypted at rest. For synced data, the trust boundary is Supabase Row Level Security. Client-side password hashing is a demo-grade control, not a production authentication scheme.

## 2. Security goals

- **Confidentiality:** no GPS, no home address, no ID number. Only the minimum data (name, email, suburb, optional phone on a listing) is collected.
- **Integrity:** a report cannot be marked Confirmed or In Progress by a single normal user, and fake reports alone cannot reach the high-severity alert band.
- **Availability:** the app runs offline after first load, and a weather outage falls back to the last saved forecast.
- **POPIA compliance:** data minimisation, no trackers, one-tap export and one-tap deletion.

## 3. Risk assessment

### High risks

| Risk | Mitigation |
| --- | --- |
| **Home-address exposure** via the free-text suburb field | Report form, help board and help-message dialog all test text against a street-address pattern (`ADDRESS_RE`) and reject street addresses with a clear message. |
| **Fake or malicious reports** | Three independent community confirmations are needed to auto-promote a report to Confirmed; users cannot confirm their own report; statuses beyond "resolved" require a verified-partner role. |
| **Personal information (POPIA)** held locally and in the cloud | One-click JSON export of everything held about the user; one-click "Delete account and all data" (device and synced data); Privacy Notice on the About page; DPO contact published. |
| **Password storage** | Passwords are hashed with SHA-256 (Web Crypto) with a fixed salt before storage. This is **demo-grade**. The production plan is server-side hashing through Supabase Auth. |
| **Help-board fraud** | Banking-detail patterns (`BANKING_RE`) and street addresses are blocked in listings and messages; a safety banner reminds users to meet in public, never share banking details or PINs, and never pay upfront. |

### Medium risks

| Risk | Mitigation |
| --- | --- |
| **XSS** via report descriptions and help titles | User-controlled values pass through a single escaping function before reaching the DOM. The app uses no `eval`, `new Function` or `document.write`. |
| **Photo metadata (EXIF GPS)** | Every upload is size-checked (8 MB), type-checked (`image/*`), redrawn on a `<canvas>` at a maximum of 900 px and re-encoded as JPEG at 0.72 quality, which drops EXIF including GPS. |
| **Client-side tampering** (editing `localStorage` in DevTools) | Acknowledged limitation of local state. For synced data, Supabase RLS is the authority. Stated in the Privacy Notice. |
| **Public keys in source** | The weather API key and the Supabase *publishable* key are visible in the source. The Supabase key is designed to be public and is protected by RLS; the weather key is rate-limited per plan, so abuse exhausts quota rather than exposing data. Use a dedicated key on a low plan ceiling. The Supabase `service_role` key must never appear in the front-end. |
| **Offline cache poisoning** | The Service Worker is scoped to static assets and the last weather response. |

### Low risks

| Risk | Notes |
| --- | --- |
| **Denial of service** | A weather API quota outage degrades to a labelled "saved forecast" mode. Supabase-side rate limiting is the control for synced endpoints. |
| **Demo-account abuse** | Demo partner credentials are published on the login screen for judging and will be removed from production. |

## 4. Threat model (STRIDE)

| Threat | Scenario | Control |
| --- | --- | --- |
| **Spoofing** | A normal account pretends to be a ward-disaster committee. | Statuses beyond "resolved" require `role === 'partner'`. Real partner verification is planned; partner content carries a visible "Demo" pill. |
| **Tampering** | A user edits a report after submission or edits storage. | Report history is append-only (`{status, at, by}`), and there is no edit UI. Storage tampering is a stated limitation of the local layer; RLS protects synced rows. |
| **Repudiation** | A partner denies a public response. | Responses store author, organisation, role, note and timestamp; the partner dashboard keeps an append-only audit log. |
| **Information disclosure** | A user posts a street address or banking details. | Both patterns are blocked on every relevant field; EXIF is stripped; no GPS API is called. |
| **Denial of service** | Vote spamming or an API rate limit. | One vote per user per report (toggle, not append); weather falls back to cache with a visible status label. |
| **Elevation of privilege** | A normal user tries to set Confirmed or Resolved. | The status function checks for partner role, or owner-to-Resolved only; partner response functions return early for non-partners. |

## 5. Secure coding practices

- **Input validation:** names and emails are length-capped and email-checked; suburbs are capped at 100 characters and address-checked; report descriptions are 5–1000 characters; phone numbers must be 9–15 digits; severity is a radio button, not free text.
- **Output encoding:** one escaping function for all dynamic values.
- **Sessions:** a client-side session entry (name, email, role, organisation, sign-in time). It can be forged by anyone with DevTools access, which is why server-managed sessions from Supabase Auth are used for synced data. "Remember me" is honoured through a `sessionStorage` flag.
- **Error handling:** every `localStorage` call is wrapped in `try/catch`; a report that fails to save because storage is full is retried without its photo and the user is told.
- **Offline behaviour:** weather responses are cached and shown with a "saved forecast" label; reports written offline go to an outbox and sync on reconnect.

## 6. Cloud backend controls (Supabase)

- Row Level Security enabled on every table: public read of community feeds, write/update/delete only by the row's owner.
- Anonymous Authentication provides a stable `auth.uid()` per user.
- Storage bucket `photos`: public read, uploads restricted to the signed-in user's own folder.
- Only the publishable (anon) key is shipped in the front-end.

## 7. Security testing performed

Testing so far has been **manual**, not an automated pipeline.

**Static checks**
- Opened every `localStorage` key after each feature path and confirmed no plaintext passwords, GPS coordinates or other users' personal details.
- Searched the source for dangerous sinks (`eval`, `new Function`, `document.write`, `navigator.geolocation`) and found none.
- Secrets scan: the weather key and the Supabase publishable key are present by design (see section 3); no `service_role` key is in the source.
- Loaded the app in Chrome, Firefox and Safari with no console errors on a fresh load.

**Dynamic checks**
- Confirming your own report is blocked.
- Changing a report's status as a community user is blocked by the role check.
- A street address in the suburb field is rejected.
- A help listing mentioning bank details is rejected.
- A help message containing a street address is rejected before storage.
- A 10 MB photo is rejected ("Photo is too large (max 8 MB)").
- A PDF disguised as a photo is rejected by the type check.
- Reloading offline keeps the app working with a "saved forecast" label and an offline banner.
- A report submitted offline is queued and sent on reconnect.
- `localStorage.mm_accounts` holds a SHA-256 hash, not a plaintext password.

**Not yet tested**
- Supabase RLS policies under adversarial testing (for example, attempting to read or modify another user's rows with the anon key).
- Server-side rate limiting on report and confirmation endpoints.
- EXIF stripping verified with ExifTool on a GPS-tagged photo.
- A breach-notification drill for POPIA Section 22.

## 8. Known limitations

- Client-side password hashing is not a security boundary. Anyone with DevTools can edit `localStorage` to impersonate a local account.
- Demo partner credentials are public by design and will be removed from production.
- There is no custom server-side rate limiting. Mitigations are the three-confirmation threshold and word-similarity duplicate detection.
- `localStorage` is not encrypted at rest, so a stolen, unlocked device exposes the user's own data. This is disclosed in the Privacy Notice.
- The weather key in the source is mitigated only by provider-side rate limits.

## 9. POPIA position

- Minimum data: name, email, suburb and an optional phone number on a help listing. No ID number, date of birth or street address.
- No GPS collection and no third-party trackers or advertising.
- One-click JSON export and one-click account deletion, including data synced to Supabase.
- DPO contact published in the Privacy Notice and footer.
- Because data is now stored in Supabase, a breach-notification procedure (POPIA Section 22) must be documented and tested.

## 10. Roadmap

| Phase | Security work |
| --- | --- |
| **Current build** | Client-side validation, single escaping function, `ADDRESS_RE` / `BANKING_RE` guards, SHA-256 demo hashing, canvas EXIF stripping, offline fallback, POPIA export/delete, Supabase RLS and Storage policies. |
| **Hardening** | Adversarial RLS testing, server-side input validation, rate limiting on report and confirmation endpoints, server-side append-only audit table, tested Section 22 breach procedure, remove demo credentials. |
| **Notifications** | Push, WhatsApp and SMS channels: webhook signature verification (`X-Hub-Signature-256`), per-number rate limiting, stored opt-in consent with timestamp. |
| **Official data feeds** | Read-only consumption of SAWS and Rand Water data under a data-sharing agreement; every external data point labelled with source and freshness. |
| **Aggregate insights** | Non-personal aggregation only, small-cell suppression at k ≥ 10, POPIA-compliant data-sharing agreements with every partner. |

## 11. Summary

The build's posture suits a demonstration: it collects the minimum data, never uses GPS or trackers, strips photo metadata, role-gates risky actions, works offline and gives users one-tap export and deletion. Its honest limits are stated here and in the app's own Privacy Notice: demo-grade client-side hashing, no custom rate limiting, public demo credentials and a manual-only test record.
