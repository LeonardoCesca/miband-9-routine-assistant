import vibrator from "@system.vibrator";

var VibrationService = {
  reminder: function () {
    vibrator.vibrate({
      mode: "short",
      vibrateDuration: 200,
    });
  },
};

export default VibrationService;
