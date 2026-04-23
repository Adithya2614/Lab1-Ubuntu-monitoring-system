"""
WMI Controller — Backward Compatibility Wrapper
=================================================
Re-exports the new backend application from backend.app.main.
This file exists so that `python -m controller.main` still works.
The old startup flow is preserved:
  .venv/bin/python3 -m controller.main
"""

# Re-export the new production app
from backend.app.main import app  # noqa: F401

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
