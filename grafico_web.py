#
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class DashboardInterativo:
    def __init__(self, cliente_nome):
        self.cliente = cliente_nome

    def gerar_html(self, lista_resultados, nome_arquivo="dashboard_interativo.html"):
    
        fig = make_subplots(
            rows=len(lista_resultados), cols=1, 
            subplot_titles=[f"<b>{res['titulo']}</b> (R² = {res.get('r2', 1.0):.6f})" for res in lista_resultados],
            vertical_spacing=0.05
        )

        for i, res in enumerate(lista_resultados, 1):
            df_curva = res['df_curva']
            x_curva = df_curva[f"{res['nome_x']} (Interpolado)"].astype(float)
            y_curva = df_curva[f"{res['nome_y']} (Curva)"].astype(float)

           
            fig.add_trace(
                go.Scatter(
                    x=x_curva, y=y_curva, 
                    mode='lines', 
                    name=f'Curva Projetada', 
                    line=dict(color='#005293', width=3),
                    hovertemplate=f"{res['nome_x']}: %{{x:.4f}}<br>{res['nome_y']}: %{{y:.4f}}<extra></extra>"
                ), row=i, col=1
            )

         
            fig.add_trace(
                go.Scatter(
                    x=res['pontos_reais_x'], y=res['pontos_reais_y'], 
                    mode='markers', 
                    name='Dados Reais', 
                    marker=dict(color='#ff7f0e', size=12, line=dict(color='white', width=2)),
                    hovertemplate=f"<b>PONTO REAL</b><br>{res['nome_x']}: %{{x:.4f}}<br>{res['nome_y']}: %{{y:.4f}}<extra></extra>"
                ), row=i, col=1
            )

        
            fig.update_xaxes(title_text=res['nome_x'], row=i, col=1, showgrid=True, gridwidth=1, gridcolor='LightGray')
            fig.update_yaxes(title_text=res['nome_y'], row=i, col=1, showgrid=True, gridwidth=1, gridcolor='LightGray')

       
        fig.update_layout(
            height=450 * len(lista_resultados), 
            title_text=f"📊 Painel Interativo de Dosagem: {str(self.cliente).upper()}",
            title_font_size=24,
            title_x=0.5,
            template="plotly_white", 
            hovermode="x unified",   
            showlegend=False
        )

      
        fig.write_html(nome_arquivo, include_plotlyjs="cdn")
        print(f"[PLOTLY] Dashboard HTML interativo gerado: {nome_arquivo}")
        return nome_arquivo

#