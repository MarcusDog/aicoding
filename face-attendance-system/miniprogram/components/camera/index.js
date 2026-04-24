Component({
  methods: {
    takePhoto() {
      const camera = wx.createCameraContext(this);
      return new Promise((resolve, reject) => {
        camera.takePhoto({
          quality: "high",
          success: resolve,
          fail: reject,
        });
      });
    },
  },
});
