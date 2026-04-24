import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright-core';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const rootDir = path.resolve(__dirname, '..', '..');
const outputDir = path.join(rootDir, 'output', 'defense');
const baseUrl = process.env.BASE_URL || 'http://localhost:8080';

const accounts = {
  parent: { username: 'parent', password: '123456', route: '/parent', waitForText: '我的需求' },
  tutor: { username: 'tutor', password: '123456', route: '/tutor', waitForText: '认证资料' },
  admin: { username: 'admin', password: '123456', route: '/admin', waitForText: '审核工作台' }
};

const textRenderTasks = [
  { input: 'mysql-business-data.txt', output: 'mysql-business-data.png', title: 'MySQL 真实业务数据' },
  { input: 'mysql-schema-check.txt', output: 'mysql-schema-check.png', title: 'MySQL 表结构校验' },
  { input: 'backend-test.txt', output: 'backend-test.png', title: 'Spring Boot 后端测试结果' },
  { input: 'frontend-check.txt', output: 'frontend-check.png', title: 'Vue 前端检查结果' },
  { input: 'python-test.txt', output: 'python-test.png', title: 'Python 统计模块测试结果' }
];

async function login(username, password) {
  const response = await fetch(`${baseUrl}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(`登录失败 ${username}: ${response.status} ${detail}`);
  }

  return response.json();
}

function escapeHtml(value) {
  return value.replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;');
}

async function captureAppPage(browser, filename, route, waitForText, sessionUser = null) {
  const page = await browser.newPage({
    viewport: { width: 1440, height: 1600 },
    deviceScaleFactor: 1.25
  });

  if (sessionUser) {
    await page.goto(`${baseUrl}/login`, { waitUntil: 'domcontentloaded' });
    await page.evaluate((user) => {
      sessionStorage.setItem('tutor-platform-user', JSON.stringify(user));
    }, sessionUser);
  }

  await page.goto(`${baseUrl}${route}`, { waitUntil: 'networkidle' });
  await page.getByText(waitForText).first().waitFor({ state: 'visible', timeout: 15000 });
  await page.screenshot({
    path: path.join(outputDir, filename),
    fullPage: true
  });
  await page.close();
}

async function renderTextArtifact(browser, task) {
  const page = await browser.newPage({
    viewport: { width: 1440, height: 1800 },
    deviceScaleFactor: 1.25
  });
  const content = await fs.readFile(path.join(outputDir, task.input), 'utf8');
  const html = `<!doctype html>
  <html lang="zh-CN">
    <head>
      <meta charset="utf-8" />
      <title>${task.title}</title>
      <style>
        :root {
          color-scheme: light;
          --bg: #f5f7fb;
          --panel: #ffffff;
          --line: #d7dfeb;
          --text: #172033;
          --muted: #56627a;
          --accent: #0f5f9a;
        }
        * { box-sizing: border-box; }
        body {
          margin: 0;
          padding: 40px;
          background:
            radial-gradient(circle at top right, rgba(15, 95, 154, 0.12), transparent 32%),
            linear-gradient(180deg, #f7fbff 0%, var(--bg) 100%);
          font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
          color: var(--text);
        }
        .shell {
          max-width: 1280px;
          margin: 0 auto;
          background: var(--panel);
          border: 1px solid var(--line);
          border-radius: 24px;
          overflow: hidden;
          box-shadow: 0 18px 50px rgba(23, 32, 51, 0.10);
        }
        .head {
          padding: 28px 32px 18px;
          border-bottom: 1px solid var(--line);
          background: linear-gradient(135deg, #ffffff 0%, #eef5ff 100%);
        }
        .eyebrow {
          margin: 0 0 8px;
          color: var(--accent);
          font-size: 13px;
          letter-spacing: 0.12em;
          text-transform: uppercase;
        }
        h1 {
          margin: 0 0 8px;
          font-size: 30px;
        }
        p {
          margin: 0;
          color: var(--muted);
          font-size: 15px;
        }
        pre {
          margin: 0;
          padding: 28px 32px 36px;
          white-space: pre-wrap;
          word-break: break-word;
          font: 14px/1.55 Menlo, Monaco, Consolas, monospace;
        }
      </style>
    </head>
    <body>
      <section class="shell">
        <header class="head">
          <div class="eyebrow">Defense Artifact</div>
          <h1>${task.title}</h1>
          <p>由真实运行结果自动生成，可直接用于论文附录和答辩展示。</p>
        </header>
        <pre>${escapeHtml(content)}</pre>
      </section>
    </body>
  </html>`;

  await page.setContent(html, { waitUntil: 'domcontentloaded' });
  await page.screenshot({
    path: path.join(outputDir, task.output),
    fullPage: true
  });
  await page.close();
}

async function main() {
  await fs.mkdir(outputDir, { recursive: true });

  const browser = await chromium.launch({
    channel: 'chrome',
    headless: true
  });

  try {
    await captureAppPage(browser, 'page-login.png', '/login', '登录南华家教');

    const parentUser = await login(accounts.parent.username, accounts.parent.password);
    const tutorUser = await login(accounts.tutor.username, accounts.tutor.password);
    const adminUser = await login(accounts.admin.username, accounts.admin.password);

    await captureAppPage(browser, 'page-parent-dashboard.png', accounts.parent.route, accounts.parent.waitForText, parentUser);
    await captureAppPage(browser, 'page-tutor-dashboard.png', accounts.tutor.route, accounts.tutor.waitForText, tutorUser);
    await captureAppPage(browser, 'page-admin-dashboard.png', accounts.admin.route, accounts.admin.waitForText, adminUser);
    await captureAppPage(browser, 'page-demand-detail.png', '/demands/1', '需求详情', tutorUser);
    await captureAppPage(browser, 'page-tutor-detail.png', '/tutors/1', '简历摘要', adminUser);

    for (const task of textRenderTasks) {
      await renderTextArtifact(browser, task);
    }
  } finally {
    await browser.close();
  }
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
