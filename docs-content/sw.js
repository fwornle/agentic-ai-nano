/**
 * Service Worker for Agentic AI Nano-Degree Podcast Feature
 * Provides offline support and caching for the podcast functionality
 */

const CACHE_NAME = 'agentic-ai-podcast-v1';
const urlsToCache = [
  '/',
  '/stylesheets/podcast.css',
  '/javascripts/podcast-tts.js',
  '/javascripts/mathjax.js',
  '/stylesheets/extra.css'
];

// Install event
self.addEventListener('install', function(event) {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(function(cache) {
        console.log('Podcast SW: Opened cache');
        return cache.addAll(urlsToCache);
      })
  );
});

// Fetch event
self.addEventListener('fetch', function(event) {
  event.respondWith(
    caches.match(event.request)
      .then(function(response) {
        // Return cached version or fetch from network
        return response || fetch(event.request);
      }
    )
  );
});

// Activate event
self.addEventListener('activate', function(event) {
  event.waitUntil(
    caches.keys().then(function(cacheNames) {
      return Promise.all(
        cacheNames.map(function(cacheName) {
          if (cacheName !== CACHE_NAME) {
            console.log('Podcast SW: Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});