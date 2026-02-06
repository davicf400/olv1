import pandas as pd
import os
from leitor import registro
from cerebro import CalculoFasePlastica, InterpoladorCramer
from relatorio import GeradorRelatorio

def processar_dosagem_completa():
    print("\n" + "="*80)
    print(" SISTEMA DE DOSAGEM INTELIGENTE v1.0 ".center(80, "="))
    print("="*80)
    
    # 1. Leitura
    dados_json = registro()
    if not dados_json: return

   

    # 2. Cálculo
    inicial_agregados = dados_json['parametros_gerais']['inicial_agregados']
    lista_tracos = dados_json['dados_fase_plastica']
    calculadora = CalculoFasePlastica()
    pontos_x = [] 
    pontos_y = []

    
    for traco in lista_tracos:
        m = traco['m']
        alpha = traco['alpha']
        agua = traco['agua']
        ac = float(calculadora.aMC(agua, m, inicial_agregados, alpha))
        
       
        pontos_x.append(ac)
        pontos_y.append(m)

    # 3. Matemática
    if len(pontos_x) >= 2:
        x_ord, y_ord = zip(*sorted(zip(pontos_x, pontos_y)))
        solver = InterpoladorCramer(x_ord, y_ord)
        coefs = solver.resolver_coeficientes()
        
        # Gera dados
        df_validacao = solver.gerar_validacao()
        df_curva = solver.gerar_curva(100)

        # 4. Geração do PDF
        print("\n" + "="*80)
        print(" GERAÇÃO DE RELATÓRIO PDF ".center(80, "="))
        print("="*80)
        
        gerador = GeradorRelatorio(dados_json)
        
        gerador.gerar_grafico(df_curva, x_ord, y_ord)
        
        gerador.gerar_pdf(
            df_validacao, 
            coefs, 
            determinantes=solver.determinantes
        )

        if os.path.exists("temp_grafico_dosagem.png"):
            os.remove("temp_grafico_dosagem.png")
            print("[SISTEMA] Limpeza concluída.")
            
    else:
        print("\n[ERRO] Pontos insuficientes.")

if __name__ == "__main__":
    processar_dosagem_completa()