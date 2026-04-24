function readAsBase64(path) {
  const fs = wx.getFileSystemManager();
  return fs.readFileSync(path, "base64");
}

function compressImage(path, quality = 75) {
  return new Promise((resolve, reject) => {
    wx.compressImage({
      src: path,
      quality,
      compressedWidth: 720,
      compressedHeight: 720,
      success(res) {
        resolve(res.tempFilePath || path);
      },
      fail(err) {
        reject(err);
      },
    });
  });
}

async function captureBase64FromCamera(camera, quality = "high") {
  const photo = await new Promise((resolve, reject) => {
    camera.takePhoto({
      quality,
      success: resolve,
      fail: reject,
    });
  });
  const compressedPath = await compressImage(photo.tempImagePath, 75);
  return readAsBase64(compressedPath);
}

module.exports = {
  captureBase64FromCamera,
  readAsBase64,
  compressImage,
};
