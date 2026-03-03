#!/usr/bin/env python3
from itertools import product

shape = """C coRW-{l0n}-{s0n}-{s1n}{ub}
{{ [x] = 0; }}

P0 (int* x) {{
  int a = {l0};
  {s0};
}}

P1 (int* x) {{
  {s1};
}}

~exists (0:a=2 /\ [x]=2)"""

l0s = {
    'lrlx': 'atomic_load_explicit(x, memory_order_relaxed)',
    'faddrlx': 'atomic_fetch_add_explicit(x, 0, memory_order_relaxed)',
}

s0s = {
    'srlx': 'atomic_store_explicit(x, 1, memory_order_relaxed)',
    'faddrlx': 'atomic_fetch_add_explicit(x, 1, memory_order_relaxed)',
    'sna': '*x = 1'
}

s1s = {
    'srlx': 'atomic_store_explicit(x, 2, memory_order_relaxed)',
    'faddrlx': 'atomic_fetch_add_explicit(x, 2, memory_order_relaxed)',
    # TODO: waiting for Dartagnang store-add support
    #'saddrlx': 'atomic_store_add_explicit(x, 2, memory_order_relaxed)',
}

for l0, s0, s1 in product(l0s, s0s, s1s):
    ub = ''
    if 'sna' in s0:
        ub = '.undef'
    fname = f'coRW-{l0}-{s0}-{s1}{ub}.litmus'
    out = shape.format(l0n=l0, s0n=s0, s1n=s1, l0=l0s[l0], s0=s0s[s0], s1=s1s[s1], ub=ub.replace('.','-'))
    with open(fname, 'w') as f:
        f.write(out)
