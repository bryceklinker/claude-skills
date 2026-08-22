import { OrderService, Order } from "./OrderService";

// NOTE: the existing tests mock the owned, in-process collaborators
// (InventoryChecker, PricingCalculator). This is the mockist habit — these
// doubles assert HOW OrderService calls its collaborators rather than WHAT it
// produces, and they break on any refactor.
describe("OrderService", () => {
  function makeOrder(): Order {
    return {
      id: "o1",
      customerId: "c1",
      lines: [{ sku: "A", quantity: 2 }],
      status: "NEW",
    };
  }

  it("places an order and computes the total", () => {
    const inventory: any = {
      isInStock: jest.fn().mockReturnValue(true),
      reserve: jest.fn(),
    };
    const pricing: any = {
      subtotal: jest.fn().mockReturnValue(100),
      lineTotal: jest.fn(),
    };

    const service = new OrderService(inventory, pricing);
    const result = service.placeOrder(makeOrder());

    expect(pricing.subtotal).toHaveBeenCalled();
    expect(inventory.reserve).toHaveBeenCalledWith("A", 2);
    expect(result.total).toBe(100);
    expect(result.status).toBe("PLACED");
  });

  it("applies SAVE10", () => {
    const inventory: any = {
      isInStock: jest.fn().mockReturnValue(true),
      reserve: jest.fn(),
    };
    const pricing: any = { subtotal: jest.fn().mockReturnValue(100), lineTotal: jest.fn() };

    const service = new OrderService(inventory, pricing);
    const result = service.placeOrder(makeOrder(), "SAVE10");

    expect(result.total).toBe(90);
  });
});
