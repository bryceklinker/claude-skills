import { test } from "node:test";
import assert from "node:assert/strict";
import { checkout } from "../src/checkout/checkout.js";

test("given one item, when checking out, then the total adds flat-rate shipping", () => {
  const result = checkout({ lineItems: [{ price: 20, quantity: 1 }] });

  assert.equal(result.shipping, 4.99);
  assert.equal(result.total, 24.99);
});
