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


def _bersihkan(client, path, grup_aktif=None):
    data = {}
    if grup_aktif is not None:
        data["grup_aktif"] = json.dumps(grup_aktif)
    with open(path, "rb") as fp:
        return client.post(
            "/api/bersihkan",
            files={"file": ("data.xlsx", fp, "application/octet-stream")},
            data=data,
        )


def test_periksa_mengembalikan_grup(client):
    c, f = client
    data = _unggah(c, f).json()
    grup = data["lembar"][0]["grup"]
    assert grup, "fixture '  Ani  ' seharusnya menghasilkan perbaikan"
    assert all("kunci" in g and "jumlah" in g for g in grup)


def test_bersihkan_semua_centang_dikosongkan(client):
    c, f = client
    r = _bersihkan(c, f, grup_aktif=[])
    assert r.status_code == 200
    assert r.json()["perubahan"] == 0


def test_bersihkan_hanya_grup_tercentang(client):
    c, f = client
    data = _unggah(c, f).json()
    kunci = [f"0|{g['kunci']}" for g in data["lembar"][0]["grup"] if g["aman"]]
    assert kunci
    r = _bersihkan(c, f, grup_aktif=kunci)
    assert r.status_code == 200
    n_semua = _bersihkan(c, f).json()["perubahan"]
    assert r.json()["perubahan"] == n_semua
