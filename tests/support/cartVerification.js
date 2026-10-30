import { expect } from "@playwright/test";

// Shared assertions used by the two cart specs; no verification lives in POMs.
export async function checkCart(cart, quantity) {
  await expect(cart.cartRow).toHaveCount(1);
  await expect(cart.quantities).toHaveCount(1);
  await expect(cart.quantity).toHaveValue(String(quantity));
  const money = value => Number(value.replace(/[^\d.-]/g, ""));
  const price = money(await cart.priceCells.nth(0).innerText());
  const shipping = money(await cart.priceCells.nth(1).innerText());
  const total = money(await cart.rowTotal.innerText());
  expect(price).toBeGreaterThan(0);
  expect(total).toBeCloseTo(quantity * price + shipping, 2);
  expect(money(await cart.grandTotal.innerText())).toBeCloseTo(total, 2);
  return price;
}
