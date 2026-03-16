# IbrahimFlier

This repository deploys the static app in `masjid-flier/`.

## Vercel Deployment

Import the repository into Vercel as-is.

The repo root includes a `vercel.json` that explicitly builds `masjid-flier/index.html` as a static asset and routes all traffic there, so you do not need to move files out of that folder.

If you deploy from the Vercel dashboard:

1. Import the GitHub repository.
2. Leave the Root Directory as the repository root.
3. Deploy with the default settings.