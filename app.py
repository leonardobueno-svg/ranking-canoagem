import streamlit as st
import pandas as pd

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Ranking Nacional CBC", layout="wide", page_icon="🚣‍♂️")

st.title("🚣‍♂️ Ranking Nacional de Caiaque Cross - CBC")
st.markdown("""
Sistema de pontuação unificada: **Copa Brasil (Peso 1)** + **Campeonato Brasileiro (Peso 2)**.
""")

# --- REGRAS DE PONTUAÇÃO ---
# Tabela de pontos: 1º=30, 2º=25, 3º=20...
PONTUACAO = {
    1: 30, 2: 25, 3: 20, 4: 18, 5: 17, 6: 16, 7: 15, 8: 14, 9: 13, 10: 12,
    11: 11, 12: 10, 13: 9, 14: 8, 15: 7, 16: 6, 17: 5, 18: 4, 19: 3, 20: 2, 21: 1
}

def calcular_pontos(posicao, peso=1):
    """Converte posição em pontos aplicando o peso"""
    try:
        pos = int(posicao)
        pontos_base = PONTUACAO.get(pos, 0)
        return pontos_base * peso
    except:
        return 0

# --- UPLOAD DO ARQUIVO MESTRA ---
st.sidebar.header("Painel de Controle")
arquivo = st.sidebar.file_uploader("Carregar Planilha Excel (.xlsx)", type=["xlsx"])

if arquivo:
    try:
        # Lê o arquivo Excel completo (todas as abas)
        xls = pd.ExcelFile(arquivo)
        
        # Seletor de Categoria
        categorias_disponiveis = xls.sheet_names
        categoria_selecionada = st.selectbox("Selecione a Categoria:", categorias_disponiveis)
        
        # Carrega os dados da aba selecionada
        df = pd.read_excel(arquivo, sheet_name=categoria_selecionada)
        
        # Validação básica de colunas
        colunas_necessarias = ['Atleta', 'Copa_Tomada', 'Copa_Combate', 'Brasileiro_Tomada', 'Brasileiro_Combate']
        if all(col in df.columns for col in colunas_necessarias):
            
            # --- CÁLCULO DOS PONTOS ---
            # Copa Brasil (Peso 1)
            df['Pts_Copa_Tomada'] = df['Copa_Tomada'].apply(lambda x: calcular_pontos(x, peso=1))
            df['Pts_Copa_Combate'] = df['Copa_Combate'].apply(lambda x: calcular_pontos(x, peso=1))
            
            # Brasileiro (Peso 2)
            df['Pts_BR_Tomada'] = df['Brasileiro_Tomada'].apply(lambda x: calcular_pontos(x, peso=2))
            df['Pts_BR_Combate'] = df['Brasileiro_Combate'].apply(lambda x: calcular_pontos(x, peso=2))
            
            # TOTAL GERAL
            df['TOTAL_GERAL'] = (df['Pts_Copa_Tomada'] + df['Pts_Copa_Combate'] + 
                                 df['Pts_BR_Tomada'] + df['Pts_BR_Combate'])
            
            # Ordenar Ranking (Maior pontuação primeiro)
            ranking_final = df.sort_values(by='TOTAL_GERAL', ascending=False).reset_index(drop=True)
            ranking_final.index += 1 # Começar do 1º
            
            # --- EXIBIÇÃO ---
            st.subheader(f"🏆 Classificação: {categoria_selecionada}")
            
            # Tabela Estilizada
            st.dataframe(
                ranking_final[['Atleta', 'TOTAL_GERAL', 'Pts_Copa_Tomada', 'Pts_Copa_Combate', 'Pts_BR_Tomada', 'Pts_BR_Combate']],
                column_config={
                    "TOTAL_GERAL": st.column_config.ProgressColumn("Total de Pontos", format="%d", min_value=0, max_value=200),
                },
                use_container_width=True
            )
            
            # Download
            csv = ranking_final.to_csv().encode('utf-8')
            st.download_button(
                label=f"📥 Baixar Ranking {categoria_selecionada}",
                data=csv,
                file_name=f"Ranking_{categoria_selecionada}.csv",
                mime="text/csv"
            )
            
        else:
            st.error(f"A aba '{categoria_selecionada}' não tem as colunas corretas. Verifique o modelo.")
            st.write("Colunas esperadas:", colunas_necessarias)
            
    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")

else:
    st.info("👆 Por favor, faça o upload da planilha Excel na barra lateral.")
    st.markdown("### Instruções")
    st.markdown("1. Crie um Excel com uma aba para cada categoria.")
    st.markdown("2. Coloque as posições (1, 2, 3...) nas colunas correspondentes.")
    st.markdown("3. O sistema calcula automaticamente os pesos (x2 para Brasileiro) e gera o ranking.")
