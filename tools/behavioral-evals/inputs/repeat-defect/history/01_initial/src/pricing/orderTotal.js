export function applyDiscount(subtotal, discountRate) {
  return subtotal - subtotal * discountRate;
}

export function applyTax(amount, taxRate) {
  return amount + amount * taxRate;
}

export function applyShipping(amount, shipping) {
  const surcharge = amount * shipping.surchargeRate;
  return amount + shipping.baseCost + surcharge;
}

export function orderTotal(order) {
  const discounted = applyDiscount(order.subtotal, order.discountRate);
  const taxed = applyTax(discounted, order.taxRate);
  return applyShipping(taxed, order.shipping);
}
