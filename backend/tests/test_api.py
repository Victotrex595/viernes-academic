import os
os.environ["PHONEAPP_FORCE_SIMULATION"] = "1"
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_and_initial_seed():
    r = client.get("/api/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert data["saia"]["configured"] is True

    r_courses = client.get("/api/courses")
    assert r_courses.status_code == 200
    courses = r_courses.json()["courses"]
    assert len(courses) >= 6

    # Check that VIDEO EXPOSITIVO was auto-detected as 'video' mode
    video_tasks = [
        a
        for c in courses
        for a in c["assignments"]
        if "VIDEO EXPOSITIVO" in a["title"].upper()
    ]
    assert len(video_tasks) >= 1
    assert video_tasks[0]["task_mode"] == "video"
    assert video_tasks[0]["allow_token_spend"] is False


def test_four_pillars_research_generation():
    courses = client.get("/api/courses").json()["courses"]
    first_psm = next(c for c in courses if not c["is_external"] and c["assignments"])
    act_id = first_psm["assignments"][0]["id"]

    res = client.post(f"/api/assignments/{act_id}/research")
    assert res.status_code == 200
    payload = res.json()
    assert payload["ok"] is True
    files = payload["assignment"]["research_files"]
    assert len(files) == 4
    for item in files:
        assert os.path.exists(item["local_path"])


def test_token_protection_switch_and_resolution():
    courses = client.get("/api/courses").json()["courses"]
    first_psm = next(c for c in courses if not c["is_external"] and c["assignments"])
    act_id = first_psm["assignments"][0]["id"]

    # Ensure switch is OFF
    client.patch(f"/api/assignments/{act_id}/controls", json={"allow_token_spend": False})

    # Must block resolution when switch is OFF and no resolution exists yet (or when force=true)
    blocked = client.post(f"/api/assignments/{act_id}/resolve?force=true")
    assert blocked.status_code == 403

    # Turn switch ON and set mode to 'manuscrito'
    patched = client.patch(
        f"/api/assignments/{act_id}/controls",
        json={"allow_token_spend": True, "task_mode": "manuscrito"},
    )
    assert patched.status_code == 200
    assert patched.json()["assignment"]["allow_token_spend"] is True
    assert patched.json()["assignment"]["task_mode"] == "manuscrito"

    # Now resolution must succeed
    resolved = client.post(f"/api/assignments/{act_id}/resolve?force=true")
    assert resolved.status_code == 200
    res_data = resolved.json()
    assert res_data["ok"] is True
    first_path = res_data["assignment"]["resolution_local_path"]
    assert os.path.exists(first_path)

    # Calling again without force=true must return cached=True (0 extra tokens spent)
    cached_res = client.post(f"/api/assignments/{act_id}/resolve")
    assert cached_res.status_code == 200
    assert cached_res.json().get("cached") is True

    # Calling with force=true must create a non-destructive versioned file (_v2.docx or higher)
    v2_res = client.post(f"/api/assignments/{act_id}/resolve?force=true")
    assert v2_res.status_code == 200
    second_path = v2_res.json()["assignment"]["resolution_local_path"]
    assert os.path.exists(second_path)
    assert second_path != first_path
    assert "_v" in os.path.basename(second_path)


def test_external_non_psm_topic_creation():
    res = client.post(
        "/api/external/create",
        data={
            "title": "Arquitectura de Microservicios y Kubernetes",
            "description_text": "Investigar patrones de resiliencia, circuit breakers y despliegue en contenedores.",
            "category_name": "Curso Externo Cloud",
            "task_mode": "digital",
        },
        files=[("files", ("temario_extra.txt", b"1. Docker\n2. Kubernetes\n3. Istio Service Mesh", "text/plain"))],
    )
    assert res.status_code == 200
    created = res.json()["assignment"]
    assert created["is_external"] is True
    assert created["title"] == "Arquitectura de Microservicios y Kubernetes"

    # Run 4 pillars on external topic
    r_res = client.post(f"/api/assignments/{created['id']}/research")
    assert r_res.status_code == 200
    assert len(r_res.json()["assignment"]["research_files"]) == 4

    # Inspect generated documents and guidelines
    r_insp = client.get(f"/api/assignments/{created['id']}/inspect")
    assert r_insp.status_code == 200
    insp_data = r_insp.json()
    assert len(insp_data["ai_generated_documents"]) == 4
    assert "Pilar 1: PREPARAR" in insp_data["ai_generated_documents"][0]["content"]
