import matplotlib.pyplot as plt
from fpdf import FPDF
from fpdf.fonts import FontFace
import os
from datetime import datetime

class PDFRelatorio(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(150)
        self.cell(0, 10, "Relatório Técnico de Dosagem Experimental", align="R", new_x="LMARGIN", new_y="NEXT")
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

    def _estilizar_grafico(self):
        try:
            plt.style.use('seaborn-v0_8-whitegrid')
        except:
            plt.style.use('ggplot')
        plt.rcParams.update({'font.size': 9, 'figure.titlesize': 14})

    def gerar_grafico(self, df_curva, x_real, y_real):
        self._estilizar_grafico()
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(df_curva['a/c (Interpolado)'], df_curva['m (Curva)'], 
                label='Curva Interpolada', color='#1f77b4', linewidth=2)
        ax.scatter(x_real, y_real, color='#d62728', edgecolor='white', s=80, 
                   label='Dados Experimentais', zorder=5)
        ax.set_title(f"Curva de Abrams Inversa: {self.cliente}")
        ax.set_xlabel("Relação Água/Cimento (a/c)")
        ax.set_ylabel("Traço (m)")
        ax.legend()
        ax.grid(True, linestyle='--', alpha=0.5)
        plt.tight_layout()
        plt.savefig(self.caminho_grafico, dpi=300)
        plt.close()

    def gerar_pdf(self, df_validacao, coeficientes, determinantes=None):
        pdf = PDFRelatorio()
        pdf.add_page()
        
        # 1. CABEÇALHO
        pdf.set_font("Helvetica", "B", 16)
        pdf.set_text_color(0)
        pdf.cell(0, 10, f"ESTUDO: {str(self.cliente).upper()}", new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.ln(5)

        # 2. DADOS GERAIS
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "1. Dados do Projeto", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 10)
        
        dados_gerais = [
            ("Cliente:", self.dados['cliente_info']['nome']),
            ("Obra:", self.dados['cliente_info']['obra']),
            ("Data:", datetime.now().strftime("%d/%m/%Y")),
            ("Slump Meta:", str(self.dados['parametros_gerais']['slump_meta']))
        ]
        with pdf.table(col_widths=(40, 100)) as table:
            for label, valor in dados_gerais:
                row = table.row()
                row.cell(label, style=FontFace(emphasis="BOLD"))
                row.cell(str(valor))
        pdf.ln(5)

        # 3. DADOS FASE PLÁSTICA
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "2. Traços Experimentais", new_x="LMARGIN", new_y="NEXT")
        tracos = self.dados['dados_fase_plastica']
        if tracos:
            colunas = list(tracos[0].keys())
            with pdf.table() as table:
                row = table.row()
                for col in colunas:
                    row.cell(col.replace('_', ' ').title(), style=FontFace(emphasis="BOLD"))
                for traco in tracos:
                    row = table.row()
                    for col in colunas:
                        val = traco.get(col, "-")
                        row.cell(f"{val:.3f}" if isinstance(val, float) else str(val))
        pdf.ln(5)

        # 4. RESULTADOS MATRICIAIS (DETERMINANTES)
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "3. Resultados da Análise Matricial (Cramer)", new_x="LMARGIN", new_y="NEXT")
        
        if determinantes:
            with pdf.table(col_widths=(60, 60)) as table:
                row = table.row()
                row.cell("Determinante", style=FontFace(emphasis="BOLD"))
                row.cell("Valor Calculado", style=FontFace(emphasis="BOLD"))
                
                for key, val in determinantes.items():
                    row = table.row()
                    row.cell(key)
                    row.cell(f"{val:.5e}")
        else:
             pdf.cell(0, 10, "Determinantes não calculados.")
        pdf.ln(5)

        # 5. EQUAÇÃO
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "4. Equação Final", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Courier", "", 9)
        partes_eq = []
        for grau in range(6, -1, -1):
            key = f'a{grau}'
            val = coeficientes.get(key, 0)
            partes_eq.append(f"({val:.5f}*x^{grau})")
        pdf.multi_cell(0, 5, "Y(m) = " + " + ".join(partes_eq), border=1)
        pdf.ln(5)

        # 6. VALIDAÇÃO
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "5. Validação do Modelo", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 9)
        with pdf.table() as table:
            row = table.row()
            for col in df_validacao.columns:
                row.cell(col, style=FontFace(emphasis="BOLD"))
            for _, data_row in df_validacao.iterrows():
                row = table.row()
                for item in data_row:
                    row.cell(f"{item:.4f}" if isinstance(item, float) else str(item))

        # 7. GRÁFICO
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "6. Gráfico da Curva", new_x="LMARGIN", new_y="NEXT")
        if os.path.exists(self.caminho_grafico):
            pdf.image(self.caminho_grafico, x=15, w=180)

        nome_arquivo = f"OS_{str(self.cliente).replace(' ', '_')}.pdf"
        pdf.output(nome_arquivo)
        print(f"[PDF] Relatório gerado com sucesso: {nome_arquivo}")