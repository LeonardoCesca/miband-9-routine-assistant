import storage from "@system.storage";

var StorageService = {
  get: function (key) {
    return new Promise(function (resolve, reject) {
      storage.get({
        key: key,
        success: function (data) {
          resolve(data);
        },
        fail: function (data, code) {
          reject(code);
        },
      });
    });
  },

  set: function (key, value) {
    return new Promise(function (resolve, reject) {
      storage.set({
        key: key,
        value: value,
        success: function () {
          resolve();
        },
        fail: function (data, code) {
          reject(code);
        },
      });
    });
  },

  remove: function (key) {
    return new Promise(function (resolve, reject) {
      storage.delete({
        key: key,
        success: function () {
          resolve();
        },
        fail: function (data, code) {
          reject(code);
        },
      });
    });
  },
};

export default StorageService;
