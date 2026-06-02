import { chromium, devices } from 'playwright';

const url = process.argv[2] || 'https://ram-cosmos-dashboard.loca.lt/';
const browser = await chromium.launch({ headless: true });
const contexts = [
  { name: 'desktop', options: { viewport: { width: 1440, height: 1000 } } },
  { name: 'ipad', options: { ...devices['iPad Pro 11'], viewport: { width: 834, height: 1194 } } },
  { name: 'phone', options: { viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true } },
];
for (const cfg of contexts) {
  const context = await browser.newContext(cfg.options);
  const page = await context.newPage();
  const messages = [];
  page.on('console', msg => messages.push(`${msg.type()}: ${msg.text()}`));
  page.on('pageerror', err => messages.push(`pageerror: ${err.stack || err.message}`));
  const responses = [];
  page.on('response', res => {
    const u = res.url();
    if (u.includes('/data/live.json') || u.includes('/assets/') || u === url) responses.push(`${res.status()} ${u}`);
  });
  try {
    await page.goto(url, { waitUntil: 'networkidle', timeout: 45000 });
    await page.waitForTimeout(1500);
    const body = await page.locator('body').innerText({ timeout: 5000 }).catch(e => `INNER_TEXT_ERROR: ${e.message}`);
    const bootVisible = await page.locator('.boot').isVisible().catch(() => false);
    const shellVisible = await page.locator('.shell').isVisible().catch(() => false);
    const title = await page.title();
    await page.screenshot({ path: `/opt/data/Cosmos/dashboard/probe-${cfg.name}.png`, fullPage: true });
    console.log(JSON.stringify({ name: cfg.name, title, bootVisible, shellVisible, bodyStart: body.slice(0, 500), messages, responses }, null, 2));
  } catch (e) {
    console.log(JSON.stringify({ name: cfg.name, error: e.stack || e.message, messages, responses }, null, 2));
  }
  await context.close();
}
await browser.close();
