from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from beberes.ui.app import buat_app

BERKAS = Path(__file__).parent.parent / "data_uji" / "berantakan_kas.xlsx"


@pytest.fixture
def client():
    return TestClient(buat_app())


def _unggah(client, endpoint):
    with open(BERKAS, "rb") as f:
        return client.post(
            endpoint,
            files={"file": ("kas.xlsx", f, "application/octet-stream")},
        )


def test_index(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "beberes" in r.text


def test_periksa(client):
    r = _unggah(client, "/api/periksa")
    assert r.status_code == 200
    data = r.json()
    assert len(data["lembar"]) >= 1
    assert "temuan" in data["lembar"][0]


def test_bersihkan_dan_unduh(client):
    r = _unggah(client, "/api/bersihkan")
    assert r.status_code == 200
    data = r.json()
    assert data["perubahan"] > 0
    assert data["unduh"].startswith("/unduh/")
    r2 = client.get(data["unduh"])
    assert r2.status_code == 200
    assert r2.content[:2] == b"PK"  # file xlsx = zip
