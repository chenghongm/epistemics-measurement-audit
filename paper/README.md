# Paper (Apart AI x Epistemics Research Sprint submission)

| file | contents |
|---|---|
| `paper_zh.md` | Source (Chinese). Edit this, then rebuild. |
| `paper_zh.docx` | Built from the source with the Apart template's styles. |
| `make_figures.py` | Figure 1 (`fig_source.png`), computed from the archived step 7/8 data. |
| `apart_template.docx` | The Apart submission template, used as the pandoc reference document. |

Rebuild (needs pandoc; the figure needs matplotlib):

```sh
python paper/make_figures.py
cd paper && pandoc paper_zh.md -o paper_zh.docx --reference-doc=apart_template.docx --resource-path=.
```

Every number in the paper comes from `results/*/analysis/` (see `docs/results_map_2026-11-14.md`).
