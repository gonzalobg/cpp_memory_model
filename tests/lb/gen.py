#!/usr/bin/env python3
from itertools import product

shape = """C lb-{l0n}-{s0n}-{l1n}-{s1n}{ub}
{{ [x] = 0; [y] = 0; }}

P0 (int* x, int* y) {{
  int a = {l0};
  {s0};
}}

P1 (int* x, int* y) {{
  int b = {l1};
  if (b != 0) {{
    {s1};
  }}
}}
{P2}
{cond}"""

ok_cond = '~exists(0:a=1)'
racy_cond = 'forall(0:a=0 \/ 0:a=1)'

l0s = {
    'lna': '*y',
    'lrlx': 'atomic_load_explicit(y, memory_order_relaxed)',
    'faddrlx': 'atomic_fetch_add_explicit(y, 0, memory_order_relaxed)',
}
s0s = {
    # Undefined
    'sna': '*x = 1',

    # Racy or Unsynchronized
    'srlx': 'atomic_store_explicit(x, 1, memory_order_relaxed)',
    'faddrlx': 'atomic_fetch_add_explicit(x, 1, memory_order_relaxed)',

    # Release Patterns with fences
    'frel-srlx': 'atomic_thread_fence(memory_order_release);\n  atomic_store_explicit(x, 1, memory_order_relaxed)',
    'frel-faddrlx': 'atomic_thread_fence(memory_order_release);\n  atomic_fetch_add_explicit(x, 1, memory_order_relaxed)',
    'frel-2srlx': 'atomic_thread_fence(memory_order_release);\n  atomic_store_explicit(x, 1, memory_order_relaxed);\n  atomic_store_explicit(x, 2, memory_order_relaxed)',
    'frel-2faddrlx': 'atomic_thread_fence(memory_order_release);\n  atomic_fetch_add_explicit(x, 1, memory_order_relaxed);\n  atomic_fetch_add_explicit(x, 1, memory_order_relaxed)',
    'frel-srlx-faddrlx': 'atomic_thread_fence(memory_order_release);\n  atomic_store_explicit(x, 1, memory_order_relaxed);\n  atomic_fetch_add_explicit(x, 1, memory_order_relaxed)',
    'frel-faddrlx-srlx': 'atomic_thread_fence(memory_order_release);\n  atomic_fetch_add_explicit(x, 1, memory_order_relaxed);\n  atomic_store_explicit(x, 1, memory_order_relaxed)',

    # Release Patterns with operations:
    'srel': 'atomic_store_explicit(x, 1, memory_order_release)',
    'faddrel': 'atomic_fetch_add_explicit(x, 1, memory_order_release)',

    # Release Patterns with Release Sequences:
    'srel-faddrlx': 'atomic_store_explicit(x, 1, memory_order_release);\n  atomic_fetch_add_explicit(x, 1, memory_order_relaxed)',
    'faddrel-faddrlx': 'atomic_fetch_add_explicit(x, 1, memory_order_release);\n  atomic_fetch_add_explicit(x, 1, memory_order_relaxed)',

    # Release Patterns with Release Sequences: pre-C++17
    'srel-srlx': 'atomic_store_explicit(x, 1, memory_order_release);\n  atomic_store_explicit(x, 2, memory_order_relaxed)',
    'faddrel-srlx': 'atomic_fetch_add_explicit(x, 1, memory_order_release);\n  atomic_store_explicit(x, 2, memory_order_relaxed)',

}

l1s = {
    # Undefined
    'lna': '*x',

    # Racy or Undefined
    'lrlx': 'atomic_load_explicit(x, memory_order_relaxed)',
    'faddrlx': 'atomic_fetch_add_explicit(x, 0, memory_order_relaxed)',

    # Acquire Patterns with fences
    'lrlx-facq': 'atomic_load_explicit(x, memory_order_relaxed);\n  atomic_thread_fence(memory_order_acquire)',
    'faddrlx-facq': 'atomic_fetch_add_explicit(x, 0, memory_order_relaxed);\n  atomic_thread_fence(memory_order_acquire)',

    # Acquire Patterns with operations
    'lacq': 'atomic_load_explicit(x, memory_order_acquire)',
    'faddacq': 'atomic_fetch_add_explicit(x, 0, memory_order_acquire)',

    # Not an Acquire Sequence in C++:
    'lrlx-lacq': 'atomic_load_explicit(x, memory_order_relaxed);\n  int c = atomic_load_explicit(x, memory_order_acquire)',
}

s1s = {
    'sna': '*y = 1',
    'srlx': 'atomic_store_explicit(y, 1, memory_order_relaxed)',
    'faddrlx': 'atomic_fetch_add_explicit(y, 1, memory_order_relaxed)',
}

P2 = """
P2 (int* x) {
  atomic_store_explicit(x, 0, memory_order_relaxed);
}
"""

# Release and Acquire patterns:
release_sequences = ['frel-2srlx', 'frel-2faddrlx', 'frel-srlx-faddrlx', 'frel-faddrlx-srlx', 'srel-srel', 'srel-faddrlx', 'faddrel-faddrlx']
release_patterns_no_sequences = ['frel-srlx', 'frel-faddrlx', 'srel', 'faddrel']
release_patterns = release_patterns_no_sequences + release_sequences
acquire_patterns_no_sequences = ['lrlx-facq', 'faddrlx-facq', 'lacq', 'faddacq']
acquire_sequences = ['lrlx-lacq']
acquire_patterns = acquire_patterns_no_sequences + acquire_sequences # BUG: lrlx-lacq should not create an acquire pattern

# Pre C++17 release pattenrs include release sequences:
release_patterns_cpp11 = release_patterns + ['srel-srlx', 'faddrel-srlx']

# Test check:
def check(l0, s0, l1, s1, rel, acq):
    cond = ok_cond
    ub = ''
    # If s1 and l0 do not synchronize with release -> acquire pattern: racy
    if s0 not in rel or l1 not in acq:
        ub = '.racy'
        cond = racy_cond
        # If racy and data-race: undefined behavior:
        if 'sna' in [s0, s1] or 'lna' in [l0, l1]:
            ub = '.undef'
    map = [s0 not in rel, l1 not in acq]
    return cond, ub, map

for l0, s0, l1, s1 in product(l0s, s0s, l1s, s1s):
    cond, ub, map = check(l0, s0, l1, s1, release_patterns, acquire_patterns)
    cond11, ub11, map11 = check(l0, s0, l1, s1, release_patterns_cpp11, acquire_patterns)

    # If C++ < 17 and C++ >=17 condition differs generate two versions of the test, one for C++11 and one for C++17:
    if cond != cond11 or ub != ub11 or map != map11:
        fname = f'lb-{l0}-{s0}-{l1}-{s1}.cpp11{ub11}.litmus'
        out = shape.format(l0n=l0, s0n=s0, l1n=l1, s1n=s1, l0=l0s[l0], s0=s0s[s0], l1=l1s[l1], s1=s1s[s1], cond=cond11, ub='-cpp11' + ub11.replace('.','-'), P2='')
        with open(fname, 'w') as f:
            f.write(out)
        # If acquire sequence: generate a second version of this test with external thread
        if l1 in acquire_sequences and s0 not in release_sequences:
            condAS, ubAS, _ = check(l0, s0, l1, s1, release_patterns_cpp11, acquire_patterns_no_sequences)
            fname = f'lb-{l0}-{s0}-{l1}-{s1}-srlx.cpp11{ubAS}.litmus'
            out = shape.format(l0n=l0, s0n=s0, l1n=l1, s1n=s1, l0=l0s[l0], s0=s0s[s0], l1=l1s[l1], s1=s1s[s1], cond=condAS, ub=ubAS.replace('.','-'), P2=P2)
            with open(fname, 'w') as f:
                f.write(out)

    # If acquire sequence: generate a second version of this test with external thread
    if l1 in acquire_sequences and s0 not in release_sequences:
        condAS, ubAS, _ = check(l0, s0, l1, s1, release_patterns, acquire_patterns_no_sequences)
        fname = f'lb-{l0}-{s0}-{l1}-{s1}-srlx{ubAS}.litmus'
        out = shape.format(l0n=l0, s0n=s0, l1n=l1, s1n=s1, l0=l0s[l0], s0=s0s[s0], l1=l1s[l1], s1=s1s[s1], cond=condAS, ub=ubAS.replace('.','-'), P2=P2)
        with open(fname, 'w') as f:
            f.write(out)

    fname = f'lb-{l0}-{s0}-{l1}-{s1}{ub}.litmus'
    out = shape.format(l0n=l0, s0n=s0, l1n=l1, s1n=s1, l0=l0s[l0], s0=s0s[s0], l1=l1s[l1], s1=s1s[s1], cond=cond, ub=ub.replace('.','-'), P2='')
    with open(fname, 'w') as f:
        f.write(out)
