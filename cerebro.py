import numpy as np
import pandas as pd
from decimal import Decimal
from dataclasses import dataclass

# ==============================================================================
# MÓDULO: LÓGICA MATEMÁTICA E CLASSES
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
    
    def indice_eficiencia(self, consumo, resistencia):
        cons_dec = Decimal(str(consumo))
        res_dec = Decimal(str(resistencia))
        if res_dec == 0: return Decimal(0)
        return cons_dec / res_dec


class InterpoladorCramer:
   
    def __init__(self, dados_x, dados_y, nome_x="Eixo X", nome_y="Eixo Y"):
        x_bruto = np.array(dados_x, dtype=float)
        y_bruto = np.array(dados_y, dtype=float)
        
        # GARANTIA DE ORDENAÇÃO: Impede que o gráfico vire um rabisco se os dados vierem bagunçados
        indices_ordenados = np.argsort(x_bruto)
        self.x = x_bruto[indices_ordenados]
        self.y = y_bruto[indices_ordenados]
        
        self.nome_x = nome_x
        self.nome_y = nome_y
        self.coeficientes = {}
        self.determinantes = {}
        self.matriz_principal = None
    
    def _calcular_determinantes(self):
        expoentes = np.arange(6, -1, -1)
        self.matriz_principal = np.power(self.x[:, None], expoentes)
        self.determinantes['D_principal'] = np.linalg.det(self.matriz_principal)
        
        self.matrizes_auxiliares = {} 
        for i in range(7):
            m_temp = self.matriz_principal.copy()
            m_temp[:, i] = self.y
            self.matrizes_auxiliares[f'M_col_{i+1}'] = m_temp 
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
            diferenca = y_calc - y_real
           
            lista_resultados.append({
                f'{self.nome_x} (Real)': f"{x_val:.14f}", 
                f'{self.nome_y} (Real)': f"{y_real:.14f}", 
                f'{self.nome_y} (Calculado)': f"{y_calc:.14f}", 
                'Diferença': f"{diferenca:.14f}"
            })
        return pd.DataFrame(lista_resultados)

    def gerar_curva(self, num_pontos=51):
        if not self.coeficientes: self.resolver_coeficientes()
        eixo_x_suave = np.linspace(self.x.min(), self.x.max(), num_pontos)
        lista_curva = []
        for x_step in eixo_x_suave:
            y_smooth = self._calcular_polinomio(x_step)
            
            lista_curva.append({
                f'{self.nome_x} (Interpolado)': f"{x_step:.14f}", 
                f'{self.nome_y} (Curva)': f"{y_smooth:.14f}"
            })
        return pd.DataFrame(lista_curva)
    
    def calcular_r2(self):
      
        if not self.coeficientes: self.resolver_coeficientes()
        
        
        y_calc = np.array([self._calcular_polinomio(x) for x in self.x])
        
      
        ss_res = np.sum((self.y - y_calc) ** 2) 
        ss_tot = np.sum((self.y - np.mean(self.y)) ** 2) 
        
        if ss_tot == 0:
            return 1.0
        
        r2 = 1 - (ss_res / ss_tot)
        return r2