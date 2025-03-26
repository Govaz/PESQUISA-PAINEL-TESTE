import streamlit as st
import pandas as pd
import requests
import numpy as np
from fpdf import FPDF
from io import BytesIO

st.set_page_config(page_title="Pesquisa de Preços - Painel Federal", layout="centered")
st.title("🔎 Pesquisa de Preços - Compras Públicas")

st.markdown("Digite o nome do item e clique em buscar para ver os valores disponíveis no Painel de Preços do Governo Federal.")

query = st.text_input("Item para pesquisa:", "Fio guia hidrofílico 0.032 mm x 150 cm")
botao = st.button("Buscar Preços")

@st.cache_data
def buscar_dados(item):
    url = "https://paineldeprecos.planejamento.gov.br/api/painel/buscar-item"
    payload = {
        "termo": item,
        "pagina": 1,
        "tamanho": 100
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        return response.json()
    return []

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
    buffer = BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer

if botao:
    st.info("Buscando dados, por favor aguarde...")
    dados = buscar_dados(query)

    if not dados or not dados.get("conteudo"):
        st.error("Nenhum dado encontrado para o item pesquisado.")
    else:
        resultados = dados["conteudo"]
        registros = []
        for r in resultados:
            if "PREGÃO" in r.get("modalidade", ""):
                registros.append({
                    "orgao": r.get("orgao"),
                    "modalidade": r.get("modalidade"),
                    "valor_unitario": float(r.get("valor_unitario", 0)),
                    "data": r.get("data")
                })

        df = pd.DataFrame(registros)

        if df.empty:
            st.warning("Nenhum pregão encontrado para o item.")
        else:
            media = df['valor_unitario'].mean()
            mediana = df['valor_unitario'].median()
            sugestao = mediana

            st.success("Dados encontrados!")
            st.dataframe(df)

            st.markdown(f"**Média:** R$ {media:.2f}")
            st.markdown(f"**Mediana:** R$ {mediana:.2f}")
            st.markdown(f"**Sugestão de Preço de Referência:** R$ {sugestao:.2f}")

            pdf_buffer = gerar_pdf(df, media, mediana, sugestao)
            st.download_button(
                label="📄 Baixar Relatório em PDF",
                data=pdf_buffer,
                file_name="relatorio_pesquisa_precos.pdf",
                mime="application/pdf"
            )
