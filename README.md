# Kybele

Greenhouse simulation for Rhino and Grasshopper: Radiance, custom tailored for greenhouse
modeling and metrics (PPFD for 8760 hours, DLI for 365 days, daylight and electric lighting).
One page: https://shafiarch.github.io/Kybele/

Download the plugin: https://www.food4rhino.com/en/app/kybele-greenhouse-simulation

## Publish

Settings, Pages, Build and deployment: Deploy from a branch, `main`, folder `/ (root)`.
No build step; `.nojekyll` makes GitHub serve the files as they are.

## What is where

| What | Where |
| --- | --- |
| The page | `index.html`, `assets/style.css`, `assets/site.js` |
| Pictures the page shows (`-l` opens on click, `-n` is the Night copy) | `img/` |
| Originals, never changed | `Simulation for Food_v3.pptx` (Radiance Workshop 2026), `Kybele_logo_black and orange.png`, `case study UW.png`, `Three_channelworkflow.png`, `hyperspectral_workflow.png` |
| The script that makes `img/` | `tools/build_img.py` (Pillow, numpy, python-pptx; LibreOffice for the monthly renders) |

The charts (spectral responses; DLI, deficit and lamp hours) are drawn in SVG in `index.html`
from the data inside the presentation's charts, so they follow the theme. The logo is the grey
and orange version from the presentation.

## The group photo

The Credits section shows `img/workshop-group-photo.webp` when it exists (Radiance Workshop
2026 group photo, credit Greg Ward); until then the slot stays hidden. Save the photo there as
WebP, about 1600 px wide.

## Credits

Mehlika Inanici (research lead), Gundula Proksch, Shafiul Islam; University of Washington,
Department of Architecture. Presented as "Simulation for Food: Evaluating Urban Greenhouses"
at the 24th International Radiance Workshop, Seattle, September 1, 2026.

## Rules

- No em dashes or en dashes in text, code comments or docs.
- Commits are authored and committed as Shafiul Islam
  (`145989139+ShafiArch@users.noreply.github.com`), with no co-author lines.
- Whenever `assets/style.css` or `assets/site.js` changes, raise `?v=N` on both tags in `index.html`.
