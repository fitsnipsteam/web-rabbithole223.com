# CLAUDE.md - AI Assistant Guide for web-rabbithole223.com

## Project Overview

This is the source repository for **rabbithole223.com**, a Hugo-based static site about home mushroom cultivation and mycology. The site publishes blog posts, product recommendations, and educational content.

- **Framework:** Hugo static site generator (v0.155.3+)
- **Theme:** Mainroad (v2+)
- **Hosting:** AWS Amplify
- **Content format:** Markdown with YAML front matter
- **License:** BSD 2-Clause (Copyright 2024, Joshua SS Miller)
- **Owner:** fitsnipsteam (GitHub org)

## Repository Structure

```
├── config/                     # Hugo configuration (TOML)
│   ├── _default/
│   │   ├── config.toml         # Main site config (theme, params, widgets)
│   │   └── menus.toml          # Navigation menu items
│   ├── production/hugo.toml    # Production overrides (baseurl, title)
│   └── staging/hugo.toml       # Staging overrides
├── content/                    # All site content (Markdown)
│   ├── post/                   # Blog posts organized by year
│   │   ├── 2024/               # 2024 articles (24 posts)
│   │   ├── 2025/               # 2025 articles (7 posts)
│   │   ├── 2026/               # 2026 articles (1 post)
│   │   ├── magic-quadrant/     # Psilocybin/legal category
│   │   │   └── 2024/           # (5 posts)
│   │   ├── notes.md            # Draft notes
│   │   └── projects.md         # Projects list
│   ├── docs/                   # Static pages
│   │   ├── welcome.md          # Welcome page
│   │   ├── affiliate-links.md  # Product recommendations & affiliate links
│   │   ├── faq.md              # FAQ
│   │   └── crypto-tips.md      # Cryptocurrency donation wallets
│   └── page/                   # Standalone pages
│       └── about.md            # About page
├── layouts/partials/           # Custom layout overrides
│   └── footer.html             # Footer with Goatcounter analytics
├── themes/mainroad/            # Hugo Mainroad theme (DO NOT edit directly)
├── static/img/                 # Local static images (logos only)
├── archetypes/default.md       # Hugo new content template
├── scripts/                    # Utility scripts
│   └── validate-affiliate-links.sh
├── aws/                        # Bundled AWS CLI v2 installer
├── .github/
│   ├── workflows/              # GitHub Actions (3 workflows)
│   │   ├── claude.yml          # @claude mention handler
│   │   ├── claude-code-review.yml  # Auto PR code review
│   │   └── issue-to-pr.yml    # Auto-generate PRs from issues
│   └── scripts/
│       └── analyze_issue.py    # Issue analyzer (Python/Claude API)
├── amplify.yml                 # AWS Amplify build config
├── public/                     # Built site output (generated, do not edit)
└── resources/                  # Hugo resource cache (generated, do not edit)
```

## Git Branching & Deployment

| Branch | Purpose | Deployment Target |
|--------|---------|-------------------|
| `main` | Production | rabbithole223.com (AWS Amplify auto-deploy) |
| `stage` | Staging | staging.rabbithole223.amplifyapp.com |
| `master` | Legacy (unused) | — |

- Push to `main` triggers a production build and deploy.
- Push to `stage` triggers a staging build and deploy.
- PRs from automation target the `stage` branch.
- Build command: `hugo --environment $HUGO_ENV`
- Build output: `/public` directory.
- Automated branches use the pattern `issue-{NUMBER}-{slug}` (from issue-to-pr workflow).

## Content Authoring

### Blog Post Front Matter (YAML)

New posts go in `content/post/<YEAR>/filename.md`. Use this front matter template:

```yaml
---
title: "Article Title"
date: 2025-03-02T12:00:00Z
tags: ["tag1", "tag2"]
thumbnail: "https://static.rabbithole223.com/images/<path>.jpg"
description: "Short SEO description"
categories: ["Category"]
draft: false
---
```

**Required fields:** `title`, `date`, `draft`
**Common fields:** `tags`, `thumbnail`, `description`, `categories`
**Optional fields:** `author`, `authorbox`, `sidebar`, `pager`, `menu`, `weight`

Both inline YAML (`tags: ["a", "b"]`) and block YAML (`tags:\n  - a\n  - b`) styles are used across the codebase. Either is acceptable.

### Content Categories

| Category | Path | Notes |
|----------|------|-------|
| General cultivation | `content/post/<YEAR>/` | Most posts live here |
| Psilocybin / legal | `content/post/magic-quadrant/<YEAR>/` | Use category `["MAGIC-QUADRANT"]` |
| Documentation / static | `content/docs/` | welcome, FAQ, affiliate links, crypto tips |
| Standalone pages | `content/page/` | about page |

### Image Hosting

All images are hosted on CloudFront CDN, **not** in the repository.

- S3 bucket: `s3://static-origin.rabbithole223.com/images/`
- CDN URL pattern: `https://static.rabbithole223.com/images/<path>`
- Only logos live locally in `static/img/`
- Thumbnail images in posts reference the CDN (e.g., `https://static.rabbithole223.com/images/2025/512-growing-goldenteachers.jpg`)

## Hugo Configuration

Configuration uses TOML files in `config/`:

- `config/_default/config.toml` — Main config (theme settings, sidebar widgets, social links, fonts, colors)
- `config/_default/menus.toml` — Navigation menu (currently one item: "Magic Quadrant")
- `config/production/hugo.toml` — Production `baseurl` and `title` (note: currently empty/minimal)
- `config/staging/hugo.toml` — Staging `baseurl` (`https://staging.rabbithole223.amplifyapp.com/`) and `title`

Key site parameters:
- Theme: `mainroad`
- Pagination: 10 posts per page
- Highlight color: `#e22d30`
- Fonts: Open Sans (primary), SFMono-Regular/Menlo/Monaco (monospace)
- Markdown rendering: `unsafe = true` (allows raw HTML in content)
- Analytics: Goatcounter (`rabbits.goatcounter.com`)
- Search: DuckDuckGo site search
- Author: "RH223" with avatar hosted on CDN
- Features enabled: OpenGraph, Schema markup, Twitter Cards, TOC, MathJax

## Development Workflow

### Local Development

```bash
# Install Hugo (macOS)
brew install hugo

# Run local dev server
hugo server

# Build the site
hugo

# Build for a specific environment
hugo --environment staging
hugo --environment production

# Validate config
hugo config --environment <env_name>

# Create new content
hugo new content post/<YEAR>/my-article.md
```

### Adding a New Blog Post

1. Create a new `.md` file in `content/post/<YEAR>/` (use current year)
2. Add YAML front matter (see template above)
3. Write content in Markdown
4. Reference images via CloudFront CDN URL
5. Set `draft: false` when ready to publish
6. Commit and push to `stage` for staging preview, then merge to `main` for production

### Affiliate Link Validation

```bash
# Run the link validator (full check)
bash scripts/validate-affiliate-links.sh

# Quick mode (status codes only, skip Amazon product checks)
bash scripts/validate-affiliate-links.sh --quick
```

This checks all links in `content/docs/affiliate-links.md` and generates a timestamped report in the repo root (`affiliate-links-report-YYYYMMDD-HHMMSS.txt`).

## GitHub Actions & Automation

### 1. Claude Code (`claude.yml`)
- Triggered by `@claude` mentions in issues, PRs, and comments
- Also triggers on issue open/assign events containing `@claude`
- Uses `anthropics/claude-code-action@v1`
- Requires secret: `CLAUDE_CODE_OAUTH_TOKEN`

### 2. Claude Code Review (`claude-code-review.yml`)
- Auto-reviews all PRs on open/sync/ready/reopen
- Uses Claude Code plugin: `code-review@claude-code-plugins`
- Requires secret: `CLAUDE_CODE_OAUTH_TOKEN`

### 3. Issue-to-PR (`issue-to-pr.yml`)
- Triggered on issue creation and issue comments
- Runs `.github/scripts/analyze_issue.py` (Python 3.11)
- Uses Claude API to analyze issues and auto-generate blog post PRs
- Default model: `claude-haiku-4-5-20251001`; override via `model: <model-id>` in issue body
- Valid models: `claude-haiku-4-5-20251001`, `claude-sonnet-4-5-20250929`, `claude-opus-4-6`
- Skips processing for bot-created issues
- Auto-created branches: `issue-{NUMBER}-{slug}` based off `origin/stage`
- PRs target the `stage` branch
- Requires secrets: `ANTHROPIC_API_KEY`, `IMPLEMENT_TOKEN_RH223`
- GitHub API owner/repo is configured as `fitsnips/web-rabbithole223.com` in the script

## Key Conventions

### Do
- Keep blog posts in the correct year directory under `content/post/`
- Use CloudFront CDN URLs for all images (`https://static.rabbithole223.com/images/...`)
- Set `draft: false` only when content is ready to publish
- Target PRs to `stage` branch for review before merging to `main`
- Use YAML front matter (not TOML) in content files
- Follow existing filename conventions: lowercase, hyphen-separated (e.g., `growing-gteachers.md`)
- New automated blog posts default to `content/post/2026/` (current year)

### Don't
- Don't edit files directly inside `themes/mainroad/` — use `layouts/` overrides instead
- Don't commit images to the repo — upload to S3 and use CDN URLs
- Don't push directly to `main` without staging verification
- Don't modify `public/` or `resources/` — these are generated directories
- Don't remove the Goatcounter script from `layouts/partials/footer.html`
- Don't commit affiliate-links-report files (generated locally by the validator script)

## External Services & Secrets

| Service | Purpose | Secret Key |
|---------|---------|------------|
| AWS Amplify | Hosting & deployment | (configured in AWS) |
| Goatcounter | Privacy-focused analytics | (no secret, public script) |
| Claude API | Issue analysis & content generation | `ANTHROPIC_API_KEY` |
| GitHub API | PR creation from issues | `IMPLEMENT_TOKEN_RH223` |
| Claude Code | GitHub Actions integration | `CLAUDE_CODE_OAUTH_TOKEN` |

## Social & Branding

- Twitter: @rabbithole223
- YouTube: @therabbithole223
- Linktree: linktr.ee/rabbithole223
- Rumble: rumble.com/c/c-5592714
- Merch: rabbithole223.creator-spring.com
- Site motto: "Knowledge by Errors"
