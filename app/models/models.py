from pydantic import BaseModel


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


class PatientInfo(BaseModel):
    nome_completo: str
    idade: int
    sexo: str


class MainComplaint(BaseModel):
    sintoma_principal: str
    duracao_sintomas: str
    caracteristicas_sintomas: str


class MedicalHistory(BaseModel):
    condicoes_previas: str
    cirurgias_anteriores: str
    hospitalizacoes: str


class MedicationHistory(BaseModel):
    medicamentos_em_uso: str
    dosagens: str = None
    duracao_tratamento: str = None


class PatientAllergies(BaseModel):
    medicamentos: str = None
    alimentos: str = None
    outras_substancias: str = None


class PatientFamilyHistory(BaseModel):
    historico_familiar: str


class VitalSigns(BaseModel):
    sinais_vitais: str
