import pandas as pd
import json
# Importando as ferramentas que criamos nos outros arquivos
from leitor import registro
from cerebro import CalculoFasePlastica, InterpoladorCramer

# ==============================================================================
# ORQUESTRADOR PRINCIPAL
# ==============================================================================

def processar_dosagem_completa():
    print("\n" + "="*80)
    print(" SISTEMA DE DOSAGEM - INICIANDO ".center(80, "="))
    print("="*80)
    
    # 1. Chama o Leitor
    dados_json = registro()
    if not dados_json: return

    print(f"\n[CLIENTE] {dados_json['cliente_info']['nome']}")
    print(f"[OBRA]    {dados_json['cliente_info']['obra']}")

    # 2. Prepara os dados
    inicial_agregados = dados_json['parametros_gerais']['inicial_agregados']
    lista_tracos = dados_json['dados_fase_plastica']
    
    calculadora = CalculoFasePlastica()
    pontos_x = [] # a/c
    pontos_y = [] # m

    # 3. Executa cálculos da Fase Plástica
    print("\n--- [CÁLCULO] Conversão Fase Plástica ---")
    for traco in lista_tracos:
        m = traco['m']
        alpha = traco['alpha']
        agua = traco['agua']
        
        ac = float(calculadora.aMC(agua, m, inicial_agregados, alpha))
        print(f"Traço m={m:<5} | Água={agua:<5} => a/c: {ac:.6f}")
        
        pontos_x.append(ac)
        pontos_y.append(m)

    # 4. Executa o Interpolador Matricial
    if len(pontos_x) >= 2:
        print("\n" + "="*80)
        print(" GERAÇÃO DE CURVAS MATEMÁTICAS ".center(80, "="))
        print("="*80)

        # Ordena para o gráfico/matriz
        pontos_ordenados = sorted(zip(pontos_x, pontos_y))
        x_ord, y_ord = zip(*pontos_ordenados)

        solver = InterpoladorCramer(x_ord, y_ord)
        coefs = solver.resolver_coeficientes()
        
        # --- EXIBIÇÃO DETALHADA ---
        
        print("\n--- A. Matriz de Vandermonde ---")
        df_matriz = pd.DataFrame(solver.matriz_principal, 
                                 columns=[f"x^{i}" for i in range(6, -1, -1)])
        print(df_matriz.to_string(index=False, float_format="%.4f"))

        print("\n--- B. Determinantes ---")
        df_dets = pd.DataFrame([solver.determinantes])
        print(df_dets.T.rename(columns={0: 'Valor'}).to_string(float_format="%.4e"))

        print("\n--- C. Equação Final ---")
        for k, v in coefs.items():
            print(f"{k} = {v:.15f}")

        print("\n--- D. Validação ---")
        print(solver.gerar_validacao().to_string(index=False, float_format="%.6f"))

        print("\n--- E. Curva Interpolada (50 pts) ---")
        df_curva = solver.gerar_curva(50)
        print(df_curva.head().to_string(index=False, float_format="%.6f"))
        print("...")

    else:
        print("\n[ERRO] Pontos insuficientes para cálculo matricial.")

if __name__ == "__main__":
    processar_dosagem_completa()