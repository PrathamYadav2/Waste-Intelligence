# Design System
**Feel:** serious environmental-intelligence dashboard; restrained, legible, no decorative gradients.
**Colour (tokens.css):** ink #16282b, surface #f4f7f6, panel #fff, lagoon #0e6a6a (primary), lichen #5f8a35 (recovery/positive), amber #a97a09 (warning/unverified), brick #a53333 (error), tide #2f5d8a (ML/info). Dark mode via `prefers-color-scheme`.
**Type:** Schibsted Grotesk with system fallback (font file not bundled; add via self-hosting later). Scale 12/14/16/20/26/34 px, tabular numerals for data. Sentence case.
**Space:** 4/8/12/16/24/32/48. **Radius:** 4 (inputs, badges), 8 (cards), 14 (chain nodes). **Shadow:** one subtle level for cards.
**Components:** card, button (primary/default/danger), input + hint + error, table, badge (ML/Rule/Scoring/Analytics/TODO), status dot (shape differs for error), confidence bar, recovery score ring, chart/map containers, recommendation card (priority edge), recovery chain, empty/loading/error states. Gallery: `app/design-system.html`.
**Accessibility:** visible focus, skip link, colour never sole carrier (status has shape + text), reduced-motion respected, 40px targets, contrast to be audited (TBD).
