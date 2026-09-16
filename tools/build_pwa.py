# -*- coding: utf-8 -*-
"""Transform the artifact page into a standalone, offline-capable PWA."""
import io, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

SRC = os.path.join(ROOT, "src", "quiz.html")
OUT = ROOT

s = io.open(SRC, encoding="utf-8").read()
errs = []

def rep(old, new, label):
    global s
    c = s.count(old)
    if c != 1:
        errs.append("%s -> found %d" % (label, c)); return
    s = s.replace(old, new, 1)

# ---------------------------------------------------------------- 1. boot: install hint + service worker
rep("""/* ============ GO ============ */
load();
render();""",
"""/* ============ GO ============ */
load();
render();

/* ---- install prompt: a real button on Android, instructions on iOS ---- */
(function(){
  const standalone = window.navigator.standalone === true ||
                     window.matchMedia("(display-mode: standalone)").matches;
  if (standalone) return;
  let dismissed = false;
  try { dismissed = localStorage.getItem("parto.a2hs") === "1"; } catch(e){}
  if (dismissed) return;

  let deferred = null, shown = false;

  function banner(html, installable){
    if (shown) return;
    shown = true;
    const el = document.createElement("div");
    el.className = "a2hs";
    el.innerHTML = '<p>' + html + '</p>' +
      (installable ? '<button id="a2hsGo">Install</button>' : '') +
      '<button id="a2hsX">' + (installable ? 'Not now' : 'Got it') + '</button>';
    document.body.appendChild(el);
    document.getElementById("a2hsX").onclick = () => {
      try { localStorage.setItem("parto.a2hs","1"); } catch(e){}
      el.remove();
    };
    const go = document.getElementById("a2hsGo");
    if (go) go.onclick = () => {
      el.remove();
      if (!deferred) return;
      deferred.prompt();
      deferred.userChoice.then(() => { deferred = null; });
    };
  }

  // Android / desktop Chrome: capture the event and offer our own button
  window.addEventListener("beforeinstallprompt", e => {
    e.preventDefault();
    deferred = e;
    banner("Install this so it works with no signal.", true);
  });

  // iOS has no such event: Safari can only be told what to tap
  if (/iPad|iPhone|iPod/.test(navigator.userAgent)) {
    banner("Install this: tap <b>Share</b> below, then <b>Add to Home Screen</b>. " +
           "It then works with no signal.", false);
  }

  window.addEventListener("appinstalled", () => {
    try { localStorage.setItem("parto.a2hs","1"); } catch(e){}
  });
})();

/* ---- offline cache ---- */
if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => navigator.serviceWorker.register("sw.js").catch(()=>{}));
}""", "boot")

# ---------------------------------------------------------------- 2. phone layout + install banner CSS
rep("""@media (max-width:560px){
  .rail{grid-template-columns:repeat(3,1fr)}
  .card{padding:18px 16px}
  .seg .nm{font-size:10px}
}""",
"""@media (max-width:560px){
  .rail{grid-template-columns:repeat(3,1fr)}
  .card{padding:18px 16px}
  .seg .nm{font-size:10px}
}

/* ---------- phone / installed app ---------- */
@media (max-width:430px){
  body{font-size:15.5px}
  .wrap{padding-inline:16px; padding-block:0 calc(92px + env(safe-area-inset-bottom))}
  header{padding-block:calc(14px + env(safe-area-inset-top)) 10px}
  h1{font-size:23px}
  .sub, .disclaim{display:none}
  .rail{margin-top:14px; gap:4px}
  .seg{padding:7px 6px 6px}
  .controls{margin-bottom:14px}
  .streak{margin-bottom:12px}
  .stkn{min-width:60px; padding:8px 10px}
  .stkv{font-size:18px}
  .tier{font-size:11.5px; margin:-4px 0 14px}
  .card{padding:16px 14px}
  .q{font-size:17.5px}
  .opt{padding:12px; min-height:50px; align-items:center}
  .why, .ev p{font-size:14px}
  .fab{right:14px; bottom:calc(14px + env(safe-area-inset-bottom))}
  .drawer{width:100%}
  .dbody{padding:16px; padding-bottom:calc(16px + env(safe-area-inset-bottom))}
  .dhead{padding:calc(12px + env(safe-area-inset-top)) 16px 12px}
  .hint{display:none}
}
.opt, .chip, .btn, .seg, .fab, .tbtn{-webkit-tap-highlight-color:transparent; touch-action:manipulation}
body{-webkit-text-size-adjust:100%; overscroll-behavior-y:contain}

.a2hs{
  position:fixed; left:12px; right:12px; bottom:calc(12px + env(safe-area-inset-bottom));
  z-index:70; display:flex; align-items:center; gap:12px;
  background:var(--ink); color:var(--paper); border-radius:4px; padding:12px 14px;
  box-shadow:0 8px 28px -8px rgba(0,0,0,.5);
}
.a2hs p{margin:0; font-size:13px; line-height:1.45; flex:1}
.a2hs b{font-weight:600}
.a2hs button{
  appearance:none; font:inherit; font-family:var(--f-disp); font-weight:700; font-size:11px;
  letter-spacing:.05em; text-transform:uppercase; white-space:nowrap;
  background:transparent; color:var(--paper); border:1px solid var(--paper);
  border-radius:3px; padding:7px 11px; cursor:pointer;
}
.a2hs button#a2hsGo{background:var(--paper); color:var(--ink)}
.a2hs button#a2hsX{border-color:transparent; opacity:.72}""", "phone css")

# ---------------------------------------------------------------- 3. disclaimer into the drawer (hidden on phone)
rep(""" {h:"Call 112 \u2014 do not drive",""",
""" {h:"Before you trust any of this",
  i:["General protocol for the Catalan / Spanish public system, with the independent evidence noted on each answer. <b>Your midwife and your hospital's own instructions override every line here.</b>",
     "Confirm the contraction threshold, the hospital's direct phone number and the GBS result at the next visit, and write theirs down.",
     "Progress is stored on this device only. It is not uploaded anywhere."]},
 {h:"Call 112 \u2014 do not drive",""", "drawer disclaimer")

if errs:
    sys.stderr.write("FAILED:\n" + "\n".join(errs) + "\n"); sys.exit(1)

if "claude.use" in s:
    sys.stderr.write("FAILED: claude.use still referenced\n"); sys.exit(1)

# ---------------------------------------------------------------- 4. wrap as a real HTML document
HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="color-scheme" content="light dark">
<meta name="description" content="Decision drill for the birth partner: from the first contraction to the weeks at home.">

<link rel="manifest" href="manifest.webmanifest">
<meta name="theme-color" content="#FCF5F3" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#141010" media="(prefers-color-scheme: dark)">

<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="Sala de Parts">
<link rel="apple-touch-icon" href="icon-180.png">
<link rel="icon" href="icon-192.png" type="image/png">

<style>
  html{background:#FCF5F3}
  @media (prefers-color-scheme:dark){ html{background:#141010} }
  body{margin:0; font:14px system-ui, sans-serif}
  img{max-width:100%}
  [hidden]{display:none !important}
</style>
"""

marker = "\n<div class=\"wrap\">"
i = s.index(marker)
head_part, body_part = s[:i], s[i:]

doc = HEAD + head_part + "\n</head>\n<body>\n" + body_part + "\n</body>\n</html>\n"

io.open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(doc)
print("index.html written: %d chars" % len(doc))
