import streamlit as st
import pandas as pd
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Ranking Nacional CBCa Caiaque Cross 2025", layout="wide", page_icon="🚣‍♂️")

st.title("🚣‍♂️ Ranking Nacional de Caiaque Cross - CBCa 2025")
st.markdown("""
Sistema de pontuação unificada: **Copa Brasil (Peso 1)** + **Campeonato Brasileiro (Peso 2)**.
""")

# --- CONFIGURAÇÃO DO ARQUIVO OFICIAL ---
ARQUIVO_OFICIAL = "Dados_Ranking.xlsx"

# --- REGRAS DE PONTUAÇÃO ---
PONTUACAO = {
    1: 30, 2: 25, 3: 20, 4: 18, 5: 17, 6: 16, 7: 15, 8: 14, 9: 13, 10: 12,
    11: 11, 12: 10, 13: 9, 14: 8, 15: 7, 16: 6, 17: 5, 18: 4, 19: 3, 20: 2, 21: 1
}

def calcular_pontos(posicao, peso=1):
    """Converte posição em pontos aplicando o peso"""
    try:
        if pd.isna(posicao) or str(posicao).strip() in ['', '-', 'DNS', 'DSQ', 'N/A']:
            return 0
        pos = int(posicao)
        pontos_base = PONTUACAO.get(pos, 0)
        return pontos_base * peso
    except:
        return 0

# --- LEITURA AUTOMÁTICA DO ARQUIVO ---
if os.path.exists(ARQUIVO_OFICIAL):
    try:
        xls = pd.ExcelFile(ARQUIVO_OFICIAL)
        
        st.sidebar.header("Painel de Controle")
        categorias_disponiveis = xls.sheet_names
        categoria_selecionada = st.sidebar.radio("Selecione a Categoria:", categorias_disponiveis)
        
        df = pd.read_excel(ARQUIVO_OFICIAL, sheet_name=categoria_selecionada)
        
        # Limpeza dos nomes das colunas
        df.columns = df.columns.str.strip() 
        
        colunas_necessarias = ['Atleta', 'Copa_Individual', 'Copa_Cross', 'Brasileiro_Individual', 'Brasileiro_Cross']
        
        if all(col in df.columns for col in colunas_necessarias):
            
            # --- CÁLCULO DOS PONTOS ---
            df['Pts_Copa_Individual'] = df['Copa_Individual'].apply(lambda x: calcular_pontos(x, peso=1))
            df['Pts_Copa_Cross'] = df['Copa_Cross'].apply(lambda x: calcular_pontos(x, peso=1))
            df['Pts_Brasileiro_Individual'] = df['Brasileiro_Individual'].apply(lambda x: calcular_pontos(x, peso=2))
            df['Pts_Brasileiro_Cross'] = df['Brasileiro_Cross'].apply(lambda x: calcular_pontos(x, peso=2))
            
            # TOTAL GERAL
            df['TOTAL_GERAL'] = (df['Pts_Copa_Individual'] + df['Pts_Copa_Cross'] + 
                                 df['Pts_Brasileiro_Individual'] + df['Pts_Brasileiro_Cross'])
            
            # Ordenar Ranking
            ranking_final = df.sort_values(by='TOTAL_GERAL', ascending=False).reset_index(drop=True)
            ranking_final.index += 1 
            
            # --- EXIBIÇÃO ---
            st.subheader(f"🏆 Classificação: {categoria_selecionada}")
            
            # Correção do Erro INT64: Calculamos o máximo e convertemos para int nativo do Python
            max_pontos = int(ranking_final['TOTAL_GERAL'].max())
            if max_pontos == 0: max_pontos = 100 # Evita erro se tudo for zero
            
            st.dataframe(
                ranking_final[['Atleta', 'TOTAL_GERAL', 'Pts_Copa_Individual', 'Pts_Copa_Cross', 'Pts_Brasileiro_Individual', 'Pts_Brasileiro_Cross']],
                column_config={
                    "TOTAL_GERAL": st.column_config.ProgressColumn(
                        "Total de Pontos", 
                        format="%d", 
                        min_value=0, 
                        max_value=max_pontos # Agora usamos o valor convertido
                    ),
                    "Pts_Copa_Individual": st.column_config.NumberColumn("Copa Indiv.", format="%d"),
                    "Pts_Copa_Cross": st.column_config.NumberColumn("Copa Cross", format="%d"),
                    "Pts_Brasileiro_Individual": st.column_config.NumberColumn("BR Indiv. (x2)", format="%d"),
                    "Pts_Brasileiro_Cross": st.column_config.NumberColumn("BR Cross (x2)", format="%d"),
                },
                use_container_width=True,
                height=600
            )
            
            st.caption("Nota: As colunas mostram os PONTOS já calculados.")
            
        else:
            st.error(f"Erro na estrutura da aba '{categoria_selecionada}'.")
            st.warning(f"O sistema espera as colunas: {colunas_necessarias}")
            
    except Exception as e:
        st.error(f"Erro técnico ao processar os dados: {e}")

else:
    st.info("🚧 O Ranking está sendo atualizado.")
    st.markdown("Os dados oficiais estão sendo processados. Por favor, aguarde.")
