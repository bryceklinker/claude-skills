import { test } from "node:test";
import assert from "node:assert/strict";
import { checkHealth } from "../src/health/healthCheck.js";

test("given the service is running, when health is checked, then it reports Healthy", () => {
  assert.equal(checkHealth().status, "Healthy");
});
