import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import pandas as pd
from fpdf import FPDF
from io import BytesIO
import urllib.parse

def iniciar_navegador():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def buscar_dados_painel(termo):
    driver = iniciar_navegador()
    url = "https://paineldeprecos.planejamento.gov.br/"
    driver.get(url)
    time.sleep(2)

   from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Aguarda o campo aparecer até 15 segundos
try:
    campo_busca = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.ID, "search-input"))
    )
    campo_busca.clear()
    campo_busca.send_keys(termo)
    campo_busca.submit()
except Exception as e:
    st.error("Não foi possível localizar o campo de busca. Verifique se o site está online.")
    driver.quit()
    return pd.DataFrame()

    time.sleep(6)  # Aguarda carregar os resultados
    dados = []

    try:
        linhas = driver.find_elements(By.CSS_SELECTOR, "tbody tr")
        for linha in linhas:
            colunas = linha.find_elements(By.TAG_NAME, "td")
            if len(colunas) >= 5:
                modalidade = colunas[0].text.strip()
                orgao = colunas[1].text.strip()
                valor = colunas[2].text.strip().replace("R$", "").replace(",", ".").strip()
                data = colunas[4].text.strip()
                if "PREGÃO" in modalidade.upper():
                    dados.append({
                        "modalidade": modalidade,
                        "orgao": orgao,
                        "valor_unitario": float(valor),
                        "data": data
                    })
    except Exception as e:
        st.error("Erro ao extrair dados: " + str(e))
    finally:
        driver.quit()

    return pd.DataFrame(dados)

def gerar_pdf(df, media, mediana, sugestao):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Relatório de Pesquisa de Preços", ln=True, align='C')
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Média: R$ {media:.2f}", ln=True)
    pdf.cell(200, 10, txt=f"Mediana: R$ {mediana:.2f}", ln=True)
    pdf.cell(200, 10, txt=f"Sugestão de Referência: R$ {sugestao:.2f}", ln=True)
    pdf.ln(10)
    pdf.set_font("Arial", size=10)
    for _, row in df.iterrows():
        texto = f"{row['modalidade']} - {row['orgao']} - R$ {row['valor_unitario']} - {row['data']}"
        pdf.multi_cell(0, 10, texto)
        pdf.ln(1)
    pdf_bytes = pdf.output(dest='S').encode('latin-1')
    return BytesIO(pdf_bytes)

st.set_page_config(page_title="Pesquisa Painel de Preços", layout="centered")
st.title("🔎 Consulta Painel de Preços (Governo Federal)")

termo = st.text_input("Digite o item para pesquisa:", "fio guia hidrofílico 0.032 mm x 150 cm")
buscar = st.button("Buscar Preços Reais")

if buscar:
    st.info("Buscando dados reais... Aguarde!")
    df = buscar_dados_painel(termo)
    if df.empty:
        st.warning("Nenhum dado encontrado.")
    else:
        media = df["valor_unitario"].mean()
        mediana = df["valor_unitario"].median()
        sugestao = mediana

        st.success("Resultados encontrados!")
        st.dataframe(df)
        st.markdown(f"**Média:** R$ {media:.2f}")
        st.markdown(f"**Mediana:** R$ {mediana:.2f}")
        st.markdown(f"**Sugestão de preço:** R$ {sugestao:.2f}")

        link = "https://paineldeprecos.planejamento.gov.br/painel/busca?termo=" + urllib.parse.quote(termo)
        st.markdown(f"[🔗 Ver no Painel de Preços Federal]({link})")

        pdf_buffer = gerar_pdf(df, media, mediana, sugestao)
        st.download_button("📄 Baixar PDF", data=pdf_buffer, file_name="relatorio.pdf", mime="application/pdf")
