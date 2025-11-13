# Documentation Index & Publishing Plan

Central registry for every living document in `docs/`, plus the workflow to render and publish the collection to GitHub Pages with rich cross-linking.

## Document map

| Doc | Purpose | Key Links | | --- | --- | --- | | `README.md` | Quick start + CLI overview | Link to `docs/OPERATOR_GUIDE.md`, `docs/PROJECT_LAUNCH.md`, GUI docs | | `docs/PROJECT_LAUNCH.md` | Original stack rationale + feature matrix | Cross-link to CLI commands, roadmap | | `docs/OPERATOR_GUIDE.md` | Task recipes & pipelines | Links to CLI reference, Doctor instructions | | `docs/CLI_REFERENCE/*.md` | Command-by-command syntax/behavior | Linked from Operator Guide and Typer help | | `docs/GUI_OVERVIEW.md` | UX principles & flows (Reader default-app spec, navigation) | Link to `docs/GUI_TECH.md`, `docs/GUI_WIREFRAMES.md` | | `docs/GUI_TECH.md` | Architecture, Reader rendering stack, packaging | Link back to CLI utilities + CI plan | | `docs/GUI_WIREFRAMES.md` | Visual sketches | Link to overview + future screenshots | | `docs/GUI_USER_GUIDE.md` | Panel walkthrough + Reader controls appendix + default-app workflow | References Operator Guide + GUI Tech | | `docs/GUI_SCREENSHOTS.md` | Screenshot capture plan | Link to assets under `docs/assets/screenshots/` | | `docs/SURFER_FIGURE_EXPORT.md` | Presets/workflow for 2–5 MB figure exports | Link to `CLI_REFERENCE/figure.md`, GUI Optimize panel | | `docs/CONTRIBUTOR_GUIDE.md` | Dev workflow, coding standards | Link to Testing Handbook, Release Playbook | | `docs/TESTING_HANDBOOK.md` | Test layers, CI expectations | Link to Troubleshooting FAQ | | `docs/TROUBLESHOOTING_FAQ.md` | Common issues & fixes (Reader/QtPdf, CLI tools) | Link to Security/Privacy | | `docs/SECURITY_PRIVACY.md` | Handling sensitive data | Link to Redaction/Security sections | | `docs/RELEASE_PLAYBOOK.md` | Release checklist & changelog template | Link to Roadmap | | `docs/ARCHITECTURE_OVERVIEW.md` | System diagram & components | Link to GUI Tech + Project Launch | | `docs/ROADMAP.md` | Milestones, branch rules | Link to Docs Index + Contributor Guide | | `docs/DOCS_INDEX.md` | (This file) – portal + publishing plan | Link to site root |

**Linking convention:** each document should include “Related docs” section referencing neighbors via relative links (e.g., `[GUI Tech](GUI_TECH.md)`), enabling Markdown cross-refs locally and on the published site.

## Static site plan

1. **MkDocs + Material theme**
   - Add `mkdocs.yml` with navigation mirroring the table above.
   - Use `plugins: [search, awesome-pages]` for automatic nav and search.
   - Enable `markdown_extensions` for admonitions, code tabs, and `toc`.
1. **Directory layout**
   ```
   mkdocs.yml
   docs/           # existing markdown lives here
   site/           # build output (ignored)
   ```
1. **Cross-linking**
   - Use relative links (`[Operator Guide](OPERATOR_GUIDE.md)`) so both GitHub and MkDocs resolve them.
   - Add `back-to-index` links at the bottom of each doc pointing to this file.

## GitHub Actions automation

Create `.github/workflows/docs.yml`:

```yaml
name: Docs
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.x' }
      - run: pip install mkdocs-material mkdocs-awesome-pages-plugin
      - run: mkdocs build
  deploy:
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    needs: build
    runs-on: ubuntu-latest
    permissions: { pages: write, id-token: write }
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.x' }
      - run: pip install mkdocs-material mkdocs-awesome-pages-plugin
      - run: mkdocs gh-deploy --force
```

Enable GitHub Pages (`Settings ▸ Pages ▸ Build from GitHub Actions`). The deployed site will live at `https://<org>.github.io/pdfsuite/`. Link it from `README.md` once live.

## CI & documentation integration

- Docs workflow runs alongside lint/smoke tests; PRs must keep `mkdocs build` passing to avoid broken nav.
- Add `markdownlint` or `mdformat` later for consistent style.
- Use status badges in `README.md` referencing the `Docs`, `CI`, and `Release` workflows.

## Next steps

1. Add `mkdocs.yml` matching the Document map and commit minimal site config.
1. Create `.github/workflows/docs.yml` (per above) and enable GitHub Pages.
1. Update each doc with a “Related docs” section linking back here to keep cross-links healthy.

______________________________________________________________________

Related docs: [Roadmap](ROADMAP.md) · [GUI Overview](GUI_OVERVIEW.md) · [Operator Guide](OPERATOR_GUIDE.md)
