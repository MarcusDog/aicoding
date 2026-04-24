function ensureLocationPermission() {
  return new Promise((resolve, reject) => {
    wx.getSetting({
      success(res) {
        const status = res.authSetting["scope.userLocation"];
        if (status === true) {
          resolve(true);
          return;
        }
        wx.authorize({
          scope: "scope.userLocation",
          success() {
            resolve(true);
          },
          fail() {
            wx.showModal({
              title: "需要定位权限",
              content: "签到需要定位权限，请在设置中开启后重试。",
              success(modal) {
                if (modal.confirm) {
                  wx.openSetting({
                    success(settingRes) {
                      resolve(!!settingRes.authSetting["scope.userLocation"]);
                    },
                    fail: reject,
                  });
                  return;
                }
                resolve(false);
              },
            });
          },
        });
      },
      fail: reject,
    });
  });
}

async function getLocation() {
  const granted = await ensureLocationPermission();
  if (!granted) {
    throw new Error("location permission denied");
  }

  return new Promise((resolve, reject) => {
    wx.getLocation({
      type: "gcj02",
      isHighAccuracy: true,
      success: resolve,
      fail: reject,
    });
  });
}

module.exports = { getLocation, ensureLocationPermission };
