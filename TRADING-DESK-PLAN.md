# Trading Desk — Framework Plan

> A room of brains for crypto trading. Built on the same architecture as Ship Framework but adapted for a completely different domain. Claude Code framework first (Option C), then web UI later.

**Status:** Planning complete. Ready to build.
**Deadline:** 1-day hackathon sprint
**Builder:** Ismael Kose
**Based on:** Ship Framework (github.com/ismailkose/ship-framework)

---

## Core Concept

Not an assistant. Not a chatbot. A room of expert brains that think together, argue with each other, and meet you where you are — without you ever telling them your level.

The framework observes your actual trading behavior through OKX MCP and silently adjusts which brains speak loudest, how much detail they give, and what they focus on. A hodler gets a calm board of advisors. An active trader gets a lively trading desk. An advanced operator gets a full war room. No labels. No modes. No switches. Just the room reading you and adapting.

---

## Key Design Decisions

### 1. No explicit levels — silent behavioral adaptation

The framework NEVER asks "are you a beginner?" or forces you to pick a level. Instead it observes via OKX MCP:

- **Trade frequency** — 2 trades/month vs 3 trades/week
- **Hold duration** — months vs days vs hours
- **Position sizing patterns** — equal DCA vs variable entries
- **Asset diversity** — 2 coins vs 10 coins vs perps + DeFi
- **Order types used** — market buys vs limits with stops
- **Portfolio concentration** — 90% one coin vs diversified

These signals create a behavioral weight that shifts each brain's volume up or down on a gradient. No hard switches.

### 2. Brains argue — disagreement is the product

This isn't agents that execute tasks. These are opinionated experts who see the same situation differently. Scout might love a setup. Shield says the portfolio can't take it. Sage asks if there's even a thesis. Mirror notices you're acting out of character. The disagreement IS the value. You hear all sides, then you decide.

### 3. Proactive + Reactive

The room works both ways:
- **Proactive:** monitors your portfolio, surfaces alerts, delivers briefings on schedule
- **Reactive:** you bring a question or trade idea, the room discusses it

### 4. OKX MCP is the data layer

OKX MCP is already set up and working. The framework can read:
- Real portfolio balances and allocations
- Trade history and patterns
- Open orders
- Real-time prices

This means the room always has context before you even start talking.

---

## The 5 Core Brains (+2 that scale up)

Each brain has a "volume dial" that gets louder or quieter based on observed behavior. No brain is ever fully off — they just speak up when their expertise is relevant.

### Always Active

| Brain | Role | Low volume (hodler) | High volume (active trader) |
|---|---|---|---|
| **Sage** | Conviction & thesis | "Is this a good asset to hold for 2+ years?" | "What's the macro-structural case for this position?" |
| **Scout** | Data & technicals | "BTC is near a historically good accumulation zone" | "Here's the setup: entry, stop, target, confluence score" |
| **Shield** | Risk & allocation | "You're 70% in one coin, diversify" | "Correlation matrix shows 0.85 between these. Liquidation at -34%" |
| **Mirror** | Psychology & behavior | "You're panic selling at the bottom again" | "3rd trade in an hour after a loss — that's revenge trading" |
| **Ledger** | Records & patterns | Monthly portfolio snapshot, cost basis | Per-trade journal, win rate, expectancy, R-multiples |

### Scale Up With Behavior

| Brain | Activates when | Role |
|---|---|---|
| **Chain** | User shows on-chain interest or trades DeFi tokens | Wallet flows, exchange flows, funding rates, smart money tracking |
| **Exec** | User starts timing entries, using limits | Order types, entry plans, DCA strategies, slippage management |

### How Volume Shifts Look

```
Mostly holds, buys monthly, 3 assets, no stops:

  Sage     ████████░░  (loud — conviction matters most)
  Shield   ███████░░░  (loud — allocation is main risk)
  Mirror   ██████░░░░  (medium — catches panic selling)
  Scout    ███░░░░░░░  (quiet — simple zones only)
  Ledger   ████░░░░░░  (medium — monthly snapshots)
  Chain    ██░░░░░░░░  (quiet — basic signals)
  Exec     ░░░░░░░░░░  (silent — just market buys)

Starts timing entries, using limits, trading more:

  Sage     ███████░░░  (still strong)
  Shield   ████████░░  (louder — more trades = more risk)
  Mirror   ███████░░░  (louder — more decisions = more emotion)
  Scout    ██████░░░░  (turns up — they want setups)
  Ledger   ███████░░░  (turns up — per-trade tracking)
  Chain    ████░░░░░░  (contributing)
  Exec     ████░░░░░░  (contributing)
```

### Brain Personalities (detailed)

**Sage — The Conviction Brain**
Won't let you enter a trade without a clear "why." Asks about catalysts, invalidation criteria, time horizon. Kills trades that are "just a feeling." For hodlers, Sage is the one saying "BTC is a 10-year hold because X, Y, Z — does that thesis still hold?" For traders, Sage forces thesis discipline before every entry.

**Scout — The Data Brain**
Charts, indicators, market structure, on-chain metrics (when Chain is quiet). Scales from "historically good zone to accumulate" for hodlers to full technical breakdowns with entries, stops, targets, and confluence scores for active traders. Never gives a setup without context on what invalidates it.

**Shield — The Risk Brain (has veto power)**
The most important brain in the room. Tracks portfolio heat, concentration, correlation, max drawdown. Can BLOCK a trade if it violates the trader's own rules. Shield is the one who says "I know you want to buy more SOL but you're already 40% in correlated alts." Shield gets LOUDER as activity increases, not quieter.

**Mirror — The Psychology Brain**
Watches YOUR behavior, not the market. Detects patterns you don't see in yourself: panic selling at bottoms, FOMO buying tops, revenge trading after losses, checking the portfolio obsessively at 2am. For hodlers, Mirror might be the most valuable brain — it's the one that talks you off the ledge when BTC drops 30%. For active traders, Mirror catches tilt and overtrading.

**Ledger — The Record Keeper**
Tracks everything. For hodlers: portfolio snapshots over time, cost basis, DCA history. For active traders: per-trade journal with win rate, expectancy, average hold time, R-multiples, biggest win/loss. Ledger reads your actual OKX history and tells you what's true — not what you think you remember.

**Chain — The On-Chain Brain (scales up)**
Wallet flows, exchange flows, funding rates, smart money tracking, DeFi protocol metrics. Quiet for hodlers (basic signals only). Gets loud for users who trade DeFi tokens or show interest in on-chain data.

**Exec — The Execution Brain (scales up)**
Order types, DCA vs limit vs market, entry plans, slippage management. Completely silent for hodlers (they just market buy). Activates when behavior shows the user is timing entries and using limit orders.

---

## The Lifecycle (Proactive + Reactive Loop)

```
OBSERVE (always on)
  Read OKX portfolio, balances, trade history
  Infer behavior patterns
  Adjust brain volumes
         │
         ▼
THINK (proactive, scheduled)
  Run analysis at the right cadence for YOUR pattern
  Surface only what matters given YOUR behavior
  Adapt language and depth to YOUR level
         │
         ▼
SURFACE (proactive, when needed)
  Tap you on the shoulder when something needs attention
  Weighted by what the room thinks you care about
  Light touch for stackers, detailed for active traders
         │
         ▼
DISCUSS (reactive, when you show up)
  Room already has context from OKX
  Brains speak at the right volume for you
  Every brain knows what the others said
         │
         ▼
ACT (when you decide)
  Help you execute at the right level of detail
  Market buy for stackers, full order plan for traders
         │
         ▼
LEARN (always on)
  Track the outcome
  Feed it back into behavior patterns
  Adjust volumes for next time
         │
         └──→ back to OBSERVE
```

### Lifecycle Per Behavioral Weight

**Hodler behavior** — Research → Accumulate → Check-in → Crisis → Exit (monthly rhythm)

**Active trader behavior** — Scan → Plan → Execute → Manage → Close → Journal (daily/per-trade)

**Operator behavior** — Macro → Scan → Plan → Execute → Hedge → Manage → Close → Journal → Rebalance (continuous)

### Level-Up Detection (silent)

The framework detects transitions in real time from OKX data. Examples:

- "You've been timing your DCA entries for 3 months. You're already doing basic technical analysis. Want me to give you more from Scout?"
- "You haven't traded in 6 weeks. Switching to lighter check-ins."
- "You made 5 trades in 2 hours after a loss. Mirror suggests stepping back."

The framework questions the intent behind behavior shifts — doesn't just blindly adjust.

---

## Proactive Layer

### Scheduled Rhythms

| Rhythm | What the room does | Who leads |
|---|---|---|
| **Daily pulse** (morning) | Market overnight, open positions, anything needing attention | Scout + Shield |
| **Weekly review** | Portfolio health, thesis check per position, what changed | Sage + Shield + Ledger |
| **Monthly deep dive** | Full performance, allocation drift, strategy review | Full room |

Cadence adapts to behavior. Hodlers might only get weekly. Active traders get daily.

### Triggered Alerts

- **Thesis break** — major negative catalyst on something you hold (Sage)
- **Zone alert** — price enters accumulation/profit/stop zone (Scout)
- **Heat warning** — portfolio concentration or correlation crosses threshold (Shield)
- **Tilt detection** — too many decisions too fast, or interacting at unusual hours after loss (Mirror)
- **Opportunity** — watchlist item meets your criteria (Scout + Sage)
- **Environment shift** — macro regime change (Scout/Chain)

---

## Frameworks (Trading Equivalents of Ship's JTBD/HEART/RICE)

### Trade Thesis Template (replaces JTBD)

Every trade needs this before entry:

> "Given [market condition], I believe [asset] will [direction] because [catalyst], targeting [level], invalidated if [level/event]."

Sage enforces this. No thesis = no trade.

### Portfolio Heat (replaces Health Score)

Start at 100. Each open position adds heat based on size and correlation:
- Position >20% of portfolio: +20 heat
- Position >10%: +10 heat
- Correlated positions (>0.7): +15 heat per pair
- Leveraged position: +25 heat

Over 60 = no new positions. Over 80 = reduce exposure. Shield enforces this.

### Edge Score (replaces RICE)

For ranking trade ideas when multiple setups exist:

**Score = (Confluence × Conviction × R:R) / Risk**

- Confluence: how many signals align (1-5)
- Conviction: Sage + Scout agreement (1-5)
- R:R: reward-to-risk ratio
- Risk: position size as % of portfolio

Higher score = higher priority trade.

### Expectancy Formula (replaces HEART)

Tracks whether your trading is actually profitable:

**(Win Rate × Avg Win) - (Loss Rate × Avg Loss)**

Positive = keep trading the system. Negative = stop and fix. Ledger calculates this from OKX history.

---

## The Trader Section (CLAUDE.md config)

Minimal. Four fields. Framework infers the rest.

```markdown
## The Trader

Edge: What I pay attention to (narrative, charts, on-chain, gut, news)
Risk tolerance: How much drawdown I can stomach without panicking
Time I can give: How often I realistically check this
Goal: What I'm trying to achieve (retire, side income, learn, grow wealth)

<!-- Everything else is inferred from your OKX activity.
     The room watches, adapts, and adjusts. -->
```

---

## Hackathon Build Plan (1 day)

### The Demo (3 minutes)

**Step 1: /alpha-pulse** (name TBD)
→ Pulls real OKX portfolio
→ Room discusses positions live
→ Shield flags concentration risk
→ Sage checks thesis per position
→ Scout gives key levels
→ "2 things need your attention"

**Step 2: "I'm thinking about adding SOL"**
→ Sage: "Why? What's your thesis?"
→ Scout: market data, key levels
→ Shield: "You're already X% in alts, adding SOL puts you at Y%"
→ Mirror: "You looked at SOL last week and didn't buy. What changed?"
→ Room gives verdict with reasoning

Real portfolio. Real data. Brains that argue. That's the wow.

### Files to Build (5 total)

| File | Lines | Purpose |
|---|---|---|
| **team-rules.md** | ~800 | All 5 brains, personalities, silent adaptation logic, frameworks. The soul of the framework. |
| **CLAUDE.md** | ~100 | The Trader section, OKX MCP wiring, command table |
| **/alpha-team command** | ~300 | Main orchestrator — routes input, calls OKX for context, runs the room |
| **/alpha-pulse command** | ~200 | Portfolio briefing — pulls OKX data, runs room analysis, surfaces alerts |
| **references/risk-management.md** | ~300 | Deep reference Shield reads. Position sizing, portfolio heat, concentration rules. |

### Hour-by-Hour Sprint

| Block | Hours | What |
|---|---|---|
| Brain design | 2h | team-rules.md — all 5 brains, personalities, how they argue, silent adaptation, Portfolio Heat |
| CLAUDE.md | 0.5h | Trader section, OKX MCP wiring, command table |
| alpha-team command | 2h | Main orchestrator — routes input, calls OKX, runs the room |
| alpha-pulse command | 1.5h | Portfolio briefing — pull OKX, Shield allocation, Sage thesis, Scout levels |
| Risk reference | 1h | risk-management.md — position sizing, concentration limits, correlation |
| Test & tune | 2h | Run demo 5-10x. Tune brain voices until arguments feel real. Fix OKX data formatting. |
| Polish | 1h | Output formatting, brain voice, demo practice |

### What NOT to Build (save for later)

- No setup.sh / installer
- No README (demoing live, not distributing)
- No separate scan/exec/close/journal/autopsy commands
- No 10 reference files — one reference enough for demo
- No skills routing layer — bake into commands
- No CHEATSHEET
- No web UI

---

## Post-Hackathon Roadmap

### Phase 2 — Full Command Set

Add remaining commands: scan, exec, review, close, journal, autopsy, macro, sim, guard, tilt

### Phase 3 — Full Reference Library

| Reference | What it teaches |
|---|---|
| market-structure.md | Higher highs/lows, BOS, CHoCH, order blocks, liquidity sweeps |
| technical-setups.md | Setups with statistical edges, false patterns to avoid |
| risk-management.md | Kelly criterion, fixed fractional, drawdown rules, correlation ✅ (hackathon) |
| on-chain-metrics.md | MVRV, SOPR, exchange flows, whale tracking, funding rates |
| defi-protocols.md | AMM mechanics, yield strategies, liquidation cascades, MEV |
| macro-framework.md | Dollar index, yields, Fed policy, cross-market correlations |
| trading-psychology.md | Tilt detection, cognitive biases, process vs outcome thinking |
| execution-patterns.md | Order types, slippage, DCA strategies, TWAP, iceberg orders |
| cycle-analysis.md | Bitcoin dominance, alt rotation, halving cycles, sentiment phases |
| portfolio-construction.md | Core/satellite, sector allocation, rebalancing triggers |

### Phase 4 — Local Web Dashboard

Next.js on localhost. Portfolio view, alert board, journal, embedded chat with the room. Like ValueCell's UI but with our brain architecture.

### Phase 5 — Multi-Exchange

Add Binance, Hyperliquid, Coinbase MCPs alongside OKX.

---

## Comparisons

### vs Ship Framework

Same architecture (personas, commands, skills, references, CLAUDE.md), different domain. Ship is design + code. This is markets + risk + psychology. The silent adaptation layer is new — Ship doesn't have it.

### vs ValueCell

ValueCell has better infrastructure (exchange connectors, orchestrator, UI, A2A protocol). We have better intelligence (personality, tension, psychological layer, thesis discipline, silent adaptation). Could merge later — their infrastructure + our brains.

---

## Open Questions

- [ ] **Framework name** — "Alpha" works for traders but may feel intimidating for hodlers. "The Desk" (trading desk)? Something else? Need to decide before building.
- [ ] **Execution spectrum** — for hackathon, read-only (room advises, you trade manually). Post-hackathon: how far does execution go?
- [ ] **Data sources beyond OKX** — CoinGecko for broader market? DeFiLlama for on-chain? Crypto news feeds?
- [ ] **Multi-user** — currently single-user (your CLAUDE.md, your OKX). If this becomes a product, how does it adapt per user?

---

*This document captures everything discussed between Ismael and Claude across one planning session. Pick up from here on any machine with Claude Code.*
