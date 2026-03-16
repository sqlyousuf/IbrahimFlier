# Masjid Ibrahim — Flier Generator

A flier generator for Masjid Ibrahim Klein Islamic Center, Spring TX.

## How to Deploy

### 1. Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit — Masjid Ibrahim Flier Generator"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/masjid-flier.git
git push -u origin main
```

### 2. Deploy to Vercel

**Option A — Vercel Dashboard (easiest):**
1. Go to [vercel.com](https://vercel.com) and sign in
2. Click **"Add New Project"**
3. Import your GitHub repo
4. Click **Deploy** — no settings needed, it auto-detects static HTML

**Option B — Vercel CLI:**
```bash
npm install -g vercel
vercel login
vercel --prod
```

### 3. Done!
Vercel gives you a live URL like `https://masjid-flier.vercel.app`

---

## Usage
- Fill in event details on the left panel
- The flier preview updates live on the right
- Click **Generate Flier** then **Download as PNG**
- For moon-sighting events, check the alternate date option
- For two prayer times (e.g. Eid), check "Add 2nd Time / Prayer"
