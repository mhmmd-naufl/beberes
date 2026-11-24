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
