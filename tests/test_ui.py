import json

import pytest
from fastapi.testclient import TestClient
from openpyxl import Workbook

from beberes.ui.app import buat_app


@pytest.fixture
def client(tmp_path):
    f = tmp_path / "data.xlsx"
    wb = Workbook()
    ws = wb.active
    ws.title = "Data"
    ws.append(["Nama", "Kota"])
    ws.append(["  Ani  ", "Bandung"])
    ws.append(["Budi", "Medan"])
    wb.save(f)
    return TestClient(buat_app()), f


def _unggah(client, path):
    with open(path, "rb") as fp:
        return client.post(
            "/api/periksa",
            files={"file": ("data.xlsx", fp, "application/octet-stream")},
        )


def test_index(client):
    c, _ = client
    r = c.get("/")
    assert r.status_code == 200
    assert "beberes" in r.text


def test_periksa(client):
    c, f = client
    r = _unggah(c, f)
    assert r.status_code == 200
    data = r.json()
    assert len(data["lembar"]) == 1
    assert "temuan" in data["lembar"][0]


def test_bersihkan_dan_unduh(client):
    c, f = client
    with open(f, "rb") as fp:
        r = c.post(
            "/api/bersihkan",
            files={"file": ("data.xlsx", fp, "application/octet-stream")},
        )
    assert r.status_code == 200
    data = r.json()
    assert data["perubahan"] > 0
    r2 = c.get(data["unduh"])
    assert r2.status_code == 200
    assert r2.content[:2] == b"PK"  # file xlsx = zip


def test_periksa_mengembalikan_detail_perbaikan(client):
    c, f = client
    data = _unggah(c, f).json()
    detail = data["lembar"][0]["detail"]
    assert detail, "harus ada usulan perbaikan untuk '  Ani  '"
    p = detail[0]
    for k in ("id", "kode", "sel", "nilai_lama", "nilai_baru", "aman_otomatis"):
        assert k in p


def _bersihkan(client, path, **form):
    with open(path, "rb") as fp:
        return client.post(
            "/api/bersihkan",
            files={"file": ("data.xlsx", fp, "application/octet-stream")},
            data=form,
        )


def test_bersihkan_terpilih_subset(client):
    c, f = client
    detail = _unggah(c, f).json()["lembar"][0]["detail"]
    # hanya terapkan perbaikan pertama
    r = _bersihkan(c, f, terpilih=json.dumps([detail[0]["id"]]))
    assert r.status_code == 200
    assert r.json()["perubahan"] == 1


def test_bersihkan_terpilih_kosong(client):
    c, f = client
    r = _bersihkan(c, f, terpilih="[]")
    assert r.status_code == 200
    assert r.json()["perubahan"] == 0
