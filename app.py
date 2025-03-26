import streamlit as st
import pandas as pd
import numpy as np
from fpdf import FPDF
from io import BytesIO

st.set_page_config(page_title="Pesquisa de Preços - Painel Federal", layout="centered")
st.title("🔎 Pesquisa de Preços - Compras Públicas")

st.markdown("Digite o nome do item e clique em buscar para ver os valores simulados de pregos públicos.")

query = st.text_input("Item para pesquisa:", "Fio guia hidrofílico 0.032 mm x 150 cm")
botao = st.button("Buscar Preços")

def gerar_pdf(df, media, mediana, sugestao):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Relatório de Pesquisa de Preços", ln=True, align='C')
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Média dos Preços: R$ {media:.2f}", ln=True)
    pdf.cell(200, 10, txt=f"Mediana dos Preços: R$ {mediana:.2f}", ln=True)
    pdf.cell(200, 10, txt=f"Sugestão de Preço de Referência: R$ {sugestao:.2f}", ln=True)
    pdf.ln(10)
    pdf.set_font("Arial", size=10)
    for i, row in df.iterrows():
        texto = f"{row['modalidade']} - {row['orgao']} - R$ {row['valor_unitario']} - {row['data']}"
        pdf.multi_cell(0, 10, texto)
        pdf.ln(1)
    pdf_bytes = pdf.output(dest='S').encode('latin-1')
    buffer = BytesIO(pdf_bytes)
    return buffer

if botao:
    st.info("Buscando dados simulados...")

    # Dados simulados de exemplo
    registros = [
        {"orgao": "Ministério da Saúde", "modalidade": "PREGÃO ELETRÔNICO", "valor_unitario": 123.45, "data": "2024-10-01"},
        {"orgao": "Secretaria de Saúde MT", "modalidade": "PREGÃO ELETRÔNICO", "valor_unitario": 118.90, "data": "2024-09-15"},
        {"orgao": "Hospital Regional", "modalidade": "PREGÃO PRESENCIAL", "valor_unitario": 130.00, "data": "2024-08-20"},
        {"orgao": "Prefeitura de Cuiabá", "modalidade": "PREGÃO ELETRÔNICO", "valor_unitario": 119.75, "data": "2024-09-05"},
        {"orgao": "SES-MT", "modalidade": "PREGÃO ELETRÔNICO", "valor_unitario": 125.60, "data": "2024-10-10"},
    ]

    df = pd.DataFrame(registros)
    media = df['valor_unitario'].mean()
    mediana = df['valor_unitario'].median()
    sugestao = mediana

    st.success("Dados simulados encontrados!")
    st.dataframe(df)

    st.markdown(f"**Média:** R$ {media:.2f}")
    st.markdown(f"**Mediana:** R$ {mediana:.2f}")
    st.markdown(f"**Sugestão de Preço de Referência:** R$ {sugestao:.2f}")

    st.markdown("[🔗 Ver Painel de Preços Federal](https://paineldeprecos.planejamento.gov.br)")

    pdf_buffer = gerar_pdf(df, media, mediana, sugestao)
    st.download_button(
        label="📄 Baixar Relatório em PDF",
        data=pdf_buffer,
        file_name="relatorio_pesquisa_precos.pdf",
        mime="application/pdf"
    )
