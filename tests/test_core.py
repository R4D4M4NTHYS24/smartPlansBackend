# tests/test_core.py
from backend.main import Plan

def test_plan_validation():
    """El modelo Plan deja prioridad vacía por defecto y normaliza la fecha."""
    p = Plan(
        nombre="Dummy", responsable="QA", cargo="Test",
        objetivo="Aumentar ventas", fecha="2025-12-31",
        descripcion="desc"
    )
    assert p.fecha == "2025-12-31"
    assert p.prioridad is None            # default OK
