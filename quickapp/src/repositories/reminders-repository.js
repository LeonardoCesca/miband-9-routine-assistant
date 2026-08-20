import ReminderConfigService from "../services/reminder-config-service.js";
import bundledConfig from "../data/reminders.json";

var ReminderRepository = {
  init: function () {
    return ReminderConfigService.seed(bundledConfig);
  },

  getAll: function () {
    return ReminderConfigService.getAll();
  },

  getActive: function () {
    return ReminderConfigService.getActive();
  },

  getById: function (id) {
    return ReminderConfigService.getById(id);
  },

  getNext: function () {
    return ReminderConfigService.getNext();
  },
};

export default ReminderRepository;
