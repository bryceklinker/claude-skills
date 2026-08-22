export class DeviceCache {
  #devicesById = new Map();

  replaceAll(devices) {
    this.#devicesById = new Map(devices.map((device) => [device.id, device]));
  }

  all() {
    return [...this.#devicesById.values()];
  }

  find(id) {
    return this.#devicesById.get(id) ?? null;
  }
}
