from typing import Dict, Type
from pydantic import BaseModel, Field, create_model


class User(BaseModel):
    id: int
    name: str
    email: str
    password: str


class UserCreate(BaseModel):
    name: str
    email: str
    password: str


class AudioResponse(BaseModel):
    transcription: str


class Token(BaseModel):
    access_token: str
    token_type: str


def criar_modelo_pydantic(json_data: dict) -> Type[BaseModel]:
    """
    Cria uma classe Pydantic dinamicamente a partir do payload recebido da API.

    Args:
        json_data (dict): Dicionário contendo as definições dos campos.

    Returns:
        Type[BaseModel]: Classe Pydantic gerada dinamicamente.
    """

    type_map = {
        "text": str,
        "textarea": str,
        "string": str,
        "number": float,
        "integer": int,
        "float": float,
        "date": str,
        "boolean": bool,
        "bool": bool,
    }

    fields: Dict[str, tuple] = {}
    for field in json_data["fields"]:
        field_type = field.get("type", "string")
        pydantic_type = type_map.get(field_type, str)
        required = field.get("required", False)
        default = ... if required else None
        description = field.get("llm_instruction", "")

        fields[field["title"]] = (
            pydantic_type,
            Field(default, description=description),
        )

    class_name = json_data.get("template_name", "DynamicModel").replace(" ", "")

    DynamicModel = create_model(class_name, **fields)
    return DynamicModel
