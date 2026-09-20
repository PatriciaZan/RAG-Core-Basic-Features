# AJUDA DA IA
from enum import Enum

PERMISSION_LEVELS = {
    "publico": {
        "allowed_sensitivity": ["publico"]
    },

    "interno": {
        "allowed_sensitivity": [
            "publico",
            "interno"
        ]
    },

    "restrito": {
        "allowed_sensitivity": [
            "publico",
            "interno",
            "restrito"
        ]
    }
}


VALID_PERMISSION_LEVELS = set(PERMISSION_LEVELS.keys())
def resolve_permissions(permission_level: str) -> dict:
    """
    A regra é cumulativa:
        public     -> public
        internal   -> public + internal
        restricted -> public + internal + restricted
    """

    if not isinstance(permission_level, str):
        raise TypeError(
            "permission_level deve ser uma string."
        )

    permission_level = permission_level.strip().lower()

    if permission_level not in VALID_PERMISSION_LEVELS:
        raise ValueError(
            f"Permissão inválida: '{permission_level}'. "
            f"Valores permitidos: {sorted(VALID_PERMISSION_LEVELS)}"
        )

    return {
        "permission_level": permission_level,
        "allowed_sensitivity": PERMISSION_LEVELS[
            permission_level
        ]["allowed_sensitivity"].copy()
    }


def apply_vector_permissions(
    vector_plan,
    permissions: dict
):
    """
    Adiciona ao plano vetorial a restrição de sensibilidade
    determinada pelo backend.

    A LLM não decide quais níveis o usuário pode acessar.
    """

    vector_plan.filters["doc_sensitivity"] = (permissions["allowed_sensitivity"])

    return vector_plan

class PermissionLevel(str, Enum):
    PUBLIC = "publico"
    INTERNAL = "interno"
    RESTRICTED = "restrito"

class PostgresPermissionError(Exception):
    """Erro lançado quando o usuário não possui acesso ao PostgreSQL."""
    pass

class PostgresPermissionGuard:
    REQUIRED_PERMISSION = PermissionLevel.RESTRICTED

    def validate(self, permission_level: str) -> None:

        try:
            permission = PermissionLevel(
                permission_level.lower()
            )
        except ValueError as exc:
            raise PostgresPermissionError(
                f"Nível de permissão inválido: "
                f"{permission_level}"
            ) from exc

        if permission != self.REQUIRED_PERMISSION:
            raise PostgresPermissionError(
                "Acesso ao PostgreSQL permitido somente para usuários com permissão 'restricted'."
            )