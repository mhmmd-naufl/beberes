"""Deteksi duplikat (DUP001 persis, DUP002 mirip).

Duplikat TIDAK pernah dihapus otomatis (docs/03) — hanya ditandai.
Fuzzy memakai difflib (stdlib) dengan blocking huruf pertama supaya
 tidak O(n²) pada file besar. rapidfuzz bisa dipertimbangkan nanti.
"""

from .deteksi import deteksi

__all__ = ["deteksi"]
