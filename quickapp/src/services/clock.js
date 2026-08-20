var Clock = {
  now: function () {
    return new Date();
  },

  todayString: function () {
    var d = new Date();
    return (
      d.getFullYear() +
      "-" +
      this._pad(d.getMonth() + 1) +
      "-" +
      this._pad(d.getDate())
    );
  },

  currentTime: function () {
    var d = new Date();
    return this._pad(d.getHours()) + ":" + this._pad(d.getMinutes());
  },

  formatHour: function (h, m) {
    return this._pad(h) + ":" + this._pad(m);
  },

  _pad: function (n) {
    return n < 10 ? "0" + n : "" + n;
  },
};

export default Clock;
