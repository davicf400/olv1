
🚀 Release Notes v1.3.0: Motor Multi-Variáveis e Dump Acadêmico (40+ Páginas)
Data: 05 de Março de 2026Status: Versão Estável (v1.3)📝 
Visão Geral
A versão v1.3.0 marca a transição definitiva da dependência do Excel para o Python. O motor matemático foi abstraído para processar cruzamentos dinâmicos de quaisquer variáveis da Fase Plástica, gerando estudos paralelos simultâneos. O módulo de relatórios sofreu um upgrade massivo, passando a gerar um "Dump" completo de dezenas de páginas com a memória de cálculo minuciosa de cada matriz e determinante.
✨ Changelog (Mudanças Recentes)
Funcionalidades (Features)[x] Motor Cego e Dinâmico: Refatoração da classe InterpoladorCramer (cerebro.py) para receber chaves universais (X, Y) com ordenação de eixos automática, permitindo cruzar qualquer parâmetro ($a/c \times m$, $m \times Consumo$, etc.) sem reescrever a lógica matricial.[x] 

Cálculo Nativo de Indicadores: Implementada a função indice_eficiencia direto na classe CalculoFasePlastica. O Python agora calcula a relação Consumo/Resistência em tempo real com alta precisão, abandonando as células pré-calculadas da planilha.[x] Loop de Orquestração: O main.py agora processa uma lista de "Análises Solicitadas", executando o motor de Cramer múltiplas vezes no mesmo ciclo de processamento (Batch Processing).[x] Relatório PDF de Alta Densidade (Dump): O relatorio.py foi reescrito para gerar documentos extensos (40+ páginas). Agora ele documenta cada cruzamento individualmente, imprimindo: a Matriz Principal, as 7 Matrizes Auxiliares (Vetor Y substituído), Tabela de Validação, Gráfico e Equação.

🐛 Correções (Bug Fixes)[x]
Zeros Ilusórios (Underflow de Impressão): Correção de um bug visual no PDF onde determinantes de alta ordem (ex: $a/c^6$) apareciam como zero. Implementada a formatação em Notação Científica de alta precisão (:.14e) nas tabelas do fpdf2, revelando os valores microscópicos e batendo 100% com os cálculos de software de terceiros (Excel/Calc).





🚀 Release Notes v1.2.0: Integração ERP, API REST e Precisão Numérica Avançada
Data: 04 de Março de 2026
Status: Versão Estável (v1.2)

📝 Visão Geral
A versão v1.2.0 representa o maior salto arquitetônico do projeto até agora. O sistema deixa de ser um script isolado e se transforma em uma API RESTful conectada diretamente a um ecossistema ERP empresarial (Odoo). Além da comunicação em nuvem, o motor matemático foi refatorado para operar com o máximo rigor acadêmico exigido em projetos de engenharia, garantindo a visualização de todas as etapas de cálculo.

🏗 Arquitetura do Sistema (Atualizada)
A arquitetura foi expandida e agora conta com 6 módulos principais, introduzindo a camada de comunicação e serviços web:

5. 🌐 A API (Serviço Web) [NOVO]
Implementação de um servidor assíncrono utilizando FastAPI para transformar o motor em um microsserviço.

Rotas REST: Criação dos endpoints /upload-planilha (para ingestão de arquivos Excel) e /novo-formulario (para receber dados em formato JSON nativo).

6. 🔌 O Conector ERP (Odoo Integration) [NOVO]
Módulo dedicado à comunicação com o banco de dados do Odoo ERP via protocolo JSON-RPC.

Autenticação Segura: Login via API e obtenção de UID de sessão.

Criação de Registros: Inserção autônoma de dados na tabela customizada x_concretotec.

Anexos Base64: O PDF gerado pelo Relator é codificado em Base64 e anexado automaticamente ao registro da OS correspondente no Odoo.

✨ Changelog (Mudanças Recentes)
🌟 Funcionalidades (Features)
[x] Comunicação Odoo ERP: O sistema agora cria as Ordens de Serviço (OS) diretamente no banco de dados e atrela o PDF final ao registro (x_relatorio).

[x] Dump Acadêmico Completo: O PDF agora atua como uma "Caixa Preta" transparente para auditoria, imprimindo a Matriz Principal 7x7 (em notação científica), os determinantes do sistema, e uma tabela projetada com exatos 51 pontos equidistantes da curva.

[x] Execução CLI Híbrida: Adicionado gatilho de execução local (if __name__ == "__main__":) no main.py, permitindo rodar e debugar o sistema direto no terminal, gerando o PDF localmente sem a necessidade de instanciar o servidor web.

[x] Segurança de Credenciais: Implementação de regras de .gitignore para proteger dados sensíveis de servidor, acompanhado de um odooconectar_exemplo.py para versionamento público seguro.

⚙️ Melhorias Técnicas (Refatoração)
[x] Precisão de Engenharia (14 Casas Decimais): O cerebro.py e o relatorio.py foram reescritos para travar a precisão flutuante. O sistema agora não arredonda cálculos intermediários e formata a saída em string (:.14f), garantindo o rigor exigido nos relatórios da UFMT.

[x] Reestilização do Gráfico: Atualização do matplotlib para o estilo bmh, incluindo preenchimento de área sob a curva (fill_between) e maior contraste nos pontos experimentais reais.

🛠 Stack Tecnológico Atualizado
Core: Python

API & Web: FastAPI, Uvicorn, JSON-RPC

Dados & Matemática: Pandas, NumPy (float64 precision)

Relatórios & Gráficos: FPDF2, Matplotlib

ERP: Odoo




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
