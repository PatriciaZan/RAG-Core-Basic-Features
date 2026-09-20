
class VectorPermissionGuard:
    PERMISSION_LEVELS = {
        "publico": ["publico"],
        "interno": ["publico", "interno"],
        "restrito": ["publico", "interno", "restrito"],
    }

    def validate_permission(self, permission_level: str) -> list[str]:
    # Retorna os níveis de sensitivity que o usuáriopode consultar.

        if not permission_level:
            raise ValueError("Nível de permissão não informado.")

        permission_level = permission_level.lower()
        if permission_level not in self.PERMISSION_LEVELS:
            raise ValueError(
                f"Nível de permissão inválido: "
                f"{permission_level}"
            )

        return self.PERMISSION_LEVELS[
            permission_level
        ]

    def build_filters(
        self,
        permission_level: str
    ) -> dict:
        #Constrói o filtro de metadata que seráutilizado pelo VectorRetriever.

        allowed_sensitivities = (
            self.validate_permission(
                permission_level
            )
        )

        return {
            "sensitivity": allowed_sensitivities
        }