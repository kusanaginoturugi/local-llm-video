// Short-lived CDP helper for capturing the real extension demo.
// Usage: node browser-cdp.mjs targets | eval <url-fragment> <expression>
const [, , action, fragment, expression] = process.argv;
const targets = await (await fetch('http://127.0.0.1:9223/json')).json();

if (action === 'targets') {
  for (const target of targets) console.log(`${target.type}\t${target.url}`);
  process.exit(0);
}

const target = targets.find(item => item.url.includes(fragment));
if (!target) throw new Error(`No CDP target includes ${fragment}`);
const ws = new WebSocket(target.webSocketDebuggerUrl);
await new Promise((resolve, reject) => {
  ws.addEventListener('open', resolve, { once: true });
  ws.addEventListener('error', reject, { once: true });
});

const command = { id: 1, method: 'Runtime.evaluate', params: {
    expression, awaitPromise: true, returnByValue: true, userGesture: true
} };
if (action === 'activate') {
  command.method = 'Page.bringToFront';
  command.params = {};
}
const reply = new Promise((resolve, reject) => {
  ws.addEventListener('message', event => {
    const message = JSON.parse(event.data);
    if (message.id !== 1) return;
    if (message.error || message.result?.exceptionDetails) reject(new Error(JSON.stringify(message)));
    else resolve(message.result.result?.value);
  });
});
ws.send(JSON.stringify(command));
console.log(JSON.stringify(await reply, null, 2));
ws.close();
