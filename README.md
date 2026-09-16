# Sala de Parts

An offline decision drill for the **birth partner** — 92 multiple-choice questions covering the
six phases of a birth in the Catalan / Spanish public system, from the first contraction to the
weeks at home.

Built as an installable PWA so it works in a hospital corridor with no signal.

## What's in it

- **92 questions** across six chronological modules: senyals · dilatació · expulsiu ·
  intervencions · postpart · nadó.
- **Independent evidence** on 83 of them — Cochrane reviews, WHO, NICE, RCOG, ACOG, AAP, ABM,
  SEGO/AEP — named and summarised under each answer, separately from the course material.
- **Contested filter** for the 19 topics where guidelines genuinely disagree (bed-sharing,
  39-week induction, GBS screening, mastitis management, tongue-tie, and others).
- **Red flags filter** — the 26 go-to-hospital facts, drillable in five minutes.
- **Spaced repetition** — two correct answers in a row to master a question; wrong answers
  requeue. Options reshuffle every time and the high-stakes questions rotate through several
  phrasings, so you learn the fact rather than the position of the right button.
- **Reference drawer** — the full red-flag card plus a contraction timer that measures
  start-to-start and calls the 5-1-1 threshold.

## Install

Open the site in **Safari** on iOS (only Safari can install to the home screen), then
Share → Add to Home Screen. The first launch needs a connection so the fonts are cached;
after that it runs fully offline.

On Android, Chrome will offer to install it directly.

## Layout

    src/quiz.html    the source page: question bank, evidence, scheduler, styles
    tools/           build scripts
    index.html       generated from src/ — do not edit directly
    sw.js            offline cache; bump CACHE when index.html changes
    manifest.webmanifest, icon-*.png

## Building

Requires Python with Pillow, and Node only for the simulation.

    cd tools
    python build_pwa.py     # src/quiz.html -> ../index.html (PWA head, phone CSS, offline hooks)
    python make_icons.py    # regenerate the icons
    node sim.js             # simulate the scheduler: repeat gaps, tier ramp, mastery

Edit `src/quiz.html`, rebuild, then **bump `CACHE` in `sw.js`** or installed
devices will keep serving the old version. Commit and push; GitHub Pages
redeploys in about a minute.

`sim.js` is the regression test that matters — it loads the real scheduler out of
the built `index.html` and reports how often a question repeats. Adding questions
or changing the spacing constants should not push "repeats within 2 slots" above
zero.

## Scheduler

Leitner boxes with spacing of 4/10/25/60/150 questions. A correct answer promotes
a question one box, a miss resets it to box 0 and returns it after 6 questions.
Two spaced correct answers count as mastered; mastered questions still come back
for review when their spacing elapses.

The streak sets the difficulty the drill aims at — tier 1 foundations, tier 2 at
streak 4, tier 3 at streak 8 — as a weighting rather than a gate, so the whole
bank stays reachable at any streak and the rotation stays wide.

## Privacy

There is no backend. Quiz progress and the contraction log live in the browser's local
storage on the device and are never transmitted anywhere.

## Caveat

General protocol for the Catalan / Spanish public system. Your midwife and your hospital's own
instructions override every answer here — particularly the contraction threshold for going in,
which varies between units.
