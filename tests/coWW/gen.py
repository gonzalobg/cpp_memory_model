#!/usr/bin/env python3
from itertools import product

shape = """C coWW-{s0n}-{s1n}-{l0n}
{{ [x] = 0; }}

P0 (int* x) {{
  {s0};
  {s1};
}}
{l0}
~exists ([x]=0 \/ [x]=1)"""

# If either s0 or l1 is non-atomic, then we expect Undef.

s0s = {
    'srlx': 'atomic_store_explicit(x, 1, memory_order_relaxed)',
    'faddrlx': 'atomic_fetch_add_explicit(x, 1, memory_order_relaxed)',
    'sna': '*x = 1',
}

s1s = {
    'srlx': 'atomic_store_explicit(x, 2, memory_order_relaxed)',
    'faddrlx': 'atomic_fetch_add_explicit(x, 1, memory_order_relaxed)',
    'sna': '*x = 2',
}

P1="""

P1 (int* x) {{
  {op};
}}
"""

l0s = {
    'none': '',
    'lrlx': P1.format(op='atomic_load_explicit(x, memory_order_relaxed)'),
    'faddrlx': P1.format(op='atomic_fetch_add_explicit(x, 0, memory_order_relaxed)'),
    'lna': P1.format(op='*x'),
}

for s0, s1, l0 in product(s0s, s1s, l0s):
    fname = f'coWW-{s0}-{s1}-{l0}.litmus'
    out = shape.format(s0n=s0, s1n=s1, l0n=l0, s0=s0s[s0], s1=s1s[s1], l0=l0s[l0])
    with open(fname, 'w') as f:
        f.write(out)
