/*!
 * Static Async Dynamic — read a sharded dataset from a static host.
 *
 * A static host will not run your code, but it will serve files, and a <script>
 * tag has always been allowed to load one from anywhere. That is the whole
 * trick: the data is written as JavaScript rather than JSON, so it needs no
 * CORS header, no API, and no server — and it works from file:// too, where
 * fetch() does not.
 *
 * The data is cut into shards and indexed, so a lookup costs one small index
 * and one small shard instead of the whole dataset.
 *
 *     const store = new StaticStore("static-async-data");
 *     const company = await store.get("cvr", "10001528");
 *
 * MIT licensed.
 */
(function (global) {
  "use strict";

  /* Shards call back into this registry as they load. Store names are global
     to the page, which is the price of being loadable by <script>. */
  var registry = global.__STORE || (global.__STORE = {
    _index: {}, _shard: {}, _manifest: null,
    index: function (name, payload) { this._index[name] = payload; },
    put: function (name, sid, payload) { this._shard[name + "/" + sid] = payload; },
    manifest: function (payload) { this._manifest = payload; }
  });

  /* Keys are ordered as plain strings, exactly as the builder sorted them.
     Both sides use the same rule so the binary search cannot disagree with the
     file layout. (For keys outside the Basic Multilingual Plane, JavaScript
     orders by UTF-16 code unit and Python by code point; use ASCII keys, or
     hash them, if that could ever matter to you.) */
  function before(a, b) { return a < b; }

  function StaticStore(base, options) {
    if (!(this instanceof StaticStore)) return new StaticStore(base, options);
    options = options || {};
    this.base = String(base || ".").replace(/\/+$/, "");
    this.timeout = options.timeout || 20000;
    this._pending = {};          // url -> Promise, so a shard loads once
  }

  /* One <script> injection, as a promise. The tag is removed either way: the
     data it carried now lives in the registry, and leaving hundreds of dead
     script elements in the document head helps nobody. */
  StaticStore.prototype._script = function (url) {
    var self = this;
    if (this._pending[url]) return this._pending[url];

    var promise = new Promise(function (resolve, reject) {
      var el = document.createElement("script");
      var done = false;
      var timer = setTimeout(function () {
        finish(new Error("timed out loading " + url));
      }, self.timeout);

      function finish(err) {
        if (done) return;
        done = true;
        clearTimeout(timer);
        if (el.parentNode) el.parentNode.removeChild(el);
        err ? reject(err) : resolve();
      }

      el.src = url;
      el.async = true;
      el.charset = "utf-8";
      el.onload = function () { finish(null); };
      el.onerror = function () { finish(new Error("could not load " + url)); };
      (document.head || document.documentElement).appendChild(el);
    });

    /* A failure is not cached: a shard that 404s because the tree was mid-deploy
       should be retryable, whereas a success never needs fetching twice. */
    this._pending[url] = promise;
    promise.catch(function () { delete self._pending[url]; });
    return promise;
  };

  StaticStore.prototype.index = function (name) {
    var self = this;
    if (registry._index[name]) return Promise.resolve(registry._index[name]);
    return this._script(this.base + "/" + name + "/index.js").then(function () {
      var idx = registry._index[name];
      if (!idx) throw new Error("index.js for '" + name + "' loaded but registered nothing");
      return idx;
    });
  };

  /* Whatever the builder found at the top level beside the records — string
     pools, field layouts, a schema. Shared by every shard, so it rides in the
     index and is already loaded by the time any record is. */
  StaticStore.prototype.meta = function (name) {
    return this.index(name).then(function (idx) { return idx.meta || {}; });
  };

  StaticStore.prototype.count = function (name) {
    return this.index(name).then(function (idx) { return idx.count; });
  };

  /* The last shard whose first key is not after the key wanted. */
  function shardFor(idx, key) {
    var shards = idx.shards;
    if (!shards || !shards.length || before(key, shards[0][0])) return null;
    var lo = 0, hi = shards.length - 1;
    while (lo < hi) {
      var mid = (lo + hi + 1) >> 1;
      if (before(key, shards[mid][0])) hi = mid - 1; else lo = mid;
    }
    return shards[lo][1];
  }
  StaticStore._shardFor = shardFor;   // exported for the tests

  StaticStore.prototype._shard = function (name, sid) {
    var slot = name + "/" + sid;
    if (registry._shard[slot]) return Promise.resolve(registry._shard[slot]);
    return this._script(this.base + "/" + slot + ".js").then(function () {
      return registry._shard[slot] || {};
    });
  };

  /* One record, or null if the store does not have it. A missing key still
     costs a shard load — the index knows the ranges, not the contents. */
  StaticStore.prototype.get = function (name, key) {
    var self = this;
    key = String(key);
    return this.index(name).then(function (idx) {
      var sid = shardFor(idx, key);
      if (!sid) return null;
      return self._shard(name, sid).then(function (records) {
        return Object.prototype.hasOwnProperty.call(records, key) ? records[key] : null;
      });
    });
  };

  StaticStore.prototype.has = function (name, key) {
    return this.get(name, key).then(function (v) { return v !== null; });
  };

  /* Several keys at once, grouped so that keys sharing a shard cost one load
     between them rather than one each. */
  StaticStore.prototype.getMany = function (name, keys) {
    var self = this;
    return this.index(name).then(function (idx) {
      var byShard = {}, out = {};
      keys.forEach(function (k) {
        k = String(k);
        var sid = shardFor(idx, k);
        if (!sid) { out[k] = null; return; }
        (byShard[sid] || (byShard[sid] = [])).push(k);
      });
      return Promise.all(Object.keys(byShard).map(function (sid) {
        return self._shard(name, sid).then(function (records) {
          byShard[sid].forEach(function (k) {
            out[k] = Object.prototype.hasOwnProperty.call(records, k) ? records[k] : null;
          });
        });
      })).then(function () { return out; });
    });
  };

  /* Warm the shard a key lives in without waiting for it — for a hover, or for
     the record you can already tell will be asked for next. */
  StaticStore.prototype.prefetch = function (name, key) {
    var self = this;
    return this.index(name).then(function (idx) {
      var sid = shardFor(idx, String(key));
      return sid ? self._shard(name, sid).then(function () { return true; }) : false;
    }).catch(function () { return false; });
  };

  StaticStore.prototype.manifest = function () {
    if (registry._manifest) return Promise.resolve(registry._manifest);
    return this._script(this.base + "/manifest.js").then(function () {
      return registry._manifest;
    });
  };

  if (typeof module === "object" && module.exports) module.exports = StaticStore;
  global.StaticStore = StaticStore;
})(typeof globalThis !== "undefined" ? globalThis : this);
