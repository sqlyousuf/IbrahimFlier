# Masjid Ibrahim — Flier Studio

A single-page flier generator for Masjid Ibrahim, Klein Islamic Center, Spring TX.
Fill in the event on the left, watch the flier build on the right, then export a
print-quality PNG or a PDF.

## Usage

- Pick an **event type**, then fill in the title, date, and time. Everything else
  (subtitle, speaker, description) is optional and simply disappears when blank.
- For Eid and other moon-dependent events, tick **Moon-sighting** to print an
  alternate date underneath the main one.
- For two jamaats, tick **Add a 2nd time**. The detail band becomes three columns
  and each timing gets its own speaker line.
- Six **palettes** are available — five dark grounds and one ivory. The logo,
  hairlines, and background texture all re-ink themselves to match.
- **Download PNG** exports at 3× (1380 px wide). **Save as PDF / Print** opens the
  flier alone in a print window.

## Layout

```
masjid-flier/
  index.html              the whole app — no build step, no dependencies
  assets/
    IBRAHIM LOGO.ai       vector master
    IBRAHIM LOGO-02.jpg   white lockup on navy   (source for the masks)
    IBRAHIM LOGO-03.jpg   navy lockup on white
    logo-mask.png         greyscale alpha of the full lockup
    crest-mask.png        just the dome + calligraphy, used as the ghost watermark
    pattern.png           seamless 8-point khatam tile, white ink
    pattern-dark.png      the same tile in navy, for the ivory palette
    donate-qr.png         payments.madinaapps.com/masjidibrahimtx
  tools/
    build_assets.py       regenerates everything in assets/ from the logo masters
```

## About the inlined images

`index.html` carries its images as base64 rather than linking them. That is
deliberate: `html2canvas` renders the export through a `<canvas>`, and an image
loaded over `file://` or from another origin would either taint the canvas or
fail outright. Inlining keeps **Download PNG** working when the page is opened
straight off disk.

The logo is stored once, as a **greyscale alpha mask**. At load the page reads
that mask into a canvas, turns the grey level into transparency, and repaints it
in whichever ink the current palette calls for — so one asset serves the white
lockup on navy and the navy lockup on ivory. The same reason the pattern ships as
two tiles instead of one plus a CSS `filter`: `html2canvas` ignores CSS filters,
so a filtered tile would vanish from the exported PNG.

To regenerate the derived art after a logo change:

```bash
pip install pillow numpy
python tools/build_assets.py --emit-b64
```

Then paste each `assets/<name>.b64` into the matching constant at the top of the
`<script>` block in `index.html`.

## Deploy

Static — any host will do. The repo root has a `vercel.json` that serves this
directory, so importing the repo into Vercel and deploying needs no settings.

```bash
npm i -g vercel
vercel --prod
```
