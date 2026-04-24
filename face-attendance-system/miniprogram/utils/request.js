const app = getApp();

function buildHeaders(extra = {}) {
  const token = app.globalData.token || wx.getStorageSync("token") || "";
  return Object.assign(
    {
      "Content-Type": "application/json",
      Authorization: token ? `Bearer ${token}` : "",
    },
    extra
  );
}

function request(options) {
  const { url, method = "GET", data = {}, headers = {}, retry = 1 } = options;
  return new Promise((resolve, reject) => {
    wx.request({
      url: `${app.globalData.baseURL}${url}`,
      method,
      data,
      header: buildHeaders(headers),
      timeout: 12000,
      success(res) {
        if (res.statusCode >= 200 && res.statusCode < 300 && res.data?.success !== false) {
          resolve(res.data);
          return;
        }
        if (res.statusCode === 401) {
          app.globalData.token = "";
          wx.removeStorageSync("token");
        }
        reject(new Error(res.data?.message || `HTTP ${res.statusCode}`));
      },
      fail(err) {
        if (retry > 0) {
          setTimeout(() => {
            request({ ...options, retry: retry - 1 }).then(resolve).catch(reject);
          }, 500);
          return;
        }
        reject(err);
      },
    });
  });
}

module.exports = { request };
