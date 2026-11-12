#!/bin/sh
# Record the real Microsoft Learn English page as the extension translates it.
# Requires Chromium CDP on 9223, the English tab and extension popup tab open,
# learn.microsoft.com host permission, the PLaMo Custom settings, and workspace 9.
set -eu
cd "$(dirname "$0")/../../.."

page='/en-us/dotnet/api/microsoft.bot.builder.formflow.commanddescription.help'
out=${1:-episodes/ep04/demo/mslearn-plamo-raw.mkv}
recorder_pid=
cleanup() {
  if [ -n "$recorder_pid" ]; then
    kill -INT "$recorder_pid" 2>/dev/null || true
    wait "$recorder_pid" 2>/dev/null || true
  fi
  hyprctl eval 'return hl.dispatch(hl.dsp.focus({ workspace = 1 }))' >/dev/null 2>&1 || true
}
trap cleanup EXIT INT TERM

node episodes/ep04/demo/browser-cdp.mjs eval "$page" 'location.reload()' >/dev/null
sleep 2
node episodes/ep04/demo/browser-cdp.mjs eval "$page" 'window.scrollTo(0, 220)' >/dev/null
node episodes/ep04/demo/browser-cdp.mjs eval "$page" 'document.head.insertAdjacentHTML("beforeend", "<style id=\"demo-status\">#llm-translator-status{top:230px!important;bottom:auto!important;right:26px!important;font-size:13px!important}</style>")' >/dev/null
node episodes/ep04/demo/browser-cdp.mjs activate "$page" >/dev/null
hyprctl eval 'return hl.dispatch(hl.dsp.focus({ workspace = 9 }))' >/dev/null
sleep 1
wtype -k Escape
sleep 1
wf-recorder -g '480,292 1600x900' -r 30 -D -c libx264 -p preset=ultrafast -p crf=18 -f "$out" -y >/tmp/mslearn-wf-recorder.log 2>&1 &
recorder_pid=$!
sleep 3

node episodes/ep04/demo/browser-cdp.mjs eval popup/popup.html '(async()=>{const [tab]=await chrome.tabs.query({url:"https://learn.microsoft.com/en-us/dotnet/api/microsoft.bot.builder.formflow.commanddescription.help*"});await chrome.scripting.executeScript({target:{tabId:tab.id},files:["/content.js"]});return chrome.tabs.sendMessage(tab.id,{type:"START_TRANSLATION",targetLanguage:"ja",sourceLanguage:"en",showGlow:false,maxConcurrentRequests:1})})()'
for count in $(seq 1 90); do
  status=$(node episodes/ep04/demo/browser-cdp.mjs eval popup/popup.html '(async()=>{const [tab]=await chrome.tabs.query({url:"https://learn.microsoft.com/en-us/dotnet/api/microsoft.bot.builder.formflow.commanddescription.help*"});return chrome.tabs.sendMessage(tab.id,{type:"GET_TRANSLATION_STATUS"})})()')
  if [ "$count" -gt 1 ] && ! printf '%s' "$status" | grep -q '"isTranslating": true'; then
    break
  fi
  sleep 1
done
sleep 3
node episodes/ep04/demo/browser-cdp.mjs eval "$page" 'document.querySelector(".summaryHolder p")?.textContent'
printf 'Recorded %s\n' "$out"
