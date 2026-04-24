Component({
  data: {
    text: "定位中...",
  },
  lifetimes: {
    attached() {
      wx.getLocation({
        type: "gcj02",
        success: (res) => {
          this.setData({
            text: `${res.latitude.toFixed(5)}, ${res.longitude.toFixed(5)}`,
          });
        },
        fail: () => {
          this.setData({ text: "定位失败" });
        },
      });
    },
  },
});
