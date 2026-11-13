"""Small MPS replay against stored A100 measurements, not a new experiment."""
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'vendor/digital_mind'))
sys.path.insert(0, str(ROOT / 'scripts'))
import torch
import transformers
import runner
from frozen_audit import history, sha, save

model = Path('/Users/chm.1/pyenvs/genai/digital-mind/Llama-3.1-8B-Instruct')
manifest = json.loads((ROOT / 'provenance/checkpoints.json').read_text())
item = manifest['checkpoints'][0]
record, messages, turn = history(item)
start = time.monotonic()
rr = runner.Runner(str(model), device='mps')
loaded = time.monotonic()
with torch.no_grad():
    p, mass, orders = rr.probe_stance_averaged(messages, record['side_a'], record['side_b'])
torch.mps.synchronize()
result = dict(checkpoint=item, device='mps', model=str(model),
              tokenizer_sha256=sha(model / 'tokenizer.json'),
              historical_tokenizer_sha256=manifest['tokenizer_sha256'],
              torch=torch.__version__, transformers=transformers.__version__, dtype=str(rr.model.dtype),
              load_seconds=loaded-start, probe_seconds=time.monotonic()-loaded,
              p_a=p, orders=orders, mass=mass, stored_p_a=turn['p_a'],
              stored_orders=turn['p_a_orders'],
              max_reconstruction_delta=max(abs(a-b) for a,b in zip(orders, turn['p_a_orders'])),
              allocated_bytes=torch.mps.current_allocated_memory(),
              driver_bytes=torch.mps.driver_allocated_memory())
save(ROOT / 'results/local_pilot/replay.json', result)
print(json.dumps(result, indent=2), flush=True)
