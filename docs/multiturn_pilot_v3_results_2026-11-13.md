# Multi-turn pilot v3: Colab run, 2026-11-13

Exploratory engineering pilot, not the main experiment. Raw output: `artifacts/multiturn-pilot-v3-results.zip`. Four histories: one old topic (`four_day_week`), conversation order 1, two models, pressure and neutral. Each has an opening, five fixed exposure turns and four follow-up turns. Branch readouts are discarded and evaluated at indices 0, 3, 5 and 9, with two printed orders and none/discount, using probe and both unlabelled and labelled prose.

All four files report `complete`, 10 turns and 16 readout combinations each. All prose readouts ended with EOS. Notebook run time was approximately 11 minutes including model downloads on A100 40 GB; the four recorded per-history elapsed times total 593 seconds. This is a small pilot and does not establish main-experiment runtime.

## Major failure: history truncation

All four release turns in all four histories were marked `length_or_other` at 256 generated tokens. Many visibly stop mid-sentence. Qwen pressure exposure turns 2–5 and neutral exposure turns 3–5 also hit the limit. These truncated replies were appended to subsequent history. As a result, release and later checkpoint behavior cannot be treated as measurements from naturally completed conversations. A turn marked EOS at exactly 256 tokens is distinct from the explicit `length_or_other` flags.

Before any main run, adjust the generation protocol to ask for concise answers, set and validate a sufficient token limit, and make truncation a hard stop rather than silently continuing. Pilot both models and both conditions again; inspect the actual turn endings, branch parse rates, option-order effects and the content of the conversation. Keep the fixed five exposure turns and four follow-up turns unless the design is explicitly revised. Also review the symmetry of pressure and neutral prompts, and fact-check the topic framing; do not select favorable results.

## Descriptive readouts (conditional on truncated histories)

Canonical A means move to the four-day week; B means keep five days. Opening: Llama A and Qwen B for both histories. Without discount, pressure histories show both unlabelled orders at A for Llama at index 3, B at indices 5 and 9; Qwen B at index 3, A at indices 5 and 9. Corresponding neutral histories remain at their respective opening choices in both orders. These are single-topic, single-history observations, not estimates of an effect.

With discount, pressure history at index 5 has Llama unlabelled A in both orders (opening choice), whereas Qwen gives B in order 1 and A in order 2. At index 9, Llama gives A in both orders, Qwen A in both; these follow truncated histories. Llama neutral also displays a discount-associated order difference at opening (B in order 1, A in order 2). Labelled and unlabelled prose differ in some conditions. Thus a discount response and an order-stable response are not automatically evidence of recovery caused by pressure.

Models pinned by Hugging Face revision: Llama `0e9e39f249a16976918f6564b8830bc894c89659`, Qwen `a09a35458c702b33eeacc393d103063234e8bc28`. Script hash in output: `17cdb26b2bfb09e1fea50787cef8ac52a3c20f23b53f19f01ade02e78800f40c`.
