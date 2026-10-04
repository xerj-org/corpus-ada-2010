# corpus-ada-2010 — ADA 2010 Standards for Accessible Design

Per-section plain-text mirror of the **2010 ADA Standards for Accessible Design**
(28 CFR Parts 35 and 36 appendices; the 2004 ADAAG technical provisions as adopted
by the US Department of Justice), built for the XERJ corpus hub.

- **Source page:** https://www.ada.gov/law-and-regs/design-standards/2010-stds/
  (fetched 2026-10-04; the page's own footer notes "last updated December 7, 2012").
- **Structure finding:** the current ada.gov publishes the 2010 Standards as a
  single HTML page. The older per-section URLs no longer exist — every internal
  link on the page is an in-page anchor. Section files are therefore sliced from
  the single page at its own heading structure.
- **Section unit:** the page's `<h3>` elements are the numbered sections
  (e.g. `603 Toilet and Bathing Rooms`, `213 Toilet Facilities and Bathing
  Facilities`). Subsections (`604.4 Seats.`, `308.2.1 Forward Reach.`) are
  strong-lead paragraphs inside their section file — every section number in the
  printed Standards is preserved verbatim in the text.
- **Figures:** the Standards' figures are images with detailed technical `alt`
  text (dimension-level descriptions). These are preserved as
  `[Figure: caption — alt text]` lines in place.

## Layout

| Item | Count | Notes |
|---|---|---|
| `sections/*.txt` | 145 | 128 numbered sections (content), 14 chapter/division index files (`CHAPTER 1`–`10`, `2010 STANDARDS FOR … Title II/III`), 3 standalone content pages (28 CFR 35.151 + appendix, 28 CFR part 36 subpart D heading) |
| `MANIFEST.tsv` | 145 rows | `path` → canonical source URL (with anchor) → section title |

Coverage: Chapters 1–10 complete (101–106; 201–243; 301–309; 401–410; 501–505;
601–612; 701–708; 801–811; 901–904; 1001–1010) plus the CFR front matter
(28 CFR 35.151 and appendix, 28 CFR 36.401–36.407) and the page introduction.

Rebuild: `python3 tools/extract.py _src/2010-stds.html .` (fetch the page into
`_src/` first; `_src/` is not committed).

## Licence

US federal government work — **public domain under 17 U.S.C. §105** (no copyright
subsists in US Government works). Verified at fetch time: the source page carries
**no copyright notice and no reuse caveat** of any kind — the only disclaimer on
the page concerns external links (DOJ non-endorsement), which is not a copyright
claim. The technical content derives from the 2004 ADAAG authored by the US Access
Board (also a federal agency).

Note: §105 (Referenced Standards) cites private standards (e.g. ICC A117.1-2003,
NFPA 72) by reference only; their text is not reproduced in the Standards or here.
No additional claim is made on this mirror's text.
