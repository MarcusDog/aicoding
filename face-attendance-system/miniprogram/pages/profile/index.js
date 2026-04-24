const { request } = require("../../utils/request");
const { ensureLogin, wxLogin } = require("../../utils/auth");
const { setRuntimeEnv } = require("../../config/index");

Page({
  data: {
    profile: {},
    env: getApp().globalData.env || "dev",
    envOptions: ["dev", "test", "prod"],
  },

  async onShow() {
    await this.reload();
  },

  async reload() {
    try {
      await ensureLogin();
      const result = await request({ url: "/auth/profile" });
      this.setData({ profile: result.data.profile || {}, env: getApp().globalData.env || "dev" });
    } catch (error) {
      wx.showToast({ title: error.message || "获取资料失败", icon: "none" });
    }
  },

  async relogin() {
    try {
      await wxLogin();
      await this.reload();
      wx.showToast({ title: "登录成功", icon: "success" });
    } catch (error) {
      wx.showToast({ title: error.message || "登录失败", icon: "none" });
    }
  },

  goRegister() {
    wx.navigateTo({ url: "/pages/face-register/index" });
  },

  onEnvChange(e) {
    const idx = Number(e.detail.value);
    const env = this.data.envOptions[idx];
    setRuntimeEnv(env);
    wx.showModal({
      title: "环境已切换",
      content: `已切换到 ${env}，请重新启动小程序生效。`,
      showCancel: false,
    });
  },
});
