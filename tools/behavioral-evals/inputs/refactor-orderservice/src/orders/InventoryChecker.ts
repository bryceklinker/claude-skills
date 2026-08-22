import { Order } from "./OrderService";

// Owned, in-process, deterministic collaborator.
export class InventoryChecker {
  private stock: Record<string, number>;

  constructor(stock: Record<string, number>) {
    this.stock = stock;
  }

  isInStock(sku: string, quantity: number): boolean {
    const available = this.stock[sku] ?? 0;
    return available >= quantity;
  }

  reserve(sku: string, quantity: number): void {
    this.stock[sku] = (this.stock[sku] ?? 0) - quantity;
  }
}
