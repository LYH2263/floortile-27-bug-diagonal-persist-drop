from fastapi import APIRouter, HTTPException

from app.repositories import settings_repo
from app.schemas.estimate import DiagFactorRequest

router = APIRouter(tags=["settings"])


@router.get("/settings")
def get_settings():
    return settings_repo.get_all()


@router.put("/settings/diag-factor")
def update_diag_factor(body: DiagFactorRequest):
    try:
        factor = settings_repo.set_diag_factor(body.diag_factor)
    except ValueError as exc:
        raise HTTPException(422, str(exc))
    return {"diag_factor": factor}
