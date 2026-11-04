#!/usr/bin/env python3
"""Content-addressed Git tree OIDs for the reconciliation verifiers.

The predecessor walk in the three community reconciliation verifiers built a
PurePosixPath object for every source path, then hashed each tree from scratch.
Those verifiers call it once per pinned commit and, for two of the audits, once
more per CI checkout. Many of those listings repeat.

This module keeps that digest definition and reuses a result only when the
complete (path, mode, blob) listing matches. A changed path, mode or blob is a
different key. Callers still require the returned OID to equal an independently
pinned tree SHA. ``audit=True`` recomputes even on a hit and rejects a cache
value that disagrees with that recomputation.

The predecessor implementation is retained so a differential check can compare
the two functions directly. Apache-2.0.
"""
import hashlib
from pathlib import PurePosixPath


_SHARED = {}


def git_oid(kind, raw):
    return hashlib.sha1(kind.encode() + b' ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()


def listing_key(files):
    """Every dependency of the tree digest, in listed order."""
    return tuple((item['path'], item['mode'], item['blob']) for item in files)


def predecessor_tree_oid(files):
    """The tree walk previously inlined in the three reconciliation verifiers."""
    tree = {}
    for item in files:
        path = PurePosixPath(item['path'])
        if path.is_absolute() or '..' in path.parts or str(path) != item['path']:
            raise ValueError('Unsafe source path')
        node = tree
        for part in path.parts[:-1]:
            node = node.setdefault(part, {})
        if path.name in node:
            raise ValueError('Duplicate source path')
        if item['mode'] not in ('100644', '100755'):
            raise ValueError('Unexpected source mode')
        node[path.name] = (item['mode'], item['blob'])

    def encode(node):
        entries = []
        for name, value in node.items():
            directory = isinstance(value, dict)
            mode, sha = ('40000', encode(value)) if directory else value
            entries.append((
                (name + ('/' if directory else '')).encode(),
                mode.encode() + b' ' + name.encode() + b'\0' + bytes.fromhex(sha),
            ))
        return git_oid('tree', b''.join(raw for _key, raw in sorted(entries)))

    return encode(tree)


def _components(path):
    """Match PurePosixPath acceptance used by predecessor_tree_oid.

    Legal listings in the pinned audits are ordinary relative paths. This
    rejects the same absolute paths, empty components, '.' components and '..'
    components that the predecessor rejects, without building a path object.
    The single path '.' is the one predecessor exception and is preserved.
    """
    if not isinstance(path, str) or path == '' or path[0] == '/':
        raise ValueError('Unsafe source path')
    if path == '.':
        return ()
    parts = path.split('/')
    if any(part in ('', '.', '..') for part in parts):
        raise ValueError('Unsafe source path')
    return tuple(parts)


def _encode(node):
    entries = []
    for name, value in node.items():
        directory = isinstance(value, dict)
        mode, sha = ('40000', _encode(value)) if directory else value
        entries.append((
            (name + ('/' if directory else '')).encode(),
            mode.encode() + b' ' + name.encode() + b'\0' + bytes.fromhex(sha),
        ))
    return git_oid('tree', b''.join(raw for _key, raw in sorted(entries)))


def compute_tree_oid(files):
    tree = {}
    for item in files:
        parts = _components(item['path'])
        node = tree
        for part in parts[:-1]:
            child = node.get(part)
            if child is None:
                child = {}
                node[part] = child
            elif not isinstance(child, dict):
                raise ValueError('Unsafe source path')
            node = child
        name = parts[-1] if parts else ''
        if name in node:
            raise ValueError('Duplicate source path')
        if item['mode'] not in ('100644', '100755'):
            raise ValueError('Unexpected source mode')
        node[name] = (item['mode'], item['blob'])
    return _encode(tree)


def tree_oid(files, cache=None, audit=False):
    """Return the Git tree OID for ``files``.

    ``cache`` defaults to a process-local table. Pass a fresh dict to isolate
    a call. On a hit the listing is not walked again unless ``audit`` is set.
    A hit whose stored OID differs from a fresh walk raises ``ValueError``.
    """
    if cache is None:
        cache = _SHARED
    key = listing_key(files)
    cached = cache.get(key)
    if cached is not None and not audit:
        return cached
    fresh = compute_tree_oid(files)
    if cached is not None and cached != fresh:
        raise ValueError('Stale tree cache')
    cache[key] = fresh
    return fresh
