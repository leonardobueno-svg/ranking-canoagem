import streamlit as st
import pandas as pd
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Ranking Nacional CBC", layout="wide", page_icon="🚣‍♂️")

st.title("🚣‍♂️ Ranking Nacional de Caiaque Cross - CBC")
st.markdown("**Sistema Oficial de Pontuação Unificada**")
st.markdown("---")

# --- NOME DO ARQUIVO OFICIAL ---
ARQUIVO_OFICIAL = "Dados_Ranking.xlsx"

# --- TABELA DE PONTOS ---
PONTUACAO = {
    1: 30, 2: 25, 3: 20, 4: 18, 5: 17, 6: 16, 7: 15, 8: 14, 9: 13, 10: 12,
    11: 11, 12: 10, 13: 9, 14: 8, 15: 7, 16: 6, 17: 5, 18: 4, 19: 3, 20: 2, 21: 1
}

def calcular_pontos(posicao, peso=1):
    try:
        if pd.isna(posicao) or str(posicao).strip() in ['', '-', 'DNS', 'DSQ', 'N/A']:
            return 0
        pos = int(posicao)
        if pos < 1: return 0
        pontos_base = PONTUACAO.get(pos, 0)
        return pontos_base * peso
    except:
        return 0

def processar_dataframe(df):
    """Lógica central de cálculo"""
    df['TOTAL_GERAL'] = 0
    cols_para_exibir = ['Atleta']
    
    # Procura colunas de Individual e Cross
    cols_validas = [c for c in df.columns if 'Individual' in c or 'Cross' in c or 'Tomada' in c or 'Combate' in c]
    
    if not cols_validas:
        st.error("❌ As colunas do Excel não estão com os nomes certos (Individual/Cross).")
        st.write("Colunas encontradas:", df.columns.tolist())
        return None

    for col in cols_validas:
        # Peso 2 se for Brasileiro
        peso = 2 if 'Brasileiro' in col else 1
        
        # Cálculo
        col_pts = f"Pts_{col}"
        df[col_pts] = df[col].apply(lambda x: calcular_pontos(x, peso))
        df['TOTAL_GERAL'] += df[col_pts]
        cols_para_exibir.append(col)
    
    cols_para_exibir.insert(1, 'TOTAL_GERAL')
    
    # Ordenação
    ranking = df.sort_values(by='TOTAL_GERAL', ascending=False).reset_index(drop=True)
    ranking.index += 1
    return ranking[cols_para_exibir]

# --- LÓGICA PRINCIPAL (HÍBRIDA) ---
df_final = None
origem = ""

# 1. Tenta ler do GitHub direto
if os.path.exists(ARQUIVO_OFICIAL):
    try:
        xls = pd.ExcelFile(ARQUIVO_OFICIAL)
        origem = "GitHub (Automático)"
    except Exception as e:
        st.warning(f"⚠️ Erro ao ler arquivo do GitHub: {e}")
        xls = None
else:
    xls = None

# 2. Se falhar, pede Upload Manual
if xls is None:
    st.info("📂 Arquivo oficial não encontrado. Por favor, faça o upload manual abaixo.")
    upload = st.file_uploader("Carregar Excel", type=["xlsx"])
    if upload:
        xls = pd.ExcelFile(upload)
        origem = "Upload Manual"

# --- EXIBIÇÃO ---
if xls:
    st.sidebar.header(f"Fonte: {origem}")
    categorias = xls.sheet_names
    categoria = st.sidebar.radio("Escolha a Categoria:", categorias)
    
    try:
        df_raw = pd.read_excel(xls, sheet_name=categoria)
        resultado = processar_dataframe(df_raw)
        
        if resultado is not None:
            # Pódio
            st.subheader(f"🏆 Classificação: {categoria}")
            top3 = resultado.head(3)
            c1, c2, c3 = st.columns(3)
            if len(top3) >= 1: c2.metric("🥇 1º Lugar", top3.iloc[0]['Atleta'], f"{int(top3.iloc[0]['TOTAL_GERAL'])}")
            if len(top3) >= 2: c1.metric("🥈 2º Lugar", top3.iloc[1]['Atleta'], f"{int(top3.iloc[1]['TOTAL_GERAL'])}")
            if len(top3) >= 3: c3.metric("🥉 3º Lugar", top3.iloc[2]['Atleta'], f"{int(top3.iloc[2]['TOTAL_GERAL'])}")
            
            st.dataframe(resultado, use_container_width=True, height=600)
            
    except Exception as e:
        st.error(f"Erro ao processar aba: {e}")

else:
    if not os.path.exists(ARQUIVO_OFICIAL):
        st.warning(f"DICA: Para o modo automático funcionar, suba o arquivo '{ARQUIVO_OFICIAL}' no seu GitHub.")
