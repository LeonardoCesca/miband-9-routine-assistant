export function createReminder(id, title, message, hour, minute, type) {
  return {
    id: id,
    title: title,
    message: message,
    hour: hour,
    minute: minute || 0,
    active: true,
    type: type || "generic",
  };
}
