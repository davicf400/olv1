# 🚀 Release Notes v1.4.0: Modelagem de Dados ERP e Dashboards Interativos Web

**Data:** 12 de Março de 2026
**Status:** Versão Estável (v1.4)

## 📝 Visão Geral
A versão v1.4.0 consolida a persistência de dados no ecossistema Odoo ERP e introduz a nova geração de visualização de dados via Web. A estrutura do banco de dados relacional foi customizada para receber as variáveis de engenharia geradas pelo motor matemático. 

## ✨ Changelog (Mudanças Recentes)

### 🌟 Funcionalidades (Features)
* [x] **Modelagem de Dados Odoo:** Criação de colunas customizadas (Fields) direto na estrutura do banco PostgreSQL do Odoo (Modelo `x_concretotec`) para receber: Traço, Alpha, Água, Slump e os resultados do Python (Resistência, Consumo Estimado e Índice de Eficiência).
* [x] **Arquitetura de Registro Único (Clean UI):** Refatoração do script de conexão (`odooconectar.py`) para abandonar a criação de múltiplas linhas poluidoras. O sistema agora consolida o estudo de dosagem em um único registro mestre (Cliente/Obra) com o Relatório "Dump" em PDF convertido via Base64.
* [x] **Motor de Estatística:** O `cerebro.py` foi atualizado para calcular o R² (Coeficiente de Determinação) comparando os pontos reais de laboratório com a curva do polinômio projetado.


### 🛣️ Próximos Passos (Roadmap da API)
O núcleo matemático e a persistência de dados estão homologados. O próximo ciclo de desenvolvimento será focado em transformar o script num microsserviço robusto, preparando-o para o ambiente de Produção:
1. **Contratos Estritos de Dados (Pydantic):** Substituir a recepção genérica de dados por modelos de validação rígidos. A API passará a exigir tipos de dados exatos (ex: floats para água, inteiros para slump), rejeitando automaticamente requisições malformadas antes que cheguem ao motor matemático.
2. **Camada de Autenticação (API Keys):** Implementação de tokens de segurança nas rotas do FastAPI para garantir que apenas sistemas autorizados (como o servidor do Odoo ou o App do Engenheiro) possam disparar o processamento pesado de matrizes.
3. **Deploy em Nuvem:** Transição do "localhost" para um servidor em nuvem (Cloud Computing) rodando 24/7 permitindo acesso universal via endpoints REST.

<br>

---

# 🚀 Release Notes v1.3.0: Motor Multi-Variáveis e Dump Acadêmico (40+ Páginas)

**Data:** 05 de Março de 2026
**Status:** Versão Estável (v1.3)

## 📝 Visão Geral
A versão v1.3.0 marca a transição definitiva da dependência do Excel para o Python. O motor matemático foi abstraído para processar cruzamentos dinâmicos de quaisquer variáveis da Fase Plástica, gerando estudos paralelos simultâneos. O módulo de relatórios sofreu um upgrade massivo, passando a gerar um "Dump" completo de dezenas de páginas com a memória de cálculo minuciosa de cada matriz e determinante.

## ✨ Changelog (Mudanças Recentes)

### 🌟 Funcionalidades (Features)
* [x] **Motor Cego e Dinâmico:** Refatoração da classe `InterpoladorCramer` (`cerebro.py`) para receber chaves universais (X, Y) com ordenação de eixos automática, permitindo cruzar qualquer parâmetro (a/c vs m, m vs Consumo, etc.) sem reescrever a lógica matricial.
* [x] **Cálculo Nativo de Indicadores:** Implementada a função `indice_eficiencia` direto na classe de Fase Plástica. O Python agora calcula a relação Consumo/Resistência em tempo real com alta precisão, abandonando as células pré-calculadas da planilha.
* [x] **Loop de Orquestração:** O `main.py` agora processa uma lista de "Análises Solicitadas", executando o motor de Cramer múltiplas vezes no mesmo ciclo de processamento (Batch Processing).
* [x] **Relatório PDF de Alta Densidade (Dump):** O `relatorio.py` foi reescrito para gerar documentos extensos (40+ páginas). Agora ele documenta cada cruzamento individualmente, imprimindo: a Matriz Principal, as 7 Matrizes Auxiliares (Vetor Y substituído), Tabela de Validação, Gráfico e Equação.

### 🐛 Correções (Bug Fixes)
* [x] **Zeros Ilusórios (Underflow de Impressão):** Correção de um bug visual no PDF onde determinantes de alta ordem apareciam como zero. Implementada a formatação em Notação Científica de alta precisão (`:.14e`) nas tabelas do `fpdf2`, revelando os valores microscópicos e batendo 100% com os cálculos de software de terceiros (Excel/Calc).

<br>

---

# 🚀 Release Notes v1.2.0: Integração ERP, API REST e Precisão Numérica Avançada

**Data:** 04 de Março de 2026
**Status:** Versão Estável (v1.2)

## 📝 Visão Geral
A versão v1.2.0 representa o maior salto arquitetônico do projeto até agora. O sistema deixa de ser um script isolado e se transforma em uma API RESTful conectada diretamente a um ecossistema ERP empresarial (Odoo). Além da comunicação em nuvem, o motor matemático foi refatorado para operar com o máximo rigor acadêmico exigido em projetos de engenharia, garantindo a visualização de todas as etapas de cálculo.

## 🏗 Arquitetura do Sistema (Atualizada)
A arquitetura foi expandida e agora conta com 6 módulos principais, introduzindo a camada de comunicação e serviços web:

### 5. 🌐 A API (Serviço Web) **[NOVO]**
Implementação de um servidor assíncrono utilizando FastAPI para transformar o motor em um microsserviço.
* **Rotas REST:** Criação dos endpoints `/upload-planilha` (para ingestão de arquivos Excel) e `/novo-formulario` (para receber dados em formato JSON nativo).

### 6. 🔌 O Conector ERP (Odoo Integration) **[NOVO]**
Módulo dedicado à comunicação com o banco de dados do Odoo ERP via protocolo JSON-RPC.
* **Autenticação Segura:** Login via API e obtenção de UID de sessão.
* **Criação de Registros:** Inserção autônoma de dados na tabela customizada `x_concretotec`.
* **Anexos Base64:** O PDF gerado pelo Relator é codificado em Base64 e anexado automaticamente ao registro da OS correspondente no Odoo.

## ✨ Changelog (Mudanças Recentes)

### 🌟 Funcionalidades (Features)
* [x] **Comunicação Odoo ERP:** O sistema agora cria as Ordens de Serviço (OS) diretamente no banco de dados e atrela o PDF final ao registro (`x_relatorio`).
* [x] **Dump Acadêmico Completo:** O PDF agora atua como uma "Caixa Preta" transparente para auditoria, imprimindo a Matriz Principal 7x7 (em notação científica), os determinantes do sistema, e uma tabela projetada com exatos 51 pontos equidistantes da curva.
* [x] **Execução CLI Híbrida:** Adicionado gatilho de execução local (`if __name__ == "__main__":`) no `main.py`, permitindo rodar e debugar o sistema direto no terminal, gerando o PDF localmente sem a necessidade de instanciar o servidor web.
* [x] **Segurança de Credenciais:** Implementação de regras de `.gitignore` para proteger dados sensíveis de servidor, acompanhado de um `odooconectar_exemplo.py` para versionamento público seguro.

### ⚙️ Melhorias Técnicas (Refatoração)
* [x] **Precisão de Engenharia (14 Casas Decimais):** O `cerebro.py` e o `relatorio.py` foram reescritos para travar a precisão flutuante. O sistema agora não arredonda cálculos intermediários e formata a saída em string (`:.14f`), garantindo o rigor exigido nos relatórios da UFMT.
* [x] **Reestilização do Gráfico:** Atualização do matplotlib para o estilo `bmh`, incluindo preenchimento de área sob a curva (`fill_between`) e maior contraste nos pontos experimentais reais.

<br>

---

# 🚀 Release Notes v1.1.0: Relatórios Técnicos e Visualização Gráfica

**Data:** 11 de Fevereiro de 2026
**Status:** Versão Estável (v1.1)

## 📝 Visão Geral
A versão v1.1.0 eleva o nível do sistema, transformando-o de uma ferramenta de cálculo em terminal para um **Gerador de Documentação Técnica**. Agora, o sistema produz automaticamente um relatório PDF completo contendo os dados da obra, a curva de dosagem visual (gráfico) e a memória de cálculo detalhada (matrizes), facilitando a análise e o arquivamento dos estudos de dosagem.

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
* **Visualização de Dados:** Integração com `matplotlib` para plotar a Curva de Abrams Inversa (Gráfico m vs a/c).
* **Caixa Preta Aberta:** Uma seção exclusiva no PDF que imprime a Matriz 7x7 e os Determinantes, servindo como memória de cálculo auditável.

### 4. 🔄 O Fluxo (Orchestrator)
* O `main.py` agora gerencia o ciclo: `Leitura -> Cálculo -> Gráfico -> PDF`.
* Limpeza automática de arquivos temporários após a geração do documento.

## ✨ Changelog (Mudanças Recentes)

### 🌟 Funcionalidades (Features)
* [x] **Relatório PDF Completo:** O sistema agora entrega um arquivo `.pdf` pronto, salvo localmente.
* [x] **Gráficos Automáticos:** A curva de interpolação é desenhada e inserida automaticamente no documento.
* [x] **Auditoria Matricial:** Inclusão dos dados brutos da álgebra linear (Vandermonde e Cramer) no corpo do relatório PDF.

### 🐛 Correções (Bug Fixes)
* [x] **FPDF FontFace:** Correção do erro de formatação devido à atualização da biblioteca `fpdf2`.
* [x] **Argumentos do Relatório:** Ajuste na assinatura da classe para aceitar dicionários dinâmicos.

<br>

---

# 🚀 Release Notes v1.0.0: Sistema de Dosagem e Interpolação de Concreto

**Data:** 28 de Janeiro de 2026
**Status:** Versão Estável (v1.0)

## 📝 Visão Geral
Esta é a primeira versão estável do sistema automatizado para cálculo de dosagem de concreto. O software elimina o erro humano e a dependência de planilhas manuais complexas, integrando extração de dados brutos, cálculo de precisão (Fase Plástica) e modelagem matemática avançada (Interpolação Polinomial via Regra de Cramer) para gerar curvas de dosagem (Abrams Inversa).

## 🏗 Arquitetura do Sistema
O projeto foi reestruturado seguindo o padrão de **Separação de Responsabilidades (SoC)**:

### 1. 🔍 O Leitor (Data Extraction Layer)
* **Busca Robusta:** Algoritmo dinâmico que localiza rótulos (labels) na planilha e captura valores adjacentes.
* **Parser Inteligente:** Extrai Cliente, Parâmetros e tabela de Fase Plástica.

### 2. 🧠 O Cérebro (Core Logic Layer)
* **Alta Precisão:** Utilização da biblioteca `Decimal` para cálculos.
* **Matemática Matricial:** Implementação da **Matriz de Vandermonde** e **Regra de Cramer**.
* **Polinômio de Grau 6:** Modelagem de comportamento não-linear com validação automática de dados.

### 3. 🔄 O Fluxo (Pipeline Integration)
* O orquestrador (`main.py`) processa os dados de entrada, calcula o a/c real, interpola a curva e gera o JSON de saída.

## ✨ Funcionalidades Principais
* [x] **Leitura de Excel:** Tratamento de `.xlsx` e células vazias.
* [x] **Cálculo de a/c:** Conversão automática.
* [x] **Engine Matricial:** Resolução de determinantes.
* [x] **Curva de Dosagem:** Geração de 50 pontos.
