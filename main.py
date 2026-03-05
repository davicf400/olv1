import os
import shutil
from fastapi import FastAPI, UploadFile, File
from leitor import registro
from cerebro import CalculoFasePlastica, InterpoladorCramer
from relatorio import GeradorRelatorio
# from odooconectar import OdooConnector

app = FastAPI(title="Motor de Dosagem VMIX API", version="1.2")

def executar_motor_matematico(dados_json):
    print("\n" + "="*80)
    print(" INICIANDO MOTOR MATEMÁTICO (MÚLTIPLAS ANÁLISES) ".center(80, "="))
    
    inicial_agregados = dados_json['parametros_gerais']['inicial_agregados']
    lista_tracos = dados_json['dados_fase_plastica']
    calculadora = CalculoFasePlastica()
    
  
    eixo_ac, eixo_m, eixo_res, eixo_ind, eixo_cons = [], [], [], [], []

    for traco in lista_tracos:
        m = traco['m']
        alpha = traco['alpha']
        agua = traco['agua']
        consumo = traco.get('consumo_estimado', 0)
        res = traco.get('resistencia', 0)

        
        ac = float(calculadora.aMC(agua, m, inicial_agregados, alpha))
        
       
        if res > 0:
          
            ind = float(calculadora.indice_eficiencia(consumo, res))
            
            eixo_ac.append(ac)
            eixo_m.append(m)
            eixo_res.append(res)
            eixo_ind.append(ind)
            eixo_cons.append(consumo)

    resultados_finais = []

    
    if len(eixo_ac) >= 2:
        
       
        analises_solicitadas = [
            {"nome_x": "a/c", "nome_y": "m", "dados_x": eixo_ac, "dados_y": eixo_m},
            {"nome_x": "a/c", "nome_y": "Resistência", "dados_x": eixo_ac, "dados_y": eixo_res},
            {"nome_x": "m", "nome_y": "Consumo", "dados_x": eixo_m, "dados_y": eixo_cons},
            {"nome_x": "m", "nome_y": "Índice de Eficiência", "dados_x": eixo_m, "dados_y": eixo_ind},
            {"nome_x": "Resistência", "nome_y": "a/c", "dados_x": eixo_res, "dados_y": eixo_ac}
        ]

     
        for analise in analises_solicitadas:
            solver = InterpoladorCramer(
                dados_x=analise["dados_x"], 
                dados_y=analise["dados_y"], 
                nome_x=analise["nome_x"], 
                nome_y=analise["nome_y"]
            )
            
         
            resultados_finais.append({
                "titulo": f'{analise["nome_x"]} x {analise["nome_y"]}',
                "coeficientes": solver.resolver_coeficientes(),
                "determinantes": solver.determinantes,
                "matriz": solver.matriz_principal,
                "matrizes_auxiliares": solver.matrizes_auxiliares,
                "df_validacao": solver.gerar_validacao(),
                "df_curva": solver.gerar_curva(51),
                "pontos_reais_x": solver.x,
                "pontos_reais_y": solver.y,
                "nome_x": analise["nome_x"],
                "nome_y": analise["nome_y"]
            })

        print(f"\n>>> SUCESSO! {len(resultados_finais)} MOTORES MATEMÁTICOS EXECUTADOS! <<<")
        for res in resultados_finais:
            print(f" - Calculado: {res['titulo']}")

    
        print("\n GERANDO PDF MASSIVO COM TODAS AS MATRIZES E GRÁFICOS... ")
        gerador = GeradorRelatorio(dados_json)
        gerador.gerar_pdf(resultados_finais)
        

        return {
            "status": "sucesso", 
            "mensagem": f"Foram geradas {len(resultados_finais)} matrizes de cruzamento com sucesso!",
            "qtd_analises": len(resultados_finais)
        }
    else:
        return {"status": "erro", "mensagem": "Pontos insuficientes. Mínimo 2 traços com resistência a 28 dias."}

@app.post("/upload-planilha")
async def processar_via_planilha(arquivo: UploadFile = File(...)):
    nome_temp = 'Estudos de Dosagem de Concreto 2025.xlsx'
    with open(nome_temp, "wb") as buffer:
        shutil.copyfileobj(arquivo.file, buffer)
    
    dados_json = registro()
    resultado = executar_motor_matematico(dados_json)
    
    if os.path.exists(nome_temp):
        os.remove(nome_temp)
        
    return resultado

@app.post("/novo-formulario")
async def processar_via_formulario(dados_do_form: dict):
    resultado = executar_motor_matematico(dados_do_form)
    return resultado

# ==============================================================================
# EXECUÇÃO DIRETA (TESTE LOCAL SEM SERVIDOR)
# ==============================================================================
if __name__ == "__main__":
    print(">>> Iniciando Teste Local (Sem FastAPI) <<<")
    
    dados_extraidos = registro()
    
    if dados_extraidos:
        resultado = executar_motor_matematico(dados_extraidos)
        print("\nResumo da Execução:", resultado)
    else:
        print("Erro: Não foi possível extrair os dados da planilha.")