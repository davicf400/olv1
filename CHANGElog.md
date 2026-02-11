# 🚀 Release Notes v1.1.0: Relatórios Técnicos e Visualização Gráfica

**Data:** 11 de Fevereiro de 2026
**Status:** Versão Estável (v1.1)

## 📝 Visão Geral
A versão v1.1.0 eleva o nível do sistema, transformando-o de uma ferramenta de cálculo em terminal para um **Gerador de Documentação Técnica**. Agora, o sistema produz automaticamente um relatório PDF completo contendo os dados da obra, a curva de dosagem visual (gráfico) e a memória de cálculo detalhada (matrizes), facilitando a análise e o arquivamento dos estudos de dosagem.

---

## 🏗 Arquitetura do Sistema (Atualizada)

O sistema agora conta com **4 módulos principais**:

### 1. 🔍 O Leitor (Input)
* Mantida a robustez na leitura de arquivos `.xlsx` desestruturados.
* Otimização na captura de metadados do cliente para o cabeçalho dos relatórios.

### 2. 🧠 O Cérebro (Core Math)
* **Matriz de Vandermonde:** O algoritmo agora expõe a matriz gerada para fins de auditoria no relatório final.
* **Determinantes:** Cálculo explícito e exposição dos valores para validação da Regra de Cramer.

### 3. 📊 O Relator (Reporting Layer) **[NOVO]**
Módulo responsável pela materialização dos cálculos em documentos oficiais.
* **Geração de PDF:** Utiliza a biblioteca `fpdf2` para criar relatórios técnicos multipáginas.
* **Visualização de Dados:** Integração com `matplotlib` para plotar a Curva de Abrams Inversa (Gráfico $m$ vs $a/c$) com alta resolução (300 DPI).
* **Caixa Preta Aberta:** Uma seção exclusiva no PDF que imprime a Matriz 7x7 e os Determinantes, servindo como memória de cálculo auditável.
* **Design Técnico:** Tabelas formatadas com `FontFace` para destaque (Negrito) e layout profissional.

### 4. 🔄 O Fluxo (Orchestrator)
* O `main.py` agora gerencia o ciclo: `Leitura -> Cálculo -> Gráfico -> PDF`.
* Limpeza automática de arquivos temporários (imagens de gráficos) após a geração do documento.

---

## ✨ Changelog (Mudanças Recentes)

### 🌟 Funcionalidades (Features)
* [x] **Relatório PDF Completo:** O sistema agora entrega um arquivo `.pdf` pronto, salvo localmente com o nome da obra.
* [x] **Gráficos Automáticos:** A curva de interpolação é desenhada e inserida automaticamente no documento.
* [x] **Auditoria Matricial:** Inclusão dos dados brutos da álgebra linear (Vandermonde e Cramer) no corpo do relatório PDF.

### 🐛 Correções (Bug Fixes)
* [x] **FPDF FontFace:** Correção do erro `TypeError: Cannot combine FontFace with <class 'str'>` devido à atualização da biblioteca `fpdf2`.
* [x] **Argumentos do Relatório:** Ajuste na assinatura da classe `GeradorRelatorio` para aceitar dicionários de determinantes dinamicamente.

---

## 🛠 Stack Tecnológico Atualizado
* **Core:** Python 3.14+
* **Dados:** Pandas, NumPy, OpenPyXL
* **Relatórios:** FPDF2, Matplotlib

<br>

---
---

<br>

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
* **Busca Robusta:** Implementação do algoritmo `buscar_valor_no_df`, que localiza rótulos (labels) dinamicamente na planilha e captura valores adjacentes.
* **Parser Inteligente:** Extrai automaticamente informações do Cliente, Parâmetros da Obra e a tabela de Traços da Fase Plástica.
* **Output:** Gera um JSON estruturado e limpo, pronto para consumo matemático.

### 2. 🧠 O Cérebro (Core Logic Layer)
O núcleo matemático do sistema, desenvolvido com Orientação a Objetos (POO) e tipagem rigorosa.
* **Alta Precisão:** Utilização da biblioteca `Decimal` para cálculos da Fase Plástica.
* **Matemática Matricial:** Implementação "from scratch" da **Matriz de Vandermonde** e resolução de sistemas lineares via **Regra de Cramer**.
* **Polinômio de Grau 6:** Gera coeficientes ($a_6 \dots a_0$) para modelar o comportamento não-linear.
* **Validação Automática:** Compara os valores reais ($y$) com os calculados ($y_{calc}$).

### 3. 🔄 O Fluxo (Pipeline Integration)
O orquestrador (`main.py`) que conecta o Leitor ao Cérebro.
1. **Ingestão:** Carrega o Excel e converte para dicionários Python.
2. **Processamento:** Calcula o fator a/c real para cada traço experimental.
3. **Modelagem:** Alimenta o Interpolador Matricial com os pares $(x, y)$.
4. **Reporting:** Exibe no terminal a "Caixa Preta" aberta (JSON, Matriz, Equação).

---

## ✨ Funcionalidades Principais

* [x] **Leitura de Excel:** Suporte a arquivos `.xlsx` com tratamento de células vazias.
* [x] **Cálculo de a/c:** Conversão automática de dados de insumos.
* [x] **Engine Matricial:** Resolução de determinantes utilizando `numpy.linalg`.
* [x] **Curva de Dosagem:** Geração automática de 50 pontos equidistantes.
* [x] **Logs Detalhados:** O sistema imprime o passo a passo matricial.

---

## 🛠 Tecnologias Utilizadas
* **Linguagem:** Python 3.14+
* **Manipulação de Dados:** Pandas & NumPy
* **Matemática:** Decimal (Standard Lib) & Linear Algebra (NumPy)
* **Estrutura:** JSON & Dataclasses
