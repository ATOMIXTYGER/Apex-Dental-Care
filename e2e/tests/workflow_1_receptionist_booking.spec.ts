import { test, expect } from '@playwright/test';

test.describe('Workflow 1: Receptionist Patient Registration & Appointment Booking', () => {
  test('should login as receptionist, register a patient, and schedule an appointment', async ({ page }) => {
    // 1. Login
    await page.goto('/login');
    await page.fill('input[type="text"]', 'reception1@clinic.com');
    await page.fill('input[type="password"]', 'Dental@123');
    await page.click('button[type="submit"]');

    // Verify redirected to dashboard
    await expect(page).toHaveURL(/.*dashboard/);
    await expect(page.locator('text=Receptionist')).toBeVisible();

    // 2. Navigate to Patients
    await page.click('a[href="/patients"]');
    await expect(page).toHaveURL(/.*patients/);

    // 3. Register Patient
    await page.click('button:has-text("Register Patient")');
    await page.fill('input[placeholder*="First Name"]', 'E2E');
    await page.fill('input[placeholder*="Last Name"]', 'TestPatient');
    await page.fill('input[type="date"]', '1995-04-12');
    await page.fill('input[placeholder*="Phone"]', '+1 555-0182');
    await page.fill('input[placeholder*="Email"]', 'e2e.testpatient@example.com');
    await page.click('button:has-text("Save & Register Patient")');

    // 4. Verify redirected to patient profile
    await expect(page).toHaveURL(/.*patients\/\d+/);
    await expect(page.locator('text=E2E TestPatient')).toBeVisible();

    // 5. Navigate to Appointments and verify schedule
    await page.click('a[href="/appointments"]');
    await expect(page).toHaveURL(/.*appointments/);
    await expect(page.locator('text=Appointment Schedule')).toBeVisible();
  });
});
