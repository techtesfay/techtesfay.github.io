# Command Reference — lelunar.me / techtesfay.github.io

Copy-paste commands for maintaining this site, in the order you'd need them.
All commands assume you start from the repo root:
`cd ~/workplace/myresume` (local folder name is unchanged; the GitHub repo
itself is now `techtesfay/techtesfay.github.io`)

---

## 1. AWS CLI — one-time setup

Configure credentials (paste the Access key ID and Secret access key from
IAM → Users → your user → Security credentials → Create access key):

```sh
aws configure
```

- Region: `us-east-1`
- Output format: press Enter

Verify it worked:

```sh
aws sts get-caller-identity
```

Confirm you can reach the site bucket:

```sh
aws s3 ls s3://lelunar
```

---

## 2. Preview locally

```sh
python3 -m http.server 8000
```

Open http://localhost:8000 — Ctrl+C to stop the server.

---

## 3. Deploy to S3 (manual upload)

Preview what would change (uploads + deletions) without touching anything:

```sh
aws s3 sync . s3://lelunar --delete --cache-control max-age=5 --dryrun \
  --exclude ".git/*" --exclude ".github/*" --exclude "README.md" \
  --exclude ".gitignore" --exclude "COMMANDS.md"
```

Do it for real (same command without `--dryrun`):

```sh
aws s3 sync . s3://lelunar --delete --cache-control max-age=5 \
  --exclude ".git/*" --exclude ".github/*" --exclude "README.md" \
  --exclude ".gitignore" --exclude "COMMANDS.md"
```

- `--delete` removes bucket files that no longer exist locally (true replace)
- `--cache-control max-age=5` keeps CloudFront refreshing within ~5 seconds

Verify the live site:

```sh
curl -sI https://lelunar.me/ | grep last-modified
```

Or open https://lelunar.me and hard-refresh (Cmd+Shift+R).

List everything currently in the bucket:

```sh
aws s3 ls s3://lelunar --recursive
```

---

## 4. Git — save and publish changes

Check what changed:

```sh
git status
git diff
```

Stage, commit, push (pushing to main triggers both the GitHub Actions deploy
to S3 and a GitHub Pages rebuild automatically):

```sh
git add -A
git commit -m "Describe your change here"
git push origin main
```

See recent history:

```sh
git log --oneline -10
```

Undo edits to a file you haven't committed yet:

```sh
git checkout -- filename.html
```

---

## 5. Occasional / troubleshooting

Force CloudFront to drop its cache (rarely needed with max-age=5; requires
the distribution ID from the CloudFront console):

```sh
aws cloudfront list-distributions \
  --query "DistributionList.Items[].{id:Id,domain:Aliases.Items[0]}"
aws cloudfront create-invalidation --distribution-id <DIST_ID> --paths "/*"
```

Check the visitor counter API directly:

```sh
curl https://mly622flj9.execute-api.us-east-1.amazonaws.com/items
```

Check both live sites and deploy status:

```sh
curl -sI https://lelunar.me/ | grep last-modified
curl -sI https://techtesfay.github.io/ | grep last-modified
```

- GitHub Actions (S3 deploy) runs: https://github.com/techtesfay/techtesfay.github.io/actions
- GitHub Pages build status: https://github.com/techtesfay/techtesfay.github.io/deployments
