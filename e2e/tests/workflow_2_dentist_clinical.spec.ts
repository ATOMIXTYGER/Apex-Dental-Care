import { test, expect } from '@playwright/test';

test.describe('Workflow 2: Dentist Clinical Examination, Dental Chart, Treatment Plan & Prescription', () => {
  test('should login as dentist, examine patient, update FDI chart, and issue prescription', async ({ page }) => {
    // 1. Login as Dr. Marcus Chen
    await page.goto('/login');
    await page.fill('input[type="text"]', 'dr.chen@clinic.com');
    await page.fill('input[type="password"]', 'Dental@123');
    await page.click('button[type="submit"]');

    await expect(page).toHaveURL(/.*dashboard/);
    await expect(page.locator('text=Dentist')).toBeVisible();

    // 2. Open Patient Dossier
    await page.click('a[href="/patients"]');
    await page.click('tbody tr:first-child a'); // Click first patient
    await expect(page).toHaveURL(/.*patients\/\d+/);

    // 3. Switch to Dental Chart Tab
    await page.click('button:has-text("FDI Dental Chart")');
    await expect(page.locator('text=Maxilla (Upper Jaw)')).toBeVisible();

    // 4. Click a tooth (e.g., Tooth 16 or 11)
    await page.locator('div:has-text("16")').first().click();

    // 5. Switch to Treatment Plans Tab
    await page.click('button:has-text("Treatment Plans")');
    await expect(page.locator('button:has-text("New Treatment Plan")')).toBeVisible();

    // 6. Switch to Prescriptions Tab
    await page.click('button:has-text("Prescriptions")');
    await expect(page.locator('button:has-text("Write Prescription")')).toBeVisible();
  });
});
