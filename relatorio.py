import matplotlib.pyplot as plt
from fpdf import FPDF
from fpdf.fonts import FontFace
import os
from datetime import datetime

class PDFRelatorio(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(150)
        self.cell(0, 10, "Relatório Analítico Multi-Variáveis - Dosagem Experimental", align="R", new_x="LMARGIN", new_y="NEXT")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(128)
        self.cell(0, 10, f'Página {self.page_no()}', align="C")

class GeradorRelatorio:
    def __init__(self, dados_json):
        self.dados = dados_json
        self.cliente = dados_json['cliente_info'].get('nome', 'Desconhecido')
        
    def gerar_grafico(self, df_curva, x_real, y_real, titulo, nome_x, nome_y, filename):
        plt.style.use('bmh')
        fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
        
        x_plot = df_curva[f'{nome_x} (Interpolado)'].astype(float)
        y_plot = df_curva[f'{nome_y} (Curva)'].astype(float)

        ax.fill_between(x_plot, y_plot, color='#005293', alpha=0.1)
        ax.plot(x_plot, y_plot, label='Curva (Projetada)', color='#005293', linewidth=2.5)
        ax.scatter(x_real, y_real, color='#ff7f0e', edgecolor='#c55a11', s=100, label='Dados Reais', zorder=5, marker='o')
        
        ax.set_title(titulo, fontsize=14, fontweight='bold', color='#333')
        ax.set_xlabel(nome_x, fontsize=11, fontweight='bold')
        ax.set_ylabel(nome_y, fontsize=11, fontweight='bold')
        ax.legend(loc='upper right', frameon=True, shadow=True, facecolor='white')
        ax.grid(True, linestyle='--', alpha=0.6)
        
        plt.tight_layout()
        plt.savefig(filename)
        plt.close()

    def _imprimir_matriz(self, pdf, titulo, matriz):
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 6, titulo, new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Courier", "", 6.5) 
        if matriz is not None:
            matriz_str = ""
            for linha in matriz:
                matriz_str += "  ".join([f"{val:>14.6e}" for val in linha]) + "\n"
            pdf.multi_cell(0, 3.5, matriz_str, border=1)
        else:
            pdf.cell(0, 5, "Matriz não fornecida.")
        pdf.ln(3)

    def gerar_pdf(self, lista_resultados):
        pdf = PDFRelatorio()
        pdf.add_page()
        
        # --- 1. CABEÇALHO E DADOS GERAIS ---
        pdf.set_font("Helvetica", "B", 16)
        pdf.set_text_color(0)
        pdf.cell(0, 10, f"DUMP MASSIVO DE DADOS: {str(self.cliente).upper()}", new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.ln(5)

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

        # --- 2. FASE PLÁSTICA E DADOS BRUTOS ---
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "2. Traços Experimentais Brutos", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 7)
        tracos = self.dados['dados_fase_plastica']
        if tracos:
            colunas = list(tracos[0].keys())
            with pdf.table() as table:
                row = table.row()
                for col in colunas:
                    row.cell(col.upper().replace('_', ' '), style=FontFace(emphasis="BOLD"))
                for traco in tracos:
                    row = table.row()
                    for col in colunas:
                        val = traco.get(col, "-")
                        # Se for float, a gente arredonda só na tabela geral pra não poluir
                        if isinstance(val, float):
                            row.cell(f"{val:.4f}")
                        else:
                            row.cell(str(val))

        # --- 3. LOOP PELAS ANÁLISES ---
        for idx, res in enumerate(lista_resultados):
            pdf.add_page() 
            pdf.set_font("Helvetica", "B", 15)
            pdf.set_fill_color(200, 220, 255) 
            pdf.cell(0, 10, f"ESTUDO {idx+1} DE {len(lista_resultados)}: {res['titulo'].upper()}", border=1, fill=True, new_x="LMARGIN", new_y="NEXT", align="C")
            pdf.ln(5)

            # MATRIZ PRINCIPAL E AUXILIARES
            self._imprimir_matriz(pdf, "Matriz Principal (Vandermonde)", res['matriz'])

            if 'matrizes_auxiliares' in res and res['matrizes_auxiliares']:
                pdf.set_font("Helvetica", "B", 10)
                pdf.cell(0, 6, "Matrizes Auxiliares (Regra de Cramer)", new_x="LMARGIN", new_y="NEXT")
                pdf.ln(1)
                for i in range(1, 8):
                    chave = f'M_col_{i}'
                    matriz_aux = res['matrizes_auxiliares'].get(chave)
                    self._imprimir_matriz(pdf, f"Matriz Auxiliar {i} (Coluna {i} substituída)", matriz_aux)
                    if pdf.get_y() > 250:
                        pdf.add_page()

            # DETERMINANTES (AGORA EM NOTAÇÃO CIENTÍFICA!)
            pdf.add_page() 
            pdf.set_font("Helvetica", "B", 12)
            pdf.cell(0, 8, "Determinantes Calculados (14 Casas de Precisão)", new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", 8)
            with pdf.table(col_widths=(40, 120)) as table:
                row = table.row()
                row.cell("Vetor", style=FontFace(emphasis="BOLD"))
                row.cell("Valor Calculado", style=FontFace(emphasis="BOLD"))
                
                row = table.row()
                row.cell("D_principal")
                # A mágica do '.14e' revela o número real sem estourar zeros
                row.cell(f"{float(res['determinantes']['D_principal']):.14e}") 
                
                for i in range(1, 8):
                    chave = f'D_col_{i}'
                    val = res['determinantes'].get(chave, 0)
                    row = table.row()
                    row.cell(chave)
                    row.cell(f"{float(val):.14e}")
            pdf.ln(5)

            # EQUAÇÃO (AGORA EM NOTAÇÃO CIENTÍFICA!)
            pdf.set_font("Helvetica", "B", 12)
            pdf.cell(0, 8, "Equação Polinomial Resultante", new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Courier", "", 8)
            partes_eq = []
            for grau in range(6, -1, -1):
                key = f'a{grau}'
                val = float(res['coeficientes'].get(key, 0))
                # Formatação .14e para os coeficientes aparecerem bonitos como no Excel
                partes_eq.append(f"({val:.14e}*x^{grau})")
            pdf.multi_cell(0, 5, "Y = \n" + " + \n".join(partes_eq), border=1)
            pdf.ln(5)

            # VALIDAÇÃO
            pdf.set_font("Helvetica", "B", 12)
            pdf.cell(0, 8, "Validação do Modelo (Real vs Calculado)", new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", 8)
            with pdf.table() as table:
                row = table.row()
                for col in res['df_validacao'].columns:
                    row.cell(col, style=FontFace(emphasis="BOLD"))
                for _, data_row in res['df_validacao'].iterrows():
                    row = table.row()
                    for item in data_row:
                        row.cell(str(item))

            # TABELA 51 PONTOS
            pdf.add_page()
            pdf.set_font("Helvetica", "B", 12)
            pdf.cell(0, 8, f"Projeção Numérica (51 Pontos) - {res['titulo']}", new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", 7)
            with pdf.table(col_widths=(80, 80)) as table:
                row = table.row()
                for col in res['df_curva'].columns:
                    row.cell(col, style=FontFace(emphasis="BOLD", fill_color=(230, 230, 230)))
                for _, data_row in res['df_curva'].iterrows():
                    row = table.row()
                    for item in data_row:
                        row.cell(str(item))
            
            # GRÁFICO
            filename = f"temp_grafico_{idx}.png"
            self.gerar_grafico(res['df_curva'], res['pontos_reais_x'], res['pontos_reais_y'], res['titulo'], res['nome_x'], res['nome_y'], filename)
            
            pdf.add_page()
            pdf.set_font("Helvetica", "B", 12)
            pdf.cell(0, 8, f"Representação Gráfica - {res['titulo']}", new_x="LMARGIN", new_y="NEXT")
            if os.path.exists(filename):
                pdf.image(filename, x=15, w=180)
                os.remove(filename)

        # SALVAMENTO
        nome_arquivo = "OS_VMIX_CONCRETO_LTDA_COMPLETO.pdf"
        pdf.output(nome_arquivo)
        print(f"[PDF] DUMP MASSIVO GERADO COM SUCESSO: {nome_arquivo}")