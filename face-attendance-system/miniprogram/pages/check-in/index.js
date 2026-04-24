const { request } = require("../../utils/request");
const { ensureLogin } = require("../../utils/auth");
const { getLocation } = require("../../utils/location");
const { captureBase64FromCamera } = require("../../utils/image");

Page({
  data: {
    latitude: null,
    longitude: null,
    locationText: "定位中...",
    loading: false,
    resultText: "",
    ruleId: "",
    ready: false,
  },

  async onShow() {
    try {
      await ensureLogin();
      const loc = await getLocation();
      this.setData({
        latitude: loc.latitude,
        longitude: loc.longitude,
        locationText: `${loc.latitude.toFixed(5)}, ${loc.longitude.toFixed(5)}`,
        ready: true,
      });
    } catch (error) {
      this.setData({
        locationText: "定位或登录失败，请检查权限和网络",
        ready: false,
      });
      wx.showToast({ title: error.message || "初始化失败", icon: "none" });
    }
  },

  onRuleInput(e) {
    this.setData({ ruleId: e.detail.value.trim() });
  },

  async doCheckIn() {
    if (!this.data.ready) {
      wx.showToast({ title: "尚未准备好，请稍后", icon: "none" });
      return;
    }

    const camera = wx.createCameraContext();
    this.setData({ loading: true, resultText: "" });

    try {
      const imageBase64 = await captureBase64FromCamera(camera, "high");
      const systemInfo = wx.getSystemInfoSync();
      const result = await request({
        url: "/attendance/check-in",
        method: "POST",
        data: {
          image_base64: imageBase64,
          latitude: this.data.latitude,
          longitude: this.data.longitude,
          rule_id: this.data.ruleId ? Number(this.data.ruleId) : undefined,
          device_info: `${systemInfo.brand || ""} ${systemInfo.model || ""} ${systemInfo.system || ""}`.trim(),
        },
      });
      this.setData({
        resultText: `签到成功：${result.data.status}，距离 ${result.data.distance.toFixed(1)}m，匹配分 ${(
          result.data.face_score * 100
        ).toFixed(1)}%`,
      });
      wx.showToast({ title: "签到成功", icon: "success" });
    } catch (error) {
      this.setData({ resultText: `签到失败：${error.message || "请重试"}` });
      wx.showToast({ title: "签到失败", icon: "none" });
    } finally {
      this.setData({ loading: false });
    }
  },
});
