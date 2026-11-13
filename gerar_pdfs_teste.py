from fpdf import FPDF

documentos = [
    {
        "nome": "certidao_matricula_45892.pdf",
        "texto": (
            "1º OFÍCIO DE REGISTRO DE IMÓVEIS DE CURITIBA - PR\n"
            "CERTIDÃO DE INTEIRO TEOR - MATRÍCULA Nº 45.892\n\n"
            "IMÓVEL: Apartamento nº 304, Bloco B, situado na Rua XV de Novembro, nº 1250, "
            "Centro, Curitiba/PR.\n"
            "PROPRIETÁRIO ADQUIRENTE: Carlos Eduardo Mendes, brasileiro, engenheiro, "
            "inscrito no CPF sob nº 123.456.789-00.\n"
            "VALOR DA TRANSAÇÃO: R$ 480.000,00 (quatrocentos e oitenta mil reais).\n"
            "ÔNUS E GRAVAMES: Imóvel livre e desembaraçado de quaisquer ônus reais ou hipotecas."
        )
    },
    {
        "nome": "certidao_matricula_78104.pdf",
        "texto": (
            "1º OFÍCIO DE REGISTRO DE IMÓVEIS DE CURITIBA - PR\n"
            "CERTIDÃO DE INTEIRO TEOR - MATRÍCULA Nº 78.104\n\n"
            "IMÓVEL: Terreno urbano lote 12, quadra 04, localizado na Avenida Sete de Setembro, "
            "nº 4300, Batel, Curitiba/PR.\n"
            "PROPRIETÁRIA ADQUIRENTE: Mariana Souza Oliveira, brasileira, médica, "
            "inscrita no CPF sob nº 987.654.321-11.\n"
            "VALOR DA TRANSAÇÃO: R$ 1.250.000,00 (um milhão duzentos e cinquenta mil reais).\n"
            "ÔNUS E GRAVAMES: Alienado fiduciariamente em garantia ao Banco do Brasil S.A."
        )
    },
    {
        "nome": "certidao_matricula_99321.pdf",
        "texto": (
            "1º OFÍCIO DE REGISTRO DE IMÓVEIS DE CURITIBA - PR\n"
            "CERTIDÃO DE INTEIRO TEOR - MATRÍCULA Nº 99.321\n\n"
            "IMÓVEL: Sala comercial nº 802, Edifício Empresarial, Rua Marechal Deodoro, "
            "nº 630, Centro, Curitiba/PR.\n"
            "PROPRIETÁRIO ADQUIRENTE: Roberto Almeida Santos, brasileiro, empresário, "
            "inscrito no CPF sob nº 111.222.333-4.\n"  # CPF propositalmente com 10 dígitos para testar a validação!
            "VALOR DA TRANSAÇÃO: R$ 320.000,00 (trezentos e vinte mil reais).\n"
            "ÔNUS E GRAVAMES: Consta penhora trabalhista averbada sob AV-03."
        )
    }
]

for doc in documentos:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=11)
    pdf.multi_cell(0, 8, doc["texto"])
    pdf.output(doc["nome"])
    print(f"Gerado: {doc['nome']}")