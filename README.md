# Stock Skill

Growth stock research skill and example run artifacts.

## Structure

- `skills/growth-stock-research/`
  The Codex skill, including workflow instructions, references, scripts, shared helpers, and sample data.

- `openclaw/growth-stock-research/`
  An OpenClaw-compatible packaging of the same skill for direct installation into `~/.openclaw/skills/`.

- `runs/2026-04-02-growth-watchlist/`
  A real workflow run for:
  - `NBIS`
  - `IREN`
  - `CRWV`
  - `ASTS`
  - `AAOI`

## What This Includes

- First-principles growth-stock research workflow
- Metrics extraction and scorecard scripts
- Price download and backtest scripts
- Report assembly, diff, tagging, ranking, snapshot, and dashboard exports
- Batch refresh and one-command pipeline orchestration
- Sample data for learning the workflow

## Notes

- Some run inputs are normalized workflow values used to keep the scorecard comparable across very different business models.
- Treat run outputs as research scaffolding, not audited investment recommendations.
- OpenClaw install notes are in `openclaw/README.md`.
