// Fallback Service Worker for push notifications
self.addEventListener('push', function(e) {
  var data = e.data ? e.data.json() : { title: 'Mati-Metsi', body: 'New alert in your area' };
  e.waitUntil(
    self.registration.showNotification(data.title, { body: data.body })
  );
});
