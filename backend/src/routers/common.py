from fastapi import HTTPException

from src.models.group import Group
from src.state import GROUPS


def get_group_or_404(group_id: str) -> Group:
    group = GROUPS.get(group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Grupo não encontrado")
    return group
