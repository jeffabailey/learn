# ai-software-tool-usage-report

Pulls monthly cost, seat, and token usage from major AI coding tool vendors and writes a single CSV. Idempotent: rerunning for the same month overwrites the same file.

## Vendors

| Vendor | Source | Auth |
| --- | --- | --- |
| Anthropic (Claude / Claude Code) | `cost_report` and `usage_report/messages` admin endpoints | Admin API key |
| OpenAI | `/organization/costs` and `/organization/usage/completions` | Admin API key |
| GitHub Copilot | `/orgs/{org}/copilot/billing` and `/orgs/{org}/copilot/metrics` | PAT with `manage_billing:copilot` |
| Cursor | `/teams/spend` and `/teams/daily-usage-data` | Team API key |
| Google Gemini | Manual entry (Cloud Billing / Cloud Monitoring) | Manual values in `.env` |
| AWS Kiro | Cost Explorer `GetCostAndUsage` | Standard AWS credential chain |

Cost is in USD across all rows.

## Setup

```bash
cd ai-software-tool-usage-report
uv sync
cp .env.example .env
# Fill in keys for the vendors you actually use; leave the rest blank.
```

## Run

```bash
uv run python index.py                  # current month
uv run python index.py --month 2026-04  # specific calendar month
uv run python index.py --output ./out   # custom output directory
```

The script writes `ai-tool-usage-YYYY-MM.csv` in the chosen directory and prints the path. Vendors with missing keys appear as `SKIPPED` rows so the gap is obvious.

## CSV columns

```
vendor, tool, period_start, period_end, monthly_cost_usd,
active_users, licensed_seats, tokens_or_requests, pricing_model, notes
```

Empty cells mean the vendor does not expose that field (for example, Anthropic does not return seat count, GitHub does not return token count).

## Caveats

* **Vendor APIs change.** I keep the doc URL and the response field path in a comment at the top of each adapter in `vendors/`. When a vendor breaks the contract, fix the field path there.
* **Anthropic and OpenAI admin keys are different from API keys.** Project / standard API keys WILL NOT work for the cost endpoints. Create admin keys in each vendor's admin console.
* **GitHub does not return Copilot cost.** The script multiplies seat count by `GITHUB_COPILOT_SEAT_RATE_USD`. Override the default if you have negotiated pricing.
* **Gemini aggregate usage** lives in Cloud Billing BigQuery exports or Cloud Monitoring. Wiring that into a one-file script needs a service account and a billing-export dataset. The adapter accepts a manual monthly value via `.env` so Gemini still appears on the report.
* **AWS Kiro service name** in Cost Explorer can drift across renames. The default is `Amazon Kiro`. If the row reports zero, check a recent Cost Explorer report and update `AWS_KIRO_SERVICE_NAME` in `.env`.

## Development

Layout:

```
ai-software-tool-usage-report/
  index.py             # CLI entry point
  pyproject.toml       # uv-managed deps and console script
  .env.example         # template for credentials
  vendors/
    base.py            # VendorAdapter + VendorReport dataclass
    anthropic.py
    openai_admin.py
    github_copilot.py
    cursor.py
    gemini.py
    aws_kiro.py
```

Add a vendor by writing a new `VendorAdapter` subclass in `vendors/` and listing it in `vendors/__init__.py`. The adapter should:

1. Read its credentials from the env dict.
2. Make HTTP / SDK calls inside `fetch`.
3. Return a `VendorReport` (use `VendorReport.skipped` when the vendor cannot be queried).

Errors raised inside `fetch` get caught at the top level and recorded as `SKIPPED` rows so one broken vendor does not abort the run.
