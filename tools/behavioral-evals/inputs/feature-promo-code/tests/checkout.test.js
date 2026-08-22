import { test } from "node:test";
import assert from "node:assert/strict";
import { checkout } from "../src/checkout/checkout.js";

test("given line items, when checking out, then the total is their sum", () => {
  const result = checkout({ lineItems: [{ price: 10, quantity: 2 }, { price: 5, quantity: 1 }] });

  assert.equal(result.total, 25);
});
