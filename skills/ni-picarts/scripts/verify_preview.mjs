import fs from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';

const options = {};
for (let i = 2; i < process.argv.length; i += 2) {
  const key = process.argv[i];
  if (!['--url', '--output', '--module', '--browser'].includes(key) || !process.argv[i + 1]) {
    throw Error('Usage: --url <preview-url> --output <qa-dir> [--module <playwright-module>] [--browser <executable>]');
  }
  options[key.slice(2)] = process.argv[i + 1];
}
assert(options.url && options.output, '--url and --output are required');
const require = createRequire(path.join(process.cwd(), 'picarts-verify.cjs'));
const {chromium} = require(options.module || 'playwright');
const browser = await chromium.launch({headless: true, ...(options.browser ? {executablePath: options.browser} : {})});
await fs.mkdir(options.output, {recursive: true});
const report = {viewports: [], visualReview: 'not-assessed', touchMethod: 'Chromium emulation'};

try {
  for (const viewport of [{width: 1440, height: 1000}, {width: 390, height: 844}]) {
    const mobile = viewport.width < 600;
    const context = await browser.newContext({viewport, hasTouch: mobile, isMobile: mobile, deviceScaleFactor: 1});
    const page = await context.newPage();
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    page.on('console', message => { if (message.type() === 'error') errors.push(message.text()); });
    page.on('response', response => { if (response.status() >= 400) errors.push(`${response.status()} ${response.url()}`); });
    await page.goto(options.url);
    await page.waitForFunction(() => !!window.picarts, null, {timeout: 20000});
    assert(await page.evaluate(() => window.picarts.ready), await page.evaluate(() => window.picarts.error));
    await page.waitForFunction(() => window.picarts.relief.introProgress >= 1.5, null, {timeout: 10000});
    await page.locator('#art').scrollIntoViewIfNeeded();
    await page.mouse.move(1, 1);

    const config = await page.evaluate(() => {
      const {relief, maps, clip} = window.picarts;
      const canvas = relief.canvas;
      const matte = document.createElement('canvas');
      matte.width = canvas.width; matte.height = canvas.height;
      const context = matte.getContext('2d');
      context.drawImage(clip, 0, 0, matte.width, matte.height);
      window._picartsMatte = context.getImageData(0, 0, matte.width, matte.height).data;
      window._picartsBefore = canvas.getContext('2d').getImageData(0, 0, canvas.width, canvas.height).data;
      const box = canvas.getBoundingClientRect();
      return {
        duration: relief.config.introDuration, metallic: relief.config.metallic,
        shrink: relief.config.smudgeShrinkSpeed, brush: relief.config.smudgeBrushSize,
        expectedBrush: maps.brush, ratioError: Math.abs(box.width / box.height - maps.width / maps.height),
        overflow: document.documentElement.scrollWidth > innerWidth,
        texturesReady: ['base', 'normal', 'mask', 'cloud'].every(key => !!relief.textures[key]),
      };
    });
    const canvas = page.locator('#relief');
    const box = await canvas.boundingBox();
    const cdp = mobile ? await context.newCDPSession(page) : null;
    const y = box.y + box.height * 0.47;
    if (mobile) await cdp.send('Input.dispatchTouchEvent', {type: 'touchStart', touchPoints: [{x: box.x + box.width * 0.1, y}]});
    else { await page.mouse.move(box.x + box.width * 0.1, y); await page.mouse.down(); }
    for (let i = 0; i < 32; i++) {
      const x = box.x + box.width * (0.1 + 0.8 * i / 31);
      if (mobile) await cdp.send('Input.dispatchTouchEvent', {type: 'touchMove', touchPoints: [{x, y}]});
      else await page.mouse.move(x, y);
      await page.waitForTimeout(16);
    }
    await page.waitForTimeout(300);
    const pixels = await page.evaluate(() => {
      const after = window.picarts.relief.canvas.getContext('2d').getImageData(0, 0,
        window.picarts.relief.canvas.width, window.picarts.relief.canvas.height).data;
      const expected = window.picarts.maps.background.match(/[a-f\d]{2}/gi).map(value => parseInt(value, 16));
      let foreground = 0, changed = 0, background = 0, backgroundMaxDelta = 0, backgroundColorMaxError = 0;
      for (let i = 0; i < after.length; i += 4) {
        const delta = Math.max(...[0, 1, 2].map(c => Math.abs(after[i + c] - window._picartsBefore[i + c])));
        if (window._picartsMatte[i + 3] > 220) { foreground++; if (delta > 4) changed++; }
        if (window._picartsMatte[i + 3] === 0) {
          background++;
          backgroundMaxDelta = Math.max(backgroundMaxDelta, delta);
          backgroundColorMaxError = Math.max(backgroundColorMaxError, ...expected.map((value, c) => Math.abs(value - after[i + c])));
        }
      }
      return {foregroundSamples: foreground, backgroundSamples: background, foregroundChanged: changed / foreground,
        backgroundMaxDelta, backgroundColorMaxError};
    });
    await canvas.screenshot({path: path.join(options.output, `${viewport.width}-wipe.png`)});
    let hold = null;
    if (!mobile) {
      await page.waitForTimeout(500);
      await page.evaluate(() => {
        const canvas = window.picarts.relief.canvas;
        window._picartsHeld = canvas.getContext('2d').getImageData(0, 0, canvas.width, canvas.height).data;
      });
      await page.waitForTimeout(700);
      hold = await page.evaluate(() => {
        const canvas = window.picarts.relief.canvas;
        const after = canvas.getContext('2d').getImageData(0, 0, canvas.width, canvas.height).data;
        let changed = 0;
        for (let i = 0; i < after.length; i += 4) {
          if ([0, 1, 2].some(c => Math.abs(after[i + c] - window._picartsHeld[i + c]) > 3)) changed++;
        }
        return {holding: window.picarts.relief.isMouseDown, changed: changed / (after.length / 4)};
      });
    }
    if (mobile) { await cdp.send('Input.dispatchTouchEvent', {type: 'touchEnd', touchPoints: []}); await cdp.detach(); }
    else { await page.mouse.up(); await page.mouse.move(1, 1); }
    await page.waitForFunction(() => window.picarts.relief.smudgeBufferEmpty, null, {timeout: 15000});
    const dissolve = await page.evaluate(() => {
      const canvas = window.picarts.relief.canvas;
      const after = canvas.getContext('2d').getImageData(0, 0, canvas.width, canvas.height).data;
      let foreground = 0, changed = 0;
      for (let i = 0; i < after.length; i += 4) if (window._picartsMatte[i + 3] > 220) {
        foreground++;
        if ([0, 1, 2].some(c => Math.abs(after[i + c] - window._picartsBefore[i + c]) > 4)) changed++;
      }
      return {cleared: window.picarts.relief.smudgeBufferEmpty, remainingChange: changed / foreground};
    });
    const lightModes = [];
    for (const mode of ['left', 'center', 'right']) {
      await page.evaluate(mode => window.picarts.setMode(mode), mode);
      await page.waitForTimeout(150);
      const sample = await page.evaluate(() => {
        const canvas = window.picarts.relief.canvas;
        const after = canvas.getContext('2d').getImageData(0, 0, canvas.width, canvas.height).data;
        const expected = window.picarts.maps.background.match(/[a-f\d]{2}/gi).map(value => parseInt(value, 16));
        let backgroundMaxError = 0, foreground = 0, lightChanged = 0;
        for (let i = 0; i < after.length; i += 4) if (window._picartsMatte[i + 3] === 0) {
          backgroundMaxError = Math.max(backgroundMaxError, ...expected.map((value, c) => Math.abs(value - after[i + c])));
        } else if (window._picartsMatte[i + 3] > 220) {
          foreground++;
          if (window._picartsLightPrevious && [0, 1, 2].some(c => Math.abs(after[i + c] - window._picartsLightPrevious[i + c]) > 4)) lightChanged++;
        }
        const changedFromPrevious = window._picartsLightPrevious ? lightChanged / foreground : null;
        window._picartsLightPrevious = after;
        return {backgroundMaxError, changedFromPrevious};
      });
      lightModes.push({mode, ...sample});
      await canvas.screenshot({path: path.join(options.output, `${viewport.width}-${mode}.png`)});
    }
    const pass = errors.length === 0 && config.texturesReady && !config.overflow && config.ratioError < 0.02
      && config.duration === 4.7 && config.metallic === 0.85 && config.shrink === 0.58 && config.brush === config.expectedBrush
      && pixels.foregroundSamples > 0 && pixels.backgroundSamples > 0 && pixels.foregroundChanged > 0.005
      && pixels.backgroundMaxDelta === 0 && pixels.backgroundColorMaxError === 0
      && (!hold || (hold.holding && hold.changed < 0.005)) && dissolve.cleared && dissolve.remainingChange < 0.005
      && lightModes.every(sample => sample.backgroundMaxError === 0)
      && lightModes.slice(1).every(sample => sample.changedFromPrevious > 0.005);
    report.viewports.push({viewport, mobile, config, pixels, hold, dissolve, lightModes, errors, pass});
    await context.close();
  }
  report.pass = report.viewports.every(viewport => viewport.pass);
  console.log(JSON.stringify({pass: report.pass, viewports: report.viewports.map(v => ({width: v.viewport.width,
    pass: v.pass, backgroundMaxDelta: v.pixels.backgroundMaxDelta})), visualReview: report.visualReview}));
  if (!report.pass) process.exitCode = 1;
} catch (error) {
  report.pass = false;
  report.error = error.message;
  throw error;
} finally {
  await fs.writeFile(path.join(options.output, 'acceptance.json'), JSON.stringify(report, null, 2));
  await browser.close();
}
