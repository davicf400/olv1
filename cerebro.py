import numpy as np
import pandas as pd

# --- A CLASSE CUIDA DE TUDO ---
class InterpoladorCramer:
    def __init__(self, dados_x, dados_y):
        self.x = np.array(dados_x)
        self.y = np.array(dados_y)
        self.coeficientes = {}
        self.determinantes = {}
    
    def _calcular_determinantes(self):
        expoentes = np.arange(6, -1, -1)
        # Cria a matriz de Vandermonde
        matriz_principal = np.power(self.x[:, None], expoentes)
        
        # Calcula Determinante Principal
        self.determinantes['D_principal'] = np.linalg.det(matriz_principal)
        
        # Calcula Determinantes das Colunas (Y passeando)
        for i in range(7):
            m_temp = matriz_principal.copy()
            m_temp[:, i] = self.y
            self.determinantes[f'D_col_{i+1}'] = np.linalg.det(m_temp)
            
    def resolver_coeficientes(self):
        # Se os determinantes estiverem vazios, calcula eles primeiro
        if not self.determinantes:
            self._calcular_determinantes()
            
        d_main = self.determinantes['D_principal']
        
        # Calcula a6, a5... a0 usando Cramer (Di / D_principal)
        for i in range(1, 8):
            self.coeficientes[f'a{7-i}'] = self.determinantes[f'D_col_{i}'] / d_main
            
        return self.coeficientes

    def _calcular_polinomio(self, x_val):
        # Aplica a fórmula: y = a6*x^6 + ... + a0
        return (self.coeficientes['a6'] * (x_val**6)) + \
               (self.coeficientes['a5'] * (x_val**5)) + \
               (self.coeficientes['a4'] * (x_val**4)) + \
               (self.coeficientes['a3'] * (x_val**3)) + \
               (self.coeficientes['a2'] * (x_val**2)) + \
               (self.coeficientes['a1'] * (x_val**1)) + \
               self.coeficientes['a0']

    def gerar_validacao(self):
        if not self.coeficientes:
            self.resolver_coeficientes()
            
        lista_resultados = []
        for x_val, y_real in zip(self.x, self.y):
            y_calc = self._calcular_polinomio(x_val)
            lista_resultados.append({
                'a/c (x)': x_val,
                'm Real': y_real,
                'm Calculado': y_calc,
                'Diferença': y_calc - y_real
            })
        return pd.DataFrame(lista_resultados)

    def gerar_curva(self, num_pontos=50):
        if not self.coeficientes:
            self.resolver_coeficientes()
            
        min_x = self.x.min()
        max_x = self.x.max()
        # Gera pontos equidistantes
        eixo_x_suave = np.linspace(min_x, max_x, num_pontos)
        
        lista_curva = []
        for x_step in eixo_x_suave:
            y_smooth = self._calcular_polinomio(x_step)
            lista_curva.append({
                'a/c (Interpolado)': x_step,
                'm (Curva)': y_smooth
            })
        return pd.DataFrame(lista_curva)

# --- EXECUÇÃO ---
if __name__ == "__main__":
    # 1. Dados de Entrada
    meu_x = [0.34104, 0.42875, 0.50568, 0.60025, 0.68404, 0.77175, 0.8771]
    meu_y = [3, 4, 5, 6, 7, 8, 9]

    # 2. Cria o objeto Solver
    solver = InterpoladorCramer(meu_x, meu_y)
    
    # 3. Força o cálculo inicial para preencher as variáveis internas
    coefs = solver.resolver_coeficientes()
    dets = solver.determinantes # Acessa o dicionário que foi preenchido acima

    # --- PRINT 1: DETERMINANTES ---
    print("\n=== 1. DETERMINANTES (Notação Científica) ===")
    df_dets = pd.DataFrame([dets])
    # Usamos %.4e para notação científica, senão aparece tudo 0.0000
    print(df_dets.to_string(index=False, float_format="%.4e"))

    # --- PRINT 2: COEFICIENTES DA EQUAÇÃO ---
    print("\n=== 2. EQUAÇÃO (Coeficientes a6...a0) ===")
    for termo, valor in coefs.items():
        print(f"{termo}: {valor:.15f}")

    # --- PRINT 3: TABELA DE VALIDAÇÃO ---
    df_val = solver.gerar_validacao()
    print("\n=== 3. VALIDAÇÃO (Real vs Calculado) ===")
    print(df_val.to_string(index=False, float_format="%.15f"))
    
    # --- PRINT 4: MONTAGEM DA CURVA ---
    df_curva = solver.gerar_curva(num_pontos=50)
    print("\n=== 4. CURVA INTERPOLADA (50 Pontos) ===")
    print(df_curva.head(10).to_string(index=False, float_format="%.15f"))
    print("... (mais 35 pontos) ...")
    print(df_curva.tail(5).to_string(index=False, float_format="%.15f"))