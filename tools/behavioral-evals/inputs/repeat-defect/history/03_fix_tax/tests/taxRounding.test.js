import { test } from "node:test";
import assert from "node:assert/strict";
import { applyTax } from "../src/pricing/orderTotal.js";

test("given tax producing fractional cents, when applying it, then the result is whole cents", () => {
  assert.equal(applyTax(16.99, 0.0825), 18.39);
});
