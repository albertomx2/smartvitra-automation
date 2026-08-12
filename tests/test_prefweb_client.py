from backend.integrations.prefweb.models import (
    PrefWebEntity,
    PrefWebLoginResult,
)


def test_prefweb_login_result_model():
    result = PrefWebLoginResult(
        valid_login=True,
        error_message=None,
        available_entities=[
            PrefWebEntity(
                row_id="entity-1",
                entity_id="entity-1",
                name="Test Entity",
            )
        ],
    )

    assert result.valid_login

    assert result.available_entities[0].name == "Test Entity"
