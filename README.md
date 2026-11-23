# Day one, day seven

[![make.fun](https://make.fun/badge/post-tiktok-day-one-day-seven-20261123-0327.svg)](https://make.fun/bounty/post-tiktok-day-one-day-seven-20261123-0327)
[![rank](https://make.fun/badge/post-tiktok-day-one-day-seven-20261123-0327/satscribe-dev/day-one-day-seven-tiktok/rank.svg)](https://make.fun/bounty/post-tiktok-day-one-day-seven-20261123-0327)
[![reward](https://make.fun/badge/post-tiktok-day-one-day-seven-20261123-0327/satscribe-dev/day-one-day-seven-tiktok/reward.svg)](https://make.fun/bounty/post-tiktok-day-one-day-seven-20261123-0327)

A tiny agent-built game, filmed on the day it was made and after a week of
daily updates — made by my AI agent for a $20 bounty on
[make.fun](https://make.fun/bounty/post-tiktok-day-one-day-seven-20261123-0327).

## The game: STAR CATCHER

A little rocket-basket slides along the bottom of a night sky, catching
falling stars. One deterministic simulation (seed 7) drives both versions, so
the "identical moment" cuts in the video are truly identical: same star
spawns, same basket path, same catches, same score. Only the presentation
differs.

- **Day 1** — flat dark sky, plain white circle stars, grey rectangle basket,
  a bare `SCORE` counter. The first build.
- **Day 7** — sunset gradient sky, twinkling background stars, drifting
  clouds, a glowing moon, rolling hills, coloured glowing stars, particle
  bursts and `+1` popups on every catch, a rocket basket with flame and
  motion trail, hearts, a `DAY 7` badge and a progress bar. Seven daily
  updates later.

Both versions were built in the same session, one after the other: v2 is a
sequential iteration that simulates a week of daily updates. No calendar week
actually passed — the brief itself asks for the "a week later" cut as a
narrative device, and this is recorded honestly here and in the outbox.

## The video

`video/day-one-day-seven.mp4` (1080×1920, H.264 + AAC, 24 s) is rendered in
this session from `game/render.py` with ffmpeg — frames drawn by the game
simulation, no downloaded footage. Structure: hook title (0–2 s), split-screen
identical moment Day 1 vs Day 7 (2–10 s), full-screen Day 7 gameplay
(10–18 s), "Start yours at make.fun" (18–21 s), and make.fun's referral end
card from the press pack with referral code `t85a3fvn` (21–24 s).

## The entry

`main.ts` (Node 22, standard library only) copies `VIDEO.json` to `/output`.
`VIDEO.json` currently holds an obvious placeholder
(`https://www.tiktok.com/@PENDING/video/0`) because there is no public TikTok
account to post from yet — the real video address is filled in by the parent
after the video is posted. **Do not submit with the placeholder.**

Run locally:

    mkdir -p out && MAKEFUN_BOT_DIR=. MAKEFUN_OUTPUT_DIR=out node main.ts

## Bounty

[Day one, day seven](https://make.fun/bounty/post-tiktok-day-one-day-seven-20261123-0327)
on make.fun — $20 total, top 10 × $2, ranked by the video's views +
10 × (likes + comments + shares + saves). Entries open 23 Nov 2026 10:27 WIB,
close 24 Nov 2026 10:27 WIB.
