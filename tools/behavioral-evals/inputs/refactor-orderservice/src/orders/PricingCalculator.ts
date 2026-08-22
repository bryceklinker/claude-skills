import { Order } from "./OrderService";

// Owned, in-process, deterministic collaborator.
export class PricingCalculator {
  private prices: Record<string, number>;

  constructor(prices: Record<string, number>) {
    this.prices = prices;
  }

  lineTotal(sku: string, quantity: number): number {
    const price = this.prices[sku] ?? 0;
    return price * quantity;
  }

  subtotal(order: Order): number {
    let total = 0;
    for (const line of order.lines) {
      total += this.lineTotal(line.sku, line.quantity);
    }
    return total;
  }
}
