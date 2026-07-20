# Personal Website — lelunar.me

A minimalist, Apple-inspired personal site built with plain HTML and CSS — no
frameworks, no build step, nothing to install. This repo is the single source
of truth: every push to `main` deploys to https://lelunar.me.

## Structure

```
myresume/
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
- **Publish**: commit and push to `main` — GitHub Actions syncs the repo to
  the S3 bucket automatically.

## Hosting (S3 + CloudFront)

The site lives at https://lelunar.me — a static site in the `lelunar` S3
bucket behind CloudFront (Cloud Resume Challenge setup), with DNS on
Cloudflare. The home page footer shows a visitor counter served by
API Gateway + Lambda + DynamoDB. CloudFront's root document is `resume.html`,
which now just redirects to `index.html`.

**Manual deploy** (if Actions is unavailable):

```sh
aws s3 sync . s3://lelunar --delete --cache-control max-age=5 \
  --exclude ".git/*" --exclude ".github/*" --exclude "README.md"
```

CloudFront caches for only 5 seconds (`max-age=5`), so changes appear almost
immediately; no invalidation needed.
