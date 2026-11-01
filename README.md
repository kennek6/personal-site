# katekennedy.ca — personal academic site (Quarto + GitHub Pages)

Built fresh rather than copied from the `lab-site` repo, so that no unpublished KEEL site
history comes with it. History was squashed to a single commit before launch (2026-11-01).

## Open items

- `publications.bib`: two co-author first names are initials-only (`Fernando, S`,
  `Jeganathan, P`). Fixes here are overwritten by a fresh Paperpile export, as is the
  shortened journal name on `Braun2026`.
- `index.qmd`: personal line still to write (placeholder comment in the file).

## Deploy

`.github/workflows/publish.yml` renders and pushes to the `gh-pages` branch on every push
to `main`. The `gh-pages` branch was created once by running `quarto publish gh-pages`
locally. If the workflow is ever disabled again: `gh workflow enable "Publish site"`.

## DNS for katekennedy.ca

`CNAME` is already in the repo and listed under `project: resources:`, so Quarto copies it
into `_site/`. At the registrar, point the apex at GitHub Pages:

```
A     @      185.199.108.153
A     @      185.199.109.153
A     @      185.199.110.153
A     @      185.199.111.153
CNAME www    kennek6.github.io
```

Then GitHub repo Settings → Pages → source `gh-pages`, and enable "Enforce HTTPS" once the
certificate provisions (can take an hour).

## Routine operations

**Add a publication**: append a BibTeX entry to `publications.bib`. Optional `pdf`, `code`,
and `data` fields become link buttons. Commit and push; the Action rebuilds (~2 min).

## Local preview

`quarto preview` (requires Quarto; Python 3 runs the pre-render script).

Render the **whole project** (`quarto render`), not a single file — rendering one file writes
its output to the repo root instead of `_site/`. Those strays are gitignored.
