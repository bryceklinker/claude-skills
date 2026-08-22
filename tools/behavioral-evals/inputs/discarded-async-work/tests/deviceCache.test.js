import { test } from "node:test";
import assert from "node:assert/strict";
import { DeviceCache } from "../src/devices/deviceCache.js";

test("given devices are replaced, when reading all, then the new devices are returned", () => {
  const cache = new DeviceCache();

  cache.replaceAll([{ id: "a", name: "Lamp" }]);

  assert.deepEqual(cache.all(), [{ id: "a", name: "Lamp" }]);
});

test("given an unknown id, when finding a device, then null is returned", () => {
  const cache = new DeviceCache();

  assert.equal(cache.find("missing"), null);
});
