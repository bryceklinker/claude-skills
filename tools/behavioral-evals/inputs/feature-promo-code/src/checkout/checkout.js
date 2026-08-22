export function checkout(order) {
  return {
    lineItems: order.lineItems,
    total: subtotalOf(order.lineItems),
  };
}

function subtotalOf(lineItems) {
  return lineItems.reduce((sum, item) => sum + item.price * item.quantity, 0);
}
