const { request } = require("../../utils/request");
const { ensureLogin } = require("../../utils/auth");

Page({
  data: {
    date: "",
    records: [],
    loading: false,
  },

  async onShow() {
    await this.fetchRecords();
  },

  async onDateChange(e) {
    this.setData({ date: e.detail.value });
    await this.fetchRecords();
  },

  async fetchRecords() {
    this.setData({ loading: true });
    try {
      await ensureLogin();
      const query = this.data.date ? `?date=${this.data.date}` : "";
      const result = await request({ url: `/attendance/records${query}` });
      this.setData({ records: result.data.items || [] });
    } catch (error) {
      wx.showToast({ title: error.message || "加载失败", icon: "none" });
    } finally {
      this.setData({ loading: false });
    }
  },
});
