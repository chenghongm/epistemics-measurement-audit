# Paper (Apart AI x Epistemics Research Sprint submission)

| file | contents |
|---|---|
| `paper_en.md` / `paper_en.docx` | **Submission version (English).** Translation of `paper_zh_meng.md`, same content. |
| `paper_zh_meng.md` / `paper_zh_meng.docx` | **Final Chinese source**, integrated by the author (Codex's related work and references, author's wording). |
| `paper_zh.md` / `paper_zh.docx` | Earlier Chinese draft (Claude), superseded by `paper_zh_meng.md`; kept for the record. |
| `paper_zh_v3_reviewed_2026-11-15.md` | Codex's independent revision of draft 3; partly adopted in `paper_zh_meng.md`, not a source. |
| `reviews/` | Codex's reviews of draft 3 and of the integrated draft, with numeric re-checks. |
| `make_figures.py` | Figure 1, computed from the archived step 7/8 data: `fig_source.png` (Chinese labels), `fig_source_en.png` (English, `python paper/make_figures.py en`). |
| `apart_template.docx` | The Apart submission template, used as the pandoc reference document. |

Rebuild (needs pandoc; the figure needs matplotlib):

```sh
python paper/make_figures.py en
cd paper && pandoc paper_en.md -o paper_en.docx --reference-doc=apart_template.docx --resource-path=.
```

Every number in the paper comes from `results/*/analysis/` (see `docs/results_map_2026-11-14.md`); the fixed-cohort discount counts in section 4.2 come from `results/main_v5/analysis/checkpoints.csv`.
