import os
import re
import io
import json
import logging
from datetime import datetime
from typing import List
from PIL import Image
import pytesseract

import pandas as pd
from pypdf import PdfReader
from pydantic import BaseModel, Field
from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from dotenv import load_dotenv
from google import genai
from google.genai import types

# 1. Carrega variáveis de ambiente e configura Log de Auditoria
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY não encontrada. Verifique o arquivo .env"
    )

client = genai.Client(
    api_key=api_key,
    http_options=types.HttpOptions(timeout=15_000)  # 15 segundos de timeout
)

logging.basicConfig(
    filename="auditoria.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

app = FastAPI(title="Automação Cartório - Extrator de Matrículas")

# 2. Schema Pydantic (Garante que a IA devolva exatamente esses campos)
class DadosMatricula(BaseModel):
    matricula: str = Field(description="Número da matrícula do imóvel")
    proprietario: str = Field(description="Nome completo do proprietário ou comprador")
    cpf: str = Field(description="CPF encontrado no documento")
    endereco_imovel: str = Field(description="Endereço completo do imóvel")
    valor_transacao: str = Field(description="Valor do imóvel ou transação em reais")
    status_onus: str = Field(description="Situação de ônus, hipoteca ou alienação")

# 3. Validação matemática/formato em Python (Não confia 100% na IA)
def validar_formato_cpf(cpf: str) -> str:
    numeros = re.sub(r"\D", "", cpf)
    if len(numeros) == 11 and len(set(numeros)) > 1:
        return "Válido"
    return "Revisar Manualmente"

def extrair_texto_pdf(file_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(file_bytes))
    texto = ""

    for page in reader.pages:
        texto += page.extract_text() or ""

    return texto.strip()


def fallback_regex(texto_pdf: str) -> dict:
    print("Usando fallback local (Regex) devido à instabilidade na API externa...")
    matricula = re.search(r"MATRÍCULA Nº\s*([\d\.]+)", texto_pdf)
    proprietario = re.search(r"PROPRIETÁRI[OA] ADQUIRENTE:\s*([^,]+)", texto_pdf)
    cpf = re.search(r"CPF sob nº\s*([\d\.\-]+\d)", texto_pdf)
    endereco = re.search(r"IMÓVEL:\s*(.+?)\.\n", texto_pdf, re.DOTALL)
    valor = re.search(r"VALOR DA TRANSAÇÃO:\s*(R\$\s*[\d\.,]+)", texto_pdf)
    onus = re.search(r"ÔNUS E GRAVAMES:\s*(.+)", texto_pdf)

    return {
        "matricula": matricula.group(1) if matricula else "Não informado",
        "proprietario": proprietario.group(1).strip() if proprietario else "Não informado",
        "cpf": cpf.group(1) if cpf else "Não informado",
        "endereco_imovel": endereco.group(1).replace("\n", " ").strip() if endereco else "Não informado",
        "valor_transacao": valor.group(1) if valor else "Não informado",
        "status_onus": onus.group(1).strip() if onus else "Não informado",
    }


def extrair_com_ia(conteudo_bytes: bytes, mime_type: str, texto_extraido: str = "") -> dict:
    instrucao = f"""
    Você é um analista de registro de imóveis.
    Extraia exclusivamente os campos definidos no schema.
    Não invente informações.
    Caso um campo não seja encontrado, retorne "Não informado".
    """

    # Se temos texto nativo, mandamos texto; se for imagem ou PDF escaneado, mandamos os bytes direto (OCR Multimodal)
    if texto_extraido:
        contents = f"{instrucao}\n\nTexto:\n{texto_extraido}"
    else:
        contents = [
            types.Part.from_bytes(data=conteudo_bytes, mime_type=mime_type),
            instrucao
        ]

    modelos = ["gemini-3.8-flash", "gemini-3.5-flash-lite"]
    ultimo_erro = None

    for modelo in modelos:
        try:
            print(f"Tentando extrair com o modelo: {modelo} ({mime_type})...")
            response = client.models.generate_content(
                model=modelo,
                contents=contents,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=DadosMatricula,
                    temperature=0.0,
                ),
            )
            print(f"Sucesso com {modelo}!")
            return json.loads(response.text)
        except Exception as e:
            print(f"Falha no modelo {modelo}: {e}")
            ultimo_erro = e

    if texto_extraido:
        return fallback_regex(texto_extraido)

    # Se a IA falhar e houver texto nativo, aciona o Plano C (Regex)
    if texto_extraido:
        return fallback_regex(texto_extraido)

    # Se a IA falhar e for uma imagem (PNG/JPG), faz OCR local com Tesseract e passa no Regex
    if mime_type.startswith("image/"):
        print("Usando OCR local (Tesseract) + Regex devido à instabilidade na API...")
        imagem = Image.open(io.BytesIO(conteudo_bytes))
        texto_ocr = pytesseract.image_to_string(imagem, lang="por")
        return fallback_regex(texto_ocr)

    raise ultimo_erro

# 4. Interface Web (Aceita PDF, JPG e PNG)
@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <title>Automação Cartório - Extrator IA</title>
        <style>
            body { font-family: Arial, sans-serif; background: #f4f6f8; display: flex; justify-content: center; padding-top: 60px; }
            .card { background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); width: 480px; }
            h2 { color: #1a365d; margin-top: 0; }
            p { color: #4a5568; font-size: 14px; }
            input[type="file"] { margin: 20px 0; width: 100%; }
            button { background: #2b6cb0; color: white; border: none; padding: 12px 20px; border-radius: 5px; cursor: pointer; width: 100%; font-size: 16px; }
            button:hover { background: #2c5282; }
            .badge { display: inline-block; background: #e6fffa; color: #234e52; padding: 4px 8px; border-radius: 4px; font-size: 12px; margin-top: 15px; }
        </style>
    </head>
    <body>
        <div class="card">
            <h2>Extrator de Documentos (PoC)</h2>
            <p>Selecione múltiplos PDFs de certidões ou matrículas para extração automatizada com validação e geração de planilha.</p>
           <form action="/processar-documentos" method="post" enctype="multipart/form-data">
                <input type="file" name="arquivos" accept=".pdf,.jpg,.jpeg,.png" multiple required>
                <button type="submit">Extrair Dados e Gerar Excel</button>
        </form>
            <div class="badge">LGPD: Processamento via API sem retenção de treino + Log de Auditoria</div>
        </div>
    </body>
    </html>
    """

# 5. Rota que processa PDFs e Imagens
@app.post("/processar-documentos")
async def processar_documentos(request: Request, arquivos: List[UploadFile] = File(...)):
    resultados = []
    ip_cliente = request.client.host

    for arquivo in arquivos:
        conteudo = await arquivo.read()
        nome_arquivo = arquivo.filename.lower()

        try:
            if nome_arquivo.endswith(".pdf"):
                mime_type = "application/pdf"
                texto = extrair_texto_pdf(conteudo)
                # Se texto vier vazio, é PDF escaneado -> vai por bytes (OCR visual)
                dados = extrair_com_ia(conteudo, mime_type, texto_extraido=texto)
            elif nome_arquivo.endswith((".jpg", ".jpeg")):
                mime_type = "image/jpeg"
                dados = extrair_com_ia(conteudo, mime_type)
            elif nome_arquivo.endswith(".png"):
                mime_type = "image/png"
                dados = extrair_com_ia(conteudo, mime_type)
            else:
                raise ValueError("Formato não suportado. Use PDF, JPG ou PNG.")

            dados["arquivo_origem"] = arquivo.filename
            dados["validacao_cpf"] = validar_formato_cpf(dados.get("cpf", ""))

        except Exception as e:
            logging.error(f"ARQUIVO={arquivo.filename} | ERRO={str(e)}")
            dados = {
                "arquivo_origem": arquivo.filename,
                "matricula": "REVISAR",
                "proprietario": "REVISAR",
                "cpf": "REVISAR",
                "validacao_cpf": "REVISAR",
                "endereco_imovel": "REVISAR",
                "valor_transacao": "REVISAR",
                "status_onus": f"Erro: {str(e)}"
            }

        resultados.append(dados)

        logging.info(
            f"USUARIO_IP={ip_cliente} | ARQUIVO={arquivo.filename} | "
            f"MATRICULA={dados.get('matricula')} | STATUS_CPF={dados['validacao_cpf']}"
        )

    df = pd.DataFrame(resultados)
    colunas_ordenadas = [
        "arquivo_origem", "matricula", "proprietario", "cpf",
        "validacao_cpf", "endereco_imovel", "valor_transacao", "status_onus"
    ]
    df = df[colunas_ordenadas]

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Matriculas_Extraidas")
    output.seek(0)

    nome_excel = f"relatorio_cartorio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={nome_excel}"}
    )