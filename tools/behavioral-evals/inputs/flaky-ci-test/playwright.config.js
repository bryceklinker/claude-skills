export default {
  testDir: "./e2e",
  timeout: 30000,
  retries: 0,
  use: {
    baseURL: "http://localhost:8080",
    trace: "off",
    video: "off",
    screenshot: "off",
  },
};
