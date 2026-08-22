import { InventoryChecker } from "./InventoryChecker";
import { PricingCalculator } from "./PricingCalculator";

export interface OrderLine {
  sku: string;
  quantity: number;
}

export interface Order {
  id: string;
  customerId: string;
  lines: OrderLine[];
  status: string;
  placedAt?: Date;
  total?: number;
  discount?: number;
}

// A classic overgrown "Service" that does everything: validation, pricing,
// inventory, discounting, persistence orchestration, and notification — all
// mutating the order in place. This is the thing to break apart.
export class OrderService {
  private inventory: InventoryChecker;
  private pricing: PricingCalculator;
  private orders: Order[] = [];

  constructor(inventory: InventoryChecker, pricing: PricingCalculator) {
    this.inventory = inventory;
    this.pricing = pricing;
  }

  placeOrder(order: Order, promoCode?: string): Order {
    // validate
    if (!order.customerId) {
      throw new Error("customer required");
    }
    if (!order.lines || order.lines.length === 0) {
      throw new Error("order must have lines");
    }
    for (const line of order.lines) {
      if (line.quantity <= 0) {
        throw new Error("quantity must be positive");
      }
      if (!this.inventory.isInStock(line.sku, line.quantity)) {
        throw new Error("out of stock: " + line.sku);
      }
    }

    // price
    let subtotal = this.pricing.subtotal(order);

    // discount
    let discount = 0;
    if (promoCode) {
      if (promoCode === "SAVE10") {
        discount = subtotal * 0.1;
      } else if (promoCode === "SAVE20") {
        discount = subtotal * 0.2;
      } else if (promoCode === "FREESHIP") {
        discount = 5;
      } else {
        throw new Error("invalid promo code");
      }
    }
    order.total = subtotal - discount;
    order.discount = discount;

    // reserve inventory (mutates)
    for (const line of order.lines) {
      this.inventory.reserve(line.sku, line.quantity);
    }

    // persist (mutates)
    order.status = "PLACED";
    order.placedAt = new Date();
    this.orders.push(order);

    return order;
  }

  getOrder(id: string): Order | null {
    for (const o of this.orders) {
      if (o.id === id) {
        return o;
      }
    }
    return null;
  }

  cancelOrder(id: string): void {
    const order = this.getOrder(id);
    if (!order) {
      throw new Error("not found");
    }
    order.status = "CANCELLED";
  }
}
