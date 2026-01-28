import pandas as pd
import json
import numpy as np
from decimal import Decimal
from dataclasses import dataclass

# ==============================================================================
# PARTE 1: O "CÉREBRO" MATEMÁTICO
# ==============================================================================

class CalculoFasePlastica:
    def britas(self, m, alpha):
        m_dec = Decimal(str(m))
        alpha_dec = Decimal(str(alpha))
        if m_dec < 3: return Decimal(0)
        return m_dec - (alpha_dec * (1 + m_dec) - 1)

    def cimento_dosagem(self, inicial_agregados, alpha, m, britas_val): 
        m_dec = Decimal(str(m))
        alpha_dec = Decimal(str(alpha))
        ini_agg_dec = Decimal(str(inicial_agregados))
        britas_dec = Decimal(str(britas_val))
        if m_dec < 3 or alpha_dec == 0: return Decimal(0)
        if britas_dec == 0: return Decimal(0)
        return ini_agg_dec / britas_dec

    def aMC(self, agua, m, inicial_agregados, alpha): 
        b_val = self.britas(m, alpha)
        c = self.cimento_dosagem(inicial_agregados, alpha, m, b_val)
        m_dec = Decimal(str(m))
        agua_dec = Decimal(str(agua))
        if m_dec < 3 or c == 0: return Decimal(0)
        return agua_dec / c

class InterpoladorCramer:
    def __init__(self, dados_x, dados_y):
        self.x = np.array(dados_x, dtype=float)
        self.y = np.array(dados_y, dtype=float)
        self.coeficientes = {}
        self.determinantes = {}
        self.matriz_principal = None # Para guardar e mostrar depois
    
    def _calcular_determinantes(self):
        expoentes = np.arange(6, -1, -1)
        # Cria a matriz de Vandermonde (X^6 ... X^0)
        self.matriz_principal = np.power(self.x[:, None], expoentes)
        
        self.determinantes['D_principal'] = np.linalg.det(self.matriz_principal)
        
        for i in range(7):
            m_temp = self.matriz_principal.copy()
            m_temp[:, i] = self.y
            self.determinantes[f'D_col_{i+1}'] = np.linalg.det(m_temp)
            
    def resolver_coeficientes(self):
        if not self.determinantes: self._calcular_determinantes()
        d_main = self.determinantes['D_principal']
        for i in range(1, 8):
            self.coeficientes[f'a{7-i}'] = self.determinantes[f'D_col_{i}'] / d_main
        return self.coeficientes

    def _calcular_polinomio(self, x_val):
        return (self.coeficientes['a6'] * (x_val**6)) + \
               (self.coeficientes['a5'] * (x_val**5)) + \
               (self.coeficientes['a4'] * (x_val**4)) + \
               (self.coeficientes['a3'] * (x_val**3)) + \
               (self.coeficientes['a2'] * (x_val**2)) + \
               (self.coeficientes['a1'] * (x_val**1)) + \
               self.coeficientes['a0']

    def gerar_validacao(self):
        if not self.coeficientes: self.resolver_coeficientes()
        lista_resultados = []
        for x_val, y_real in zip(self.x, self.y):
            y_calc = self._calcular_polinomio(x_val)
            lista_resultados.append({
                'a/c (x)': x_val, 'm Real': y_real, 'm Calculado': y_calc, 'Diferença': y_calc - y_real
            })
        return pd.DataFrame(lista_resultados)

    def gerar_curva(self, num_pontos=50):
        if not self.coeficientes: self.resolver_coeficientes()
        eixo_x_suave = np.linspace(self.x.min(), self.x.max(), num_pontos)
        lista_curva = []
        for x_step in eixo_x_suave:
            y_smooth = self._calcular_polinomio(x_step)
            lista_curva.append({'a/c (Interpolado)': x_step, 'm (Curva)': y_smooth})
        return pd.DataFrame(lista_curva)

# ==============================================================================
# PARTE 2: O EXTRATOR (COM BUSCA ROBUSTA)
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
        
        # Leitura das abas
        df_c = planilha.parse('Cadastro de Cliente').fillna(0)
        df_e = planilha.parse('Escopo de Estudo').fillna(0)
        df_p = planilha.parse('Dados - Fase Plástica').fillna(0)

        # Extração de Dados Gerais
        cliente = buscar_valor_no_df(df_c, "Cliente")
        obra = buscar_valor_no_df(df_c, "Obra")
        local = buscar_valor_no_df(df_c, "Local")
        inicial = buscar_valor_no_df(df_e, "Inicial de Agregados")
        slump = buscar_valor_no_df(df_e, "Slump")

        # Extração dos Traços
        tracos = []
        for i, row in df_p.iterrows():
            txt_celula = str(row.iloc[0]).lower()
            if "m =" in txt_celula:
                try:
                    valor_m = float(txt_celula.split('=')[1].strip())
                except:
                    valor_m = 0.0
                
                # Pegando dados nas colunas corretas (ajuste conforme sua planilha real)
                # Assumindo offsets fixos baseados no seu código anterior
                dados_traco = {
                    "m": valor_m,
                    "alpha": float(df_p.iloc[i+1, 1]),
                    "agua": float(df_p.iloc[i+1, 3]),
                    "slump_medido": df_p.iloc[i+1, 5],
                    "consumo_estimado": df_p.iloc[i+1, 7]
                }
                tracos.append(dados_traco)

        return {
            "cliente_info": {
                "nome": cliente,
                "obra": obra,
                "local": local
            },
            "parametros_gerais": {
                "inicial_agregados": inicial,
                "slump_meta": slump
            },
            "dados_fase_plastica": tracos
        }

    except FileNotFoundError:
        print("ERRO CRÍTICO: Arquivo 'Estudos de Dosagem de Concreto 2025.xlsx' não encontrado.")
        return None
    except Exception as e:
        print(f"ERRO DE EXTRAÇÃO: {e}")
        return None

# ==============================================================================
# PARTE 3: INTEGRAÇÃO COM RELATÓRIO DETALHADO
# ==============================================================================

def processar_dosagem_completa():
    print("\n" + "="*80)
    print(" INICIANDO EXTRAÇÃO DE DADOS ".center(80, "="))
    print("="*80)
    
    dados_json = registro()
    
    if not dados_json: return

    # --- 1. PRINT DO JSON COMPLETO ---
    print("\n--- [JSON] DADOS BRUTOS EXTRAÍDOS ---")
    print(json.dumps(dados_json, indent=4, ensure_ascii=False))

    inicial_agregados = dados_json['parametros_gerais']['inicial_agregados']
    lista_tracos = dados_json['dados_fase_plastica']
    
    # --- 2. CÁLCULO FASE PLÁSTICA ---
    print("\n" + "="*80)
    print(" CÁLCULO FASE PLÁSTICA (Encontrar a/c) ".center(80, "="))
    print("="*80)
    
    calculadora = CalculoFasePlastica()
    pontos_x = []
    pontos_y = []

    for traco in lista_tracos:
        m = traco['m']
        alpha = traco['alpha']
        agua = traco['agua']
        
        # Calcula a/c
        ac = float(calculadora.aMC(agua, m, inicial_agregados, alpha))
        
        print(f"Traço m={m:<5} | Alpha={alpha:<5} | Água={agua:<5} => a/c Calculado: {ac:.6f}")
        
        pontos_x.append(ac)
        pontos_y.append(m)

    # --- 3. MATRIZES E DETERMINANTES ---
    if len(pontos_x) >= 2:
        print("\n" + "="*80)
        print(" INTERPOLADOR MATRICIAL (CRAMER) ".center(80, "="))
        print("="*80)

        # Ordena os pontos para garantir consistência visual
        pontos_ordenados = sorted(zip(pontos_x, pontos_y))
        x_ord, y_ord = zip(*pontos_ordenados)

        solver = InterpoladorCramer(x_ord, y_ord)
        coefs = solver.resolver_coeficientes()
        
        # A) MOSTRAR A MATRIZ DE VANDERMONDE
        print("\n--- [MATRIZ] Principal (Vandermonde X^6 a X^0) ---")
        # Pandas deixa a visualização da matriz mais bonita
        df_matriz = pd.DataFrame(solver.matriz_principal, 
                                 columns=[f"x^{i}" for i in range(6, -1, -1)])
        print(df_matriz.to_string(index=False, float_format="%.4f"))

        # B) MOSTRAR OS DETERMINANTES
        print("\n--- [CÁLCULO] Determinantes (Regra de Cramer) ---")
        df_dets = pd.DataFrame([solver.determinantes])
        # Transpomos (.T) para ficar vertical e mais fácil de ler
        print(df_dets.T.rename(columns={0: 'Valor'}).to_string(float_format="%.4e"))

        # C) MOSTRAR A EQUAÇÃO FINAL
        print("\n--- [RESULTADO] Equação Polinomial (Coeficientes) ---")
        print("y = (a6 * x^6) + (a5 * x^5) + ... + a0")
        for k, v in coefs.items():
            print(f"{k} = {v:.15f}")

        # D) VALIDAÇÃO
        print("\n--- [VALIDAÇÃO] Comparativo Real vs Calculado ---")
        print(solver.gerar_validacao().to_string(index=False, float_format="%.8f"))

        # E) CURVA FINAL
        print("\n--- [CURVA] Interpolação (Primeiros e Últimos Pontos) ---")
        df_curva = solver.gerar_curva(50)
        print(df_curva.head().to_string(index=False, float_format="%.8f"))
        print("... (40 pontos intermediários) ...")
        print(df_curva.tail().to_string(index=False, float_format="%.8f"))

        print("\n[SUCESSO] Todos os cálculos matriciais foram exibidos.")

    else:
        print("\n[ERRO] Pontos insuficientes para gerar a matriz.")

if __name__ == "__main__":
    processar_dosagem_completa()