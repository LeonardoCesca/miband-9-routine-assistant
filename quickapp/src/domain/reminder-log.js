export function createReminderLog(reminderId, date, scheduledAt, status, answeredAt) {
  return {
    id: reminderId + "-" + date,
    reminderId: reminderId,
    date: date,
    scheduledAt: scheduledAt,
    status: status,
    answeredAt: answeredAt,
  };
}
