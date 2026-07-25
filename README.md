# Personal Website — lelunar.me / techtesfay.github.io

A minimalist, Apple-inspired personal site built with plain HTML and CSS — no
frameworks, no build step, nothing to install. This repo
([techtesfay/techtesfay.github.io](https://github.com/techtesfay/techtesfay.github.io))
is the single source of truth: every push to `main` deploys automatically to
**both** https://lelunar.me and https://techtesfay.github.io.

## Structure

```
techtesfay.github.io/
├── index.html      # Home — intro, about, at-a-glance, links, visitor counter
├── academic.html   # Experience, research, publications, education, projects
├── interests.html  # Interests + Cloud Resume Challenge resources
├── learning.html   # Topics being studied + articles/write-ups
├── resume.html     # Redirect stub (CloudFront's root document points here)
├── css/style.css   # All styling (colors, fonts, layout)
├── assets/         # Put images, PDFs, etc. here
└── .github/workflows/main.yml  # Deploys to S3 on every push
```

## Run locally

```sh
python3 -m http.server 8000
```

Then open http://localhost:8000

## How to maintain

- **Edit content**: open any `.html` file and change the text. Each list entry
  or card is a small self-contained block — copy/paste one to add more.
- **Change the look**: everything visual lives in `css/style.css`. The colors
  are CSS variables at the top of the file (light and dark mode).
- **Add a page**: copy an existing page, update the `<title>` and content, and
  add a link to it in the `<nav>` of every page.
- **Dark mode**: automatic — follows the visitor's system setting.
- **Publish**: commit and push to `main`. Two deploys fire independently:
  GitHub Actions syncs to the S3 bucket (lelunar.me), and GitHub Pages
  rebuilds automatically from the same branch (techtesfay.github.io).

## Hosting

**lelunar.me** — a static site in the `lelunar` S3 bucket behind CloudFront
(Cloud Resume Challenge setup), with DNS on Cloudflare. The home page footer
shows a visitor counter served by API Gateway + Lambda + DynamoDB.
CloudFront's root document is `resume.html`, which now just redirects to
`index.html`.

**techtesfay.github.io** — GitHub Pages, building from the `main` branch root
on every push. No custom domain is configured for Pages (no `CNAME` file in
this repo) — it's intentionally separate from the S3/CloudFront setup that
serves lelunar.me, not a mirror pointed at the same domain. This repo is
public because Pages on the free plan requires it; there are no secrets in
the codebase (AWS credentials live only in encrypted GitHub Actions secrets).

**Manual S3 deploy** (if Actions is unavailable):

```sh
aws s3 sync . s3://lelunar --delete --cache-control max-age=5 \
  --exclude ".git/*" --exclude ".github/*" --exclude "README.md" \
  --exclude ".gitignore" --exclude "COMMANDS.md"
```

CloudFront caches for only 5 seconds (`max-age=5`), so changes appear almost
immediately; no invalidation needed. GitHub Pages has no manual-deploy
equivalent — it rebuilds automatically on every push, typically within a
minute or two.
