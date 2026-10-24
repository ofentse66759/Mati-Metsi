# Mati-Metsi: Community Resilience Platform

Mati-Metsi is a South African community resilience platform designed to help households and neighbourhoods prepare for, coordinate during, and recover from disruptions to essential services: water, energy, transport, and food. 

Built as an offline-first Progressive Web App (PWA), Mati-Metsi bridges the gap between scattered community WhatsApp groups and formal municipal response.

## Core Features

*   **Predictive Risk Engine:** A transparent, rule-based model that combines live Open-Meteo weather forecasts with real-time community reports to predict localized risks (flooding, water shortage, heat stress).
*   **Offline-First Architecture:** Utilizes Service Workers and local storage. Users can submit reports, browse the help board, and view their resilience plan even without an internet connection. Data automatically syncs to the cloud when connectivity is restored.
*   **Neighbour Help Board:** A safe, community-driven marketplace for offering or requesting essential resources (water, transport, food parcels, charging stations).
*   **Two-Sided Verification:** Community members submit reports; verified partners (municipalities/NGOs) can confirm reports and post official public responses.
*   **Accessibility & Inclusion:** Fully translated into all 11 official South African languages, featuring high-contrast modes, larger text options, and text-to-speech support.
*   **POPIA Compliant:** Built with privacy at its core. No third-party trackers, no GPS tracking, and full user data export/deletion capabilities.

## Technology Stack

*   **Frontend:** Vanilla HTML5, CSS3, JavaScript (ES6+), Progressive Web App (PWA)
*   **Backend & Database:** Supabase (PostgreSQL)
*   **Authentication:** Supabase Auth (Anonymous Sign-ins)
*   **Storage:** Supabase Storage (for report photos)
*   **External APIs:** Open-Meteo (Weather & Air Quality)
*   **Hosting:** GitHub Pages

---

## Project Development Timeline

The following steps were executed to build, secure, and deploy the Mati-Metsi platform:

### Phase 1: Core Application Development
1.  Built the single-page application architecture using vanilla HTML, CSS, and JavaScript.
2.  Implemented the localization engine supporting 11 South African languages.
3.  Integrated Open-Meteo APIs for live weather, forecasts, and air quality data.
4.  Developed the "Resilience Plan" and savings calculator (estimating Rand, kWh, and Liters saved).
5.  Built the client-side rule-based risk prediction engine.
6.  Developed the local-first data layer using `localStorage` for reports, alerts, and user profiles.

### Phase 2: Progressive Web App & Offline Capabilities
1.  Created and registered `sw.js` (Service Worker) to handle app-shell caching and offline routing.
2.  Implemented an offline outbox system to queue reports submitted without internet access.
3.  Added a `manifest.json` file to enable installation on mobile devices (Add to Home Screen).
4.  Integrated connectivity detection (`navigator.onLine`) to gracefully handle network failures.

### Phase 3: Cloud Backend & Security (Supabase)
1.  Provisioned a Supabase PostgreSQL database.
2.  Created relational tables: `profiles`, `reports`, `help_listings`, and `alerts`.
3.  Implemented robust **Row Level Security (RLS)** policies to ensure users can only modify their own data, while allowing public read access to community feeds.
4.  Optimized database performance by adding indexes to foreign keys and heavily queried columns (e.g., `author_id`, `status`).
5.  Enabled Supabase Anonymous Authentication to provide a secure, zero-friction `auth.uid()` for every user.
6.  Created a database trigger (`handle_new_user`) to automatically generate a profile when a new anonymous user is created.

### Phase 4: Cloud Storage & Synchronization
1.  Provisioned a Supabase Storage bucket (`photos`) with specific RLS policies for public read and owner-restricted uploads.
2.  Migrated image handling from local Base64 strings to direct uploads to Supabase Storage.
3.  Implemented a bi-directional data sync layer:
    *   **Push:** Local report/listing creation, updates, and deletions are automatically synced to Supabase (fire-and-forget).
    *   **Pull:** On app boot, the application fetches the latest community data from Supabase to enable cross-device visibility.
4.  Updated the offline outbox to automatically sync queued reports to Supabase upon reconnection.

### Phase 5: Performance Optimization
1.  Implemented memoization (caching) for heavy `localStorage` reads (`getReports`, `getListings`) to reduce JSON parsing overhead by 30x per render cycle.
2.  Optimized the duplicate detection algorithm by filtering by category and area before running text similarity checks.
3.  Throttled the application's auto-render interval to prevent unnecessary DOM updates.
4.  Cached the heavy Risk Engine calculations to prevent re-rendering if weather and report data remain unchanged.

### Phase 6: Deployment
1.  Configured the repository for deployment via GitHub Pages.
2.  Ensured all Service Worker and Manifest paths use relative routing (`./`) to support sub-directory hosting.
3.  Conducted final cross-device and offline testing to verify PWA integrity.

---

## Local Development Setup

To run Mati-Metsi locally and test the Service Worker functionality:

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/mati-metsi.git
   cd mati-metsi
