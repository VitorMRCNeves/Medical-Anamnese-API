from jwt import decode

from app.security.security import SECRET_KEY, create_access_token


def test_jwt():
    data = {"test": "test"}
    token = create_access_token(data)

    decoded = decode(token, SECRET_KEY, algorithms=["HS256"])

    assert decoded["test"] == data["test"]
    assert "exp" in decoded


{
    "informacoes_paciente": {
        "nome_completo": "Carlos",
        "idade": 52,
        "sexo": "masculino",
    },
    "queixa_principal": {
        "sintoma_principal": "Dor no peito.",
        "duracao_sintomas": "Aproximadamente três dias.",
        "caracteristicas_sintomas": "Dor no meio do peito que às vezes irradia para o pescoço. Na segunda vez, sentiu o estômago pesado.",
    },
    "historico_medico": {
        "condicoes_previas": "Má digestão, constipação (uso de remédio com moderação)",
        "cirurgias_anteriores": "Não informado",
        "hospitalizacoes": "Não informado",
    },
    "medicacoes": {
        "medicamentos_em_uso": "Para constipação (uso com moderação)",
        "dosagens": "Não especificado",
        "duracao_tratamento": "Não especificado",
    },
    "alergias": {
        "medicamentos": "para constipação",
        "alimentos": "",
        "outras_substancias": "",
    },
    "historico_familiar": {
        "historico_familiar": "Ninguém na família teve dor no peito ou problema no coração, exceto o pai, que tem 82 anos."
    },
    "sinais_vitais": {"sinais_vitais": "Não foram mencionados sinais vitais."},
}
