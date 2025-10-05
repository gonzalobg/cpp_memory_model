#!/usr/bin/env python3
from itertools import product

shape = """C coWR-{s0n}-{l0n}-{s1n}
{{ [x] = 0; }}

P0 (int* x) {{
  {s0};
  int a = {l0};
}}

P1 (int* x) {{
  {s1};
}}

~exists (0:a=2 /\ [x]=1)"""


s0s = {
    'srlx': 'atomic_store_explicit(x, 1, memory_order_relaxed)',
    'faddrlx': 'atomic_fetch_add_explicit(x, 1, memory_order_relaxed)',
    'sna': '*x = 1',
}

l0s = {
    'lrlx': 'atomic_load_explicit(x, memory_order_relaxed)',
    'faddrlx': 'atomic_fetch_add_explicit(x, 0, memory_order_relaxed)',
    'lna': '*x',
}

s1s = {
    'srlx': 'atomic_store_explicit(x, 2, memory_order_relaxed)',
    'faddrlx': 'atomic_fetch_add_explicit(x, 2, memory_order_relaxed)',
    'sna': '*x = 2',
}

for s0, l0, s1 in product(s0s, l0s, s1s):
    fname = f'coWR-{s0}-{l0}-{s1}.litmus'
    out = shape.format(s0n=s0, l0n=l0, s1n=s1, s0=s0s[s0], l0=l0s[l0], s1=s1s[s1])
    with open(fname, 'w') as f:
        f.write(out)
