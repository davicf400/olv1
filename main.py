import pandas as pd
import os
import shutil
import numpy as np
from fastapi import FastAPI, UploadFile, File
from leitor import registro
from cerebro import CalculoFasePlastica, InterpoladorCramer
from relatorio import GeradorRelatorio
from odooconectar import OdooConnector


app = FastAPI(title="Motor de Dosagem VMIX API", version="1.0")


def executar_motor_matematico(dados_json):
    print("\n" + "="*80)
    print(" INICIANDO MOTOR MATEMÁTICO ".center(80, "="))
    
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

    if len(pontos_x) >= 2:
        x_ord, y_ord = zip(*sorted(zip(pontos_x, pontos_y)))
        solver = InterpoladorCramer(x_ord, y_ord)
        coefs = solver.resolver_coeficientes()
        
        df_validacao = solver.gerar_validacao()
        df_curva = solver.gerar_curva(51) 

   
        print(" ENVIANDO DADOS PARA O ERP... ")
      
        coefs_limpos = {k: f"{float(v):.14f}" for k, v in coefs.items()} 
        odoo = OdooConnector()
        id_os = odoo.salvar_dosagem(dados_json, coefs_limpos)

        # PDF
       # PDF
        print(" GERANDO PDF COM DUMP TOTAL... ")
        gerador = GeradorRelatorio(dados_json)
        gerador.gerar_grafico(df_curva, x_ord, y_ord)
        
        
        gerador.gerar_pdf(df_validacao, df_curva, coefs, determinantes=solver.determinantes, matriz=solver.matriz_principal)

        if os.path.exists("temp_grafico_dosagem.png"):
            os.remove("temp_grafico_dosagem.png")
            
        return {"status": "sucesso", "odoo_id": id_os, "mensagem": "OS criada e calculada com sucesso!"}
    else:
        return {"status": "erro", "mensagem": "Pontos insuficientes. Mínimo 2 traços."}

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
    """
    Rota para quando o consultor preencher a OS no Odoo. 
    Recebe o JSON direto e pula a leitura de Excel.
    """

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