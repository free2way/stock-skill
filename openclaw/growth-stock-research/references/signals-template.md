# Signals Template

Use this reference when converting a qualitative thesis into a dated signal series.

## Principle

Signals should represent a change in conviction, not every news headline.

Good examples:

- major earnings beat with stronger guide
- evidence of margin inflection
- large customer win that improves revenue visibility
- financing event that increases dilution risk
- material execution miss that breaks the thesis

Weak examples:

- generic product announcement
- price target change from a broker
- social media sentiment

## Event CSV Contract

Create an events CSV with these columns:

- `date`
- `stance`
- `reason`

Interpretation:

- `bullish` -> signal `1`
- `bearish` -> signal `0`
- `neutral` -> signal `0`

Example:

```csv
date,stance,reason
2025-05-08,bullish,Q1 revenue beat and raised guidance
2025-08-07,bearish,Gross margin miss and slower customer adds
2025-11-06,bullish,Large enterprise deal improves backlog visibility
```

## How To Think About Signal Dates

- Use the date the information became investable, usually the earnings release date.
- Do not backdate signals using information that was not public yet.
- If an event changes the thesis for several quarters, let the signal persist until a new event reverses it.

## Review Checklist

Before backtesting signals, ask:

- Does each signal correspond to a real thesis change?
- Would I have acted on this information at the time?
- Is the signal frequency low enough to reflect conviction rather than noise?
- Am I accidentally leaking hindsight into the dates?
