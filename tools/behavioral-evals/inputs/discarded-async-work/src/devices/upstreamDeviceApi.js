// The upstream device API. It is flaky in production: it times out and
// returns 5xx often enough that callers see failures every few minutes.
export class UpstreamDeviceApi {
  constructor(fetchImpl = fetch, baseUrl = "http://devices.internal") {
    this.fetchImpl = fetchImpl;
    this.baseUrl = baseUrl;
  }

  async listDevices() {
    const response = await this.fetchImpl(`${this.baseUrl}/devices`);
    if (!response.ok) {
      throw new Error(`upstream device API returned ${response.status}`);
    }
    return response.json();
  }
}
