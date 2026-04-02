# Metrics Extraction

Use this reference when converting earnings text into a `metrics.json` file for scoring.

## Principle

Treat extraction as a draft, not final truth.

The script is best at pulling common phrases such as:

- revenue grew 58% year over year
- gross margin was 64%
- free cash flow margin was negative 6%
- capex was $450 million on revenue of $530 million
- top customer represented 28% of revenue

It is weaker when:

- the company uses unusual wording
- the document mixes multiple periods
- net cash must be inferred from separate cash and debt lines
- dilution requires comparing current and prior share counts that are far apart in the text

## Recommended Workflow

1. Run the extractor on the earnings summary, shareholder letter, or notes you prepared.
2. Review the generated `sources` block and `missing` list.
3. Manually patch anything that looks wrong or missing.
4. Feed the result to `score_growth_stock.py`.

## Expected JSON Fields

The extractor tries to populate:

- `ticker`
- `analysis_date`
- `revenue_growth_yoy`
- `gross_margin`
- `fcf_margin`
- `net_cash_to_revenue`
- `share_dilution_yoy`
- `top_customer_share`
- `capex_to_revenue`
- `rule_of_40`

It also includes:

- `missing`
- `sources`

## Good Source Documents

- earnings press release
- shareholder letter
- management prepared remarks
- your own cleaned notes from those documents

Plain text or markdown works best.
