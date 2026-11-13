# Automação Extratora de Documentos Cartorários (PoC)

Prova de Conceito (PoC) desenvolvida em **Python** e **FastAPI** para automatizar a leitura, validação e estruturação de dados a partir de certidões e matrículas imobiliárias em lote, exportando os resultados diretamente para planilhas **Excel (`.xlsx`)**.

---

## Principais Funcionalidades

* **Processamento Multimodal em Lote:** Aceita upload simultâneo de **PDFs nativos**, **PDFs escaneados** e **imagens (`.jpg`, `.jpeg`, `.png`)**.
* **Extração Estruturada com IA + Schema Rígido:** Utiliza a API do **Google Gemini** com saída estruturada (`Pydantic`) e `temperature=0.0` para evitar alucinações e garantir padronização dos campos (`Matrícula`, `Proprietário`, `CPF`, `Endereço`, `Valor` e `Ônus`).
* **Alta Disponibilidade (Contingência Local):** Implementa *timeout* e *fallback* automático. Caso a API externa sofra instabilidade ou oscilações de rede, o sistema aciona processamento local via **OCR (Tesseract)** e **Expressões Regulares (Regex)** sem interromper o trabalho do escrevente.
* **Validação Determinística & Prevenção de Erros:** Valida o formato e a integridade do CPF via Python após a extração, sinalizando automaticamente registros inconsistentes como `Revisar Manualmente` ou `REVISAR` sem travar o processamento do restante do lote.
* **Governança, Segurança e LGPD:**
  * Uso exclusivo via API corporativa (sem retenção de dados para treinamento de modelos).
  * Registro automático de trilha de auditoria (`auditoria.log`) contendo timestamp, IP de origem, arquivo processado, matrícula extraída e status de validação.

---

## Tecnologias Utilizadas

* **Backend & Web UI:** Python 3.12, FastAPI, Uvicorn
* **IA & OCR:** Google GenAI SDK (`google-genai`), Tesseract OCR (`pytesseract`), Pillow, `pypdf`
* **Validação & Dados:** Pydantic, Pandas, OpenPyXL, Regex

---

## Como Executar Localmente

### 1. Pré-requisitos (Linux / Ubuntu / Mint)
Instale o motor de OCR Tesseract para suporte offline a imagens:
```bash
sudo apt update && sudo apt install -y tesseract-ocr tesseract-ocr-por
```
--- 

### 2. Clonar o repositório e configurar o ambiente virtual

```bash
git clone [https://github.com/SEU-USUARIO/extrator-cartorio.git](https://github.com/SEU-USUARIO/extrator-cartorio.git)
cd extrator-cartorio

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
---

### 3. Configurar variáveis de ambiente

Crie um arquivo .env na raiz do projeto com a sua chave da API do Google AI Studio:
```bash
Snippet de código
GEMINI_API_KEY=sua_chave_aqui
```

---

### 4. Gerar documentos fictícios para teste (opcional)

```bash
python gerar_pdfs_teste.py
```

---

### 5. Iniciar a aplicação

```bash
uvicorn main:app --reload
Acesse no navegador: http://127.0.0.1:8000
```