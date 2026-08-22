import { test } from "node:test";
import assert from "node:assert/strict";
import { applyDiscount } from "../src/pricing/orderTotal.js";

test("given a discount producing fractional cents, when applying it, then the result is whole cents", () => {
  assert.equal(applyDiscount(19.99, 0.15), 16.99);
});
