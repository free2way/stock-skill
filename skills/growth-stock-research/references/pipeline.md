# Pipeline

Use this reference when you want one command to maintain the whole growth-stock watchlist.

## Goal

Turn the common review cycle into a single repeatable workflow:

1. refresh reports
2. tag the watchlist
3. generate a short snapshot
4. generate ranking and dashboard artifacts

## Recommended use

Run the pipeline after:

- an earnings batch
- a major event batch
- a weekly watchlist maintenance session

## Inputs

The pipeline needs:

- a refresh manifest
- the list of report JSON files to summarize
- output paths for tags, snapshot, ranking, CSV, and HTML

## Output order

The snapshot is the first thing to read.
Use the ranking and dashboard only for deeper follow-up.
