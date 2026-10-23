# Mati-Metsi — Township Resilience OS

[![Live Demo](https://img.shields.io/badge/Live_Demo-GitHub_Pages-22a6bf?style=for-the-badge&logo=github)](https://ofentse66759.github.io/Mati-Metsi/)
[![Built with](https://img.shields.io/badge/Built_with-Vanilla_JS-f7df1e?style=for-the-badge&logo=javascript)](https://github.com/ofentse66759/Mati-Metsi)
[![Languages](https://img.shields.io/badge/Languages-11_official_SA_languages-6ee7a1?style=for-the-badge)](https://github.com/ofentse66759/Mati-Metsi)
[![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)](LICENSE)

> **A predictive, offline-first PWA for South African township households to prepare for water, energy, transport and food disruptions.**

---

## 🚨 The Problem

South Africa loses an estimated **40–56% of treated water** before it reaches a tap (DWS estimates). In Tshwane, roughly **1 in 3 households** report long water interruptions. Families in Ga-Rankuwa, Soshanguve, Mabopane, and Winterveldt face outages 3–4 times a week — sometimes for 12 hours, sometimes for nearly 30 days during Rand Water maintenance.

When the taps run dry, households spend **R500–R600 a month** on bottled water and wheelbarrow trips they did not budget for. Students miss classes queuing for JoJo tanks. 

Existing tools (like EskomSePush-style apps) alert *after* the water is gone; municipal updates are in English, on Twitter, two days late. **Nobody warns residents before, tells them how much to store, or shows them what to do.**

---

## 💡 The Solution

**Mati-Metsi** is a single-file, offline-first Progressive Web App (PWA) that gives households a **24–72 hour head start** before a disruption. It is built for low-end Android phones, a 50MB monthly data budget, and speaks all 11 official South African languages.

### Core Features
*   🔮 **Predict & Prepare Engine:** A transparent, rule-based risk model for **five categories**: Flood, Water Shortage, Heat & Energy Stress, Transport Disruption, Food Access. Combines live weather with recent community reports. Every score opens a **"Why this prediction?"** table listing every factor and its point contribution.
*   📢 **Community Reports:** Residents report issues by suburb (street addresses are blocked). Reports move through *Reported → Confirmed → In Progress → Resolved*. Three independent confirmations auto-promote a report. Duplicate detection prevents spam.
*   ✔️ **Verified-Partner Dashboard:** Ward committees and NGOs can bulk-confirm reports, post public response notes, and see a full audit log. *(Demo accounts only in this build).*
*   🤝 **Neighbour Help Board:** Offer or request water, containers, food, lifts, solar charging, shelter, tools and storage. Inline regex blocks banking details and street addresses.
*   ✅ **Resilience Plan & Cost Saver:** Ten practical household actions. Each action shows **litres of water**, **kWh of electricity**, and **Rand saved per month** using Tshwane tariffs. The app recommends the *next best action* based on live risk in your area.
*   🔔 **Local Alerts:** Serious reports, clusters of similar reports, and weather forecasts create Watch / Warning / Emergency alerts with recommended actions.
*   🔒 **POPIA Compliance:** No GPS, no trackers, no third-party ads. One-click JSON export and one-click account deletion. Photos are stored separately so a future backend sync can never lose them.

---

## 🚀 Live Demo

👉 **Open the app:** [https://ofentse66759.github.io/Mati-Metsi/](https://ofentse66759.github.io/Mati-Metsi/)

### Try the Verified-Partner Workflow
1. Open the app and go to **Login**.
2. Sign in with the demo partner credentials:
   *   **Email:** `partner@tshwane-demo.org`
   *   **Password:** `partner123`
3. You will see the **Partner Dashboard** in the navigation. Try bulk-confirming a report or posting a public response.

### Test the Offline Mode
1. Open the app in Chrome or Edge.
2. Press `F12` to open DevTools → Go to the **Network** tab.
3. Change "No throttling" to **Offline**.
4. Refresh the page. The app will load entirely from the Service Worker cache.
5. Submit a report. It will be saved to the **Offline Outbox** and sent automatically when you go back online.

---

## 🛠️ Technology Stack

| Layer | What we use | Why |
| :--- | :--- | :--- |
| **Frontend** | Vanilla HTML/CSS/JS (single file) | Under 2MB, works on 50MB data budget, no build step |
| **Data Storage** | Browser `localStorage` | Offline-first, zero server cost, POPIA-friendly |
| **Weather** | WeatherAPI.com + Open-Meteo fallback | Live conditions, 3-day forecast, air quality |
| **Auth** | SHA-256 via Web Crypto API | Demo-grade; replaced by server-side Argon2id in Phase 2 |
| **Photos** | Canvas downscale (strips EXIF) | Privacy by design — no GPS metadata leaks |
| **i18n** | Static dictionary in-file | 11 languages, no external requests |

---

## 📁 Repository Structure

```text
.
├── index.html              # The complete application (single file)
├── sw.js                   # Service Worker (offline cache + push)
├── .nojekyll               # Tells GitHub Pages to skip Jekyll
├── SECURITY.md             # SSDLC, risk assessment, STRIDE model
├── LICENSE                 # MIT License
└── README.md               # This file
