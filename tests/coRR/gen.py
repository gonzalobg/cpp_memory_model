#!/usr/bin/env python3
from itertools import product

shape = """C coRR-{s0n}-{l1n}-{l2n}
{{ [x] = 0; }}

P0 (int* x) {{
  {s0};
}}

P1 (int* x) {{
  int a = {l1};
  if (a == 1) {{
    int b = {l2};
  }}
}}

~exists (1:a=1 /\ 1:b=0)"""

# If either s0 or l1 is non-atomic, then we expect Undef.

s0s = {
    'srlx': 'atomic_store_explicit(x, 1, memory_order_relaxed)',
    'srel': 'atomic_store_explicit(x, 1, memory_order_release)',    
    'faddrlx': 'atomic_fetch_add_explicit(x, 1, memory_order_relaxed)',
    'faddrel': 'atomic_fetch_add_explicit(x, 1, memory_order_release)',
    'sna': '*x = 1',
}

l1s = {
    'lrlx': 'atomic_load_explicit(x, memory_order_relaxed)',
    'lrlx-facq': 'atomic_load_explicit(x, memory_order_relaxed);\n  atomic_thread_fence(memory_order_acquire)',
    'lacq': 'atomic_load_explicit(x, memory_order_acquire)',
    'faddrlx': 'atomic_fetch_add_explicit(x, 0, memory_order_relaxed)',
    'faddrlx-facq': 'atomic_fetch_add_explicit(x, 0, memory_order_relaxed);\n  atomic_thread_fence(memory_order_acquire)',    
    'faddacq': 'atomic_fetch_add_explicit(x, 0, memory_order_acquire)',
    'lna': '*x',
}

l2s = {
    'lrlx': 'atomic_load_explicit(x, memory_order_relaxed)',
    'faddrlx': 'atomic_fetch_add_explicit(x, 0, memory_order_relaxed)',
    'lna': '*x',
}

for s0, l1, l2 in product(s0s, l1s, l2s):
    fname = f'coRR-{s0}-{l1}-{l2}.litmus'
    out = shape.format(s0n=s0, l1n=l1, l2n=l2, s0=s0s[s0], l1=l1s[l1], l2=l2s[l2])
    with open(fname, 'w') as f:
        f.write(out)
