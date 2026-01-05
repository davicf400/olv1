import pandas as pd
import json

def buscar_valor_no_df(df, label_alvo):
    label_alvo = str(label_alvo).strip().lower()
    for row_idx in range(len(df)):
        for col_idx in range(len(df.columns)):
            celula = str(df.iloc[row_idx, col_idx]).strip().lower()
            
            # Filtro caprichado: verifica se o rótulo está contido na célula
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
        
        cliente = buscar_valor_no_df(df_c, "Cliente")
        obra = buscar_valor_no_df(df_c, "Obra")
        local = buscar_valor_no_df(df_c, "Local")

        df_i = planilha.parse('Cadastro de Insumos').fillna(0)
        
        def buscar_na_secao_flexivel(termo_secao, label_item):
            termo_secao = termo_secao.lower()
            # Procura a linha que contém o nome da seção (ex: "miudo", "aditivo")
            mask = df_i.iloc[:, 0].astype(str).str.lower().str.contains(termo_secao, na=False)
            idx = df_i[mask].index
            if not idx.empty:
                start_row = idx[0]
                # Pega uma fatia maior (20 linhas) para garantir que ache os campos abaixo
                fatia = df_i.iloc[start_row : start_row + 20]
                return buscar_valor_no_df(fatia, label_item)
            return "Seção não encontrada"

        cadastro_insumos= {
            "cimento": {
                "tipo": buscar_na_secao_flexivel("Cimento", "Tipo"),
                "fabricante": buscar_na_secao_flexivel("Cimento", "Fabricante"),
                "origem": buscar_na_secao_flexivel("Cimento", "Origem")
            },
            "agregado_miudo": {
                "tipo": buscar_na_secao_flexivel("Miúdo", "Tipo"),
                "origem": buscar_na_secao_flexivel("Miúdo", "Origem")
            },
            "agregado_graudo": {
                "tipo": buscar_na_secao_flexivel("Graúdo", "Tipo"),
                "origem": buscar_na_secao_flexivel("Graúdo", "Origem")
            },
            "aditivo": {
                "identificacao": buscar_na_secao_flexivel("Aditivo", "Identificação"),
                "fabricante": buscar_na_secao_flexivel("Aditivo", "Fabricante"),
                "teor": buscar_na_secao_flexivel("Aditivo", "Teor")
            },
            "adicao": {
                "identificacao": buscar_na_secao_flexivel("Adição", "Identificação"),
                "fabricante": buscar_na_secao_flexivel("Adição", "Fabricante"),
                "teor": buscar_na_secao_flexivel("Adição", "Teor")
            }
        }

        df_e = planilha.parse('Escopo de Estudo').fillna(0)
        slump = buscar_valor_no_df(df_e, "Slump")
        idade = buscar_valor_no_df(df_e, "Idade Avaliada")
        tipocp = buscar_valor_no_df(df_e, "Tipo de CP")
        inicial = buscar_valor_no_df(df_e, "Inicial de Agregados")

        df_p = planilha.parse('Dados - Fase Plástica').fillna(0)
        tracos = []
        for i, row in df_p.iterrows():
            txt_celula = str(row.iloc[0]).lower()
            if "m =" in txt_celula:
                dados_traco = {
                    "identificador": str(row.iloc[0]),
                    "alpha": df_p.iloc[i+1, 1],
                    "agua": df_p.iloc[i+1, 3],
                    "Slump(mm)": df_p.iloc[i+1, 5],
                    "Peso(kg)": df_p.iloc[i+1, 7]
                }
                tracos.append(dados_traco)

        return {
            "cadastro cliente": {"cliente": cliente, "obra": obra, "local": local},
            " cadastro de insumos": cadastro_insumos,
            "escopo": {"slump": slump, "idade": idade, "tipo de cp": tipocp, "inicial agregados graudos": inicial},
            "fase plastica": {"dados": tracos}
        }

    except Exception as e:
        print(f"Erro: {e}")
        return None

dados_os = registro()
if dados_os:
    nome_arquivo = f"OS_{str(dados_os['cadastro cliente']['cliente']).replace(' ', '_')}.json"
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        json.dump(dados_os, f, indent=4, ensure_ascii=False)
    print(f"Sucesso: {nome_arquivo} gerado.")