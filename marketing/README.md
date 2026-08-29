# OpenSourceRail Outreach

This directory turns the current design catalogue into reviewable outreach
packages without sending messages or inventing contact details.

The campaign scope is the developing world: 265 city models in 43 countries.
The Lyon engineering design remains available for comparison but is excluded
from campaign metrics, examples, images and recipient packages.

## What is generated

- `campaigns/<region>/<country>/`: one national campaign and email string;
- `campaigns/<region>/<country>/<city>/`: one municipality campaign and email
  string for every retained city design;
- `campaigns/international/`: audience-specific approaches for development banks,
  project facilities, climate and transport networks, charities, foundations,
  universities, research funders, open-data collaborators and specialist media;
- `contact-research.csv`: role-based recipient queue. Empty addresses mean
  research is still required, not permission to guess or scrape an address;
- `manifest.json`: hashes and coverage counts for deterministic review.

Each campaign links to the authoritative design, finance evidence, network map
and simulation dashboard. Planning figures remain screening results, not bids,
funding approvals, government endorsements or construction-ready estimates.

## Use

1. Verify the current office holder and an official organisational address.
2. Record the address, official source URL, verification date and lawful outreach
   basis in [`contact-overrides.toml`](contact-overrides.toml), then regenerate
   `contact-research.csv`.
3. Personalise the first paragraph; do not bulk-send unchanged messages.
4. Send from `hayder@modernecotech.com`, using the listed images as links or
   attachments, and retain opt-out and response records.
5. Keep personal data out of Git. Commit only durable role addresses published
   for public enquiries.

Regenerate or check every package with:

```bash
python3 scripts/generate-marketing-campaigns.py
python3 scripts/generate-marketing-campaigns.py --check
```

International contact routes are curated in
[`international-targets.toml`](international-targets.toml). Campaign content is
generated from the design catalogue; edit the generator rather than generated
files.

International emails are deliberately different by audience: finance targets
receive eligibility and project-preparation enquiries, nonprofits receive
technical or programme-fit requests, and media receive independent story pitches.
Regional targets receive only the matching city metrics, examples and images;
global targets retain the complete catalogue.
