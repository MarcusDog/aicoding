const { request } = require("./request");

let loginPromise = null;

function wxLogin() {
  if (loginPromise) return loginPromise;

  loginPromise = new Promise((resolve, reject) => {
    wx.login({
      success: async (res) => {
        if (!res.code) {
          loginPromise = null;
          reject(new Error("wx.login did not return code"));
          return;
        }
        try {
          const result = await request({
            url: "/auth/wx-login",
            method: "POST",
            data: { code: res.code },
          });
          const app = getApp();
          app.globalData.token = result.data.token;
          app.globalData.user = result.data.user;
          wx.setStorageSync("token", result.data.token);
          loginPromise = null;
          resolve(result.data.user);
        } catch (error) {
          loginPromise = null;
          reject(error);
        }
      },
      fail(err) {
        loginPromise = null;
        reject(err);
      },
    });
  });

  return loginPromise;
}

async function ensureLogin() {
  const app = getApp();
  if (app.globalData.token || wx.getStorageSync("token")) {
    app.globalData.token = app.globalData.token || wx.getStorageSync("token");
    return;
  }
  await wxLogin();
}

module.exports = { wxLogin, ensureLogin };
