# CLAUDE.md - AI Assistant Guide for web-rabbithole223.com

## Project Overview

This is the source repository for **rabbithole223.com**, a Hugo-based static site about home mushroom cultivation and mycology. The site publishes blog posts, product recommendations, and educational content.

- **Framework:** Hugo static site generator (v0.155.3+)
- **Theme:** Mainroad (v2+)
- **Hosting:** AWS Amplify
- **Content format:** Markdown with YAML front matter
- **License:** BSD 2-Clause (Copyright 2024, Joshua SS Miller)

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
│   │   ├── 2024/               # 2024 articles
│   │   ├── 2025/               # 2025 articles
│   │   ├── 2026/               # 2026 articles
│   │   └── magic-quadrant/     # Psilocybin/legal category
│   │       └── 2024/
│   ├── docs/                   # Static pages (welcome, FAQ, affiliate links, crypto)
│   └── page/                   # Standalone pages (about)
├── layouts/partials/           # Custom layout overrides
│   └── footer.html             # Footer with Goatcounter analytics
├── themes/mainroad/            # Hugo Mainroad theme (DO NOT edit directly)
├── static/img/                 # Local static images (logos)
├── archetypes/default.md       # Hugo new content template
├── scripts/                    # Utility scripts
│   └── validate-affiliate-links.sh
├── .github/
│   ├── workflows/              # GitHub Actions (3 workflows)
│   │   ├── claude.yml          # @claude mention handler
│   │   ├── claude-code-review.yml  # Auto PR code review
│   │   └── issue-to-pr.yml    # Auto-generate PRs from issues
│   └── scripts/
│       └── analyze_issue.py    # Issue analyzer (Python/Claude API)
├── amplify.yml                 # AWS Amplify build config
├── public/                     # Built site output (generated)
└── resources/                  # Hugo resource cache (generated)
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

### Content Categories

- General cultivation posts: `content/post/<YEAR>/`
- Psilocybin/legal content: `content/post/magic-quadrant/<YEAR>/` with category `["MAGIC-QUADRANT"]`
- Documentation/static pages: `content/docs/`

### Image Hosting

All images are hosted on CloudFront CDN, **not** in the repository.

- S3 bucket: `s3://static-origin.rabbithole223.com/images/`
- CDN URL pattern: `https://static.rabbithole223.com/images/<path>`
- Only logos live locally in `static/img/`

## Hugo Configuration

Configuration uses TOML files in `config/`:

- `config/_default/config.toml` — Main config (theme settings, sidebar widgets, social links, fonts, colors)
- `config/_default/menus.toml` — Navigation menu (currently one item: "Magic Quadrant")
- `config/production/hugo.toml` — Production `baseurl` and `title`
- `config/staging/hugo.toml` — Staging `baseurl` and `title`

Key site parameters:
- Theme: `mainroad`
- Highlight color: `#e22d30`
- Fonts: Open Sans (primary), SFMono-Regular/Menlo/Monaco (monospace)
- Markdown rendering: `unsafe = true` (allows raw HTML in content)
- Analytics: Goatcounter (`rabbits.goatcounter.com`)
- Search: DuckDuckGo site search

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

1. Create a new `.md` file in `content/post/<YEAR>/`
2. Add YAML front matter (see template above)
3. Write content in Markdown
4. Reference images via CloudFront CDN URL
5. Set `draft: false` when ready to publish
6. Commit and push to `stage` for staging preview, then merge to `main` for production

### Affiliate Link Validation

```bash
# Run the link validator
bash scripts/validate-affiliate-links.sh
```

This checks all links in `content/docs/affiliate-links.md` and generates a timestamped report.

## GitHub Actions & Automation

### 1. Claude Code (`claude.yml`)
- Triggered by `@claude` mentions in issues, PRs, and comments
- Uses `anthropics/claude-code-action@v1`
- Requires secret: `CLAUDE_CODE_OAUTH_TOKEN`

### 2. Claude Code Review (`claude-code-review.yml`)
- Auto-reviews all PRs on open/sync/ready
- Uses Claude Code plugin: `code-review@claude-code-plugins`
- Requires secret: `CLAUDE_CODE_OAUTH_TOKEN`

### 3. Issue-to-PR (`issue-to-pr.yml`)
- Triggered on issue creation
- Runs `.github/scripts/analyze_issue.py` (Python 3.11)
- Uses Claude API to analyze issues and auto-generate blog post PRs
- Supports model selection in issue body: `model: claude-opus-4-6`
- PRs target the `stage` branch
- Requires secrets: `ANTHROPIC_API_KEY`, `IMPLEMENT_TOKEN_RH223`

## Key Conventions

### Do
- Keep blog posts in the correct year directory under `content/post/`
- Use CloudFront CDN URLs for all images (`https://static.rabbithole223.com/images/...`)
- Set `draft: false` only when content is ready to publish
- Target PRs to `stage` branch for review before merging to `main`
- Use YAML front matter (not TOML) in content files
- Follow existing filename conventions: lowercase, hyphen-separated (e.g., `growing-gteachers.md`)

### Don't
- Don't edit files directly inside `themes/mainroad/` — use `layouts/` overrides instead
- Don't commit images to the repo — upload to S3 and use CDN URLs
- Don't push directly to `main` without staging verification
- Don't modify `public/` or `resources/` — these are generated directories
- Don't remove the Goatcounter script from `layouts/partials/footer.html`

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
