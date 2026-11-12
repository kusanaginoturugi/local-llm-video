// Chromium CDP から記事タブを直接録画する。デスクトップの前面ウィンドウに依存しない。
import { spawn } from 'node:child_process';

const output = process.argv[2] ?? '/tmp/ep04-12b-tab.mkv';
const step = Number(process.argv[3] ?? 12);
const delay = Number(process.argv[4] ?? 8000);
const targets = await (await fetch('http://127.0.0.1:9223/json')).json();

async function connect(fragment) {
  const target = targets.find(t => t.url.includes(fragment));
  if (!target) throw new Error(`Missing tab: ${fragment}`);
  const ws = new WebSocket(target.webSocketDebuggerUrl);
  await new Promise((ok, bad) => {
    ws.addEventListener('open', ok, { once: true });
    ws.addEventListener('error', bad, { once: true });
  });
  let next = 0;
  const pending = new Map();
  ws.addEventListener('message', ev => {
    const msg = JSON.parse(ev.data);
    const item = pending.get(msg.id);
    if (!item) return;
    pending.delete(msg.id);
    if (msg.error || msg.result?.exceptionDetails) item.bad(new Error(JSON.stringify(msg)));
    else item.ok(msg.result);
  });
  return {
    send(method, params = {}) {
      const id = ++next;
      const result = new Promise((ok, bad) => pending.set(id, { ok, bad }));
      ws.send(JSON.stringify({ id, method, params }));
      return result;
    },
    close() { ws.close(); },
  };
}

const page = await connect('browser-article.html');
const popup = await connect('popup/popup.html');
const evaluate = async (target, expression) => (await target.send('Runtime.evaluate', {
  expression, awaitPromise: true, returnByValue: true,
})).result?.value;
const statusCode = '(async()=>{const [tab]=await chrome.tabs.query({url:"http://127.0.0.1:8766/*"});return chrome.tabs.sendMessage(tab.id,{type:"GET_TRANSLATION_STATUS"})})()';
const startCode = '(async()=>{const [tab]=await chrome.tabs.query({url:"http://127.0.0.1:8766/*"});await chrome.scripting.executeScript({target:{tabId:tab.id},files:["/content.js"]});await chrome.tabs.sendMessage(tab.id,{type:"PING"});return chrome.tabs.sendMessage(tab.id,{type:"START_TRANSLATION",targetLanguage:"ja",sourceLanguage:"en",showGlow:true,maxConcurrentRequests:1})})()';

const { settings } = await evaluate(popup, 'new Promise(ok=>chrome.storage.local.get("settings",ok))');
if (settings.cacheMode !== 'off') throw new Error('Translation cache must be off');
await page.send('Emulation.setDeviceMetricsOverride', {
  width: 1600, height: 900, deviceScaleFactor: 1, mobile: false,
});
await evaluate(page, 'location.reload()');
await new Promise(ok => setTimeout(ok, 1200));
await evaluate(page, 'document.documentElement.style.overflowAnchor="none";document.body.style.overflowAnchor="none";window.scrollTo(0,0)');
await page.send('Page.bringToFront');

const ff = spawn('ffmpeg', ['-loglevel', 'error', '-y', '-f', 'image2pipe', '-framerate', '10',
  '-c:v', 'mjpeg', '-i', '-', '-vf', 'pad=ceil(iw/2)*2:ceil(ih/2)*2',
  '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '18', output],
  { stdio: ['pipe', 'inherit', 'inherit'] });
const started = Date.now();
let translated = false;
let completed = 0;
let lastPoll = 0;
let frames = 0;
let scrolled = false;
while (Date.now() - started < 120000) {
  const elapsed = Date.now() - started;
  if (!translated && elapsed >= 2000) {
    console.log('translation', JSON.stringify(await evaluate(popup, startCode)));
    translated = true;
  }
  if (!scrolled && elapsed >= delay) {
    await evaluate(page, `window.__demoScroll=setInterval(()=>{window.scrollBy(0,${step});if(window.scrollY+innerHeight>=document.documentElement.scrollHeight)clearInterval(window.__demoScroll)},100)`);
    scrolled = true;
  }
  if (translated && elapsed - lastPoll >= 1000) {
    const status = await evaluate(popup, statusCode);
    lastPoll = elapsed;
    if (!status?.isTranslating && elapsed > 4000 && !completed) completed = Date.now();
  }
  const shot = await page.send('Page.captureScreenshot', { format: 'jpeg', quality: 85 });
  if (!ff.stdin.write(Buffer.from(shot.data, 'base64'))) {
    await new Promise(ok => ff.stdin.once('drain', ok));
  }
  frames++;
  if (completed && Date.now() - completed >= 4000) break;
  await new Promise(ok => setTimeout(ok, Math.max(0, started + frames * 100 - Date.now())));
}
ff.stdin.end();
await new Promise(ok => ff.on('exit', ok));
console.log(`recorded ${output}, ${frames} frames`);
page.close();
popup.close();
