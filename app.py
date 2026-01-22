import streamlit as st
import pandas as pd
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Ranking Nacional CBC", layout="wide", page_icon="🚣‍♂️")

# Título e Subtítulo
st.title("🚣‍♂️ Ranking Nacional de Caiaque Cross - CBC")
st.markdown("""
**Regras de Pontuação:**
*   **Individual (Tomada de Tempo)** e **Cross (Combate)** somam pontos para o ranking.
*   **Copa Brasil:** Peso 1.
*   **Campeonato Brasileiro:** Peso 2 (Pontuação dobrada).
""")
st.markdown("---")

# --- NOME DO ARQUIVO OFICIAL ---
# Este arquivo deve estar no seu GitHub junto com este código
ARQUIVO_OFICIAL = "Dados_Ranking.xlsx"

# --- TABELA DE PONTOS ---
PONTUACAO = {
    1: 30, 2: 25, 3: 20, 4: 18, 5: 17, 6: 16, 7: 15, 8: 14, 9: 13, 10: 12,
    11: 11, 12: 10, 13: 9, 14: 8, 15: 7, 16: 6, 17: 5, 18: 4, 19: 3, 20: 2, 21: 1
}

def calcular_pontos(posicao, peso=1):
    """Converte posição (1, 2, 3...) em pontos (30, 25, 20...) aplicando o peso."""
    try:
        # Tratamento para células vazias, textos ou DNS
        if pd.isna(posicao) or str(posicao).strip() in ['', '-', 'DNS', 'DSQ', 'N/A']:
            return 0
        
        pos = int(posicao)
        if pos < 1: return 0
        
        pontos_base = PONTUACAO.get(pos, 0) # Se for > 21º, ganha 0 pontos
        return pontos_base * peso
    except:
        return 0

# --- LÓGICA DO SISTEMA ---
if os.path.exists(ARQUIVO_OFICIAL):
    try:
        xls = pd.ExcelFile(ARQUIVO_OFICIAL)
        
        # --- BARRA LATERAL (MENU) ---
        st.sidebar.header("Filtros")
        st.sidebar.info("Selecione a categoria abaixo para visualizar o ranking atualizado.")
        
        categorias_disponiveis = xls.sheet_names
        categoria_selecionada = st.sidebar.radio("Categorias:", categorias_disponiveis)
        
        # Lê a aba selecionada
        df = pd.read_excel(ARQUIVO_OFICIAL, sheet_name=categoria_selecionada)
        
        # Coluna de Total zerada para começar a soma
        df['TOTAL_GERAL'] = 0
        
        # --- PROCESSAMENTO INTELIGENTE DE COLUNAS ---
        cols_para_exibir = ['Atleta'] # Começamos a lista de exibição com o nome
        
        # O sistema percorre todas as colunas do Excel (exceto Atleta)
        for col in df.columns:
            if col == 'Atleta':
                continue
            
            # 1. Define o Peso
            # Se tiver "Brasileiro" no nome da coluna, multiplica por 2
            peso = 2 if 'Brasileiro' in col else 1
            
            # 2. Calcula os Pontos dessa coluna
            nome_col_pontos = f"Pts_{col}" # Cria coluna interna de memória (ex: Pts_Copa_Individual)
            df[nome_col_pontos] = df[col].apply(lambda x: calcular_pontos(x, peso))
            
            # 3. Soma ao Total Geral
            df['TOTAL_GERAL'] += df[nome_col_pontos]
            
            # 4. Adiciona à lista de colunas para mostrar na tabela final
            cols_para_exibir.append(col)

        # Adiciona o Total no final da lista de exibição
        cols_para_exibir.insert(1, 'TOTAL_GERAL') # Coloca o Total logo após o nome

        # --- ORDENAÇÃO DO RANKING ---
        ranking = df.sort_values(by='TOTAL_GERAL', ascending=False).reset_index(drop=True)
        ranking.index += 1 # Ajusta para o índice começar em 1 (1º lugar)
        
        # --- DESTAQUE DOS CAMPEÕES (PÓDIO) ---
        st.subheader(f"🏆 Pódio Atual: {categoria_selecionada}")
        top3 = ranking.head(3)
        col1, col2, col3 = st.columns(3)
        
        if len(top3) >= 1: 
            col2.metric("🥇 LÍDER", top3.iloc[0]['Atleta'], f"{int(top3.iloc[0]['TOTAL_GERAL'])} pts")
        if len(top3) >= 2: 
            col1.metric("🥈 2º Lugar", top3.iloc[1]['Atleta'], f"{int(top3.iloc[1]['TOTAL_GERAL'])} pts")
        if len(top3) >= 3: 
            col3.metric("🥉 3º Lugar", top3.iloc[2]['Atleta'], f"{int(top3.iloc[2]['TOTAL_GERAL'])} pts")
        
        st.markdown("---")
        
        # --- TABELA COMPLETA ---
        st.subheader(f"Classificação Detalhada")
        
        # Configuração visual da tabela
        st.dataframe(
            ranking[cols_para_exibir],
            use_container_width=True,
            height=600,
            column_config={
                "TOTAL_GERAL": st.column_config.ProgressColumn(
                    "Pontuação Total", 
                    format="%d", 
                    min_value=0, 
                    max_value=ranking['TOTAL_GERAL'].max()
                ),
                "Atleta": st.column_config.TextColumn("Atleta", width="medium"),
            }
        )
        
    except Exception as e:
        st.error(f"Erro ao processar o arquivo Excel: {e}")
        st.warning("Dica: Verifique se as colunas do Excel estão com os nomes corretos.")

else:
    # Caso o arquivo não exista no GitHub
    st.error("⚠️ Arquivo de dados não encontrado.")
    st.info(f"Por favor, faça o upload do arquivo '{ARQUIVO_OFICIAL}' no seu repositório do GitHub.")
