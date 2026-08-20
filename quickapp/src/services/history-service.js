import Clock from "./clock.js";

var SEVEN_DAYS_MS = 7 * 24 * 60 * 60 * 1000;

var HistoryService = {
  cleanupOldLogs: function (logs) {
    var now = Clock.now().getTime();
    var cutoff = now - SEVEN_DAYS_MS;
    var filtered = [];

    for (var i = 0; i < logs.length; i++) {
      var logDate = new Date(logs[i].date).getTime();
      if (logDate >= cutoff) {
        filtered.push(logs[i]);
      }
    }

    return filtered;
  },
};

export default HistoryService;
