# Demo Script — Planora (say it out loud while recording)

Speak slowly. Short sentences. Pause between lines. Total: ~90 seconds.

---

## 1. Intro — before you type anything (look at camera)

> "Hi, I'm Gizem. I'm building Planora.
>
> Here's the problem: when someone submits a building-permit application,
> the file usually has ten, twenty, sometimes fifty documents —
> site plans, structural calculations, forms, signatures.
>
> If even one document is missing, or one date is expired,
> or one signature is on the wrong page — the authority doesn't tell you
> right away. They send it back weeks later. And you start again.
>
> Planora checks all of that *before* you submit —
> so the authority never has a reason to send it back."

---

## 2. Type the command, then talk while it runs

```
cd ~/Claude/bauantrag && uv run python demo.py
```

> "I'm running it now on a realistic example — a real building application
> with ten documents, for a family building a house."

*(the tool prints 4 steps — read them out loud as they appear on screen)*

> "Step one: it reads every PDF.
>
> Step two: it figures out what kind of document each one is —
> is this the site plan, the structural report, the application form?
> And it tells you how confident it is about that.
>
> Step three: it checks the formal details — the date on each document,
> who signed it, whether the names match across all the files.
>
> Step four: it compares everything against the official checklist
> for this type of building and this building class."

---

## 3. When the result table appears — walk through it

> "And here's the result, as a simple traffic light.
>
> Red means: stop, don't submit yet — something is missing,
> or a deadline has expired.
>
> Yellow means: check this by hand before you send it.
>
> Green would mean: this point is fine."

*(point at the first red row — the expired site plan)*

> "Look at this one. This site plan is thirty months old.
> The authority only accepts one that's twelve months old or newer.
> Nobody would notice this by just looking at the file —
> you'd need to know the rule, and check the date by hand."

*(point at the second red row — missing document)*

> "And here — a required document is completely missing from the stack.
> Without this tool, this only comes up after you've already submitted,
> when the authority writes back."

---

## 4. Closing — why this matters (last 15 seconds)

> "Every red and yellow finding you just saw is one round-trip
> to the building authority that this application would have needed —
> costing weeks, sometimes months.
>
> Planora catches all of it in under a minute, before you ever submit.
> That's the idea."

---

## Notes for you (not spoken)

- Keep the phone steady, landscape mode, good light on the screen — no glare.
- Zoom the terminal font up first (Cmd + "+" a few times) so it's readable on video.
- If you stumble on a sentence: stop, breathe, say it again. One clean-ish take is enough — this doesn't need to be perfect.
- If it runs long, you can safely cut the "why this matters" intro shorter and lean more on the live result — the table is the strongest part.
