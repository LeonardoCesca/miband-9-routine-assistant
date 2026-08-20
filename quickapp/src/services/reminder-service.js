import { createReminderLog } from "../domain/reminder-log.js";
import ReminderLogRepository from "../repositories/reminder-logs-repository.js";
import ApiService from "./api-service.js";
import Clock from "./clock.js";

var ReminderService = {
  answer: function (reminder, status) {
    var date = Clock.todayString();
    var answeredAt = Clock.currentTime();
    var scheduledAt = Clock.formatHour(reminder.hour, reminder.minute);

    var log = createReminderLog(reminder.id, date, scheduledAt, status, answeredAt);
    return ReminderLogRepository.saveOrUpdate(log).then(function () {
      console.log("[REMINDER] log saved: " + log.id + " status=" + log.status);
      ApiService.postCallback(reminder.id, status);
      return log;
    });
  },

  getTodayProgress: function () {
    var today = Clock.todayString();
    var logs = ReminderLogRepository.getByDate(today);
    var responded = logs.length;
    var done = 0;

    for (var i = 0; i < logs.length; i++) {
      if (logs[i].status === "done") {
        done++;
      }
    }

    return {
      responded: responded,
      done: done,
    };
  },

  getTodayHistory: function () {
    var today = Clock.todayString();
    var logs = ReminderLogRepository.getByDate(today);

    logs.sort(function (a, b) {
      return a.scheduledAt > b.scheduledAt ? 1 : -1;
    });

    return logs;
  },
};

export default ReminderService;
