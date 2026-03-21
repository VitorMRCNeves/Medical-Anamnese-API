# API de Transcricao e Estruturacao de Anamnese com IA

API em `FastAPI` para receber audio criptografado de consultas, transcrever com LLM e estruturar dados de anamnese em JSON dinamico para integracao com sistemas clinicos existentes.

O projeto foi desenhado com foco de acoplar capacidades de IA em uma arquitetura de servico ja existente, com camadas claras de seguranca, orquestracao, prompts configuraveis e deploy em producao.

## Objetivo do projeto

- Integrar IA de forma pragmatica em um backend de API.
- Transformar audio medico em dado estruturado consumivel por sistemas previos (EHR, prontuario eletronico, CRM clinico, automacoes).
- Garantir seguranca no transporte/processamento de audio (JWT + AES-GCM).
- Permitir evolucao rapida de comportamento dos agentes via configuracoes YAML, sem alterar codigo de dominio.

## Stack tecnologica

- `Python 3.11`
- `FastAPI` + `Uvicorn`
- `Pydantic` / `Pydantic AI`
- `Gemini (Google GLA Provider)` como modelo de linguagem atual
- `PyJWT` para autenticacao
- `cryptography` (AES-256-GCM) para decriptacao/criptografia de payloads
- `Docker` + `docker-compose` para ambiente local
- `Railway` para deploy em producao

## Arquitetura

### Visao de alto nivel

```mermaid
flowchart TD
    A[Cliente / Sistema legado] -->|Bearer JWT + arquivo criptografado| B[FastAPI Router /audio]
    B --> C[SecurityManager]
    C -->|valida JWT| B
    C -->|AES-256-GCM decrypt| D[AudioTranscript Service]
    D --> E[TranscriptAgent - Pydantic AI]
    E --> F[Gemini Model]
    F --> G[Transcricao]
    G --> H[AgentOrchestrator]
    H --> I[AnamnesesModelingAgent]
    H --> J[TranscriptValidatorAgent]
    I --> K[JSON dinamico via Pydantic model]
    J --> K
    K --> L[Resposta JSON para sistema integrador]

    M[ConfigManager + YAML prompts] --> E
    M --> I
    M --> J

    subgraph Deploy
        N[Railway - Producao]
    end

    N --> B
```

### Componentes principais

- `app/main.py`
  - Sobe a aplicacao FastAPI.
  - Carrega dependencias globais via `AppConfigs.load_dependencies()`.
  - Configura `CORS` e `TrustedHostMiddleware`.
- `app/routers/audio.py`
  - `POST /audio/upload`: autentica request, decripta arquivo e dispara transcricao.
  - `POST /audio/prontuario`: recebe transcricao + template e gera estrutura de anamnese.
- `app/security/security.py`
  - Validacao JWT (`Authorization: Bearer <token>`).
  - Criptografia/decriptacao AES-256-GCM para payloads de audio.
- `app/services/AudioTranscript.py`
  - Encapsula pipeline de transcricao (router -> agente transcritor).
- `app/services/AgentOrchestrator.py`
  - Orquestra extracao estruturada e validacao do resultado.
- `app/agents/*`
  - `TranscriptAgent`, `AnamnesesModelingAgent`, `TranscriptValidatorAgent` com base comum em `BaseAgent`.
  - Criacao de agentes centralizada em `AgentFactory`, com retry exponencial para falhas transitorias de provider.
- `app/services/ConfigManager.py` + `app/config/configuracao/*.yaml`
  - Prompt engineering externalizado por YAML (agentes e configuracoes).
  - Suporte a reload de configuracao.
- `app/models/models.py`
  - Modelos de API e geracao dinamica de `Pydantic model` a partir do `anamnesis_template`.

## Fluxo funcional (end-to-end)

1. Cliente envia arquivo de audio criptografado para `POST /audio/upload`.
2. API valida token JWT.
3. API decripta o payload com AES-GCM.
4. `TranscriptAgent` converte audio em texto.
5. Cliente envia `transcription` + `anamnesis_template` para `POST /audio/prontuario`.
6. API gera modelo Pydantic dinamico pelo template.
7. `AnamnesesModelingAgent` extrai os campos.
8. Resultado e validado e retornado como JSON estruturado.

## Estrutura de pastas

```text
app/
  main.py
  routers/
    audio.py
  services/
    AudioTranscript.py
    AgentOrchestrator.py
    ChatInterface.py
    ConfigManager.py
  agents/
    AgentBase.py
    transcritor.py
    anamnese.py
    validator.py
  config/
    ConfigDependencies.py
    configuracao/
      transcritor.yaml
      anamnese.yaml
      validador.yaml
  models/
    models.py
  security/
    security.py
  tests/
    test_security.py
```

## Como executar

## 1) Variaveis de ambiente

Crie um arquivo `.env` na raiz:

```env
GOOGLE_API_KEY=...
API_KEY=...          # chave base64-url de 32 bytes para AES-256-GCM
SECRET_KEY=...       # chave JWT
```

## 2) Ambiente local com Docker Compose (recomendado)

```bash
docker compose up --build
```

API local em: `http://localhost:8023`

## 3) Ambiente local sem Docker

```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8005 --reload
```

## Endpoints principais

- `GET /` - health check simples
- `GET /audio/` - endpoint informativo
- `POST /audio/upload` - recebe arquivo de audio criptografado e retorna transcricao
- `POST /audio/prontuario` - recebe transcricao + template e retorna JSON de anamnese

## Exemplo de payload para estruturacao (`/audio/prontuario`)

```json
{
  "transcription": "Paciente relata dor toracica ha 3 dias...",
  "anamnesis_template": {
    "template_name": "AnamneseCardio",
    "fields": [
      {
        "title": "queixa_principal",
        "type": "text",
        "required": true,
        "llm_instruction": "Descreva a queixa principal com linguagem clinica objetiva."
      },
      {
        "title": "duracao_sintomas",
        "type": "string",
        "required": false,
        "llm_instruction": "Informar duracao em termos reportados pelo paciente."
      }
    ]
  }
}
```

## Foco para integracao de IA em sistemas previos

- `Arquitetura de integracao`: IA encapsulada em servico HTTP para plugar em sistemas existentes sem reescrever o core do produto.
- `Orquestracao de agentes`: separacao entre transcricao, extracao e validacao.
- `Schema-first output`: saida orientada a contrato (modelo Pydantic dinamico) para reduzir friccao com consumidores.
- `PromptOps`: prompts versionados em YAML, desacoplados do codigo.
- `Resiliencia`: retries com backoff para falhas transitorias de LLM provider.
- `Seguranca aplicada`: JWT + criptografia de arquivo em transito/aplicacao.
- `Deploy real`: execucao em producao via Railway.

## Deploy em producao (Railway)

A aplicacao esta sendo deployada em producao no `Railway`.

Pontos importantes:

- Definir variaveis de ambiente no projeto Railway (`GOOGLE_API_KEY`, `API_KEY`, `SECRET_KEY`).
- Garantir porta esperada pela plataforma (`PORT`) e health check em `/`.
- Revisar CORS/hosts permitidos conforme dominio publico.
- Monitorar logs e latencia de chamadas LLM.

## Melhorias futuras

### Adicao de Whisper local para transcricao

Incorporar um motor de transcricao `Whisper` local na API para aumentar robustez, controle e possivel reducao de custo por chamada externa.

### Adaptação da ConfigManager para leitura de serviço externo

Modificar a CongifManager para leitura dos arquivos YAML de um serviço externo como S3, e adicionar um endpoint de hot-reload dos prompts, permitindo versionamento e iterações rápidas de prompts com agentes, sem necessitar de um novo deploy da aplicação

- Adicionar visibilidade via OpenTelemetry

