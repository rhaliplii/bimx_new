# Publishing to Hostinger

`.github/workflows/deploy.yml`:

| Event | What happens |
|---|---|
| push to `main` | the test copy is built (`BIMX_MIRROR=1`) and uploaded to the **staging** site (password, noindex) |
| push of a tag `v…` (`npm run release`) | the site is built from that tag and uploaded to **bimx.md**, after a backup of the current site |
| Actions → Deploy → Run workflow, choosing an older tag | that release is published again (rollback) |

Every run keeps the built site as an artifact for 90 days and checks the published site afterwards (`version.txt`
shows the commit, main pages answer 200, `…/index.html` answers 301, unknown pages 404). Until the secrets below exist,
the workflow builds the site and stops with a warning instead of publishing.

## One-time setup

### 1. Hostinger (hPanel)

1. **SSH:** Advanced → SSH Access → enable. Note host, port (usually 65002) and user.
2. **Deploy key:** on your computer `ssh-keygen -t ed25519 -f bimx-deploy -N ""`; in hPanel → SSH Access → SSH keys,
   add the content of `bimx-deploy.pub`. The private key `bimx-deploy` goes to GitHub (step 3) and nowhere else.
3. **Site folder:** check the path of the site in the file manager, for example `domains/bimx.md/public_html`
   (relative to the SSH home folder). Look at what is in it: files that are not part of the site and must stay go to
   `deploy/keep.txt`, everything else is replaced by the deployment (`rsync --delete`). The old `new_site/` copy can be deleted.
4. **Staging subdomain:** Domains → Subdomains → `staging` → note its folder. If hPanel puts it inside `public_html`
   (e.g. `public_html/staging`), keep `staging/` in `deploy/keep.txt` so that publishing bimx.md does not delete it.
5. **Staging password:** create the password file outside the site folders, e.g. over SSH:
   `htpasswd -c ~/.htpasswd-staging bimx` (or hPanel → Password Protect Directories, then note the file path).
6. **SSL for staging:** Security → SSL → install the free certificate for `staging.bimx.md` once the DNS record works.

### 2. DNS (dns.md)

The DNS of bimx.md is not at Hostinger but at dns.md. Whoever manages the domain adds:

```
staging   A   45.84.207.239
```

(the same address as bimx.md; check it in hPanel → Domains if the hosting changes).

### 3. GitHub (repository Settings)

**Secrets** (Settings → Secrets and variables → Actions → Secrets):

| Name | Value |
|---|---|
| `HOSTINGER_HOST` | SSH host from hPanel |
| `HOSTINGER_PORT` | SSH port (65002 if empty) |
| `HOSTINGER_USER` | SSH user |
| `HOSTINGER_SSH_KEY` | content of the private key `bimx-deploy` |
| `HOSTINGER_KNOWN_HOSTS` | output of `ssh-keyscan -p <port> <host>` |
| `STAGING_AUTH` | `user:password` of the staging site (for the check after publishing) |

**Variables** (same page → Variables):

| Name | Example |
|---|---|
| `PROD_PATH` | `domains/bimx.md/public_html` |
| `STAGING_PATH` | `domains/bimx.md/public_html/staging` |
| `STAGING_URL` | `https://staging.bimx.md/` |
| `STAGING_HTPASSWD` | `/home/u123456789/.htpasswd-staging` (absolute path on the server) |

Optional: Settings → Environments → `production` → *Deployment branches and tags*: only tags `v*`, and, if wanted,
*Required reviewers* (needs an organisation or admin rights on the repository).

## Publishing a release

```
npm run release           # tags origin/main as vYYYY.MM.DD (.2, .3 … the same day) and pushes the tag
```

Or on GitHub: Releases → Draft a new release → new tag `v2026.12.05` on `main` → Publish. Follow it in Actions → Deploy.

## Rollback

- Actions → Deploy → Run workflow → *Use workflow from*: the previous tag → Run. That release is built and published again.
- Emergency: every production deployment first saves the site to `~/backups/bimx-<date>-<tag>.tar.gz` on the server
  (the last 10 are kept); unpack one into the site folder.
