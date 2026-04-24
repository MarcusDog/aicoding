const { resolveRuntimeConfig } = require("./config/index");

App({
  globalData: {
    env: "dev",
    baseURL: "",
    token: wx.getStorageSync("token") || "",
    user: null,
  },
  onLaunch() {
    const runtime = resolveRuntimeConfig();
    this.globalData.env = runtime.env;
    this.globalData.baseURL = runtime.baseURL;
  },
});
