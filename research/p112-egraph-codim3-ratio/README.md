# Exact frame-hit ratio for codimension-at-most-3 P112 E-graph supports

**Scoped exact ratio. No new kappa.** On the P112 E-graph, every support cut
out by an F2^9 subspace of dimension at least 6 has frame-substitution ratio
at most **17/35**. The bound is attained. The resulting covering relaxation
is **280/17**, which is below 64, so this family does not force the
eight-term copy floor.

PR717 D1(e) sampled 20,000 codimension-at-most-3 pairs and reported a best
ratio of about 0.1825, namely 920/(1260·4) = 23/126. That sample is not the
maximum. The exhaustive maximum on the same family is 612/(1260·1) = 17/35.
The eight-term all-pairs theorem is not rerun. Masked E-graph supports are
one of its excluded classes.

## Ratio

Ports are the 112 E8 root lines outside the coordinate frame. Labels lie in
F2^9. The E-graph is the 1260 cliques of eight mutually orthogonal ports.
Each port lies in 90 cliques. A term with row support R and column support A
has cost beta equal to the F2 rank of the even-inner-product pairing between
R and A, and it hits the cliques that meet both supports. The ratio is

```text
(cliques hit) / (1260 * beta).
```

The supports in this census are exactly the sets of ports whose labels lie
in one subspace of dimension 6, 7, 8, or 9. That is the search space of
PR717 D1(e): kernels of at most three label functionals, including every
hyperplane section. Proper subsets of those kernels are not included.

The maximum is 17/35, from a 6-dimensional flat with 8 ports, port-span
dimension 4, against a 6-dimensional flat with 12 ports, port-span
dimension 6. They hit 612 cliques at pairing rank 1. Both sets are the full
port set of their flat. The rank inequality beta ≥ dim U + dim W − 9 is
sharp on this pair: 4 + 6 − 9 = 1.

Because the label form is nondegenerate, any two port-spans of dimensions
d1 and d2 satisfy beta ≥ d1 + d2 − 9. In particular:

- a span of dimension at least 7 against a span of dimension at least 6 has
  beta at least 4, hence ratio at most 1/4, which is below 17/35;
- two spans of dimension 6 have beta at least 3, hence ratio at most 1/3,
  also below 17/35;
- a beta-2 pair beats 17/35 only if it hits at least 1225 of the 1260
  cliques.

The census therefore evaluates every positive port-span of dimension at most
5 against every flat of dimension at least 6, and it checks the self-ratio
of every flat. No such pair exceeds 17/35.

## Covering bound

Each clique needs eight terms in an exact frame factorization. If every
costly term has ratio at most rho, the total cost satisfies cst ≥ 8/rho.
Here rho = 17/35, so

```text
cst ≥ 8 / (17/35) = 280/17 ≈ 16.4706.
```

This is below 64. The relaxation does not prove the coordinate-decoder floor,
and it does not produce a decoder. Restoration, frame changes, and recursive
children were not priced; the ratio is only the D1(e) frame-substitution
quotient.

## Reproduce

From the repository root, with Python 3.12, assertions not required, and
`g++` available:

```sh
python3 -B research/p112-egraph-codim3-ratio/verify.py
```

Expected last line:

```text
PASS_P112_EGRAPH_CODIM3_RATIO hits=612 beta=1 ratio=17/35 covering=280/17 frames=1260 controls=3 no_new_kappa
```

The Python half rebuilds the E8 model and checks the witness, three failure
controls, and the rational comparisons. It then compiles `census.cpp` with
`g++ -O2 -std=c++17` and requires `PASS_CENSUS 17/35` on the same roots.
The run takes about one minute. `PYTHONOPTIMIZE` may be set or unset; the
checks use explicit exceptions.

Environment used for the recorded run: CPython 3.12.3, g++ 13.3.0 at
`/usr/bin/g++`, the `c++` alternative pointing at `/usr/bin/g++`, and
libboost-dev 1.83 installed but unused. No third-party Python modules are
imported.

Orientation before the census: `python3 -B research/complex-decoder-field-extension-seed44/verify.py`
returned `PASS_COMPLEX_DECODER_FIELD_EXTENSION_S44`. `make frontier1094-verify`
was not run. No proof assistant was run.

## Scope

Chooser seed `39ef946a2412071e8cd6dfbea07d3a77`, track `complex-mechanisms`,
card `complex-masked-decoder`, scope key `7acfe4d9cac04f7ba4cb`, priority
revision 2. Base `ef5f39403610d231a0c27e8a6b4f08c10209bcd6`. Scope is
**refined** to this one finite support alphabet: full kernels of at most
three label functionals, with the E-graph frame ratio as the exact
constraint. The eight-term all-pairs search is not repeated.

Not claimed: a physical decoder, a supplier, a change in kappa, or a bound
on supports that are proper subsets of these kernels. Trimmed-star frame
counts, including the separate 784/13 bound in discussion 1210, are a
different family.

Discussion writes from this account are forbidden by the host integration.
That limitation is recorded here and was not retried.

## Open next questions

Can a proper subset of one of these kernels raise the ratio above 17/35?
A subset that keeps pairing rank 1 cannot, because deleting a port cannot
add cliques, but a subset of a higher-rank kernel could drop beta faster
than it drops the clique count. The first step is to delete one port from
each dimension-6 kernel whose self-pairing rank is at least 4 and keep a
subset only if its ratio exceeds 17/35. The blocker is that this is no
longer the D1(e) flat family, and the deletion tree is larger than the
flat census.

## Credit

The E-graph, the 1260 frames, and the sampled ratio 23/126 come from
DreamingOfClouds, PR717 D1(e). The eight-term all-pairs floor is the
frame-pair package and the complex field-extension note. The single-lift
obstructions in PR845 fix the coordinate readers and are not this alphabet.
Discussion 1210 studies trimmed stars, not these kernels.

Substantial AI assistance was used for the census, the witness check, and
the packaging. No independent human review is claimed. Apache-2.0.
