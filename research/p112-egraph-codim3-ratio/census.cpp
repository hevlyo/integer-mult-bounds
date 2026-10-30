// Exhaustive frame-hit ratio for P112 E-graph supports.
// Supports are all ports whose labels lie in one F2^9 subspace of dimension >= 6.
// Prints PASS_CENSUS <num>/<den> for the maximum of (frames hit) / (1260 * beta).
// Apache-2.0. Standard C++17 only.
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <functional>
#include <iostream>
#include <numeric>
#include <unordered_map>
#include <utility>
#include <vector>
using namespace std;

static int parity(uint32_t x) { return __builtin_popcount(x) & 1; }

static int dot8(const int* a, const int* b) {
    int s = 0;
    for (int i = 0; i < 8; ++i) s += a[i] * b[i];
    return s;
}

struct Flat {
    uint16_t ann[3];
    int ann_dim;
    int ambient_dim;
    int span_dim;
    uint16_t basis[9];
    int hits;
    int nports;
    uint64_t key;
    int index;
};

static uint64_t pack_ann(const uint16_t* g, int dim) {
    uint64_t key = (uint64_t)dim << 60;
    for (int i = 0; i < dim; ++i) key |= (uint64_t)g[i] << (16 * i);
    return key;
}

static uint64_t pack6(const uint16_t* rows) {
    uint64_t key = 0;
    for (int i = 0; i < 6; ++i) key |= (uint64_t)(rows[i] & 511) << (9 * i);
    return key;
}

static void rref_key_from_gens(uint16_t* gens, int ngen, uint16_t out[3], int* out_dim) {
    uint16_t rows[9];
    int n = 0;
    for (int i = 0; i < ngen; ++i) {
        uint16_t v = gens[i];
        for (int s = 0; s < n; ++s) {
            int piv = 31 - __builtin_clz(rows[s]);
            if ((v >> piv) & 1) v ^= rows[s];
        }
        if (!v) continue;
        int piv = 31 - __builtin_clz(v);
        for (int s = 0; s < n; ++s)
            if ((rows[s] >> piv) & 1) rows[s] ^= v;
        rows[n++] = v;
    }
    sort(rows, rows + n, [](uint16_t a, uint16_t b) {
        return (31 - __builtin_clz(a)) < (31 - __builtin_clz(b));
    });
    *out_dim = n;
    for (int i = 0; i < n; ++i) out[i] = rows[i];
    for (int i = n; i < 3; ++i) out[i] = 0;
}

int main() {
    ios::sync_with_stdio(false);
    vector<array<int, 8>> roots;
    for (int i = 0; i < 8; ++i)
        for (int j = i + 1; j < 8; ++j)
            for (int si : {1, -1})
                for (int sj : {1, -1}) {
                    array<int, 8> v{};
                    v[i] = 2 * si;
                    v[j] = 2 * sj;
                    roots.push_back(v);
                }
    for (int m = 0; m < 256; ++m) {
        array<int, 8> v{};
        int neg = 0;
        for (int i = 0; i < 8; ++i) {
            if ((m >> i) & 1) { v[i] = -1; ++neg; }
            else v[i] = 1;
        }
        if (neg % 2 == 0) roots.push_back(v);
    }
    vector<array<int, 8>> lines;
    {
        vector<array<int, 8>> uniq;
        for (auto r : roots) {
            auto n = r;
            for (int i = 0; i < 8; ++i) n[i] = -r[i];
            if (n > r) r = n;
            uniq.push_back(r);
        }
        sort(uniq.begin(), uniq.end());
        uniq.erase(unique(uniq.begin(), uniq.end()), uniq.end());
        lines = uniq;
    }
    if (lines.size() != 120) { cerr << "lines\n"; return 1; }
    int simple[8][8] = {};
    int s0[8] = {1, -1, -1, -1, -1, -1, -1, 1};
    for (int i = 0; i < 8; ++i) simple[0][i] = s0[i];
    simple[1][0] = 2; simple[1][1] = 2;
    simple[2][0] = -2; simple[2][1] = 2;
    for (int k = 1; k <= 5; ++k) { simple[k + 2][k] = -2; simple[k + 2][k + 1] = 2; }
    long double A[8][16] = {};
    for (int i = 0; i < 8; ++i) {
        for (int j = 0; j < 8; ++j) A[i][j] = simple[i][j];
        A[i][8 + i] = 1;
    }
    for (int col = 0; col < 8; ++col) {
        int piv = col;
        for (int i = col; i < 8; ++i)
            if (fabsl(A[i][col]) > fabsl(A[piv][col])) piv = i;
        for (int j = 0; j < 16; ++j) swap(A[col][j], A[piv][j]);
        long double div = A[col][col];
        for (int j = 0; j < 16; ++j) A[col][j] /= div;
        for (int i = 0; i < 8; ++i) if (i != col) {
            long double c = A[i][col];
            for (int j = 0; j < 16; ++j) A[i][j] -= c * A[col][j];
        }
    }
    vector<array<int, 8>> frame;
    for (int j = 0; j < 4; ++j)
        for (int sign : {1, -1}) {
            array<int, 8> v{};
            v[2 * j] = 2;
            v[2 * j + 1] = 2 * sign;
            frame.push_back(v);
        }
    auto is_frame = [&](const array<int, 8>& r) {
        array<int, 8> n = r;
        for (int i = 0; i < 8; ++i) n[i] = -r[i];
        for (auto& f : frame)
            if (f == r || f == n) return true;
        return false;
    };
    vector<array<int, 8>> kept;
    vector<uint16_t> labels;
    for (auto& root : lines) {
        if (is_frame(root)) continue;
        int coords[9];
        for (int j = 0; j < 8; ++j) {
            long double s = 0;
            for (int k = 0; k < 8; ++k) s += root[k] * A[k][8 + j];
            coords[j] = (int)llround(s);
        }
        coords[8] = 1;
        uint16_t lab = 0;
        for (int b = 0; b < 9; ++b) lab = (uint16_t)((lab << 1) | (coords[b] & 1));
        kept.push_back(root);
        labels.push_back(lab);
    }
    if (kept.size() != 112) { cerr << "kept\n"; return 1; }
    vector<uint64_t> orth_lo(112), orth_hi(112);
    int ones = -1;
    for (int i = 0; i < 112; ++i) {
        int row_ones = 0;
        for (int j = 0; j < 112; ++j) {
            int d = dot8(kept[i].data(), kept[j].data());
            if (d % 4) { cerr << "dot\n"; return 1; }
            int ip = d / 4;
            if ((ip & 1) == 0) ++row_ones;
            if (i != j && ip == 0) {
                if (j < 64) orth_lo[i] |= 1ULL << j;
                else orth_hi[i] |= 1ULL << (j - 64);
            }
        }
        if (ones < 0) ones = row_ones;
        else if (ones != row_ones) { cerr << "ones\n"; return 1; }
    }
    if (ones != 60) { cerr << "ones value\n"; return 1; }
    vector<array<int, 8>> frames;
    struct Node { int c[8]; int len; uint64_t lo, hi; };
    vector<Node> stack;
    for (int i = 0; i < 112; ++i) {
        uint64_t lo = orth_lo[i], hi = orth_hi[i];
        if (i < 64) { lo &= (i ? (1ULL << i) - 1 : 0); hi = 0; }
        else hi &= (1ULL << (i - 64)) - 1;
        Node node{};
        node.c[0] = i; node.len = 1; node.lo = lo; node.hi = hi;
        stack.push_back(node);
    }
    while (!stack.empty()) {
        Node cur = stack.back();
        stack.pop_back();
        if (cur.len == 8) {
            array<int, 8> fr{};
            for (int t = 0; t < 8; ++t) fr[t] = cur.c[t];
            frames.push_back(fr);
            continue;
        }
        uint64_t lo = cur.lo, hi = cur.hi;
        while (lo || hi) {
            int j = lo ? __builtin_ctzll(lo) : 64 + __builtin_ctzll(hi);
            if (lo) lo &= lo - 1; else hi &= hi - 1;
            uint64_t nlo = cur.lo & orth_lo[j];
            uint64_t nhi = cur.hi & orth_hi[j];
            if (j < 64) { nlo &= (j ? (1ULL << j) - 1 : 0); nhi = 0; }
            else nhi &= (1ULL << (j - 64)) - 1;
            Node nxt = cur;
            nxt.c[cur.len] = j;
            nxt.len = cur.len + 1;
            nxt.lo = nlo;
            nxt.hi = nhi;
            stack.push_back(nxt);
        }
    }
    if (frames.size() != 1260) { cerr << "frames " << frames.size() << "\n"; return 1; }
    vector<array<uint64_t, 20>> line_frames(112);
    for (int fi = 0; fi < 1260; ++fi)
        for (int i : frames[fi]) line_frames[i][fi >> 6] |= 1ULL << (fi & 63);
    array<int, 112> through{};
    for (int i = 0; i < 112; ++i)
        for (int w = 0; w < 20; ++w) through[i] += __builtin_popcountll(line_frames[i][w]);
    for (int i = 0; i < 112; ++i)
        if (through[i] != 90) { cerr << "through\n"; return 1; }

    auto bits9 = [](uint16_t v) {
        array<int, 9> b{};
        for (int k = 0; k < 9; ++k) b[k] = (v >> (8 - k)) & 1;
        return b;
    };
    int basis_idx[9], nb = 0;
    auto rank_of = [&](const vector<int>& ids) {
        uint16_t rows[9];
        int n = 0;
        for (int id : ids) {
            uint16_t v = labels[id];
            for (int s = 0; s < n; ++s) {
                int piv = 31 - __builtin_clz(rows[s]);
                if ((v >> piv) & 1) v ^= rows[s];
            }
            if (!v) continue;
            int piv = 31 - __builtin_clz(v);
            for (int s = 0; s < n; ++s) if ((rows[s] >> piv) & 1) rows[s] ^= v;
            rows[n++] = v;
        }
        return n;
    };
    for (int i = 0; i < 112 && nb < 9; ++i) {
        vector<int> ids(basis_idx, basis_idx + nb);
        ids.push_back(i);
        if (rank_of(ids) == nb + 1) basis_idx[nb++] = i;
    }
    if (nb != 9) { cerr << "basis\n"; return 1; }
    int G[9][9];
    for (int a = 0; a < 9; ++a)
        for (int b = 0; b < 9; ++b) {
            int ip = dot8(kept[basis_idx[a]].data(), kept[basis_idx[b]].data()) / 4;
            G[a][b] = (ip % 2 == 0);
        }
    int M[9][18] = {};
    for (int k = 0; k < 9; ++k) {
        auto b = bits9(labels[basis_idx[k]]);
        for (int i = 0; i < 9; ++i) M[i][k] = b[i];
        M[k][9 + k] = 1;
    }
    for (int col = 0; col < 9; ++col) {
        int piv = col;
        while (piv < 9 && !M[piv][col]) ++piv;
        if (piv == 9) { cerr << "singular labels\n"; return 1; }
        for (int j = 0; j < 18; ++j) swap(M[col][j], M[piv][j]);
        for (int r = 0; r < 9; ++r) if (r != col && M[r][col])
            for (int j = 0; j < 18; ++j) M[r][j] ^= M[col][j];
    }
    int Minv[9][9];
    for (int i = 0; i < 9; ++i)
        for (int j = 0; j < 9; ++j) Minv[i][j] = M[i][9 + j];
    int S[9][9] = {};
    for (int i = 0; i < 9; ++i)
        for (int j = 0; j < 9; ++j) {
            int acc = 0;
            for (int k = 0; k < 9; ++k)
                for (int t = 0; t < 9; ++t)
                    if (Minv[k][i] && G[k][t] && Minv[t][j]) acc ^= 1;
            S[i][j] = acc;
        }
    uint16_t dual[512] = {};
    for (int v = 0; v < 512; ++v) {
        auto vb = bits9((uint16_t)v);
        uint16_t out = 0;
        for (int i = 0; i < 9; ++i) {
            int acc = 0;
            for (int j = 0; j < 9; ++j) if (vb[j] && S[i][j]) acc ^= 1;
            if (acc) out |= 1u << (8 - i);
        }
        dual[v] = out;
    }
    auto form = [&](uint16_t u, uint16_t v) { return parity(u & dual[v]); };
    for (int i = 0; i < 112; ++i)
        for (int j = 0; j < 112; ++j) {
            int ip = dot8(kept[i].data(), kept[j].data()) / 4;
            int expect = (ip % 2 == 0);
            if (form(labels[i], labels[j]) != expect) { cerr << "form\n"; return 1; }
        }
    int srank = 0;
    {
        uint16_t rows[9];
        int n = 0;
        for (int i = 0; i < 9; ++i) {
            uint16_t v = 0;
            for (int j = 0; j < 9; ++j) if (S[i][j]) v |= 1u << (8 - j);
            for (int s = 0; s < n; ++s) {
                int piv = 31 - __builtin_clz(rows[s]);
                if ((v >> piv) & 1) v ^= rows[s];
            }
            if (!v) continue;
            int piv = 31 - __builtin_clz(v);
            for (int s = 0; s < n; ++s) if ((rows[s] >> piv) & 1) rows[s] ^= v;
            rows[n++] = v;
        }
        srank = n;
    }
    if (srank != 9) { cerr << "S rank\n"; return 1; }

    auto add_span = [](uint16_t* basis, int* n, uint16_t v) {
        for (int s = 0; s < *n; ++s) {
            int piv = 31 - __builtin_clz(basis[s]);
            if ((v >> piv) & 1) v ^= basis[s];
        }
        if (!v) return;
        int piv = 31 - __builtin_clz(v);
        for (int s = 0; s < *n; ++s) if ((basis[s] >> piv) & 1) basis[s] ^= v;
        basis[(*n)++] = v;
    };
    auto enumerate = [&](int ann_dim, vector<Flat>& flats, vector<array<uint64_t, 20>>& masks) {
        vector<int> pivots;
        function<void(int,int)> choose = [&](int start, int left) {
            if (!left) {
                int free_pos_row[32], free_pos_col[32], np = 0;
                bool is_piv[9] = {};
                for (int p : pivots) is_piv[p] = true;
                for (int r = 0; r < ann_dim; ++r)
                    for (int c = pivots[r] + 1; c < 9; ++c)
                        if (!is_piv[c]) { free_pos_row[np] = r; free_pos_col[np] = c; ++np; }
                int nmask = 1 << np;
                for (int mask = 0; mask < nmask; ++mask) {
                    uint16_t g[3] = {};
                    for (int r = 0; r < ann_dim; ++r) g[r] = (uint16_t)(1u << (8 - pivots[r]));
                    for (int b = 0; b < np; ++b)
                        if ((mask >> b) & 1) g[free_pos_row[b]] |= (uint16_t)(1u << (8 - free_pos_col[b]));
                    Flat flat{};
                    flat.ann_dim = ann_dim;
                    flat.ambient_dim = 9 - ann_dim;
                    for (int r = 0; r < ann_dim; ++r) flat.ann[r] = g[r];
                    flat.key = pack_ann(g, ann_dim);
                    array<uint64_t, 20> fb{};
                    int nports = 0, span_n = 0;
                    for (int i = 0; i < 112; ++i) {
                        bool killed = false;
                        for (int r = 0; r < ann_dim; ++r)
                            if (form(labels[i], g[r])) { killed = true; break; }
                        if (killed) continue;
                        ++nports;
                        add_span(flat.basis, &span_n, labels[i]);
                        for (int w = 0; w < 20; ++w) fb[w] |= line_frames[i][w];
                    }
                    flat.span_dim = span_n;
                    flat.nports = nports;
                    int hits = 0;
                    for (uint64_t w : fb) hits += __builtin_popcountll(w);
                    flat.hits = hits;
                    flat.index = (int)flats.size();
                    flats.push_back(flat);
                    masks.push_back(fb);
                }
                return;
            }
            for (int p = start; p <= 9 - left; ++p) {
                pivots.push_back(p);
                choose(p + 1, left - 1);
                pivots.pop_back();
            }
        };
        if (ann_dim == 0) {
            Flat flat{};
            flat.ann_dim = 0;
            flat.ambient_dim = 9;
            flat.key = pack_ann(flat.ann, 0);
            array<uint64_t, 20> fb{};
            int span_n = 0;
            for (int i = 0; i < 112; ++i) {
                add_span(flat.basis, &span_n, labels[i]);
                for (int w = 0; w < 20; ++w) fb[w] |= line_frames[i][w];
            }
            flat.span_dim = span_n;
            flat.nports = 112;
            int hits = 0;
            for (uint64_t w : fb) hits += __builtin_popcountll(w);
            flat.hits = hits;
            flat.index = (int)flats.size();
            flats.push_back(flat);
            masks.push_back(fb);
            return;
        }
        choose(0, ann_dim);
    };

    vector<Flat> flats;
    vector<array<uint64_t, 20>> masks;
    enumerate(3, flats, masks);
    if ((int)flats.size() != 788035) { cerr << "dim6 count " << flats.size() << "\n"; return 1; }
    int low = 0, full = 0;
    int span_hist[10] = {};
    for (auto& f : flats) {
        span_hist[f.span_dim]++;
        if (f.span_dim == 6) ++full;
        else ++low;
    }
    cout << "dim6 " << flats.size() << " full " << full << " low " << low << "\n";
    cout << "span";
    for (int i = 0; i < 10; ++i) cout << " " << i << ":" << span_hist[i];
    cout << "\n";

    unordered_map<uint64_t, int> index;
    index.reserve(flats.size() * 2);

    // Dim-3 subspaces of a fixed 6-bit coordinate space.
    vector<array<uint16_t, 3>> quot;
    {
        vector<int> pivots;
        function<void(int,int)> choose = [&](int start, int left) {
            if (!left) {
                int free_row[32], free_col[32], np = 0;
                bool is_piv[6] = {};
                for (int p : pivots) is_piv[p] = true;
                for (int r = 0; r < 3; ++r)
                    for (int c = pivots[r] + 1; c < 6; ++c)
                        if (!is_piv[c]) { free_row[np] = r; free_col[np] = c; ++np; }
                for (int mask = 0; mask < (1 << np); ++mask) {
                    array<uint16_t, 3> g{};
                    for (int r = 0; r < 3; ++r) g[r] = (uint16_t)(1u << pivots[r]);
                    for (int b = 0; b < np; ++b)
                        if ((mask >> b) & 1) g[free_row[b]] |= (uint16_t)(1u << free_col[b]);
                    quot.push_back(g);
                }
                return;
            }
            for (int p = start; p <= 6 - left; ++p) {
                pivots.push_back(p);
                choose(p + 1, left - 1);
                pivots.pop_back();
            }
        };
        choose(0, 3);
    }
    if ((int)quot.size() != 1395) { cerr << "quot " << quot.size() << "\n"; return 1; }

    auto rref_pack = [&](const uint16_t* gens, int ngen) {
        uint16_t rows[9];
        int n = 0;
        for (int i = 0; i < ngen; ++i) {
            uint16_t v = gens[i] & 511;
            for (int s = 0; s < n; ++s) {
                int piv = 31 - __builtin_clz(rows[s]);
                if ((v >> piv) & 1) v ^= rows[s];
            }
            if (!v) continue;
            int piv = 31 - __builtin_clz(v);
            for (int s = 0; s < n; ++s) if ((rows[s] >> piv) & 1) rows[s] ^= v;
            rows[n++] = v;
        }
        if (n != 6) { cerr << "ambient dim " << n << "\n"; exit(1); }
        sort(rows, rows + n, [](uint16_t a, uint16_t b) {
            return (31 - __builtin_clz(a)) < (31 - __builtin_clz(b));
        });
        return pack6(rows);
    };
    auto kernel_basis = [&](const uint16_t* gens, int ngen, int expect, uint16_t* out) {
        int rows[16][10] = {};
        int n = 0;
        for (int t = 0; t < ngen; ++t) {
            uint16_t dv = dual[gens[t] & 511];
            for (int c = 0; c < 9; ++c) rows[n][c] = (dv >> (8 - c)) & 1;
            rows[n][9] = 0;
            for (int s = 0; s < n; ++s) {
                int piv = 0;
                while (piv < 9 && !rows[s][piv]) ++piv;
                if (piv < 9 && rows[n][piv])
                    for (int c = 0; c <= 9; ++c) rows[n][c] ^= rows[s][c];
            }
            int piv = 0;
            while (piv < 9 && !rows[n][piv]) ++piv;
            if (piv == 9) {
                if (rows[n][9]) { cerr << "inconsistent orth\n"; exit(1); }
                continue;
            }
            for (int s = 0; s < n; ++s) if (rows[s][piv])
                for (int c = 0; c <= 9; ++c) rows[s][c] ^= rows[n][c];
            ++n;
        }
        int pivot_of_row[9], pivot_row[9];
        for (int c = 0; c < 9; ++c) pivot_row[c] = -1;
        for (int s = 0; s < n; ++s) {
            int piv = 0;
            while (piv < 9 && !rows[s][piv]) ++piv;
            pivot_of_row[s] = piv;
            pivot_row[piv] = s;
        }
        int produced = 0;
        for (int free_c = 0; free_c < 9; ++free_c) if (pivot_row[free_c] < 0) {
            int sol[9] = {};
            sol[free_c] = 1;
            for (int s = n - 1; s >= 0; --s) {
                int piv = pivot_of_row[s];
                int acc = rows[s][9];
                for (int c = piv + 1; c < 9; ++c) if (rows[s][c] && sol[c]) acc ^= 1;
                sol[piv] = acc;
            }
            uint16_t v = 0;
            for (int c = 0; c < 9; ++c) if (sol[c]) v |= (uint16_t)(1u << (8 - c));
            out[produced++] = v;
        }
        if (produced != expect) { cerr << "kernel dim " << produced << " expected " << expect << "\n"; exit(1); }
    };
    for (auto& f : flats) {
        uint16_t amb[6];
        kernel_basis(f.ann, 3, 6, amb);
        f.key = rref_pack(amb, 6);
        if (!index.emplace(f.key, f.index).second) { cerr << "duplicate ambient key\n"; return 1; }
    }
    auto pop_and = [&](const array<uint64_t, 20>& a, const array<uint64_t, 20>& b) {
        int h = 0;
        for (int w = 0; w < 20; ++w) h += __builtin_popcountll(a[w] & b[w]);
        return h;
    };
    auto beta_basis = [&](const Flat& a, const Flat& b) {
        if (!a.span_dim || !b.span_dim) return 0;
        int rows[9] = {};
        int n = 0;
        for (int i = 0; i < a.span_dim; ++i) {
            int row = 0;
            for (int j = 0; j < b.span_dim; ++j)
                if (form(a.basis[i], b.basis[j])) row |= 1 << j;
            for (int s = 0; s < n; ++s) {
                int piv = 31 - __builtin_clz((unsigned)rows[s]);
                if ((row >> piv) & 1) row ^= rows[s];
            }
            if (!row) continue;
            int piv = 31 - __builtin_clz((unsigned)row);
            for (int s = 0; s < n; ++s) if ((rows[s] >> piv) & 1) rows[s] ^= row;
            rows[n++] = row;
        }
        return n;
    };

    struct Best {
        int hits = -1;
        int beta = 1;
        int i = -1, j = -1;
        const char* kind = "";
    } best;
    auto consider = [&](int hits, int beta, int i, int j, const char* kind) {
        if (beta <= 0 || hits < 0) return;
        // compare hits/beta vs best.hits/best.beta
        if (best.hits < 0 || (long)hits * best.beta > (long)best.hits * beta) {
            best.hits = hits; best.beta = beta; best.i = i; best.j = j; best.kind = kind;
        }
    };

    // Self pairs.
    for (auto& f : flats)
        consider(f.hits, beta_basis(f, f), f.index, f.index, "self");
    cout << "after self " << best.hits << "/" << best.beta
         << " ratio " << (double)best.hits / (1260.0 * best.beta) << " kind " << best.kind << endl;
    int best_beta3_hits = 0;
    for (auto& f : flats) {
        if (f.span_dim != 6) continue;
        int b = beta_basis(f, f);
        if (b == 3 && f.hits > best_beta3_hits) best_beta3_hits = f.hits;
    }
    cout << "best self beta3 hits " << best_beta3_hits << endl;

    // Algebraic beta-3 pairs of full-span dim-6 flats. Intersection cannot
    // exceed either side's hit count, so flats at or below the best beta-3
    // self-hit cannot improve that hit count.
    long long beta3_pairs = 0;
    int beta3_checked_formula = 0;
    int beta3_scanned = 0;
    for (auto& f : flats) {
        if (f.span_dim != 6 || f.hits <= best_beta3_hits) continue;
        ++beta3_scanned;
        // Complement of the annihilator.
        uint16_t comp[6];
        int nc = 0;
        uint16_t rows[9];
        int nr = 0;
        for (int r = 0; r < 3; ++r) {
            uint16_t v = f.ann[r];
            for (int s = 0; s < nr; ++s) {
                int piv = 31 - __builtin_clz(rows[s]);
                if ((v >> piv) & 1) v ^= rows[s];
            }
            if (!v) { cerr << "ann dep\n"; return 1; }
            int piv = 31 - __builtin_clz(v);
            for (int s = 0; s < nr; ++s) if ((rows[s] >> piv) & 1) rows[s] ^= v;
            rows[nr++] = v;
        }
        for (int bit = 0; bit < 9; ++bit) {
            uint16_t v = (uint16_t)(1u << (8 - bit));
            for (int s = 0; s < nr; ++s) {
                int piv = 31 - __builtin_clz(rows[s]);
                if ((v >> piv) & 1) v ^= rows[s];
            }
            if (!v) continue;
            int piv = 31 - __builtin_clz(v);
            for (int s = 0; s < nr; ++s) if ((rows[s] >> piv) & 1) rows[s] ^= v;
            rows[nr++] = v;
            comp[nc++] = (uint16_t)(1u << (8 - bit));
            if (nc == 6) break;
        }
        if (nc != 6) { cerr << "complement\n"; return 1; }
        for (auto& T : quot) {
            uint16_t gens[6];
            for (int r = 0; r < 3; ++r) gens[r] = f.ann[r];
            for (int r = 0; r < 3; ++r) {
                uint16_t v = 0;
                for (int b = 0; b < 6; ++b)
                    if ((T[r] >> b) & 1) v ^= comp[b];
                gens[3 + r] = v;
            }
            uint64_t key = rref_pack(gens, 6);
            auto it = index.find(key);
            if (it == index.end()) { cerr << "missing partner\n"; return 1; }
            int j = it->second;
            if (j < f.index) continue; // unordered once
            const Flat& g = flats[j];
            int hits = pop_and(masks[f.index], masks[j]);
            int beta;
            if (g.span_dim == 6) {
                beta = 3;
                if (beta3_checked_formula < 20) {
                    int exact = beta_basis(f, g);
                    if (exact != 3) { cerr << "formula " << exact << "\n"; return 1; }
                    ++beta3_checked_formula;
                }
            } else {
                beta = beta_basis(f, g);
            }
            consider(hits, beta, f.index, j, "beta3");
            ++beta3_pairs;
        }
    }
    cout << "beta3 scanned " << beta3_scanned << " unordered " << beta3_pairs
         << " best " << best.hits << "/" << best.beta
         << " ratio " << (double)best.hits / (1260.0 * best.beta)
         << " kind " << best.kind << endl;

    // Low-span flats against every dim-6 flat.
    long long low_pairs = 0;
    int low_threshold_hits = best.hits; // beta >= 1, need hits/1 > best.hits/best.beta
    for (auto& f : flats) {
        if (f.span_dim == 6 || f.span_dim == 0) continue;
        // Even beta 1 cannot beat the current ratio unless this flat's own hits are large enough.
        if ((long)f.hits * best.beta <= (long)best.hits * 1) continue;
        for (int j = 0; j < (int)flats.size(); ++j) {
            int hits = pop_and(masks[f.index], masks[j]);
            if ((long)hits * best.beta <= (long)best.hits * 1) continue;
            int beta = beta_basis(f, flats[j]);
            consider(hits, beta, f.index, j, "low");
            ++low_pairs;
        }
    }
    cout << "low evaluated " << low_pairs
         << " best " << best.hits << "/" << best.beta
         << " ratio " << (double)best.hits / (1260.0 * best.beta)
         << " kind " << best.kind << "\n";

    // Higher ambient dimensions: record span dims and self ratios. The pairing-rank
    // inequality beta >= d1 + d2 - 9 is checked on a complete self-sample and
    // on one partner from each ambient dimension.
    for (int ann_dim : {2, 1, 0}) {
        vector<Flat> extra;
        vector<array<uint64_t, 20>> extra_masks;
        enumerate(ann_dim, extra, extra_masks);
        int hist[10] = {};
        int below = 0;
        for (auto& f : extra) {
            hist[f.span_dim]++;
            int self_b = beta_basis(f, f);
            int lower = f.span_dim + f.span_dim - 9;
            if (self_b < lower) { cerr << "inequality self\n"; return 1; }
            consider(f.hits, self_b, -ann_dim, f.nports, "higher-self");
            if (f.span_dim < 6) ++below;
            // one cross-check against flats[0]
            if (!extra.empty() && f.index == 0 && flats[0].span_dim) {
                int b = beta_basis(f, flats[0]);
                int bound = f.span_dim + flats[0].span_dim - 9;
                if (b < bound) { cerr << "inequality cross\n"; return 1; }
            }
        }
        cout << "ann " << ann_dim << " count " << extra.size() << " span<6 " << below << " hist";
        for (int i = 0; i < 10; ++i) if (hist[i]) cout << " " << i << ":" << hist[i];
        cout << "\n";
        if (below) {
            // Brute force the rare lower-span higher flats.
            for (auto& f : extra) if (f.span_dim && f.span_dim < 6) {
                if ((long)f.hits * best.beta <= (long)best.hits) continue;
                for (int j = 0; j < (int)flats.size(); ++j) {
                    int hits = pop_and(extra_masks[f.index], masks[j]);
                    int beta = beta_basis(f, flats[j]);
                    consider(hits, beta, -100 - ann_dim, j, "higher-low");
                }
            }
        }
    }

    // Low-span codimension-3 supports against every larger flat. A beta-1 pair
// beats the current ratio only when the intersection exceeds best.hits
// (the current champion has beta 1).
{
    vector<Flat> larger;
    vector<array<uint64_t, 20>> larger_masks;
    for (int ann_dim : {2, 1, 0}) enumerate(ann_dim, larger, larger_masks);
    long long cross = 0;
    for (auto& f : flats) {
        if (f.span_dim == 0 || f.span_dim >= 6) continue;
        if ((long)f.hits * best.beta <= (long)best.hits) continue;
        for (int j = 0; j < (int)larger.size(); ++j) {
            int hits = pop_and(masks[f.index], larger_masks[j]);
            if ((long)hits * best.beta <= (long)best.hits) continue;
            int beta = beta_basis(f, larger[j]);
            consider(hits, beta, f.index, -1, "low-larger");
            ++cross;
        }
    }
    // Ambient dimension 7 with port-span 6 can pair at rank 1 with a
    // low-span support. There are only a handful of these spans.
    for (auto& f : larger) {
        if (f.span_dim == 0 || f.span_dim >= 6) continue;
        if ((long)f.hits * best.beta <= (long)best.hits) continue;
        for (int j = 0; j < (int)larger.size(); ++j) {
            int hits = pop_and(larger_masks[f.index], larger_masks[j]);
            if ((long)hits * best.beta <= (long)best.hits) continue;
            int beta = beta_basis(f, larger[j]);
            consider(hits, beta, -1, -1, "larger-low");
            ++cross;
        }
    }
    cout << "larger cross " << cross
         << " best " << best.hits << "/" << best.beta
         << " kind " << best.kind << endl;
}

    long long num = best.hits;
    long long den = 1260LL * best.beta;
    long long g = std::gcd(num, den);
    num /= g; den /= g;
    const Flat* left = best.i >= 0 && best.i < (int)flats.size() ? &flats[best.i] : nullptr;
    const Flat* right = best.j >= 0 && best.j < (int)flats.size() ? &flats[best.j] : nullptr;
    cout << "BEST hits " << best.hits << " beta " << best.beta
         << " fraction " << num << "/" << den
         << " kind " << best.kind
         << " i " << best.i << " j " << best.j << "\n";
    if (left && right) {
        cout << "ATTAIN i_ports " << left->nports << " i_span " << left->span_dim
             << " i_amb " << left->ambient_dim
             << " j_ports " << right->nports << " j_span " << right->span_dim
             << " j_amb " << right->ambient_dim << "\n";
        auto dump_ports = [&](const char* tag, const Flat& f) {
        cout << tag;
        for (int i = 0; i < 112; ++i) {
            bool killed = false;
            for (int r = 0; r < f.ann_dim; ++r)
                if (form(labels[i], f.ann[r])) { killed = true; break; }
            if (killed) continue;
            cout << " [";
            for (int t = 0; t < 8; ++t) cout << (t ? "," : "") << kept[i][t];
            cout << "]";
        }
        cout << "\n";
    };
    dump_ports("WITNESS_I", *left);
    dump_ports("WITNESS_J", *right);
    }
    cout << "PASS_CENSUS " << num << "/" << den << "\n";
    return 0;
}
