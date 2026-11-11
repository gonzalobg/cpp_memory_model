#!/usr/bin/env python3
from itertools import product

# Normal MP shape.
shape = """C mp-{s0n}-{s1n}-{l0n}-{l1n}{ub}
{{ [x] = 0; [y] = 0; }}

P0 (int* x, int* y) {{
  {s0};
  {s1};
}}

P1 (int* x, int* y) {{
  int a = {l0};
  int b = 0;
  if (a != 0) {{
    b = {l1};
  }}
}}
{P2}
{cond}"""

# A non-returning update cannot guard the payload read. Observe final y instead.
sadd_shape = """C mp-{s0n}-{s1n}-{l0n}-{l1n}{ub}
{{ [x] = 0; [y] = 0; }}

P0 (int* x, int* y) {{
  {s0};
  {s1};
}}

P1 (int* x, int* y) {{
  {l0};
  int b = {l1};
}}

filter ([y]={final_y})
{cond}"""

ok_cond='~exists(~1:a=0 /\ 1:b=0)'
undef_cond='forall(1:b=0 \/ 1:b=1)'
racy_checks = ['exists(1:b=0)', 'exists(1:b=1)']

s0s = {
    'sna': '*x = 1',
    'srlx': 'atomic_store_explicit(x, 1, memory_order_relaxed)',
    'faddrlx': 'atomic_fetch_add_explicit(x, 1, memory_order_relaxed)',
}

s1s = {
    # Undefined
    'sna' : '*y = 1',

    # Racy or Undefined
    'srlx': 'atomic_store_explicit(y, 1, memory_order_relaxed)',
    'faddrlx': 'atomic_fetch_add_explicit(y, 1, memory_order_relaxed)',

    # Release Patterns with fences
    'frel-srlx': 'atomic_thread_fence(memory_order_release);\n  atomic_store_explicit(y, 1, memory_order_relaxed)',
    'frel-faddrlx': 'atomic_thread_fence(memory_order_release);\n  atomic_fetch_add_explicit(y, 1, memory_order_relaxed)',
    'frel-2srlx': 'atomic_thread_fence(memory_order_release);\n  atomic_store_explicit(y, 1, memory_order_relaxed);\n  atomic_store_explicit(y, 2, memory_order_relaxed)',
    'frel-2faddrlx': 'atomic_thread_fence(memory_order_release);\n  atomic_fetch_add_explicit(y, 1, memory_order_relaxed);\n  atomic_fetch_add_explicit(y, 1, memory_order_relaxed)',
    'frel-srlx-faddrlx': 'atomic_thread_fence(memory_order_release);\n  atomic_store_explicit(y, 1, memory_order_relaxed);\n  atomic_fetch_add_explicit(y, 1, memory_order_relaxed)',
    'frel-faddrlx-srlx': 'atomic_thread_fence(memory_order_release);\n  atomic_fetch_add_explicit(y, 1, memory_order_relaxed);\n  atomic_store_explicit(y, 2, memory_order_relaxed)',
    'frel-saddrlx': 'atomic_thread_fence(memory_order_release);\n  atomic_store_add_explicit(y, 1, memory_order_relaxed)',
    'frel-2saddrlx': 'atomic_thread_fence(memory_order_release);\n  atomic_store_add_explicit(y, 1, memory_order_relaxed);\n  atomic_store_add_explicit(y, 1, memory_order_relaxed)',
    'frel-srlx-saddrlx': 'atomic_thread_fence(memory_order_release);\n  atomic_store_explicit(y, 1, memory_order_relaxed);\n  atomic_store_add_explicit(y, 1, memory_order_relaxed)',
    'frel-saddrlx-srlx': 'atomic_thread_fence(memory_order_release);\n  atomic_store_add_explicit(y, 1, memory_order_relaxed);\n  atomic_store_explicit(y, 2, memory_order_relaxed)',

    # Release Patterns with operations
    'srel': 'atomic_store_explicit(y, 1, memory_order_release)',
    'faddrel': 'atomic_fetch_add_explicit(y, 1, memory_order_release)',
    'saddrel': 'atomic_store_add_explicit(y, 1, memory_order_release)',

    # Release Patterns with Release Sequences:
    'srel-faddrlx': 'atomic_store_explicit(y, 1, memory_order_release);\n  atomic_fetch_add_explicit(y, 1, memory_order_relaxed)',
    'faddrel-faddrlx': 'atomic_fetch_add_explicit(y, 1, memory_order_release);\n  atomic_fetch_add_explicit(y, 1, memory_order_relaxed)',
    'srel-saddrlx': 'atomic_store_explicit(y, 1, memory_order_release);\n  atomic_store_add_explicit(y, 1, memory_order_relaxed)',
    'saddrel-saddrlx': 'atomic_store_add_explicit(y, 1, memory_order_release);\n  atomic_store_add_explicit(y, 1, memory_order_relaxed)',

    # Release Patterns with Release Sequences: pre-C++17
    'srel-srlx': 'atomic_store_explicit(y, 1, memory_order_release);\n  atomic_store_explicit(y, 2, memory_order_relaxed)',

    # Not a Release Sequence in C++:
    'faddrel-srlx': 'atomic_fetch_add_explicit(y, 1, memory_order_release);\n  atomic_store_explicit(y, 2, memory_order_relaxed)',
    'saddrel-srlx': 'atomic_store_add_explicit(y, 1, memory_order_release);\n  atomic_store_explicit(y, 2, memory_order_relaxed)',
}

l0s = {
    # Undefined
    'lna': '*y',

    # Racy or Undefined
    'lrlx': 'atomic_load_explicit(y, memory_order_relaxed)',
    'faddrlx': 'atomic_fetch_add_explicit(y, 0, memory_order_relaxed)',

    # Acquire Patterns with fences
    'lrlx-facq': 'atomic_load_explicit(y, memory_order_relaxed);\n  atomic_thread_fence(memory_order_acquire)',
    'faddrlx-facq': 'atomic_fetch_add_explicit(y, 0, memory_order_relaxed);\n  atomic_thread_fence(memory_order_acquire)',

    # Store updates do not form an acquire pattern, even with an acquire fence.
    'saddrlx-facq': 'atomic_store_add_explicit(y, 1, memory_order_relaxed);\n  atomic_thread_fence(memory_order_acquire)',

    # Acquire Patterns with operations
    'lacq': 'atomic_load_explicit(y, memory_order_acquire)',
    'faddacq': 'atomic_fetch_add_explicit(y, 0, memory_order_acquire)',

    # Not an Acquire Sequence in C++:
    'lrlx-lacq': 'atomic_load_explicit(y, memory_order_relaxed);\n  int c = atomic_load_explicit(y, memory_order_acquire)',
}

l1s = {
    'lna': '*x',
    'lrlx': 'atomic_load_explicit(x, memory_order_relaxed)',
    'faddrlx': 'atomic_fetch_add_explicit(x, 0, memory_order_relaxed)',
}

P2 = """
P2 (int* y) {
  atomic_store_explicit(y, 0, memory_order_relaxed);
}
"""

# Release and Acquire patterns:
release_sequences = ['frel-2srlx', 'frel-2faddrlx', 'frel-srlx-faddrlx', 'frel-faddrlx-srlx', 'srel-srel', 'srel-faddrlx', 'faddrel-faddrlx', 'srel-saddrlx', 'frel-2saddrlx', 'frel-srlx-saddrlx', 'frel-saddrlx-srlx', 'saddrel-saddrlx']
release_patterns_no_sequences = ['frel-srlx', 'frel-faddrlx', 'srel', 'faddrel', 'saddrel', 'frel-saddrlx']
release_patterns = release_patterns_no_sequences + release_sequences
acquire_patterns_no_sequences = ['lrlx-facq', 'faddrlx-facq', 'lacq', 'faddacq']
acquire_sequences = ['lrlx-lacq']
acquire_patterns = acquire_patterns_no_sequences + acquire_sequences # BUG: lrlx-lacq should not create an acquire pattern

# Pre C++17 release pattenrs include release sequences:
release_patterns_cpp11 = release_patterns + ['srel-srlx']

# Test check:
def check(s0, s1, l0, l1, rel, acq):
    cond = ok_cond
    ub = ''
    # If s1 and l0 do not synchronize with release -> acquire pattern: racy
    if s1 not in rel or l0 not in acq:
        ub = '.racy'
        cond = None
        # If racy and data-race: undefined behavior:
        if 'sna' in [s0, s1] or 'lna' in [l0, l1]:
            ub = '.undef'
            cond = undef_cond
    map = [s1 not in rel, l0 not in acq]
    return cond, ub, map


def write_tests(fname, cond, outcome, **fields):
    checks = racy_checks if outcome == '.racy' else [cond]
    template = shape
    if fields['l0n'] == 'saddrlx-facq':
        template = sadd_shape
        # Final y after P0 then P1. For a terminal store, this also establishes
        # that P1's update follows that store in modification order. With only
        # additive updates, final y does not distinguish their order.
        publisher_writes_two = {
            'frel-2faddrlx', 'frel-srlx-faddrlx', 'frel-faddrlx-srlx',
            'frel-2saddrlx', 'frel-srlx-saddrlx', 'frel-saddrlx-srlx',
            'srel-faddrlx', 'faddrel-faddrlx', 'srel-saddrlx',
            'saddrel-saddrlx', 'srel-srlx', 'faddrel-srlx', 'saddrel-srlx',
        }
        fields['final_y'] = 3 if fields['s1n'] in publisher_writes_two else 2
    for variant, racy_check in enumerate(checks):
        variant_fname = fname
        variant_fields = fields.copy()
        if outcome == '.racy':
            variant_fname = fname[:-len('.litmus')] + f'.{variant}.litmus'
            variant_fields['ub'] += f'-{variant}'
        out = template.format(cond=racy_check, **variant_fields)
        with open(variant_fname, 'w') as f:
            f.write(out)


for s0, s1, l0, l1 in product(s0s, s1s, l0s, l1s):
    cond, ub, map = check(s0, s1, l0, l1, release_patterns, acquire_patterns)
    cond11, ub11, map11 = check(s0, s1, l0, l1, release_patterns_cpp11, acquire_patterns)

    # If C++ < 17 and C++ >=17 condition differs generate two versions of the test, one for C++11 and one for C++17:
    if cond != cond11 or ub != ub11 or map != map:
        fname = f'mp-{s0}-{s1}-{l0}-{l1}.cpp11{ub11}.litmus'
        write_tests(fname, cond11, ub11, s0n=s0, s1n=s1, l0n=l0, l1n=l1, s0=s0s[s0], s1=s1s[s1], l0=l0s[l0], l1=l1s[l1], ub='-cpp11' + ub11.replace('.','-'), P2='')
        # If acquire sequence: generate a second version of this test with external thread
        if l0 in acquire_sequences and s1 not in release_sequences:
            condAS, ubAS, _ = check(s0, s1, l0, l1, release_patterns_cpp11, acquire_patterns_no_sequences)
            fname = f'mp-{s0}-{s1}-{l0}-{l1}-srlx.cpp11{ubAS}.litmus'
            write_tests(fname, condAS, ubAS, s0n=s0, s1n=s1, l0n=l0, l1n=l1, s0=s0s[s0], s1=s1s[s1], l0=l0s[l0], l1=l1s[l1], ub=ubAS.replace('.','-'), P2=P2)

    # If acquire sequence: generate a second version of this test with external thread
    if l0 in acquire_sequences and s1 not in release_sequences:
        condAS, ubAS, _ = check(s0, s1, l0, l1, release_patterns, acquire_patterns_no_sequences)
        fname = f'mp-{s0}-{s1}-{l0}-{l1}-srlx{ubAS}.litmus'
        write_tests(fname, condAS, ubAS, s0n=s0, s1n=s1, l0n=l0, l1n=l1, s0=s0s[s0], s1=s1s[s1], l0=l0s[l0], l1=l1s[l1], ub=ubAS.replace('.','-'), P2=P2)

    fname = f'mp-{s0}-{s1}-{l0}-{l1}{ub}.litmus'
    write_tests(fname, cond, ub, s0n=s0, s1n=s1, l0n=l0, l1n=l1, s0=s0s[s0], s1=s1s[s1], l0=l0s[l0], l1=l1s[l1], ub=ub.replace('.','-'), P2='')
