#!/usr/bin/env python3
"""
Mati-Metsi — Step 3 patch applier
Reads 'Mati-Metsi fixed.html', applies all Step 3 patches, writes
'Mati-Metsi fixed.patched.html'. Never overwrites the original.
"""
import sys, pathlib

SRC = pathlib.Path("Mati-Metsi fixed.html")
DST = pathlib.Path("Mati-Metsi fixed.patched.html")

PATCHES = []

# ---------- Patch 1 ----------
PATCHES.append(("1  Supabase helpers", r"""  function $(id) { return document.getElementById(id); }
  function $$(sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); }
  function show(el) { if (el) el.classList.remove('hidden'); }
  function hide(el) { if (el) el.classList.add('hidden'); }
""", r"""  function $(id) { return document.getElementById(id); }
  function $$(sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); }
  function show(el) { if (el) el.classList.remove('hidden'); }
  function hide(el) { if (el) el.classList.add('hidden'); }

  // ===== STEP 3: Supabase integration (additive — app works without it) =====
  var SUPABASE_URL = 'https://imopicicoekcsgbqugai.supabase.co';
  var SUPABASE_KEY = 'sb_publishable_YsFLdoEplA46N34M9LThVA_z93_VSYT';
  var _sb = null;

  async function getSupabase() {
    if (_sb) return _sb;
    if (!window.supabase) {
      await new Promise(function (resolve, reject) {
        var s = document.createElement('script');
        s.src = 'https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2';
        s.onload = resolve;
        s.onerror = reject;
        document.head.appendChild(s);
      });
    }
    _sb = window.supabase.createClient(SUPABASE_URL, SUPABASE_KEY, {
      auth: { persistSession: true, autoRefreshToken: true, detectSessionInUrl: false }
    });
    try {
      var r = await _sb.auth.getSession();
      if (!r.data.session) {
        var a = await _sb.auth.signInAnonymously();
        if (a.error) console.warn('[Mati-Metsi] Anon sign-in failed:', a.error.message);
      }
      var u = await _sb.auth.getUser();
      if (u.data.user) lsSet('mm_sb_uid', u.data.user.id);
    } catch (e) {
      console.warn('[Mati-Metsi] Supabase unreachable, staying local-only:', e.message);
    }
    return _sb;
  }
  window.getSupabase = getSupabase;

  async function syncReportToSupabase(report) {
    try {
      var client = await getSupabase();
      var ur = await client.auth.getUser();
      if (!ur.data.user) return false;
      if (!report.author_id) report.author_id = ur.data.user.id;
      var payload = {
        id: report.id, author_id: report.author_id, author_name: report.author,
        category: report.category, type: report.type, area: report.area,
        severity: report.severity, description: report.description,
        status: report.status, source: report.source || 'community',
        org: report.org || null, votes: report.votes || [],
        history: report.history || [], responses: report.responses || [],
        demo: !!report.demo, lat: report.lat || null, lng: report.lng || null,
        photo_path: report.photo_path || null, created_at: report.createdAt
      };
      var res = await client.from('reports').upsert(payload, { onConflict: 'id' });
      if (res.error) { console.warn('[Mati-Metsi] Report sync failed (' + report.id + '):', res.error.message); return false; }
      return true;
    } catch (e) { console.warn('[Mati-Metsi] Report sync error:', e.message); return false; }
  }

  async function syncListingToSupabase(listing) {
    try {
      var client = await getSupabase();
      var ur = await client.auth.getUser();
      if (!ur.data.user) return false;
      if (!listing.author_id) listing.author_id = ur.data.user.id;
      var payload = {
        id: listing.id, author_id: listing.author_id, author_name: listing.author,
        kind: listing.kind, category: listing.category, title: listing.title,
        description: listing.description || null, area: listing.area,
        quantity: listing.quantity || null, until_at: listing.until || null,
        contact: listing.contact, contact_value: listing.contactValue || null,
        status: listing.status, claimed_by: listing.claimedByUid || null,
        messages: listing.messages || [], demo: !!listing.demo,
        created_at: listing.createdAt
      };
      var res = await client.from('help_listings').upsert(payload, { onConflict: 'id' });
      if (res.error) { console.warn('[Mati-Metsi] Listing sync failed (' + listing.id + '):', res.error.message); return false; }
      return true;
    } catch (e) { console.warn('[Mati-Metsi] Listing sync error:', e.message); return false; }
  }

  async function deleteReportFromSupabase(id) {
    try {
      var client = await getSupabase();
      var res = await client.from('reports').delete().eq('id', id);
      if (res.error) console.warn('[Mati-Metsi] Report delete failed:', res.error.message);
    } catch (e) { /* offline */ }
  }

  async function deleteListingFromSupabase(id) {
    try {
      var client = await getSupabase();
      var res = await client.from('help_listings').delete().eq('id', id);
      if (res.error) console.warn('[Mati-Metsi] Listing delete failed:', res.error.message);
    } catch (e) { /* offline */ }
  }

  async function pullReportsFromSupabase() {
    try {
      var client = await getSupabase();
      var res = await client.from('reports').select('*').order('created_at', { ascending: false }).limit(300);
      if (res.error || !res.data) return;
      var local = getReports(), localIds = {}, added = 0;
      local.forEach(function (r) { localIds[r.id] = true; });
      res.data.forEach(function (r) {
        if (localIds[r.id]) return;
        local.push({
          id: r.id, author_id: r.author_id, author: r.author_name, authorEmail: null,
          category: r.category, type: r.type, area: r.area, severity: r.severity,
          description: r.description, photo_path: r.photo_path, photo: null,
          status: r.status, source: r.source, org: r.org || '',
          votes: r.votes || [], history: r.history || [], responses: r.responses || [],
          demo: !!r.demo, lat: r.lat, lng: r.lng, createdAt: r.created_at
        });
        added++;
      });
      if (added) { saveReports(local); renderAll(); console.log('[Mati-Metsi] Pulled ' + added + ' report(s)'); }
    } catch (e) { /* offline */ }
  }

  async function pullListingsFromSupabase() {
    try {
      var client = await getSupabase();
      var res = await client.from('help_listings').select('*').order('created_at', { ascending: false }).limit(300);
      if (res.error || !res.data) return;
      var local = getListings(), localIds = {}, added = 0;
      local.forEach(function (l) { localIds[l.id] = true; });
      res.data.forEach(function (l) {
        if (localIds[l.id]) return;
        local.push({
          id: l.id, author_id: l.author_id, author: l.author_name, authorEmail: null,
          kind: l.kind, category: l.category, title: l.title, description: l.description,
          area: l.area, quantity: l.quantity, until: l.until_at, contact: l.contact,
          contactValue: l.contact_value, status: l.status,
          claimedBy: null, claimedByUid: l.claimed_by, claimedByName: '',
          messages: l.messages || [], demo: !!l.demo, createdAt: l.created_at
        });
        added++;
      });
      if (added) { saveListings(local); renderAll(); }
    } catch (e) { /* offline */ }
  }

  async function catchUpSync() {
    try {
      var client = await getSupabase();
      var r = await client.from('reports').select('id').limit(1000);
      var rIds = {}; (r.data || []).forEach(function (x) { rIds[x.id] = true; });
      getReports().forEach(function (x) { if (!x.demo && x.id && !rIds[x.id]) syncReportToSupabase(x); });
      var l = await client.from('help_listings').select('id').limit(1000);
      var lIds = {}; (l.data || []).forEach(function (x) { lIds[x.id] = true; });
      getListings().forEach(function (x) { if (!x.demo && x.id && !lIds[x.id]) syncListingToSupabase(x); });
    } catch (e) { /* offline */ }
  }

  window.syncReportToSupabase = syncReportToSupabase;
  window.syncListingToSupabase = syncListingToSupabase;
  // ===== End STEP 3 Supabase integration =====
"""))

# ---------- Patch 3 ----------
PATCHES.append(("3  isMine()", r"""  function isMine(r) {
    var u = getUser();
    return !!(u && (r.authorEmail === u.email || (!r.authorEmail && r.author === u.name)));
  }
""", r"""  function isMine(r) {
    // ===== STEP 3: also match by Supabase uid (for pulled reports) =====
    var u = getUser();
    if (!u) return false;
    if (r.authorEmail === u.email) return true;
    if (!r.authorEmail && r.author === u.name) return true;
    var sbUid = lsGet('mm_sb_uid', null);
    if (sbUid && r.author_id === sbUid) return true;
    return false;
  }
"""))

# ---------- Patch 4 ----------
PATCHES.append(("4  isMyListing()", r"""  function isMyListing(l) { var u = getUser(); return !!(u && l.authorEmail === u.email); }""", r"""  function isMyListing(l) {
    // ===== STEP 3: also match by Supabase uid =====
    var u = getUser();
    if (!u) return false;
    if (l.authorEmail === u.email) return true;
    var sbUid = lsGet('mm_sb_uid', null);
    if (sbUid && l.author_id === sbUid) return true;
    return false;
  }"""))

# ---------- Patch 5 ----------
PATCHES.append(("5  Photo upload + submit sync", r"""      var pin = window.__pin;
      if (pin && isFinite(pin.lat) && isFinite(pin.lng) && pin.lat > -35.5 && pin.lat < -21.5 && pin.lng > 15.5 && pin.lng < 33.5) { report.lat = pin.lat; report.lng = pin.lng; }
      if (window.__pinClear) window.__pinClear();
      if (pendingPhoto) stashPhoto(report.id, pendingPhoto);   // keep the image out of mm_reports
      var list = getReports();
      list.unshift(report);
      if (!saveReports(list)) {
        report.photo = null;
        if (!saveReports(list)) { fail('Could not save — this device\'s storage is full. Try removing old data.'); return; }
        toast('Saved without the photo — device storage is full.', 'error');
      }

      msg.textContent = 'Report submitted. Thank you!';
""", r"""      var pin = window.__pin;
      if (pin && isFinite(pin.lat) && isFinite(pin.lng) && pin.lat > -35.5 && pin.lat < -21.5 && pin.lng > 15.5 && pin.lng < 33.5) { report.lat = pin.lat; report.lng = pin.lng; }
      if (window.__pinClear) window.__pinClear();
      // ===== STEP 3: upload photo to Supabase Storage =====
      if (pendingPhoto) {
        stashPhoto(report.id, pendingPhoto);
        (async function () {
          try {
            var client = await getSupabase();
            var ur = await client.auth.getUser();
            if (!ur.data.user) return;
            var parts = pendingPhoto.split(',');
            var bytes = Uint8Array.from(atob(parts[1]), function (c) { return c.charCodeAt(0); });
            var path = ur.data.user.id + '/' + report.id + '.jpg';
            var up = await client.storage.from('photos').upload(path, bytes, { contentType: 'image/jpeg', upsert: true });
            if (up.error) throw up.error;
            var list2 = getReports();
            var r2 = list2.find(function (x) { return x.id === report.id; });
            if (!r2) return;
            r2.photo_path = path;
            saveReports(list2);
            syncReportToSupabase(r2);
            stashPhoto(report.id, null);
            renderAll();
          } catch (e) {
            console.warn('[Mati-Metsi] Photo upload failed, kept base64 locally:', e.message);
          }
        })();
      }
      var list = getReports();
      list.unshift(report);
      if (!saveReports(list)) {
        report.photo = null;
        if (!saveReports(list)) { fail('Could not save — this device\'s storage is full. Try removing old data.'); return; }
        toast('Saved without the photo — device storage is full.', 'error');
      }
      syncReportToSupabase(report);   // ===== STEP 3 =====

      msg.textContent = 'Report submitted. Thank you!';
"""))

# ---------- Patch 6 ----------
PATCHES.append(("6  updateReport() sync", r"""  function updateReport(id, fn) {
    var list = getReports();
    var r = list.find(function (x) { return x.id === id; });
    if (!r) return null;
    fn(r);
    saveReports(list);
    return r;
  }
""", r"""  function updateReport(id, fn) {
    var list = getReports();
    var r = list.find(function (x) { return x.id === id; });
    if (!r) return null;
    fn(r);
    saveReports(list);
    syncReportToSupabase(r);   // ===== STEP 3: sync votes/status/responses =====
    return r;
  }
"""))

# ---------- Patch 7 ----------
PATCHES.append(("7  deleteReport() sync", r"""    if (!ok) return;
    saveReports(getReports().filter(function (x) { return x.id !== id; }));
    renderAll();
    if (currentView === 'profile') loadProfile();
    toast('Report deleted.', 'success');
""", r"""    if (!ok) return;
    saveReports(getReports().filter(function (x) { return x.id !== id; }));
    deleteReportFromSupabase(id);   // ===== STEP 3 =====
    renderAll();
    if (currentView === 'profile') loadProfile();
    toast('Report deleted.', 'success');
"""))

# ---------- Patch 8 ----------
PATCHES.append(("8  helpForm submit sync", r"""    var list = getListings();
    list.unshift(l);
    if (!saveListings(list)) { fail('Could not save — device storage is full.'); return; }
    hide($('helpForm'));
""", r"""    var list = getListings();
    list.unshift(l);
    if (!saveListings(list)) { fail('Could not save — device storage is full.'); return; }
    syncListingToSupabase(l);   // ===== STEP 3 =====
    hide($('helpForm'));
"""))

# ---------- Patch 9 ----------
PATCHES.append(("9  updateListing + claimListing sync", r"""  function updateListing(id, fn) {
    var list = getListings();
    var l = list.find(function (x) { return x.id === id; });
    if (!l) return null;
    fn(l);
    saveListings(list);
    return l;
  }
  function claimListing(id) {
    if (!requireLogin('claim listings')) return;
    var u = getUser();
    updateListing(id, function (l) { l.status = 'claimed'; l.claimedBy = u.email; l.claimedByName = u.name; l.claimedAt = nowIso(); });
""", r"""  function updateListing(id, fn) {
    var list = getListings();
    var l = list.find(function (x) { return x.id === id; });
    if (!l) return null;
    fn(l);
    saveListings(list);
    syncListingToSupabase(l);   // ===== STEP 3 =====
    return l;
  }
  function claimListing(id) {
    if (!requireLogin('claim listings')) return;
    var u = getUser();
    // ===== STEP 3: also record Supabase uid on claim =====
    updateListing(id, function (l) { l.status = 'claimed'; l.claimedBy = u.email; l.claimedByUid = lsGet('mm_sb_uid', null); l.claimedByName = u.name; l.claimedAt = nowIso(); });
"""))

# ---------- Patch 10 ----------
PATCHES.append(("10 deleteListing() sync", r"""    saveListings(getListings().filter(function (x) { return x.id !== id; }));
    refreshHelpViews();
    toast('Listing deleted.', 'success');
""", r"""    saveListings(getListings().filter(function (x) { return x.id !== id; }));
    deleteListingFromSupabase(id);   // ===== STEP 3 =====
    refreshHelpViews();
    toast('Listing deleted.', 'success');
"""))

# ---------- Patch 11 ----------
PATCHES.append(("11 reportCard() photo URL", r"""      '<span id="speak-src-' + sid + '" hidden>' + esc(typeLabel(r.category, r.type) + '. ' + (r.area || '') + '. ' + (r.description || '')) + '</span>' +
      ((r.photo || loadPhoto(r.id)) ? '<img class="report-photo" src="' + (r.photo || loadPhoto(r.id)) + '" alt="Photo attached to this report" data-action="photo" data-id="' + r.id + '" loading="lazy">' : '') +
""", r"""      '<span id="speak-src-' + sid + '" hidden>' + esc(typeLabel(r.category, r.type) + '. ' + (r.area || '') + '. ' + (r.description || '')) + '</span>' +
      (function () {   // ===== STEP 3: prefer Supabase Storage URL =====
        var src = (r.photo_path && _sb ? _sb.storage.from('photos').getPublicUrl(r.photo_path).data.publicUrl : null) || r.photo || loadPhoto(r.id);
        return src ? '<img class="report-photo" src="' + src + '" alt="Photo attached to this report" data-action="photo" data-id="' + r.id + '" loading="lazy">' : '';
      })() +
"""))

# ---------- Patch 12 ----------
PATCHES.append(("12 boot() pull remote", r"""    setInterval(function () {
      if (!document.hidden) refreshWeather();
    }, 15 * 60 * 1000);
""", r"""    // ===== STEP 3: pull remote data + sync catch-up on boot =====
    setTimeout(function () {
      pullReportsFromSupabase();
      pullListingsFromSupabase();
      catchUpSync();
    }, 2000);
    setInterval(function () {
      if (!document.hidden) refreshWeather();
    }, 15 * 60 * 1000);
"""))

# ---------- Patch 13 ----------
PATCHES.append(("13 deleteAccount() purge Supabase", r"""    clearUser();
    [K.prefs, K.plan, K.draft, K.location, K.prevScore].forEach(lsRemove);
""", r"""    // ===== STEP 3: purge Supabase rows + photos (RLS restricts to our own) =====
    (async function () {
      try {
        var client = await getSupabase();
        var ur = await client.auth.getUser();
        if (!ur.data.user) return;
        var pr = await client.from('reports').select('photo_path').eq('author_id', ur.data.user.id);
        var paths = (pr.data || []).map(function (x) { return x.photo_path; }).filter(Boolean);
        if (paths.length) await client.storage.from('photos').remove(paths);
        await client.from('reports').delete().eq('author_id', ur.data.user.id);
        await client.from('help_listings').delete().eq('author_id', ur.data.user.id);
      } catch (e) {
        console.warn('[Mati-Metsi] Supabase cleanup failed:', e.message);
      }
    })();
    clearUser();
    [K.prefs, K.plan, K.draft, K.location, K.prevScore].forEach(lsRemove);
"""))

# ---------- Patch 14 ----------
PATCHES.append(("14 Offline outbox sync", r"""    var partner = u.role === 'partner', list = get(REP, []);
    send.forEach(function (x) {
      var st = partner ? 'confirmed' : 'reported';
      list.unshift({ id: 'r-' + Date.now().toString(36) + '-' + Math.random().toString(36).slice(2, 7), category: x.category, type: x.type, area: x.area, severity: x.severity, description: x.description, photo: null, createdAt: x.queuedAt, status: st, votes: [], author: x.name, authorEmail: u.email, source: partner ? 'partner' : 'community', org: partner ? (u.org || '') : '', responses: [], history: [{ status: st, at: x.queuedAt, by: u.name + (partner && u.org ? ' (' + u.org + ')' : '') }], demo: false });
    });
    if (put(REP, list)) {
      put(OUT, q.filter(function (x) { return x.authorEmail !== u.email; }));
""", r"""    var partner = u.role === 'partner', list = get(REP, []), newlyAdded = [];
    send.forEach(function (x) {
      var st = partner ? 'confirmed' : 'reported';
      var nr = { id: 'r-' + Date.now().toString(36) + '-' + Math.random().toString(36).slice(2, 7), category: x.category, type: x.type, area: x.area, severity: x.severity, description: x.description, photo: null, createdAt: x.queuedAt, status: st, votes: [], author: x.name, authorEmail: u.email, source: partner ? 'partner' : 'community', org: partner ? (u.org || '') : '', responses: [], history: [{ status: st, at: x.queuedAt, by: u.name + (partner && u.org ? ' (' + u.org + ')' : '') }], demo: false };
      list.unshift(nr);
      newlyAdded.push(nr);
    });
    if (put(REP, list)) {
      put(OUT, q.filter(function (x) { return x.authorEmail !== u.email; }));
      // ===== STEP 3: sync flushed reports to Supabase =====
      setTimeout(function () {
        newlyAdded.forEach(function (r) { if (window.syncReportToSupabase) window.syncReportToSupabase(r); });
      }, 800);
"""))


def main():
    if not SRC.exists():
        sys.exit(f"ERROR: '{SRC}' not found. Run this script from the same folder as the HTML file.")
    html = SRC.read_text(encoding="utf-8")
    applied, skipped, failed = 0, 0, 0
    print(f"Reading: {SRC} ({len(html):,} chars)\n")
    for name, search, replace in PATCHES:
        if search in html:
            html = html.replace(search, replace, 1)
            print(f"  ✅ {name}")
            applied += 1
        elif replace in html:
            print(f"  ↺  {name}  (already applied — skipped)")
            skipped += 1
        else:
            print(f"  ❌ {name}  (SEARCH string not found — patch NOT applied)")
            failed += 1
    DST.write_text(html, encoding="utf-8")
    print(f"\nWrote: {DST} ({len(html):,} chars)")
    print(f"\nSummary: {applied} applied · {skipped} already applied · {failed} failed")
    if failed:
        print("\n⚠️  Some patches failed. Do NOT overwrite the original — keep the patched file separate")
        print("   and report which patch numbers failed.")
        sys.exit(1)
    print("\n✅ All patches applied. Rename 'Mati-Metsi fixed.patched.html' over your original when verified.")


if __name__ == "__main__":
    main()
