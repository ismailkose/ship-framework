// Ship's gibberish test, for web pages: every letter and digit on the page becomes a random one of the
// same kind; spaces, punctuation, layout, type, colour and images stay. Nobody can read it, so only the
// style and visuals can say what the product is. Run it in the page (a browser tool's JavaScript, a
// Playwright page.evaluate, or the console), screenshot, then ask someone who wasn't told the product:
// "What does this sell, and who is it for?"
//
//   shipGibberish()            → garbles document.body, returns how many text pieces changed
//   shipGibberish(root, seed)  → a part of the page, with a fixed seed (same seed, same gibberish)
//
// Native apps and any screenshot: python3 .claude/skills/ship/design/bin/gibberish.py <screenshot.png>

function shipGibberishText(text, rnd) {
  const lower = "abcdefghijklmnopqrstuvwxyz";
  return text
    .replace(/[a-zà-ÿ]/g, () => lower[Math.floor(rnd() * 26)])
    .replace(/[A-ZÀ-Þ]/g, () => lower[Math.floor(rnd() * 26)].toUpperCase())
    .replace(/[0-9]/g, () => String(Math.floor(rnd() * 10)));
}

function shipGibberish(root, seed) {
  root = root || document.body;
  let state = seed || 7;
  const rnd = () => (state = (state * 16807) % 2147483647) / 2147483647;
  let changed = 0;
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
    acceptNode: (node) => node.parentElement && node.parentElement.closest("script, style, noscript")
      ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT,
  });
  for (let node = walker.nextNode(); node; node = walker.nextNode()) {
    if (node.nodeValue.trim()) { node.nodeValue = shipGibberishText(node.nodeValue, rnd); changed++; }
  }
  root.querySelectorAll("[placeholder]").forEach((el) => { el.placeholder = shipGibberishText(el.placeholder, rnd); });
  root.querySelectorAll("input[type=submit], input[type=button]").forEach((el) => { el.value = shipGibberishText(el.value, rnd); });
  root.querySelectorAll("option").forEach((el) => { el.text = shipGibberishText(el.text, rnd); });
  if (root === document.body) document.title = shipGibberishText(document.title, rnd);
  return changed;
}

if (typeof module !== "undefined") module.exports = { shipGibberishText };
else if (typeof window !== "undefined") window.shipGibberish = shipGibberish;
