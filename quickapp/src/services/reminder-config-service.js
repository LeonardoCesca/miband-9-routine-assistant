import StorageService from "./storage-service.js";
import { STORAGE_KEYS } from "../constants/storage-keys.js";
import Clock from "./clock.js";

var _reminders = null;

var ReminderConfigService = {
  load: function () {
    var self = this;
    return StorageService.get(STORAGE_KEYS.REMINDERS).then(function (data) {
      if (data) {
        _reminders = JSON.parse(data);
      }
      return _reminders || [];
    });
  },

  seed: function (configData) {
    var self = this;
    return StorageService.get(STORAGE_KEYS.REMINDERS).then(function (existing) {
      if (existing) {
        var parsed = JSON.parse(existing);
        var existingVersion = 0;
        try {
          var meta = JSON.parse(existing);
          existingVersion = meta.schemaVersion || 0;
        } catch (e) {}
      }

      var needsUpdate = false;
      if (!existing) {
        needsUpdate = true;
      } else if (configData && configData.schemaVersion) {
        try {
          var stored = JSON.parse(existing);
          if (stored.schemaVersion && configData.schemaVersion > stored.schemaVersion) {
            needsUpdate = true;
          } else if (configData.generatedAt && stored.generatedAt && configData.generatedAt > stored.generatedAt) {
            needsUpdate = true;
          }
        } catch (e) {
          needsUpdate = true;
        }
      }

      if (needsUpdate && configData && configData.reminders) {
        _reminders = configData.reminders;
        return StorageService.set(STORAGE_KEYS.REMINDERS, JSON.stringify(configData));
      }

      if (!needsUpdate && existing) {
        _reminders = JSON.parse(existing).reminders || JSON.parse(existing);
      }

      return _reminders || [];
    });
  },

  getAll: function () {
    if (_reminders) {
      return Promise.resolve(_reminders);
    }
    return this.load();
  },

  getActive: function () {
    return this.getAll().then(function (all) {
      var active = [];
      for (var i = 0; i < all.length; i++) {
        if (all[i].active) {
          active.push(all[i]);
        }
      }
      return active;
    });
  },

  getNext: function () {
    return this.getActive().then(function (active) {
      var now = Clock.now();
      var currentMinutes = now.getHours() * 60 + now.getMinutes();

      for (var i = 0; i < active.length; i++) {
        var r = active[i];
        var rMinutes = r.hour * 60 + r.minute;
        if (rMinutes > currentMinutes) {
          return r;
        }
      }
      return null;
    });
  },

  getById: function (id) {
    return this.getAll().then(function (all) {
      for (var i = 0; i < all.length; i++) {
        if (all[i].id === id) {
          return all[i];
        }
      }
      return null;
    });
  },
};

export default ReminderConfigService;
