import { DeviceCache } from "./deviceCache.js";

export class DeviceService {
  constructor(cache = new DeviceCache()) {
    this.cache = cache;
  }

  listDevices() {
    return this.cache.all();
  }

  getDevice(id) {
    return this.cache.find(id);
  }
}
