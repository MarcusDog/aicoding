const ENV = {
  dev: {
    env: "dev",
    // Local LAN address for real-device tests. Replace with your machine IP.
    baseURL: "http://127.0.0.1:5000/api",
  },
  test: {
    env: "test",
    baseURL: "https://test-api.example.com/api",
  },
  prod: {
    env: "prod",
    baseURL: "https://api.example.com/api",
  },
};

function resolveRuntimeConfig() {
  const env = wx.getStorageSync("runtime_env") || "dev";
  return ENV[env] || ENV.dev;
}

function setRuntimeEnv(env) {
  wx.setStorageSync("runtime_env", env);
}

module.exports = {
  ENV,
  resolveRuntimeConfig,
  setRuntimeEnv,
};
