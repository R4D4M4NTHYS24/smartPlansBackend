 # ■ tests/test_core.py
import builtins, json

from main import Plan

def test_plan_validation():
     """El modelo Plan valida fechas ISO y prioridad por defecto."""
     p = Plan(
         nombre="Dummy", responsable="QA", cargo="Test",
         objetivo="Aumentar ventas", fecha="2025-12-31",
         descripcion="desc"
     )
     assert p.fecha == "2025-12-31"
     assert p.prioridad is None
