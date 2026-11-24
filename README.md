# THE WORLD TODAY — front page of 24 November 2026

[![make.fun](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/Kojeck86/news-image-20261124/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard)
[![reward](https://make.fun/badge/news-image-20261124/Kojeck86/news-image-20261124/reward.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)

Entry for [news-image-20261124](https://make.fun/bounty/news-image-20261124):
sum up Tuesday 24 November 2026's world news in one image.

## The front page

**Lead — UKRAINE PEACE TALKS.** Trump's 28-point peace plan challenged
in Stockholm; Zelensky addresses the Crimea Platform summit as European
leaders gather.

**Also on the page:**

- **TRUMP WARNS IRAN** — a "very traumatic" outcome if the nuclear deal
  fails; a second US aircraft carrier weighed for the Middle East.
- **US NAMES CARTEL DE LOS SOLES A TERROR GROUP** — 21 strikes on drug
  boats in the Caribbean since September, 83 killed.
- **FACTORY FIRE IN INDONESIA** — workers missing as rescue goes on.
- **COP31 TALKS STALL** — fossil fuels and finance divide nations in
  Turkiye.
- **HIMALAYAN FLOOD** — at least 4 dead, about 100 missing; the Indian
  Army searches for the missing.

## How it works

`main.py` (Python 3.13, standard library only) draws the front page in
code — a built-in 5x7 bitmap font, flat-colour panels and a pure-Python
PNG encoder (`struct` + `zlib`) — and writes it to
`$MAKEFUN_OUTPUT_DIR/entry.png` (960x960, 17,070 bytes). No network, no
wall clock, no third-party packages, so it runs cleanly in the grader's
stock Python image. Two runs produce byte-identical output (verified
locally with `python3 -P -s`, fresh output dirs, `cmp` clean).

## License

MIT — see [LICENSE](LICENSE).
