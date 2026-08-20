import StorageService from "../services/storage-service.js";
import { STORAGE_KEYS } from "../constants/storage-keys.js";
import HistoryService from "../services/history-service.js";

var _cache = null;

var ReminderLogRepository = {
  _load: function () {
    return StorageService.get(STORAGE_KEYS.REMINDER_LOGS).then(function (data) {
      if (!data) {
        _cache = [];
        return _cache;
      }
      _cache = JSON.parse(data);
      return _cache;
    });
  },

  _persist: function () {
    var cleaned = HistoryService.cleanupOldLogs(_cache);
    _cache = cleaned;
    return StorageService.set(
      STORAGE_KEYS.REMINDER_LOGS,
      JSON.stringify(cleaned)
    );
  },

  init: function () {
    return this._load();
  },

  saveOrUpdate: function (log) {
    if (!_cache) {
      _cache = [];
    }

    var found = false;
    for (var i = 0; i < _cache.length; i++) {
      if (_cache[i].id === log.id) {
        _cache[i].status = log.status;
        _cache[i].answeredAt = log.answeredAt;
        found = true;
        break;
      }
    }

    if (!found) {
      _cache.push(log);
    }

    return this._persist();
  },

  getByDate: function (date) {
    if (!_cache) {
      return [];
    }
    var result = [];
    for (var i = 0; i < _cache.length; i++) {
      if (_cache[i].date === date) {
        result.push(_cache[i]);
      }
    }
    return result;
  },

  getByReminder: function (reminderId, date) {
    if (!_cache) {
      return null;
    }
    for (var i = 0; i < _cache.length; i++) {
      if (_cache[i].reminderId === reminderId && _cache[i].date === date) {
        return _cache[i];
      }
    }
    return null;
  },

  cleanup: function () {
    if (!_cache) {
      return Promise.resolve();
    }
    return this._persist();
  },

  getAll: function () {
    if (_cache) {
      return Promise.resolve(_cache);
    }
    return this._load();
  },
};

export default ReminderLogRepository;
