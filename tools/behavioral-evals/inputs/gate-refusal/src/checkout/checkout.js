import { shippingFor } from "./shipping.js";

export function checkout(order) {
  const subtotal = order.lineItems.reduce((sum, item) => sum + item.price * item.quantity, 0);
  const shipping = shippingFor(subtotal);
  return { lineItems: order.lineItems, subtotal, shipping, total: subtotal + shipping };
}
