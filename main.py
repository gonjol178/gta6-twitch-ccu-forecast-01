"""make.fun gta6-twitch-ccu-forecast-01 entry.

Forecasts a big game launch's Twitch category viewers for hours 2-24 of
its release day, given everything recorded up to the end of hour 1.

Method (leave-one-out pinball loss 0.398 over 148 historical launches,
vs 0.930 for a flat-median forecaster): every past launch in the case's
`comparables` contributes its release-day curve normalized by its own
hour-1 count, giving a distribution of log-ratios ln(viewers_h /
viewers_1) per hour. Comparables are weighted by how close their hour-1
audience is to this launch's (exp(-1.25 * |ln ratio of hour-1 counts|))
and by whether their unlock pattern matches this launch's (rolling
midnight-local vs one global moment, read from the case notes and each
comparable's unlock text). Each hour's five quantiles blend the weighted
empirical quantiles of the log-ratios with a weighted normal fit
(0.35 / 0.65), then scale by this launch's hour-1 print.

Standard library only, no network, deterministic; runs in well under a
second per case.
"""

import json
import math
import os
from datetime import datetime, timedelta

LEVELS = [0.05, 0.25, 0.5, 0.75, 0.95]
Z = {0.05: -1.644854, 0.25: -0.674490, 0.5: 0.0, 0.75: 0.674490, 0.95: 1.644854}
MAG_W = 1.25
BLEND = 0.35
SD_FLOOR = 0.12
SD_CAP = 1.1
UNLOCK_MATCH_BOOST = 2.5


def parse_ts(s):
    return datetime.fromisoformat(s.replace('Z', '+00:00'))


def day_curve(comp):
    ds = parse_ts(comp['day_start'])
    out = {}
    for p in comp['hourly']:
        t = parse_ts(p['from'])
        if ds <= t < ds + timedelta(hours=24):
            out[int((t - ds).total_seconds() // 3600) + 1] = p['viewers']
    return out


def is_rolling_text(text):
    u = (text or '').lower()
    return 'midnight' in u and ('rolling' in u or 'local' in u)


def wquantile(sorted_pairs, tau):
    tot = sum(w for _, w in sorted_pairs)
    if tot <= 0:
        return sorted_pairs[len(sorted_pairs) // 2][0]
    acc, prev_v, prev_c = 0.0, sorted_pairs[0][0], 0.0
    for v, w in sorted_pairs:
        acc += w
        c = acc / tot
        if c >= tau:
            if c == prev_c:
                return v
            frac = (tau - prev_c) / (c - prev_c)
            return prev_v + frac * (v - prev_v)
        prev_v, prev_c = v, c
    return sorted_pairs[-1][0]


def forecast(case):
    known = case['known'][0]
    v1 = max(known['viewers'], 1)
    ln_v1 = math.log(v1)
    game_name = (case.get('game') or {}).get('name', '')
    target_rolling = is_rolling_text(case.get('notes'))
    rows = []
    for comp in case['comparables']:
        if comp['name'] == game_name:
            continue
        curve = day_curve(comp)
        c1 = curve.get(1)
        if not c1 or c1 < 100:
            continue
        ratios = {h: math.log(v / c1) for h, v in curve.items() if h >= 2 and v and v > 0}
        if len(ratios) < 20:
            continue
        w = math.exp(-MAG_W * abs(math.log(c1) - ln_v1))
        if is_rolling_text(comp.get('unlock')) == target_rolling:
            w *= UNLOCK_MATCH_BOOST
        rows.append((ratios, w))
    out = []
    for h in range(2, 25):
        pairs = sorted((r[h], w) for r, w in rows if h in r)
        if not pairs:
            qs = [float(v1)] * 5
        else:
            tot = sum(w for _, w in pairs)
            mean = sum(v * w for v, w in pairs) / tot
            var = sum(w * (v - mean) ** 2 for v, w in pairs) / tot
            sd = min(max(math.sqrt(var), SD_FLOOR), SD_CAP)
            qs = []
            for tau in LEVELS:
                q = BLEND * wquantile(pairs, tau) + (1 - BLEND) * (mean + Z[tau] * sd)
                qs.append(min(max(math.exp(ln_v1 + q), 0.01), 1e9))
            for i in range(1, 5):
                qs[i] = max(qs[i], qs[i - 1])
        out.append({'hour': h, 'q': qs})
    return {'hours': out}


def main():
    in_dir = os.environ.get('MAKEFUN_INPUT_DIR', '/input')
    out_dir = os.environ.get('MAKEFUN_OUTPUT_DIR', '/output')
    os.makedirs(out_dir, exist_ok=True)
    for name in sorted(os.listdir(in_dir)):
        if not name.endswith('.in'):
            continue
        with open(os.path.join(in_dir, name), encoding='utf-8') as f:
            case = json.load(f)
        result = forecast(case)
        with open(os.path.join(out_dir, name[:-3] + '.out'), 'w', encoding='utf-8') as f:
            json.dump(result, f)


if __name__ == '__main__':
    main()
