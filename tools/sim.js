/* Load the REAL scheduler out of the built app and simulate a session. */
const fs = require("fs");
const path = require("path");
const html = fs.readFileSync(path.join(__dirname, "..", "index.html"), "utf8");
const js = html.match(/<script>([\s\S]*)<\/script>/)[1];

function span(a, b) {
  const i = js.indexOf(a), j = js.indexOf(b);
  if (i < 0 || j < 0) throw new Error("span not found: " + a);
  return js.slice(i, j);
}

const code =
  span("const MODULES", "/* ============ REFERENCE CARD") +
  span("/* ============ STATE ============ */", "/* ============ RENDER ============ */");

// The scheduler block is pure logic; nothing here touches the DOM.
// Only COLUMN-0 declarations become var, so the harness shares the module scope
// with the eval'd state (with let/const they land in eval's own scope and the
// per-run reset below silently does nothing).
eval(code.replace(/^(?:const|let) /gm, "var "));

console.log("questions:", BANK.length);
const byTier = {1: 0, 2: 0, 3: 0};
BANK.forEach(q => byTier[q.d]++);
console.log("tier sizes:", JSON.stringify(byTier), "(1 foundations / 2 procedure / 3 judgment)");

function run(acc, n, label) {
  stats = {}; tick = 0; streak = 0; best = 0; cur = null; filter = null; scope = "all";
  const lastSeen = {}, gaps = [];
  let capHits = {1: 0, 2: 0, 3: 0}, immediate = 0;

  for (let t = 0; t < n; t++) {
    capHits[targetTier()]++;
    const q = choose();
    if (!q) break;
    if (lastSeen[q.id] !== undefined) {
      const g = t - lastSeen[q.id];
      gaps.push(g);
      if (g <= 2) immediate++;
    }
    lastSeen[q.id] = t;
    cur = q;
    const a = st(q.id);
    a.seen++; tick++;
    if (Math.random() < acc) {
      a.box = Math.min(a.box + 1, BOXES);
      a.next = tick + SPACING[a.box];
      streak++; if (streak > best) best = streak;
    } else {
      a.box = 0; a.miss++; a.next = tick + MISS_GAP; streak = 0;
    }
  }
  const avg = gaps.length ? (gaps.reduce((x, y) => x + y, 0) / gaps.length) : 0;
  const min = gaps.length ? Math.min(...gaps) : 0;
  const distinct = Object.keys(lastSeen).length;
  console.log(
    `\n${label} (accuracy ${Math.round(acc * 100)}%, ${n} answers)` +
    `\n  distinct questions seen : ${distinct}/${BANK.length}` +
    `\n  repeat gap  avg/min     : ${avg.toFixed(1)} / ${min}` +
    `\n  repeats within 2 slots  : ${immediate}` +
    `\n  aiming at tier 1/2/3   : ${capHits[1]}/${capHits[2]}/${capHits[3]}` +
    `\n  best streak             : ${best}` +
    `\n  mastered                : ${BANK.filter(q => mastered(q.id)).length}`
  );
}

run(0.85, 120, "Strong run");
run(0.60, 120, "Shaky run");
run(1.00, 120, "Perfect run");
