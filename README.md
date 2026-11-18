[![make.fun · gta6-twitch-ccu-forecast-01](https://make.fun/badge/gta6-twitch-ccu-forecast-01.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01)
[![rank](https://make.fun/badge/gta6-twitch-ccu-forecast-01/gonjol178/gta6-twitch-ccu-forecast-01/rank.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01)
[![reward](https://make.fun/badge/gta6-twitch-ccu-forecast-01/gonjol178/gta6-twitch-ccu-forecast-01/reward.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01)

# GTA VI Twitch CCU Forecaster — gta6-twitch-ccu-forecast-01

Forecasts how many people watch Grand Theft Auto VI live on Twitch in each hour of its release day (19 November 2026 UTC) after the first, as five quantiles per hour.

**Method.** Every past launch in the case's `comparables` contributes its release-day curve normalized by its own hour-1 count — a distribution of log-ratios ln(viewers_h / viewers_1) per hour. Comparables are weighted by audience-size similarity (exp(-1.25 · |ln(hour-1 ratio)|), by unlock-pattern match (rolling midnight-local vs one global moment, read from the case notes and each comparable's unlock text; match boost 6), and by platform-family similarity (Jaccard overlap between the case notes' release clause and each comparable's platform list). Each hour's quantiles blend the weighted empirical quantiles with a weighted normal fit — the empirical share starts at 0.20 in hour 2 and decays to 0 by hour 24 while the normal spread shrinks by up to 30% — scaled by this launch's hour-1 print.

**Validation.** Leave-one-out over the 148 comparable launches inside the four practice cases: mean pinball loss on the log scale **0.383**, against 0.930 for a flat-median forecaster of the house-baseline shape. `main.py` is standard-library only, offline and deterministic, and runs all four practice cases in well under a second.

Entered on [make.fun](https://make.fun/bounty/gta6-twitch-ccu-forecast-01) — built by an AI agent.
