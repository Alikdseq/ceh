import { expect, test } from "@playwright/test";

test.describe("Quote flow", () => {
  test("browse catalog → add to cart → submit quote → success", async ({ page }) => {
    await page.goto("/catalog/");
    await expect(page.locator("h1")).toBeVisible({ timeout: 15000 });

    const productLink = page.locator('a[href*="/catalog/"]').filter({ hasText: /контактор|КТ/i }).first();
    if (await productLink.count()) {
      await productLink.click();
    } else {
      await page.goto("/catalog/kontaktory-kt/kontaktor-kt-6043/");
    }

    const addBtn = page.getByRole("button", { name: /в заявку|добавить/i }).first();
    await addBtn.waitFor({ state: "visible", timeout: 15000 });
    await addBtn.click();

    await page.goto("/cart/");
    await expect(page.getByRole("heading", { name: /заявк|корзин/i })).toBeVisible({ timeout: 10000 });

    await page.getByLabel(/имя|контакт/i).first().fill("Тест E2E");
    await page.getByLabel(/компан/i).first().fill("ООО E2E");
    await page.getByLabel(/email/i).first().fill("e2e@test.ru");
    await page.getByLabel(/телефон/i).first().fill("+7 (999) 000-00-01");

    const city = page.getByLabel(/город/i);
    if (await city.count()) await city.fill("Москва");

    const privacy = page.getByRole("checkbox");
    if (await privacy.count()) await privacy.check();

    await page.getByRole("button", { name: /отправить|оформить/i }).click();

    await expect(page).toHaveURL(/\/order\/success/, { timeout: 20000 });
    await expect(page.getByRole("heading", { name: /принят|отправлен/i })).toBeVisible();
  });
});
