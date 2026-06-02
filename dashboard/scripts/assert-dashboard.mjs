import { chromium, devices } from 'playwright';
const url = process.argv[2];
const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ ...devices['iPad Pro 11'], viewport: { width: 834, height: 1194 } });
const messages = [];
page.on('console', msg => messages.push(`${msg.type()}: ${msg.text()}`));
page.on('pageerror', err => messages.push(`pageerror: ${err.message}`));
await page.goto(url, { waitUntil: 'networkidle', timeout: 45000 });
await page.waitForTimeout(1000);
const result = {
  title: await page.title(),
  shellVisible: await page.locator('.shell').isVisible(),
  bootVisible: await page.locator('.boot').isVisible().catch(() => false),
  missionCards: await page.locator('text=Mission Workflow Cards').count(),
  commandMode: await page.locator('text=iPad Command Mode').count(),
  captureCard: await page.locator('text=Capture').count(),
  copyButton: await page.locator('text=Copy command').count(),
  messages,
};
console.log(JSON.stringify(result, null, 2));
if (!result.shellVisible || result.bootVisible || result.missionCards < 1 || result.commandMode < 1 || result.messages.some(m => m.includes('pageerror'))) process.exit(1);
await browser.close();
