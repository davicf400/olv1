import pandas as pd

# ==============================================================================
# MÓDULO: EXTRAÇÃO DE DADOS (EXCEL)
# ==============================================================================

def buscar_valor_no_df(df, label_alvo):
    label_alvo = str(label_alvo).strip().lower()
    for row_idx in range(len(df)):
        for col_idx in range(len(df.columns)):
            celula = str(df.iloc[row_idx, col_idx]).strip().lower()
            if label_alvo in celula:
                for offset in range(1, 10): 
                    if col_idx + offset < len(df.columns):
                        valor = df.iloc[row_idx, col_idx + offset]
                        if valor != 0 and pd.notna(valor) and str(valor).strip() != "" and str(valor).strip() != "0":
                            return valor
    return "Não Encontrado"

def registro():
    try:
        planilha = pd.ExcelFile('Estudos de Dosagem de Concreto 2025.xlsx')
        
        df_c = planilha.parse('Cadastro de Cliente').fillna(0)
        df_e = planilha.parse('Escopo de Estudo').fillna(0)
        df_p = planilha.parse('Dados - Fase Plástica').fillna(0)

        # Extração
        dados = {
            "cliente_info": {
                "nome": buscar_valor_no_df(df_c, "Cliente"),
                "obra": buscar_valor_no_df(df_c, "Obra"),
                "local": buscar_valor_no_df(df_c, "Local")
            },
            "parametros_gerais": {
                "inicial_agregados": buscar_valor_no_df(df_e, "Inicial de Agregados"),
                "slump_meta": buscar_valor_no_df(df_e, "Slump")
            },
            "dados_fase_plastica": []
        }

        # Extração dos Traços
        for i, row in df_p.iterrows():
            txt_celula = str(row.iloc[0]).lower()
            if "m =" in txt_celula:
                try:
                    valor_m = float(txt_celula.split('=')[1].strip())
                except:
                    valor_m = 0.0
                
                dados["dados_fase_plastica"].append({
                    "m": valor_m,
                    "alpha": float(df_p.iloc[i+1, 1]),
                    "agua": float(df_p.iloc[i+1, 3]),
                    "slump_medido": df_p.iloc[i+1, 5],
                    "consumo_estimado": df_p.iloc[i+1, 7]
                })

        return dados

    except FileNotFoundError:
        print("ERRO CRÍTICO: Arquivo Excel não encontrado.")
        return None
    except Exception as e:
        print(f"ERRO DE EXTRAÇÃO: {e}")
        return None
    
 