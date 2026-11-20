# Portfolio privacy and publication checklist

**The original source and client deliverable remain unchanged and private.** Make a dedicated `portfolio_preview/` folder for public material, outside any real client's private data directory.

## Prefer aggregate screenshots

Show KPIs, month/category charts, general method, and non-sensitive product rankings. Never show original transaction, customer, receipt, support-note, or change-log tabs just because those tabs exist in a workbook.

## If row-level examples are necessary

1. **Best:** Make a fresh, completely synthetic dataset with plausible invented records and clearly label it an illustration.
2. **Sometimes appropriate:** Replace names with consistent pseudonyms such as `Customer 001`, `Customer 002`; use a separate mapping if needed for consistent references. Do not publish the mapping.
3. **Remove entirely:** emails, addresses, phone numbers, free-text notes, raw receipt IDs, account numbers, payment IDs, and other identifying or commercially sensitive fields.
4. **Consider indirect identifiers:** unusual combinations of dates, exact purchase amounts, locations, categories, and events can still reveal identity. Generalize or replace them as necessary.
5. **Check product confidentiality:** internal SKUs, suppliers, costs, and margins may be sensitive even when customer names are removed.

`[REDACTED]` is suitable for an occasional intentionally hidden field, not as a substitute for a designed demonstration dataset.

## Publication safety checks

- [ ] Label the project **SIMULATED / FICTIONAL CLIENT** near its title and wherever a testimonial appears.
- [ ] Never claim fictional clients were real paying customers or that permission from a fictional owner is real-world authorization.
- [ ] Use only safe data in screenshots; keep the private workbook out of public GitHub and website folders.
- [ ] If showing a workbook, inspect **every tab**, hidden tab, defined name, formulas, comments, hyperlinks, charts, images, and file properties for identifiers.
- [ ] Check screenshots for cropped/offscreen rows, selection bars, personal Windows paths, file names, and tooltips.
- [ ] Keep true source data and a portfolio copy in different directories.
- [ ] If actual clients are involved later, obtain explicit written permission about specific content before posting.

**Important:** `pseudonymize_column()` swaps one named column; it does not make an entire dataset anonymous. Avoid publishing a row-level export unless manually reviewed and approved.
