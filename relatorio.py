import matplotlib.pyplot as plt
from fpdf import FPDF
from fpdf.fonts import FontFace
import os
from datetime import datetime

class PDFRelatorio(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(150)
        self.cell(0, 10, "Relatório Analítico Completo - Dosagem Experimental", align="R", new_x="LMARGIN", new_y="NEXT")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(128)
        self.cell(0, 10, f'Página {self.page_no()}', align="C")

class GeradorRelatorio:
    def __init__(self, dados_json):
        self.dados = dados_json
        self.cliente = dados_json['cliente_info']['nome']
        self.caminho_grafico = "temp_grafico_dosagem.png"

    def gerar_grafico(self, df_curva, x_real, y_real):
        # Mantendo o gráfico básico só para o código não quebrar, arrumamos ele na próxima fase!
        plt.style.use('bmh')
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(df_curva['a/c (Interpolado)'].astype(float), df_curva['m (Curva)'].astype(float), label='Curva')
        ax.scatter(x_real, y_real, color='red', label='Real', zorder=5)
        ax.legend()
        plt.tight_layout()
        plt.savefig(self.caminho_grafico)
        plt.close()

    def gerar_pdf(self, df_validacao, df_curva, coeficientes, determinantes=None, matriz=None):
        pdf = PDFRelatorio()
        pdf.add_page()
        
        # 1. CABEÇALHO
        pdf.set_font("Helvetica", "B", 14)
        pdf.set_text_color(0)
        pdf.cell(0, 10, f"DUMP DE DADOS: {str(self.cliente).upper()}", new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.ln(5)

        # 2. DADOS GERAIS 
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "1. Dados do Projeto (Extraídos)", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 9)
        
        info = self.dados['cliente_info']
        param = self.dados['parametros_gerais']
        dados_gerais = [
            ("Cliente:", info.get('nome', '')),
            ("Obra:", info.get('obra', '')),
            ("Local:", info.get('local', '')),
            ("Inicial Agregados:", str(param.get('inicial_agregados', ''))),
            ("Slump Meta:", str(param.get('slump_meta', '')))
        ]
        with pdf.table(col_widths=(40, 120)) as table:
            for label, valor in dados_gerais:
                row = table.row()
                row.cell(label, style=FontFace(emphasis="BOLD"))
                row.cell(str(valor))
        pdf.ln(5)

        # 3. DADOS FASE PLÁSTICA 
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "2. Traços Experimentais (Dados Brutos)", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 8)
        tracos = self.dados['dados_fase_plastica']
        if tracos:
            colunas = list(tracos[0].keys()) 
            with pdf.table() as table:
                row = table.row()
                for col in colunas:
                    row.cell(col.upper(), style=FontFace(emphasis="BOLD"))
                for traco in tracos:
                    row = table.row()
                    for col in colunas:
                        row.cell(str(traco.get(col, "-")))
        pdf.ln(5)

        # 4. MATRIZ PRINCIPAL 
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "3. Matriz Principal do Sistema (7x7)", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Courier", "", 6) 
        if matriz is not None:
            matriz_str = ""
            for linha in matriz:
             
                matriz_str += "  ".join([f"{val:>15.8e}" for val in linha]) + "\n"
            pdf.multi_cell(0, 4, matriz_str, border=1)
        else:
            pdf.cell(0, 5, "Matriz não fornecida.")
        pdf.ln(5)

        # 5. DETERMINANTES
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "4. Determinantes Calculados (14 Casas Decimais)", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 8)
        if determinantes:
            with pdf.table(col_widths=(60, 100)) as table:
                row = table.row()
                row.cell("Vetor", style=FontFace(emphasis="BOLD"))
                row.cell("Valor Calculado", style=FontFace(emphasis="BOLD"))
                for key, val in determinantes.items():
                    row = table.row()
                    row.cell(key)
                    row.cell(f"{float(val):.14f}")
        pdf.ln(5)

        # 6. EQUAÇÃO
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "5. Equação de Dosagem (14 Casas Decimais)", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Courier", "", 8)
        partes_eq = []
        for grau in range(6, -1, -1):
            key = f'a{grau}'
            val = float(coeficientes.get(key, 0))
            partes_eq.append(f"({val:.14f}*x^{grau})")
        pdf.multi_cell(0, 5, "Y(m) = \n" + " + \n".join(partes_eq), border=1)
        pdf.ln(5)

        # 7. VALIDAÇÃO
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "6. Validação do Modelo", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 8)
        with pdf.table() as table:
            row = table.row()
            for col in df_validacao.columns:
                row.cell(col, style=FontFace(emphasis="BOLD"))
            for _, data_row in df_validacao.iterrows():
                row = table.row()
                for item in data_row:
                    row.cell(str(item))
        
      
        pdf.add_page()

        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, f"7. Projeção Numérica ({len(df_curva)} Pontos Calculados)", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 7)
        with pdf.table(col_widths=(80, 80)) as table:
            row = table.row()
            for col in df_curva.columns:
                row.cell(col, style=FontFace(emphasis="BOLD", fill_color=(230, 230, 230)))
            for _, data_row in df_curva.iterrows():
                row = table.row()
                for item in data_row:
                    row.cell(str(item))
        pdf.ln(10)

        
        if os.path.exists(self.caminho_grafico):
          
            pdf.image(self.caminho_grafico, x=15, w=180)

        nome_arquivo = "OS_VMIX_CONCRETO_LTDA.pdf"
        pdf.output(nome_arquivo)
        print(f"[PDF] DUMP COMPLETO GERADO: {nome_arquivo}")