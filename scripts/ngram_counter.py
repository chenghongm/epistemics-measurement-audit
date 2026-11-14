"""Counting wrapper for HF's no-repeat-n-gram block (v5 main histories).

It applies transformers' NoRepeatNGramLogitsProcessor unchanged and records, per generated
turn, the decoding steps at which the block changed the greedy (argmax) token. A turn with
zero changed steps is token-for-token what plain greedy would have produced from the same
prefix, so a history whose turns all have zero is identical to the no-flag run (its readouts
too). Steps are counted from 0 at the first generated token. After the first change, later
steps compare against greedy on the already-altered prefix.

Torch-free: the inner processor is built lazily, so tests can inject a fake one."""


class CountingNoRepeatNGram:
    def __init__(self, n, inner=None):
        if inner is None:
            from transformers import NoRepeatNGramLogitsProcessor
            inner = NoRepeatNGramLogitsProcessor(n)
        self.n = n
        self.inner = inner
        self.steps = 0
        self.changed = []

    def __call__(self, input_ids, scores):
        if len(scores) != 1:
            raise ValueError('CountingNoRepeatNGram expects batch size 1')
        # Read the greedy choice before the inner call, in case it edits scores in place.
        before = int(scores[0].argmax())
        out = self.inner(input_ids, scores)
        if int(out[0].argmax()) != before:
            self.changed.append(self.steps)
        self.steps += 1
        return out

    def record(self):
        return {'ngram_changed_steps': len(self.changed),
                'ngram_first_changed_step': self.changed[0] if self.changed else None}
