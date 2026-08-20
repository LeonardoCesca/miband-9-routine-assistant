var API_BASE_URL = "https://miband-9-routine-assistant.onrender.com";

var ApiService = {
  postCallback: function (reminderId, action) {
    var url =
      API_BASE_URL +
      "/band/callback?reminder_id=" +
      encodeURIComponent(reminderId) +
      "&action=" +
      encodeURIComponent(action);

    return fetch({
      url: url,
      method: "POST",
      headers: { "Content-Type": "application/json" },
    })
      .then(function (res) {
        console.log("[API] callback response: " + res.response);
        return res;
      })
      .catch(function (err) {
        console.log("[API] callback failed: " + err);
        return null;
      });
  },
};

export default ApiService;
