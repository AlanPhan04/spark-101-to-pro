# 08 — Chapter 1 strategy

## The concrete problem it opens on

A query the reader would actually write: a week of `trips` joined to
`dim_route`, aggregated to on-time rate per route. It runs. It takes four
minutes. The reader has no idea why four and not one, or four and not forty.

Chapter 1 does not optimize it. It uses it as the specimen: run it, then open the
UI and *name every moving part* — one job, three stages, the shuffle between them,
200 tasks in the middle stage, one executor doing more than the others.

## The payoff by the end of the chapter

The reader can point at the Spark UI for their own job and say: this is the
driver's timeline, these are my executors, this is the job, here are its stages,
the boundary here is a shuffle, and this stage's tasks are uneven. They cannot
fix it yet — that is Parts II–III — but they can *see* it, which they could not
before.

## First-page promise

The first page states the through-line plainly: performance work is about seeing
where data moves and deciding to move it differently, and every chapter adds one
place you can see or one lever you can pull. The four-minute query is right there
on page one as the thing we will still be explaining ten chapters later.

## What the reader can do after Chapter 1 that they could not before

- Run a query and read the job/stage/task breakdown in the UI instead of a
  progress bar.
- Identify a stage boundary as a shuffle.
- Spot uneven task times (the first sighting of skew, named properly in Ch 6).
- Know the difference between the driver planning and the executors running, and
  which one their `collect()` just overloaded.
