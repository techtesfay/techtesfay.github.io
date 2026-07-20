# Personal Website

A minimalist, Apple-inspired personal site built with plain HTML and CSS — no
frameworks, no build step, nothing to install.

## Structure

```
personal-website/
├── index.html      # Home — intro, about, links
├── academic.html   # Publications, research projects, education
├── interests.html  # Articles, tools, ideas worth sharing
├── learning.html   # Topics being studied + notes
├── css/style.css   # All styling (colors, fonts, layout)
└── assets/         # Put images, PDFs, etc. here
```

## Run locally

```sh
cd personal-website
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

## Deploy to lelunar.me (S3 + CloudFront)

The site lives at https://lelunar.me — a static site in an S3 bucket behind
CloudFront (Cloud Resume Challenge setup), with DNS on Cloudflare. The home
page footer shows a visitor counter served by API Gateway + Lambda + DynamoDB.

**Via the existing GitHub Actions pipeline (recommended):** copy these files
into the Cloud Resume Challenge repo (replacing the old `index.html`), commit,
and push — the workflow syncs to S3 automatically.

**Directly from this machine:**

```sh
aws configure                          # one-time credential setup
aws s3 ls                              # find the bucket name
cd personal-website
aws s3 sync . s3://<BUCKET> --delete --exclude "README.md" --exclude ".git/*"
```

CloudFront caches for only 5 seconds (`max-age=5`), so changes appear almost
immediately; no invalidation needed. If that ever changes:

```sh
aws cloudfront create-invalidation --distribution-id <DIST_ID> --paths "/*"
```
