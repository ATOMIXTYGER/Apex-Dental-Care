import { test, expect } from '@playwright/test';

test.describe('Workflow 4: Administrator Audit Logs & Staff Management', () => {
  test('should login as admin, inspect audit trail, and manage clinic staff', async ({ page }) => {
    // 1. Login as Admin
    await page.goto('/login');
    await page.fill('input[type="text"]', 'admin@clinic.com');
    await page.fill('input[type="password"]', 'Dental@123');
    await page.click('button[type="submit"]');

    await expect(page).toHaveURL(/.*dashboard/);
    await expect(page.locator('text=Admin')).toBeVisible();

    // 2. Navigate to Audit Logs
    await page.click('a[href="/audit-logs"]');
    await expect(page).toHaveURL(/.*audit-logs/);
    await expect(page.locator('text=System Audit & Compliance Log')).toBeVisible();
    await expect(page.locator('text=HIPAA Compliant')).toBeVisible();

    // 3. Navigate to Staff & Users
    await page.click('a[href="/users"]');
    await expect(page).toHaveURL(/.*users/);
    await expect(page.locator('text=Staff & User Management')).toBeVisible();
    await expect(page.locator('button:has-text("Add Staff Member")')).toBeVisible();
  });
});
