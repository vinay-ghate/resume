# 📄 LaTeX Resume & CI/CD Build Archive

[![Compile All LaTeX Files](https://github.com/vinay-ghate/resume/actions/workflows/main.yml/badge.svg)](https://github.com/vinay-ghate/resume/actions/workflows/main.yml)
[![Latest PDF Archive](https://img.shields.io/github/v/release/vinay-ghate/resume?include_prereleases&label=release%20tag&color=2563eb)](https://github.com/vinay-ghate/resume/releases/tag/pdf-archive)
[![Live Dashboard](https://img.shields.io/badge/live%20dashboard-v1nay.is--a.dev%2Fresume-10b981?style=flat&logo=githubpages&logoColor=white)](https://v1nay.is-a.dev/resume/)
[![Engine](https://img.shields.io/badge/LaTeX-XeLaTeX%20%2F%20pdfLaTeX-008080?logo=latex&logoColor=white)](https://www.latex-project.org/)

An automated, version-controlled LaTeX resume repository paired with a lightweight, accessible **Build History Dashboard** hosted on GitHub Pages.

---

## 🌐 Live Dashboard

Access the latest compiled resume builds, branch timelines, and document previews directly:

👉 **[v1nay.is-a.dev/resume](https://v1nay.is-a.dev/resume/)**

---

## ⚡ Key Highlights

- **Automated Compilation**: Every push to `main` automatically compiles all `.tex` files into production-ready PDFs via GitHub Actions.
- **Permanent Release Archive**: All compiled PDFs are uploaded and version-tagged under the permanent [`pdf-archive`](https://github.com/vinay-ghate/resume/releases/tag/pdf-archive) release tag.
- **Branch-Aware Dashboard**:
  - Independent Hero Cards for parallel resume tracks and branches (e.g. `Dev • 2001`, `GenAI • 1001`, `GenAI • 1005`, and future variants like `1006`).
  - Distinguishes **Preview** (in-browser inspection) from **Download** (direct `.pdf` file).
  - Compact historical build timeline with collapsible past revisions.
  - Client-side caching (10-minute TTL) to safeguard against GitHub API rate limits.
  - Real-time instant search and track filtering.
  - Native Dark & Light theme with automatic OS scheme detection.

---

## 📁 Repository Structure

```text
├── .github/
│   └── workflows/
│       └── main.yml        # CI/CD compilation and release upload pipeline
├── Dev/
│   └── 2001.tex            # Developer track resume source
├── GenAI/
│   ├── 1001.tex            # GenAI track variant 1001
│   └── 1005.tex            # GenAI track variant 1005
├── index.html              # Standalone vanilla JS/CSS build history dashboard
├── robots.txt              # Search engine crawler exclusions
└── README.md               # Repository documentation
```

---

## 🔄 How the CI/CD Pipeline Works

```
   git push origin main
            │
            ▼
┌───────────────────────────┐
│   GitHub Actions Runner   │
│  (ubuntu-latest)          │
└───────────┬───────────────┘
            │
            ├─► 1. Compile all .tex files with xu-cheng/latex-action
            │
            ├─► 2. Rename PDFs: Vinay-Ghate-<Track>-<Variant>-v<Run>.pdf
            │
            └─► 3. Upload to Release tag 'pdf-archive' via softprops/action-gh-release
                        │
                        ▼
┌────────────────────────────────────────────────────────┐
│              GitHub Pages Web Dashboard                │
│             https://v1nay.is-a.dev/resume/             │
│  - Fetches GitHub Release API assets                   │
│  - Groups by Track (Dev / GenAI / Other) & Branch      │
│  - Displays Latest Hero Cards + Historical Timelines   │
└────────────────────────────────────────────────────────┘
```

---

## ➕ Adding a New Resume Track or Branch

The compilation and dashboard system dynamically discovers new tracks and variants without configuration changes:

1. **Add to an existing track**:
   Place a new `.tex` file in `GenAI/` (e.g., `GenAI/1006.tex`) or `Dev/` (e.g., `Dev/2002.tex`).
2. **Add a new track folder**:
   Create a new folder (e.g., `Research/3001.tex`).
3. **Commit & Push**:
   ```bash
   git add .
   git commit -m "feat: add 1006 resume branch"
   git push origin main
   ```
4. **Automatic Detection**:
   - The workflow compiles `1006.tex` to `Vinay-Ghate-GenAI-1006-v<RunNumber>.pdf`.
   - The dashboard automatically detects `GenAI • 1006` as a distinct branch and displays its own **Latest** hero card and revision history.

---

## 🛠️ Local Development & Preview

### Local LaTeX Compilation

Compile any resume directly using your local LaTeX distribution (`TeX Live`, `MacTeX`, or `MiKTeX`). By default, a placeholder `+91-XXXXXXXXXX` will be used unless you pass your phone number:

**With Environment Variable (Linux/macOS/Bash):**
```bash
export PHONE="+91-8605078054"

cd Dev
pdflatex "\def\phoneNumber{$PHONE}\input{2001.tex}"
```

**With Environment Variable (Windows PowerShell):**
```powershell
$env:PHONE = "+91-8605078054"

cd Dev
pdflatex "\def\phoneNumber{$($env:PHONE)}\input{2001.tex}"
```

**Standard compilation (uses default fallback placeholder):**
```bash
cd Dev
pdflatex 2001.tex

cd ../GenAI
pdflatex 1001.tex
pdflatex 1005.tex
```

### Dashboard Preview

The dashboard in `index.html` is completely self-contained (zero build steps, no CDNs or external fonts):

```bash
# Using Python
python -m http.server 8000

# Open in browser:
# http://localhost:8000
```

---

## 🔒 Privacy & Search Indexing

- **Robots Exclusion**: Contains `<meta name="robots" content="noindex">` and [robots.txt](file:///D:/Programming/Web/resume/robots.txt) to prevent search engine indexing.
- **Sanitized UI**: Headings and titles on the dashboard strip personal author prefixes and display clean track and branch identifiers.
