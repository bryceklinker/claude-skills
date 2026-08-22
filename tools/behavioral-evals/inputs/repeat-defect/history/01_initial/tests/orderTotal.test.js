import { test } from "node:test";
import assert from "node:assert/strict";
import { orderTotal } from "../src/pricing/orderTotal.js";

test("given no discount and no tax, when totalling, then subtotal plus shipping is returned", () => {
  const total = orderTotal({
    subtotal: 100,
    discountRate: 0,
    taxRate: 0,
    shipping: { baseCost: 5, surchargeRate: 0 },
  });

  assert.equal(total, 105);
});
