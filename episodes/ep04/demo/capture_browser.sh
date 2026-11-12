#!/bin/sh
# Record the real Chromium window while the unpacked extension translates a page.
set -eu
cd "$(dirname "$0")/../../.."

out=${1:-episodes/ep04/demo/browser-translation-raw.mkv}
scroll_step=${2:-8}
scroll_delay=${3:-1000}
recorder_pid=
cleanup() {
  if [ -n "$recorder_pid" ]; then
    kill -INT "$recorder_pid" 2>/dev/null || true
    wait "$recorder_pid" 2>/dev/null || true
  fi
  hyprctl eval 'return hl.dispatch(hl.dsp.focus({ workspace = 1 }))' >/dev/null 2>&1 || true
}
trap cleanup EXIT INT TERM

node episodes/ep04/demo/browser-cdp.mjs eval browser-article.html 'location.reload()' >/dev/null
sleep 1
node episodes/ep04/demo/browser-cdp.mjs eval browser-article.html 'window.scrollTo(0, 0)' >/dev/null
node episodes/ep04/demo/browser-cdp.mjs activate browser-article.html >/dev/null
hyprctl eval 'return hl.dispatch(hl.dsp.focus({ workspace = 9 }))' >/dev/null
sleep 1
wf-recorder -g '480,292 1600x900' -r 30 -D -c libx264 -p preset=ultrafast -p crf=18 -f "$out" -y >/tmp/plamo-wf-recorder.log 2>&1 &
recorder_pid=$!
sleep 2

node episodes/ep04/demo/browser-cdp.mjs eval browser-article.html "setTimeout(()=>{window.__demoScroll=setInterval(()=>{window.scrollBy(0,$scroll_step);if(window.scrollY+innerHeight>=document.documentElement.scrollHeight)clearInterval(window.__demoScroll)},100)},$scroll_delay)" >/dev/null
node episodes/ep04/demo/browser-cdp.mjs eval popup/popup.html '(async()=>{const [tab]=await chrome.tabs.query({url:"http://127.0.0.1:8766/*"});await chrome.scripting.executeScript({target:{tabId:tab.id},files:["/content.js"]});await chrome.tabs.sendMessage(tab.id,{type:"PING"});return chrome.tabs.sendMessage(tab.id,{type:"START_TRANSLATION",targetLanguage:"ja",sourceLanguage:"en",showGlow:true,maxConcurrentRequests:1})})()'
sleep 1
for count in $(seq 1 90); do
  status=$(node episodes/ep04/demo/browser-cdp.mjs eval popup/popup.html '(async()=>{const [tab]=await chrome.tabs.query({url:"http://127.0.0.1:8766/*"});return chrome.tabs.sendMessage(tab.id,{type:"GET_TRANSLATION_STATUS"})})()')
  if [ "$count" -gt 1 ] && ! printf '%s' "$status" | grep -q '"isTranslating": true'; then
    break
  fi
  sleep 2
done
sleep 4
node episodes/ep04/demo/browser-cdp.mjs eval browser-article.html 'document.querySelector("h1").textContent'
printf 'Recorded %s\n' "$out"
