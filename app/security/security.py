from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import base64
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from fastapi import HTTPException, Request, UploadFile
from jwt import encode, decode, InvalidTokenError
import base64
import json

# Configurações padrão
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
TOKEN_REFRESH_THRESHOLD_MINUTES = 5


class SecurityManager:
    def __init__(self):
        # Carregar variáveis de ambiente com validação
        self.SECRET_KEY = os.getenv("SECRET_KEY")
        if not self.SECRET_KEY:
            raise ValueError("SECRET_KEY environment variable is not set")

        self.API_KEY = os.getenv("API_KEY")
        if not self.API_KEY:
            raise ValueError("API_KEY environment variable is not set")

        self.ALGORITHM = ALGORITHM
        self.ACCESS_TOKEN_EXPIRE_MINUTES = ACCESS_TOKEN_EXPIRE_MINUTES
        self.TOKEN_REFRESH_THRESHOLD_MINUTES = TOKEN_REFRESH_THRESHOLD_MINUTES

    async def decrypt_file(self, file: UploadFile) -> bytes:
        file_bytes = await file.read()
        json_str = file_bytes.decode("utf-8")  # Converte para string
        encrypted_dict = json.loads(json_str)
        decrypted_data = self.decrypt_bytes(encrypted_dict, self.API_KEY)
        return decrypted_data

    def decode_jwt(self, token: str) -> dict:
        try:
            payload = decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            return payload
        except InvalidTokenError as e:
            print(f"Erro ao decodificar JWT: {str(e)}")
            raise HTTPException(status_code=401, detail=f"Token inválido: {str(e)}")
        except Exception as e:
            print(f"Erro inesperado ao decodificar JWT: {str(e)}")
            raise HTTPException(status_code=401, detail="Erro interno de autenticação")

    def create_access_token(self, data: dict):
        """
        Cria um token JWT com dados fornecidos e tempo de expiração.
        """
        to_encode = data.copy()
        expire = datetime.now(tz=ZoneInfo("UTC")) + timedelta(
            minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode.update({"exp": expire})
        encoded_jwt = encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_jwt

    def authenticate_user(self, headers: Request):
        authorization_header = headers.headers.get("authorization")
        if not authorization_header:
            raise HTTPException(
                status_code=401, detail="Header Authorization não encontrado"
            )

        if not authorization_header.startswith("Bearer "):
            raise HTTPException(
                status_code=401,
                detail="Formato do token inválido. Use 'Bearer <token>'",
            )

        self.decode_jwt(authorization_header[7:])
        print(f"Token decodificado com sucesso!!")

    def b64u_enc(self, b: bytes) -> str:
        """
        Codifica bytes em base64-url sem padding.

        Parâmetros:
            b (bytes): Dados em bytes a serem codificados.

        Retorna:
            str: String codificada em base64-url, sem sinais de '=' no final (sem padding).

        Observação:
            - Útil para serialização de dados binários em URLs ou JSON.
            - Remove o padding '=' do final para compatibilidade com JWT/JWE.
        """
        import base64

        b64u = base64.urlsafe_b64encode(b)  # Codifica em base64-url
        return b64u.rstrip(b"=").decode(
            "utf-8"
        )  # Remove padding e converte para string

    def b64u_dec(self, s: str) -> bytes:
        """
        Decodifica uma string em base64-url (sem padding) para bytes.

        Parâmetros:
            s (str): String codificada em base64-url, possivelmente sem padding.

        Retorna:
            bytes: Dados decodificados em bytes.

        Observação:
            - Adiciona o padding '=' necessário para decodificação correta.
        """

        raw = s.encode("utf-8")
        raw += b"=" * (-len(raw) % 4)
        return base64.urlsafe_b64decode(raw)

    def encrypt_bytes_for_upload(self, data: bytes, API_KEY: str) -> bytes:
        """
        Criptografa dados para upload de arquivo, retornando bytes criptografados.

        Args:
            data: Dados em bytes para criptografar
            API_KEY: Chave da API em base64

        Returns:
            bytes: Dados criptografados prontos para upload
        """
        import json

        encrypted_dict = self.encrypt_bytes(data, API_KEY)
        json_str = json.dumps(encrypted_dict)
        return json_str.encode("utf-8")

    def encrypt_bytes(self, data: bytes, API_KEY: str, aad: bytes = b"") -> dict:
        """
        Criptografa dados usando AES-256-GCM.

        Parâmetros:
            data (bytes): Dados a serem criptografados (plaintext).
            key32 (bytes): Chave secreta de 32 bytes (256 bits) para AES-256.
            aad (bytes, opcional): Dados adicionais autenticados (não criptografados, mas autenticados). Padrão: b"".

        Retorna:
            dict: Dicionário com os seguintes campos:
                - 'alg': Algoritmo utilizado (sempre "AES-256-GCM").
                - 'iv': Vetor de inicialização (IV) codificado em base64-url.
                - 'ct': Ciphertext (dados criptografados + tag de autenticação) em base64-url.
                - 'aad': Dados adicionais autenticados em base64-url.

        Significado das variáveis:
            - data: os dados em bytes que você deseja proteger.
            - key32: chave secreta de 32 bytes (256 bits) para o AES-256.
            - aad: dados adicionais autenticados (opcional), útil para garantir integridade de metadados.
            - iv: vetor de inicialização aleatório de 12 bytes (96 bits), necessário para GCM.
            - aead: objeto AESGCM para operações de criptografia/autenticação.
            - ct: ciphertext, resultado da criptografia (inclui a tag de autenticação GCM no final).

        Exemplo de uso:
            resultado = encrypt_bytes(b"mensagem", chave_32_bytes)
        """

        key32 = base64.urlsafe_b64decode(API_KEY)
        if len(key32) != 32:
            raise ValueError("A chave key32 precisa ter exatamente 32 bytes (AES-256).")
        iv = os.urandom(96)
        aead = AESGCM(key32)
        ct = aead.encrypt(iv, data, aad)
        return {
            "alg": "AES-256-GCM",
            "iv": self.b64u_enc(iv),
            "ct": self.b64u_enc(ct),
            "aad": self.b64u_enc(aad),
        }

    def decrypt_bytes(self, env: dict, API_KEY: str) -> bytes:
        """
        Descriptografa dados cifrados com AES-256-GCM.

        Parâmetros:
            env (dict): Dicionário contendo os campos 'iv', 'ct' e opcionalmente 'aad', todos em base64-url.
            key32 (bytes): Chave secreta de 32 bytes (256 bits) usada na criptografia.

        Retorna:
            bytes: Dados originais descriptografados (plaintext).

        Significado das variáveis:
            - env: dicionário com os dados criptografados e metadados.
            - key32: chave secreta de 32 bytes.
            - iv: vetor de inicialização decodificado.
            - ct: ciphertext (dados criptografados + tag) decodificado.
            - aad: dados adicionais autenticados decodificados.
            - aead: objeto AESGCM para descriptografia.

        Exemplo de uso:
            plaintext = decrypt_bytes(resultado, chave_32_bytes)
        """
        key32 = base64.urlsafe_b64decode(API_KEY)
        if len(key32) != 32:
            raise ValueError("A chave key32 precisa ter exatamente 32 bytes (AES-256).")
        iv = self.b64u_dec(env["iv"])
        ct = self.b64u_dec(env["ct"])
        aad = self.b64u_dec(env.get("aad", ""))
        aead = AESGCM(key32)
        return aead.decrypt(iv, ct, aad)
