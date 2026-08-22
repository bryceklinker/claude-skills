import { test, expect } from "@playwright/test";

test("given an unassigned device, when it is dragged onto a room, then it appears in that room", async ({ page }) => {
  await page.goto("/rooms");

  const device = page.getByTestId("device-lamp");
  const kitchen = page.getByTestId("room-kitchen");

  await device.dragTo(kitchen);

  await expect(kitchen.getByTestId("device-lamp")).toBeVisible();
});
