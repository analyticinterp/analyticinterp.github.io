# Analytic Interpretability Blog

Static blog generator using pandoc with LaTeX math support and GitHub comments.

## Prerequisites

- Python 3.6+
- [pandoc](https://pandoc.org/installing.html)

## Usage

### Writing Posts

Create markdown files in `posts/` with this format:

```markdown
---
title: "Your Post Title"
author: "Your Name"
date: "2025-01-21"
description: "Brief description for index/RSS"
---

# Your Post Title

Content with $\LaTeX$ math: $\alpha + \beta = \gamma$

Display equations:
$$\int_0^\infty e^{-x^2} dx = \frac{\sqrt{\pi}}{2}$$
```

### Development

```bash
# Development server with auto-reload (recommended)
python dev-server.py

# Simple live preview (manual refresh)
python watch-simple.py

# Manual build
python build.py
```

### Deployment

```bash
# Build and commit
./deploy.sh
git push
```

Configure GitHub Pages to serve from the `docs/` directory.

**If you get "Address already in use" errors:**
```bash
# Kill any running servers
pkill -f "python.*server"
```

## Features

- **Math rendering**: KaTeX for LaTeX equations
- **Comments**: GitHub Discussions via Giscus
- **RSS feed**: Automatically generated
- **Fast builds**: Pandoc processing

## File Structure

```
├── posts/             # Markdown files
├── templates/         # HTML templates  
├── static/            # CSS and JS
├── docs/              # Generated site
├── build.py           # Build script
├── dev-server.py      # Development server with auto-reload
├── watch-simple.py    # Simple live preview (manual refresh)
└── deploy.sh          # Deployment script
``` 