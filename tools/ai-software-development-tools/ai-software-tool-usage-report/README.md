# AI Software Tool Usage Report

Pulls monthly cost, seat, and token usage from major AI coding tool vendors and writes a single CSV. Idempotent: rerunning for the same month overwrites the same file.

## Vendors

| Vendor | Source | Auth |
| --- | --- | --- |
| Anthropic (Claude / Claude Code) | `cost_report` and `usage_report/messages` admin endpoints | Admin API key |
| OpenAI | `/organization/costs` and `/organization/usage/completions` | Admin API key |
| GitHub Copilot | `/orgs/{org}/copilot/billing` and `/orgs/{org}/copilot/metrics` | PAT with `manage_billing:copilot` |
| Cursor | `/teams/spend` and `/teams/daily-usage-data` | Team API key |
| Google Gemini Code Assist | Cloud Monitoring `timeSeries.list` (users); manual or BigQuery export (cost) | Application Default Credentials |
| AWS Kiro | Cost Explorer `GetCostAndUsage` | Standard AWS credential chain |

Cost is in USD across all rows.

## Setup

```bash
cd ai-software-tool-usage-report
uv sync
cp .env.example .env
# Fill in keys for the vendors you actually use; leave the rest blank.
```

## Get the credentials

Each vendor uses a different credential type. Skip any vendor your org does not pay; missing keys produce a `SKIPPED` row, not a failure.

### Anthropic

* **What you need:** an **Admin API key**. Project / standard API keys (the ones that start with `sk-ant-...` and live under a workspace) will NOT reach the cost or usage endpoints. Admin keys live under the org owner.
* **Who can create it:** an org owner (admin role).
* **Where to create it:** [Anthropic Console -> Settings -> Admin Keys](https://console.anthropic.com/settings/admin-keys).
* **Env var:** `ANTHROPIC_ADMIN_KEY`.
* **Endpoints used:** `cost_report` and `usage_report/messages` (see [Admin API docs](https://docs.anthropic.com/en/api/administration-api)).

### OpenAI

* **What you need:** an **Admin API key** scoped to the organization. Project keys WILL NOT work for the `/organization/costs` and `/organization/usage/*` endpoints.
* **Who can create it:** an organization owner.
* **Where to create it:** [OpenAI platform -> Settings -> Organization -> Admin keys](https://platform.openai.com/settings/organization/admin-keys).
* **Env var:** `OPENAI_ADMIN_KEY`.
* **Endpoints used:** [`/organization/costs`](https://platform.openai.com/docs/api-reference/usage/costs) and [`/organization/usage/completions`](https://platform.openai.com/docs/api-reference/usage/completions).

### GitHub Copilot

* **What you need:** a **personal access token** plus the **org login** (the slug in `https://github.com/<org>`). GitHub does not return Copilot cost via the API, so the script multiplies seats by `GITHUB_COPILOT_SEAT_RATE_USD`.
* **Who can create it:** an org owner (or someone with the Copilot admin role on the target org).
* **Where to create it:**
  * **Classic PAT:** [github.com/settings/tokens/new](https://github.com/settings/tokens/new) -> select scopes **`manage_billing:copilot`**, **`read:org`**, and **`read:enterprise`** (the last only if your org is inside an enterprise account).
  * **Fine-grained PAT:** [github.com/settings/personal-access-tokens/new](https://github.com/settings/personal-access-tokens/new) -> resource owner = your org -> permissions: **GitHub Copilot Business: read-only** and **Organization administration: read-only**.
* **Env vars:** `GITHUB_TOKEN`, `GITHUB_ORG`, `GITHUB_COPILOT_SEAT_RATE_USD` (defaults to `19`).
* **Endpoints used:** [`/orgs/{org}/copilot/billing`](https://docs.github.com/en/rest/copilot/copilot-user-management#get-copilot-seat-information-and-settings-for-an-organization) and [`/orgs/{org}/copilot/metrics`](https://docs.github.com/en/rest/copilot/copilot-metrics).

### Cursor

* **What you need:** a **team admin API key**. Personal account API keys will NOT work for the team endpoints.
* **Who can create it:** a Team Owner (the role label in Cursor's UI).
* **Where to create it:** [Cursor Dashboard -> Settings -> Team -> API Keys](https://www.cursor.com/dashboard?tab=team-settings).
* **Env var:** `CURSOR_API_KEY`.
* **Endpoints used:** [`/teams/spend` and `/teams/daily-usage-data`](https://docs.cursor.com/account/teams/admin-api).

### Google Gemini Code Assist

This is the Google equivalent of Copilot / Cursor / Claude Code: an in-IDE coding assistant under "Gemini for Google Cloud" (formerly Duet AI for Developers). Its metrics live under the Cloud Monitoring resource type `cloudaicompanion.googleapis.com/Instance`. (The raw Gemini API at `generativelanguage.googleapis.com`, intended for app developers building on Gemini, is a different product and outside the scope of this tool.)

The adapter pulls **active users** from Cloud Monitoring's `timeSeries.list` REST endpoint via a real API call. **Cost** is not exposed by Cloud Monitoring; the standard automated source is a [BigQuery billing export](https://cloud.google.com/billing/docs/how-to/export-data-bigquery). Until you wire that up, you can paste a monthly cost into `.env` and the row will still populate.

* **What you need:**
  * A **GCP project ID** that hosts the Code Assist subscription.
  * A **Cloud Monitoring metric type** string (you copy it from Metrics Explorer; details below).
  * **Application Default Credentials** for an identity with `roles/monitoring.viewer` on that project.
  * (Optional) a **manual monthly cost** in USD until you wire the BigQuery export.
* **Who can grant it:** a project owner or someone with `roles/resourcemanager.projectIamAdmin`.
* **Where to authenticate:**
  * **Local dev:** run [`gcloud auth application-default login`](https://cloud.google.com/sdk/gcloud/reference/auth/application-default/login). The script picks up the resulting credentials automatically.
  * **CI / non-interactive:** download a service-account JSON key from [IAM -> Service Accounts](https://console.cloud.google.com/iam-admin/serviceaccounts), set `GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json`, and grant the service account `roles/monitoring.viewer`.
* **Where to find the metric type:**
  * Open [Cloud Monitoring -> Metrics Explorer](https://console.cloud.google.com/monitoring/metrics-explorer).
  * In the metric picker, search for **"Gemini for Google Cloud Instance"** as the resource type.
  * Pick a metric under the **usage** category (for example *Twenty-eight day Active User Responses* or *Lines of code*).
  * The metric type string (`cloudaicompanion.googleapis.com/...`) is shown directly under the display name. Copy it into `GOOGLE_GEMINI_METRIC_TYPE` in `.env`.
* **Env vars:** `GOOGLE_GEMINI_PROJECT_ID`, `GOOGLE_GEMINI_METRIC_TYPE`, optionally `GOOGLE_GEMINI_MONTHLY_COST_USD`, optionally `GOOGLE_GEMINI_MONTHLY_TOKENS`.
* **Endpoint used:** [`projects.timeSeries.list`](https://cloud.google.com/monitoring/api/ref_v3/rest/v3/projects.timeSeries/list) on `monitoring.googleapis.com`.
* **Cost upgrade path:** enable [BigQuery billing export](https://cloud.google.com/billing/docs/how-to/export-data-bigquery), then replace `_manual_cost` in `vendors/gemini.py` with a query against the export table filtered by `service.description LIKE 'Gemini%'`. The standard schema is documented [here](https://cloud.google.com/billing/docs/how-to/export-data-bigquery-tables/standard-usage).

### AWS Kiro (and other AWS-billed AI services)

* **What you need:** AWS credentials with permission to call **Cost Explorer's `GetCostAndUsage`**. Any of the standard credential paths works: env vars, a profile in `~/.aws/credentials`, IAM Identity Center SSO, or an attached IAM role.
* **Who can grant it:** an AWS account admin.
* **Required IAM permission:** `ce:GetCostAndUsage`. The AWS-managed policy [`AWSBillingReadOnlyAccess`](https://console.aws.amazon.com/iam/home#/policies/arn:aws:iam::aws:policy/AWSBillingReadOnlyAccess) covers this. Account admins must also enable **IAM user / role billing access** (root account setting) before non-root principals can read Cost Explorer.
* **Where to create credentials:**
  * **IAM access keys (long-lived):** [IAM -> Users -> {your user} -> Security credentials -> Create access key](https://console.aws.amazon.com/iam/home#/users) (select "Application running outside AWS").
  * **Short-lived SSO credentials (recommended):** [IAM Identity Center](https://console.aws.amazon.com/singlesignon/home) -> assign yourself a permission set with `AWSBillingReadOnlyAccess`, then `aws sso login`.
* **Env vars:** `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION` (defaults to `us-east-1` because Cost Explorer lives there). Leave them blank if you use a profile or SSO and let boto3's [default credential chain](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html) resolve them.
* **Verify the service name:** open [Cost Explorer](https://console.aws.amazon.com/cost-management/home#/cost-explorer), group by **Service** for the previous month, and copy the exact label for the Kiro / Q Developer row into `AWS_KIRO_SERVICE_NAME` in `.env`. AWS occasionally renames services and the default may go stale.

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
* **Gemini Code Assist active users** come from a real Cloud Monitoring `timeSeries.list` call, not a manual entry. Cost still does: Cloud Monitoring does not expose dollar amounts. The standard automated cost source is a BigQuery billing export; until you wire that, paste a value into `GOOGLE_GEMINI_MONTHLY_COST_USD`.
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
