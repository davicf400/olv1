import pandas as pd
import numpy as np
from dataclasses import dataclass
from decimal import Decimal, getcontext
from typing import List, Dict, Any, Optional

getcontext().prec = 10

# ==============================================================================
# MÓDULO 1: FASE PLÁSTICA
# ==============================================================================
@dataclass
class IPFasePlastica:
    traco: str
    m: int 
    agua: Decimal
    slump: int
    peso: Decimal
    volume: Decimal
    tara: Decimal
    inicial_agregados: Decimal 
    alpha: Decimal
    percentual_cimento: Decimal

class CalcFasePlastica:
    def calcular_tudo(self, dados: IPFasePlastica) -> dict:
        britas_val = self.britas(dados.m, dados.alpha)
        mc_val = self.cimento_dosagem(dados.inicial_agregados, dados.alpha, dados.m, britas_val)
        a_mc_val = self.aMC(dados.agua, dados.m, dados.inicial_agregados, dados.alpha)
        me_val = self.ME(dados.peso, dados.volume, dados.tara, dados.m)
        ccimentos_val = self.Ccimentos(dados.m, me_val, a_mc_val)
        portland_val = self.cimentosP(ccimentos_val, dados.percentual_cimento)

        return {
             "britas": britas_val,
             "cimento_dosagem": mc_val,
             "A/MC": a_mc_val,
             "MASSAESPECIFICA": me_val,
             "Cimentos": ccimentos_val,
             "CIMENTOSPORTLANDO": portland_val,
             "m": dados.m
        }

    def britas(self, m, alpha):
        if m < 3: return Decimal(0)
        return m - (alpha * (1 + m) - 1)

    def cimento_dosagem(self, inicial_agregados, alpha, m, britas_val): 
        if m < 3 or alpha == 0: return Decimal(0)
        if britas_val == 0: return Decimal(0)
        return inicial_agregados / britas_val

    def aMC(self, agua, m, inicial_agregados, alpha): 
        b_val = self.britas(m, alpha)
        c = self.cimento_dosagem(inicial_agregados, alpha, m, b_val)
        if m < 3 or c == 0: return Decimal(0)
        return agua / c

    def ME(self, peso, vol, tara, m): 
        if m < 3 or vol == 0: return Decimal(0)
        return (peso - tara) / vol

    def Ccimentos(self, m, me_val, a_mc_val):
        if m < 3: return Decimal(0)
        divisor = (1 + m + a_mc_val)
        if divisor == 0: return Decimal(0)
        return me_val / divisor

    def cimentosP(self, ccimentos_val, percentual_cimento): 
        return ccimentos_val * percentual_cimento

# ==============================================================================
# MÓDULO 2: FASE ENDURECIDA (CÁLCULO FCJ e IE)
# ==============================================================================

@dataclass
class dadosresistencia:
    cargat: float
    tipocp: str
    idade: int
    idaderef: int
    cpref: str
    m: int

class CalcResistencia:
    def calc_resistencia(self, dados: dadosresistencia) -> float:
        """ Calcula o Fcj baseado na carga e no tipo de CP (Tradução do PROCV interno). """
       
        tabela_fatores = {
            "10x20 axial": 1.2487,
            "10x20": 0.3183,
            "10x10x40 flexao": 0.0981
        }
        
        fator = tabela_fatores.get(dados.tipocp, 0.0)
        
        fcj = dados.cargat * fator
        return fcj

    def calcular_indice_eficiencia(self, dados: dadosresistencia, fcj: float) -> float:
        """
        Tradução da fórmula de Excel: IE = Traço m / Fcj (MPa) com condicionais.
        """
        
      
        
        
        # 3. O Numerador é o próprio Traço m (dados.m)
        fator_m = dados.m # O fator m é o valor do traço m
        
        # 4. Divisão final: (Traço m) / Fcj
        return fator_m / fcj

# ==============================================================================
# MÓDULO 3 & 4: MATRICIAL E CURVA
# ==============================================================================
@dataclass
class CoeficientesDet:
    deter7: float = 0.0
    deter6: float = 0.0
    deter5: float = 0.0
    deter4: float = 0.0
    deter3: float = 0.0
    deter2: float = 0.0
    deter1: float = 0.0

class CalculadoraUniversal:
    def gerar_tabela_curva(self, c: CoeficientesDet, m_start: float, m_end: float, num_pontos: int = 51) -> List[Dict]:
        pontos = []
        array_input = np.linspace(m_start, m_end, num_pontos)
        for val_input in array_input:
            val_output = (
                c.deter7 * (val_input ** 6) + 
                c.deter6 * (val_input ** 5) + 
                c.deter5 * (val_input ** 4) + 
                c.deter4 * (val_input ** 3) + 
                c.deter3 * (val_input ** 2) + 
                c.deter2 * (val_input ** 1) + 
                c.deter1
            )
            pontos.append({ "x_calculado": val_input, "y_calculado": val_output })
        return pontos

# ==============================================================================
# PIPELINE CENTRAL
# ==============================================================================
def executar_pipeline_completo(df_input_site, config_globais, tipo_grafico):
    
    calc_fase1 = CalcFasePlastica()
    calc_fase2 = CalcResistencia()
    
    resultados_brutos = []

    for _, row in df_input_site.iterrows():
        try:
            # --- FASE 1: DADOS E CÁLCULOS BÁSICOS ---
            res_manual = float(row.get('resistencia', 0.0))
            
            dados_f1 = IPFasePlastica(
                m=int(row['m']),
                agua=Decimal(str(row['agua'])),
                slump=int(row['slump']),
                peso=Decimal(str(row['peso'])),
                volume=Decimal(str(config_globais['volume'])),
                tara=Decimal(str(config_globais['tara'])),
                inicial_agregados=Decimal(str(config_globais['agregados'])),
                alpha=Decimal(str(row['alpha']))/100,
                percentual_cimento=Decimal(str(config_globais['pct_cimento']))/100
            )
            res_f1 = calc_fase1.calcular_tudo(dados_f1)
            item = {k: float(v) if isinstance(v, Decimal) else v for k, v in res_f1.items()}
            
            # --- FASE 2: RESISTÊNCIA E EFICIÊNCIA ---
            dados_f2 = dadosresistencia(
                cargat=float(row.get('Carga', res_manual)), 
                tipocp=str(row.get('Tipo CP', '10x20')),
                idade=int(row.get('Idade', 28)),
                idaderef=int(config_globais.get('Idade Ref', 28)),    
                cpref=str(config_globais.get('Tipo CP Ref', '10x20')), 
                m=int(row['m'])
            )
            
            fcj_calculado = calc_fase2.calc_resistencia(dados_f2)
            ie_calculado = calc_fase2.calcular_indice_eficiencia(dados_f2, fcj_calculado)
            
            # Salva Resultados
            item['fcj'] = fcj_calculado
            item['Eficiencia'] = ie_calculado

            resultados_brutos.append(item)

        except Exception as e:
            continue

    # --- 4. PREPARA GRÁFICO ---
    eixo_x, eixo_y = [], []
    
    if tipo_grafico == "m/a/c":
        eixo_x = [r['m'] for r in resultados_brutos]
        eixo_y = [r['A/MC'] for r in resultados_brutos]
    elif tipo_grafico == "resistencia/ac":
        eixo_x = [r['A/MC'] for r in resultados_brutos]
        eixo_y = [r['fcj'] for r in resultados_brutos] 
    elif tipo_grafico == "a/c/resistencia":
        eixo_x = [r['fcj'] for r in resultados_brutos]
        eixo_y = [r['A/MC'] for r in resultados_brutos]
    elif tipo_grafico == "m/consumo":
        eixo_x = [r['m'] for r in resultados_brutos]
        eixo_y = [r['Cimentos'] for r in resultados_brutos]
    elif tipo_grafico == "m/indide de eficiencia":
        eixo_x = [r['m'] for r in resultados_brutos]
        eixo_y = [r['Eficiencia'] for r in resultados_brutos]

    dados_curva = []
    if len(eixo_x) >= 3:
        try:
            coeffs = np.polyfit(eixo_x, eixo_y, deg=6)
            meus_coefs = CoeficientesDet(coeffs[0], coeffs[1], coeffs[2], coeffs[3], coeffs[4], coeffs[5], coeffs[6])
            calc_univ = CalculadoraUniversal()
            dados_curva = calc_univ.gerar_tabela_curva(meus_coefs, min(eixo_x), max(eixo_x), 51)
        except: pass

    return resultados_brutos, dados_curva, tipo_grafico