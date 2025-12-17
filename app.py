import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import cerebro  

st.set_page_config(layout="wide", page_title="Sistema de Dosagem por Etapas")

# --- CONTROLE DE ETAPAS (MEMÓRIA) ---
if 'etapa' not in st.session_state:
    st.session_state.etapa = 1
if 'resultados_cache' not in st.session_state:
    st.session_state.resultados_cache = None
if 'curva_cache' not in st.session_state:
    st.session_state.curva_cache = None

if 'df_input' not in st.session_state:
    st.session_state.df_input = pd.DataFrame({
        "m": [3, 4, 5, 6, 7, 8, 9],
        "alpha": [51.0]*7,
        "agua": [3.48, 3.50, 3.44, 3.50, 3.49, 3.50, 3.58],
        "peso": [19.58]*7,
        "slump": [200, 200, 200, 200, 200, 200, 100],
        
        # <<< ESSAS COLUNAS ESTAVAM FALTANDO NA SUA PRIMEIRA IMAGEM >>>
        "Carga": [40.0, 35.0, 30.0, 25.0, 20.0, 18.0, 15.0], 
        "Tipo CP": ['10x20 axial'] *7,
        "Idade": [28]*7
        # << FIM DAS NOVAS COLUNAS >>
    })   

def avancar_etapa():
    st.session_state.etapa += 1

def voltar_etapa():
    st.session_state.etapa -= 1

def reiniciar():
    st.session_state.etapa = 1
    st.session_state.resultados_cache = None

# --- BARRA LATERAL (SEMPRE VISÍVEL) ---
st.sidebar.title("Configurações")
st.sidebar.markdown(f"**Etapa Atual: {st.session_state.etapa}/3**")
progress = st.sidebar.progress(0)
if st.session_state.etapa == 1: progress.progress(33)
elif st.session_state.etapa == 2: progress.progress(66)
elif st.session_state.etapa == 3: progress.progress(100)

tipo = st.sidebar.selectbox("Tipo de Gráfico Final", 
    ["m/a/c", "resistencia/ac", "a/c/resistencia", "m/consumo", "m/indide de eficiencia"]
)

st.sidebar.divider()
config = {
    'volume': st.sidebar.number_input("Volume (m³)", 0.00530, format="%.5f"),
    'tara': st.sidebar.number_input("Tara (kg)", 6.540, format="%.3f"),
    'agregados': st.sidebar.number_input("Agregados Iniciais", 1.000),
    'pct_cimento': st.sidebar.number_input("% Cimento", 100.0)
}

# ==============================================================================
# ETAPA 1: ENTRADA DE DADOS
# ==============================================================================
if st.session_state.etapa == 1:
    st.title("📝 Etapa 1: Entrada de Dados")
    st.info("Preencha os dados do laboratório abaixo.")

    # Dados padrão
    if 'df_input' not in st.session_state:
        dados_padrao = {
            "m": [3, 4, 5, 6, 7, 8, 9],
            "alpha": [51.0]*7,
            "agua": [3.48, 3.50, 3.44, 3.50, 3.49, 3.50, 3.58],
            "peso": [19.58]*7,
            "slump": [200, 200, 200, 200, 200, 200, 100],
          
        }
        st.session_state.df_input = pd.DataFrame(dados_padrao)

    df_usuario = st.data_editor(st.session_state.df_input, use_container_width=True, height=300)
    
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("CALCULAR FASES 1 & 2 ➡️", type="primary"):
            try:
                # Salva o input na memória
                st.session_state.df_input = df_usuario
                
                # Roda o Cérebro
                brutos, curva, tipo_atual = cerebro.executar_pipeline_completo(df_usuario, config, tipo)
                
                # Guarda o resultado na memória
                st.session_state.resultados_cache = brutos
                st.session_state.curva_cache = curva
                st.session_state.tipo_atual_cache = tipo_atual
                
                avancar_etapa()
                st.rerun()
                
            except Exception as e:
                st.error(f"Erro nos cálculos: {e}")

# ==============================================================================
# ETAPA 2: VALIDAÇÃO (VER A TABELA CALCULADA)
# ==============================================================================
elif st.session_state.etapa == 2:
    st.title("🔍 Etapa 2: Validação dos Resultados")
    st.success("Cálculos das Fases 1 e 2 realizados com sucesso! Confira abaixo.")

    # Recupera os dados calculados
    df_res = pd.DataFrame(st.session_state.resultados_cache)
    
    # Formata para ficar bonito na tela (seleciona colunas importantes)
    colunas_visiveis = ['m', 'A/MC', 'Cimentos', 'MASSAESPECIFICA', 'Eficiencia', 'resistencia_manual']
    
    # Mostra tabela completa
    st.dataframe(
        df_res.style.format("{:.3f}"), 
        use_container_width=True, 
        height=300
    )

    st.warning("⚠️ Verifique se o Consumo de Cimento e o Fator A/C estão coerentes antes de gerar a curva.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Corrigir Dados"):
            voltar_etapa()
            st.rerun()
    with col2:
        if st.button("CONFIRMAR E GERAR GRÁFICO 📈", type="primary"):
            avancar_etapa()
            st.rerun()

# ==============================================================================
# ETAPA 3: GRÁFICO FINAL
# ==============================================================================
elif st.session_state.etapa == 3:
    st.title("📊 Etapa 3: Curva de Dosagem")
    
    # Recupera tudo da memória
    df_pontos = pd.DataFrame(st.session_state.resultados_cache)
    df_linha = pd.DataFrame(st.session_state.curva_cache)
    tipo_atual = st.session_state.tipo_atual_cache
    
    # Mapeamento
    mapa = {
        "m/a/c": ("m", "A/MC"), 
        "resistencia/ac": ("A/MC", "resistencia_manual"),
        "a/c/resistencia": ("resistencia_manual", "A/MC"),
        "m/consumo": ("m", "Cimentos"),
        "m/indide de eficiencia": ("m", "Eficiencia")
    }
    
    if tipo_atual in mapa:
        col_x, col_y = mapa[tipo_atual]
        
        # R²
        r2_txt = ""
        if len(df_pontos) > 2:
            try:
                correlation = np.corrcoef(df_pontos[col_x], df_pontos[col_y])[0,1]
                r2_val = correlation**2
                r2_txt = f"R² = {r2_val:.4f}"
            except: pass

        # Gráfico Estilo Excel
        fig = go.Figure()

        if not df_linha.empty:
            fig.add_trace(go.Scatter(
                x=df_linha['x_calculado'], y=df_linha['y_calculado'],
                mode='lines', name='Curva Ajustada',
                line=dict(color='rgb(31, 119, 180)', width=2)
            ))

        fig.add_trace(go.Scatter(
            x=df_pontos[col_x], y=df_pontos[col_y],
            mode='markers', name='Experimental',
            marker=dict(color='black', size=8, line=dict(width=1, color='white'))
        ))

        fig.update_layout(
            title=dict(text=f"Relação: {tipo_atual.upper()}", x=0.5),
            xaxis_title=col_x, yaxis_title=col_y,
            template="plotly_white", height=600,
            xaxis=dict(showgrid=True, gridcolor='lightgray', showline=True, linecolor='black', mirror=True),
            yaxis=dict(showgrid=True, gridcolor='lightgray', showline=True, linecolor='black', mirror=True),
            legend=dict(x=0.8, y=0.9, bgcolor='rgba(255,255,255,0.8)', bordercolor='black', borderwidth=1)
        )

        fig.add_annotation(
            x=0.05, y=0.95, xref="paper", yref="paper",
            text=f"<b>{r2_txt}</b>", showarrow=False,
            font=dict(size=16, color="black"),
            bgcolor="white", bordercolor="black", borderwidth=1
        )

        if tipo_atual == "m/a/c": fig.update_yaxes(autorange="reversed")

        st.plotly_chart(fig, use_container_width=True)
    
    if st.button("🔄 Novo Ensaio (Reiniciar)"):
        reiniciar()
        st.rerun()