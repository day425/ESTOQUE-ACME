# -*- coding: utf-8 -*-
"""
Created on Fri Dec 12 15:50:25 2025

@author: djoao
"""

import streamlit as st
import pandas as pd
import os

ARQUIVO_BASE = "estoque_acme.xlsx"


# ---------------------------
# CARREGAR / SALVAR BASE
# ---------------------------

def carregar_base():
    if os.path.exists(ARQUIVO_BASE):
        return pd.read_excel(ARQUIVO_BASE)
    else:
        # Criar base vazia caso não exista
        colunas = ["Rua", "Nível", "Prédio", "Qtde", "Categoria", "Código", "Produto"]
        df = pd.DataFrame(columns=colunas)
        df.to_excel(ARQUIVO_BASE, index=False)
        return df


def salvar_base(df):
    df.to_excel(ARQUIVO_BASE, index=False)


# ---------------------------
# LEITOR UNIVERSAL DE ARQUIVOS
# ---------------------------

def ler_arquivo(uploaded_file):
    nome = uploaded_file.name.lower()

    if nome.endswith(".csv"):
        return pd.read_csv(uploaded_file, sep=None, engine="python")
    else:
        return pd.read_excel(uploaded_file, engine="openpyxl")


# ============================================================
# INÍCIO DA INTERFACE
# ============================================================

st.set_page_config(page_title="ESTOQUE - ACME", layout="wide")
st.title("📦 ESTOQUE - ACME")


# ------------------------------------------------------------
# MENU LATERAL
# ------------------------------------------------------------
menu = st.sidebar.radio(
    "Menu",
    ["Dashboard", "Cadastrar Produto", "Consultar / Atualizar", "Importar Dados", "Exportar Dados"]
)

df = carregar_base()


# ============================================================
# 1) CADASTRO MANUAL DE PRODUTOS
# ============================================================
if menu == "Cadastrar Produto":
    st.subheader("Cadastrar novo produto")

    col1, col2, col3 = st.columns(3)
    with col1:
        rua = st.selectbox("Rua", ["RUA A", "RUA B", "RUA C", "RUA D","RUA E"])
    with col2:
        nivel = st.text_input("Nível")
    with col3:
        predio = st.text_input("Prédio")

    qtde = st.number_input("Quantidade", min_value=0)
    categoria = st.text_input("Categoria")
    codigo = st.text_input("Código (SKU)")
    produto = st.text_input("Nome do Produto")

    if st.button("Salvar Cadastro"):
        if codigo.strip() == "":
            st.error("Código não pode estar vazio.")
        else:
            novo = pd.DataFrame([{
                "Rua": rua,
                "Nível": nivel,
                "Prédio": predio,
                "Qtde": qtde,
                "Categoria": categoria,
                "Código": codigo,
                "Produto": produto
            }])

            df = pd.concat([df, novo], ignore_index=True)
            df = df.drop_duplicates(subset=["Código"], keep="last")
            salvar_base(df)

            st.success("Produto cadastrado com sucesso!")


# ============================================================
# 2) CONSULTAR E ATUALIZAR PRODUTOS
# ============================================================
elif menu == "Consultar / Atualizar":

    st.subheader("Lista de produtos cadastrados")

    st.dataframe(df, use_container_width=True)

    st.subheader("Atualizar produto")

    codigo_edit = st.text_input("Digite o código (SKU) para editar")

    if codigo_edit:
        filtro = df[df["Código"] == codigo_edit]

        if filtro.empty:
            st.error("Código não encontrado.")
        else:
            linha = filtro.iloc[0]

            col1, col2, col3 = st.columns(3)
            with col1:
                lista_ruas = ["RUA A", "RUA B", "RUA C", "RUA D", "RUA E"]

                # Garante correspondência ignorando espaços
                rua_linha = str(linha["Rua"]).strip().upper()

                # Se a rua não existir, seleciona a primeira
                index_rua = lista_ruas.index(rua_linha) if rua_linha in lista_ruas else 0

                rua = st.selectbox(
                    "Rua",
                    lista_ruas,
                    index=index_rua
                )

            with col2:
                nivel = st.text_input("Nível", linha["Nível"])

            with col3:
                predio = st.text_input("Prédio", linha["Prédio"])

            qtde = st.number_input("Quantidade", value=int(linha["Qtde"]))
            categoria = st.text_input("Categoria", linha["Categoria"])
            produto = st.text_input("Produto", linha["Produto"])

            if st.button("Salvar Alterações"):
                df.loc[df["Código"] == codigo_edit, ["Rua", "Nível", "Prédio", "Qtde", "Categoria", "Produto"]] = \
                    [rua, nivel, predio, qtde, categoria, produto]

                salvar_base(df)
                st.success("Produto atualizado com sucesso!")


# ============================================================
# 3) IMPORTAR DADOS (Excel ou CSV)
# ============================================================
elif menu == "Importar Dados":
    st.subheader("Importar base")

    uploaded = st.file_uploader("Envie arquivo Excel ou CSV", type=["xlsx", "xlsm", "xls", "csv"])

    if uploaded:
        df_import = ler_arquivo(uploaded)

        st.write("Pré-visualização:")
        st.dataframe(df_import)

        if st.button("Importar para o sistema"):
            df_final = pd.concat([df, df_import], ignore_index=True)

            # Remover duplicações pelo SKU (Código)
            df_final = df_final.drop_duplicates(subset=["Código"], keep="last")

            salvar_base(df_final)

            st.success("Importação realizada com sucesso!")


# ============================================================
# 4) EXPORTAR DADOS
# ============================================================
elif menu == "Exportar Dados":
    st.subheader("Download da base de estoque")

    df_xlsx = df.to_excel("estoque_exportado.xlsx", index=False)

    with open("estoque_exportado.xlsx", "rb") as f:
        st.download_button(
            label="Baixar Excel",
            data=f,
            file_name="estoque_exportado.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
# ============================================================
# 5) DASHBOARD
# ============================================================
elif menu == "Dashboard":
    st.subheader("📊 Dashboard de Estoque - ACME")

    # Indicadores principais
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total de SKUs", len(df))
    with col2:
        st.metric("Total de Itens no Estoque", int(df["Qtde"].sum()))
    with col3:
        categorias_unicas = df["Categoria"].nunique()
        st.metric("Categorias Cadastradas", categorias_unicas)

    st.divider()

    # Quantidade por Rua
    st.subheader("Distribuição por Rua")
    qtd_rua = df.groupby("Rua")["Qtde"].sum().sort_values(ascending=False)
    st.bar_chart(qtd_rua)

    st.divider()

    # Quantidade por Categoria
    st.subheader("Quantidade por Categoria")
    qtd_cat = df.groupby("Categoria")["Qtde"].sum().sort_values(ascending=False)
    st.bar_chart(qtd_cat)

    st.divider()

    # Top 10 produtos por quantidade
    st.subheader("Top 10 Produtos com Maior Quantidade")
    top10 = df.sort_values(by="Qtde", ascending=False).head(10)
    st.dataframe(top10, use_container_width=True)




