import { test } from "node:test";
import assert from "node:assert/strict";
import { Coordinator } from "../src/coordinator/coordinator.js";

test("given a connected coordinator, when it disconnects, then it reports not connected", () => {
  const coordinator = new Coordinator();
  coordinator.connect();

  coordinator.disconnect();

  assert.equal(coordinator.isConnected, false);
});
