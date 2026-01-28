# 🚀 Release Notes v1.0.0: Sistema de Dosagem e Interpolação de Concreto

**Data:** 28 de Janeiro de 2026
**Status:** Versão Estável (v1.0)

## 📝 Visão Geral
Esta é a primeira versão estável do sistema automatizado para cálculo de dosagem de concreto. O software elimina o erro humano e a dependência de planilhas manuais complexas, integrando extração de dados brutos, cálculo de precisão (Fase Plástica) e modelagem matemática avançada (Interpolação Polinomial via Regra de Cramer) para gerar curvas de dosagem (Abrams Inversa).

---

## 🏗 Arquitetura do Sistema

O projeto foi reestruturado seguindo o padrão de **Separação de Responsabilidades (SoC)**, dividido em três módulos principais:

### 1. 🔍 O Leitor (Data Extraction Layer)
Responsável por transformar planilhas Excel desestruturadas em dados computáveis.
* **Busca Robusta:** Implementação do algoritmo `buscar_valor_no_df`, que localiza rótulos (labels) dinamicamente na planilha e captura valores adjacentes, tornando o sistema resiliente a pequenas mudanças de layout no Excel.
* **Parser Inteligente:** Extrai automaticamente informações do Cliente, Parâmetros da Obra e a tabela de Traços da Fase Plástica.
* **Output:** Gera um JSON estruturado e limpo, pronto para consumo matemático.

### 2. 🧠 O Cérebro (Core Logic Layer)
O núcleo matemático do sistema, desenvolvido com Orientação a Objetos (POO) e tipagem rigorosa.
* **Alta Precisão:** Utilização da biblioteca `Decimal` para cálculos da Fase Plástica (Britas, Cimento, a/c), eliminando erros de ponto flutuante comuns em dosagens finas.
* **Matemática Matricial:** Implementação "from scratch" da **Matriz de Vandermonde** e resolução de sistemas lineares via **Regra de Cramer**.
* **Polinômio de Grau 6:** Gera coeficientes ($a_6 \dots a_0$) para modelar o comportamento não-linear da relação Água/Cimento vs. Traço $m$.
* **Validação Automática:** Compara os valores reais ($y$) com os calculados ($y_{calc}$) para garantir a aderência da curva (R² virtualmente igual a 1).

### 3. 🔄 O Fluxo (Pipeline Integration)
O orquestrador (`main.py`) que conecta o Leitor ao Cérebro.
1. **Ingestão:** Carrega o Excel e converte para dicionários Python.
2. **Processamento:** Calcula o fator a/c real para cada traço experimental.
3. **Modelagem:** Alimenta o Interpolador Matricial com os pares $(x, y)$.
4. **Reporting:** Exibe no terminal a "Caixa Preta" aberta:
    * JSON completo dos dados extraídos.
    * Matriz de Vandermonde visualizada.
    * Determinantes individuais (Principal e Colunas).
    * Equação final da curva.
    * Tabela de validação e interpolação (50 pontos).

---

## ✨ Funcionalidades Principais (Changelog)

* [x] **Leitura de Excel:** Suporte a arquivos `.xlsx` com tratamento de células vazias e formatação inconsistente.
* [x] **Cálculo de a/c:** Conversão automática de dados de insumos (água, alpha, m) para a relação água/cimento precisa.
* [x] **Engine Matricial:** Resolução de determinantes utilizando `numpy.linalg` com visualização formatada em notação científica.
* [x] **Curva de Dosagem:** Geração automática de 50 pontos equidistantes para plotagem de gráficos suaves.
* [x] **Logs Detalhados:** O sistema imprime o passo a passo matricial para auditoria dos cálculos.

---

## 🛠 Tecnologias Utilizadas
* **Linguagem:** Python 3.14+
* **Manipulação de Dados:** Pandas & NumPy
* **Matemática:** Decimal (Standard Lib) & Linear Algebra (NumPy)
* **Estrutura:** JSON & Dataclasses

---

## ▶️ Como Rodar
Certifique-se de ter o arquivo `Estudos de Dosagem de Concreto 2025.xlsx` na raiz do projeto.

```bash
# Instalar dependências
pip install pandas numpy openpyxl

# Executar o fluxo completo
python main.py