const { request } = require("../../utils/request");
const { ensureLogin } = require("../../utils/auth");
const { captureBase64FromCamera } = require("../../utils/image");

Page({
  data: {
    loading: false,
    tips: "请保持正面、光线充足，拍摄时摘下口罩。",
  },

  async onShow() {
    try {
      await ensureLogin();
    } catch (error) {
      wx.showToast({ title: error.message || "登录失败", icon: "none" });
    }
  },

  async registerFace() {
    const camera = wx.createCameraContext();
    this.setData({ loading: true });

    try {
      const imageBase64 = await captureBase64FromCamera(camera, "high");
      await request({
        url: "/face/register",
        method: "POST",
        data: { image_base64: imageBase64 },
      });
      wx.showToast({ title: "注册成功", icon: "success" });
      setTimeout(() => wx.navigateBack(), 900);
    } catch (error) {
      wx.showToast({ title: error.message || "注册失败", icon: "none" });
    } finally {
      this.setData({ loading: false });
    }
  },
});
