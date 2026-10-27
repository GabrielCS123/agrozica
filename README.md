# 🌱 AgroZica — Inteligência Analítica e Gestão Rastreável de Insumos Rurais

**Desafio Oficial AGROHACK 2026/2 — IFRO Campus Ariquemes**  
**Arquitetura:** MTC (*Model-Template-Controller*) + *Strategy Pattern* + *Adapter Pattern* + *Observer Pattern*  
**Stack Tecnológica:** Python 3.11+, CustomTkinter (Dark Mode Verde Floresta), Pandas, NumPy, Matplotlib, OpenPyXL e PyInstaller.

---

## Sumário Oficial (10 Seções do Anexo II do Regulamento)

1. [Identificação do Projeto e Contextualização do Problema Rural](#1-identificação-do-projeto-e-contextualização-do-problema-rural)
2. [Objetivos do Sistema e Escopo Analítico (Propriedade de 500 ha)](#2-objetivos-do-sistema-e-escopo-analítico-propriedade-de-500-ha)
3. [Arquitetura de Software MTC e Engenharia para Mutabilidade](#3-arquitetura-de-software-mtc-e-engenharia-para-mutabilidade)
4. [Dicionário de Dados, Adaptador de Colunas e Regras de Higienização](#4-dicionário-de-dados-adaptador-de-colunas-e-regras-de-higienização)
5. [Metodologia Matemática, Estatística e Regras de Negócio](#5-metodologia-matemática-estatística-e-regras-de-negócio)
6. [Conciliação Rastreável por Lote, FEFO e Alocação de Custos sem Duplicidade](#6-conciliação-rastreável-por-lote-fefo-e-alocação-de-custos-sem-duplicidade)
7. [Comunicação de Incerteza, Governança e Conformidade Legal (inpEV)](#7-comunicação-de-incerteza-governança-e-conformidade-legal-inpev)
8. [Guia das 5 Abas da Interface Gráfica Desktop](#8-guia-das-5-abas-da-interface-gráfica-desktop)
9. [Limitações Técnicas Reconhecidas e Diretrizes de Uso Gerencial](#9-limitações-técnicas-reconhecidas-e-diretrizes-de-uso-gerencial)
10. [Instruções de Instalação, Execução e Compilação para `.exe`](#10-instruções-de-instalação-execução-e-compilação-para-exe)

---

## 1. Identificação do Projeto e Contextualização do Problema Rural

Em propriedades rurais de médio e grande porte, o almoxarifado movimenta continuamente fertilizantes, corretivos, sementes, defensivos químicos, bioinsumos, combustíveis, lubrificantes, peças mecânicas, materiais de irrigação e EPIs. Embora o registro básico de entradas e saídas costume existir em planilhas, o crescimento do volume de lançamentos provoca cinco dores críticas:
1. **Fragmentação de histórico por falhas de digitação** (ex.: `"Glifosato 480"`, `"roundup glifosato"`, `"Uréia"` vs `"Ureia Agrícola"`) e mistura de unidades (`kg`, `saco`, `ton`, `L`, `galao`, `tambor`, `mL`);
2. **Rupturas inesperadas de estoque** no meio de janelas críticas de plantio, adubação ou colheita;
3. **Vencimento de lotes na prateleira**, sobretudo de defensivos biológicos (`Bradyrhizobium`, `Trichoderma`) cuja validade expira antes que o ritmo atual de consumo esgote o lote;
4. **Anomalias invisíveis e inflação silenciosa**, como retiradas atípicas fora do padrão histórico, crescimento progressivo de demanda e aumentos abruptos no preço de compra;
5. **Capital imobilizado e risco ambiental**, com estoque parado há meses e embalagens vazias de agrotóxicos sem controle de devolução ao posto de recebimento credenciado (`inpEV`).

O **AgroZica** resolve esse cenário atuando como um **Cérebro Analítico de Almoxarifado Rural**, transformando registros brutos e imperfeitos em diagnósticos auditáveis e alertas priorizados com justificativas matemáticas em linguagem natural.

---

## 2. Objetivos do Sistema e Escopo Analítico (Propriedade de 500 ha)

O sistema foi calibrado sobre uma propriedade-modelo de **500 hectares** localizada na região de Ariquemes/RO, estruturada em **8 Centros de Custo Rastreáveis**:
- `Almoxarifado Central (Entrada)` — Recebimento patrimonial de compras;
- `Talhão 01 - Soja (150ha)` — Cultivo principal de verão;
- `Talhão 02 - Milho Safrinha (120ha)` — Sucessão produtiva;
- `Pastos Rotacionados (30 Piquetes - 140ha)` — Pastejo intensivo;
- `Semiconfinamento (200 Bovinos)` — Terminação intensiva;
- `Silos e Armazenagem` — Conservação e expurgo pós-colheita;
- `Manutenção de Cercas e Infraestrutura` — Corredores, cercas elétricas/lisas e irrigação;
- `Manutenção de Máquinas e Frota` — Tratores, pulverizadores e colheitadeiras.

---

## 3. Arquitetura de Software MTC e Engenharia para Mutabilidade

O **AgroZica** implementa estritamente o padrão **MTC (*Model-Template-Controller*)** aliado a 4 mecanismos de mutabilidade para resposta imediata durante o hackathon:

1. **Externalização Total (`config/settings.json` + `ConfigModel`):** Nenhum limiar matemático ou fator de conversão é fixo (*hardcoded*) no código. Tudo reside em `config/settings.json` e pode ser alterado ao vivo na **Aba 5 (Configurações)**.
2. **Motor de Regras Plugável (`src/models/rules_engine.py` — *Strategy Pattern*):** A classe abstrata `BaseAlertRule` define o contrato `evaluate(df_movs, df_saldos, config) -> List[Alert]`. As 7 regras analíticas são subclasses independentes registradas no `RuleRegistry`, podendo ser ligadas ou desligadas individualmente via *checkbox*.
3. **Adaptador Inteligente de Colunas (`src/models/column_mapper.py` — *Adapter Pattern*):** Ao importar a planilha oficial da banca avaliadora (`.csv` ou `.xlsx`), o `ColumnMapper` normaliza cabeçalhos (removendo acentos e pontuação) e cruza com um dicionário de sinônimos para mapear automaticamente os dados para as **13 colunas canônicas** do AgroZica.
4. **Atualização Reativa (`src/controllers/main_controller.py` — *Observer Pattern*):** Sempre que um lançamento é inserido, uma planilha é importada ou um *slider* de parâmetro é movido, o `MainController` notifica todas as 5 abas instantaneamente, sem reiniciar o software.

---

## 4. Dicionário de Dados, Adaptador de Colunas e Regras de Higienização

### As 13 Colunas Canônicas do AgroZica
| # | Coluna Canônica | Tipo | Descrição e Regra de Governança |
|---|---|---|---|
| 1 | `id_movimento` | Texto | Identificador único do registro (`MOV-0001`). |
| 2 | `data_movimento` | Data (`YYYY-MM-DD`) | Data efetiva da operação no almoxarifado. |
| 3 | `tipo_movimento` | Texto | `Entrada` (aquisição) ou `Saída` (consumo/aplicação). |
| 4 | `produto` | Texto | Nome do insumo (higienizado pelo `DataCleaner` mantendo `produto_original`). |
| 5 | `categoria` | Texto | Uma das 9 categorias oficiais de insumos rurais. |
| 6 | `lote` | Texto | Código do lote para conciliação física e ordenação FEFO. |
| 7 | `quantidade` | Numérico (`float`) | Volume/quantidade na unidade informada no lançamento. |
| 8 | `unidade` | Texto | Unidade informada (`kg`, `saco`, `ton`, `L`, `galao`, `tambor`, `mL`, `un`, `m`). |
| 9 | `custo_unitario` | Numérico / `NaN` | Preço unitário em R$. **Ausência é mantida como `NaN`, nunca `0`**. |
| 10 | `data_validade` | Data / `NaN` | Data de vencimento do lote. **Ausência é mantida como `NaN`, nunca `0`**. |
| 11 | `destino_centro_custo` | Texto | Talhão, pasto, semiconfinamento, silo ou setor de manutenção. |
| 12 | `responsavel` | Texto | Colaborador responsável pela retirada ou conferência. |
| 13 | `devolucao_embalagem` | Texto | Status `inpEV`: `Não Aplicável`, `Pendente`, `Devolvida` ou `Prazo Vencido`. |

---

## 5. Metodologia Matemática, Estatística e Regras de Negócio

1. **Consumo Médio Diário (CMD) e Autonomia Estimada (`RULE_ESTOQUE_CRITICO`):**
   $$\text{CMD} = \frac{\sum \text{Saídas Padronizadas na Janela}}{\Delta t_{\text{janela}}} \quad ; \quad \text{Autonomia (dias)} = \frac{\text{Saldo Atual}}{\text{CMD}}$$
   Dispara alerta **CRÍTICO** se $\text{Autonomia} \le \text{dias\_estoque\_critico}$ (padrão: `8` dias) e **ATENÇÃO** se $\le \text{dias\_estoque\_atencao}$ (`20` dias).

2. **Cruzamento Validade por Lote vs. Giro (`RULE_VALIDADE_GIRO` — FEFO):**
   $$\text{Dias p/ Esgotar Lote} = \frac{\text{Saldo do Lote FEFO}}{\text{CMD}} \quad ; \quad \text{Perda Estimada} = \max\left(0,\; \text{Saldo Lote} - (\text{CMD} \times \text{Dias até Vencer})\right)$$
   Alerta quando o lote vai vencer antes de ser totalmente consumido no ritmo atual.

3. **Anomalia Estatística de Retirada (`RULE_ANOMALIA_RETIRADA` — Z-Score):**
   $$Z = \frac{X_i - \mu_{\text{saídas}}}{\sigma_{\text{saídas}}} \ge Z_{\text{limiar}} \quad (\text{padrão: } 2.0\sigma)$$

4. **Crescimento Progressivo de Demanda (`RULE_TENDENCIA_ALTA`):**
   Compara a média da metade recente das retiradas ($\bar{X}_{\text{recente}}$) com a metade inicial ($\bar{X}_{\text{inicial}}$) combinada ao coeficiente angular positivo ($\beta_1 > 0$) da regressão linear.

5. **Inflação Abrupta de Preço de Aquisição (`RULE_VARIACAO_PRECO`):**
   $$\Delta P\% = \left(\frac{P_{\text{última entrada}} - \bar{P}_{\text{histórico anterior}}}{\bar{P}_{\text{histórico anterior}}}\right) \times 100 \ge \text{variacao\_preco\_pct}\%$$

6. **Capital Parado e Excesso de Estoque (`RULE_CAPITAL_PARADO`):**
   Acionado quando $\text{Dias sem Saída} \ge 45\text{ dias}$ ou $\text{Autonomia} \ge 180\text{ dias}$.

7. **Logística Reversa de Embalagens de Agrotóxicos (`RULE_EMBALAGENS_DEFENSIVOS`):**
   Rastreia saídas de `Defensivos Químicos` e `Defensivos Biológicos` com status `Pendente` ou `Prazo Vencido`.

---

## 6. Conciliação Rastreável por Lote, FEFO e Alocação de Custos sem Duplicidade

- **Identidade de Conciliação Física:** Todo lote é auditado individualmente por:
  $$\text{Saldo Inicial} + \text{Entradas Padronizadas} - \text{Saídas Padronizadas} = \text{Saldo Final}$$
  Se um lote apresentar $\text{Saldo Final} < 0$ (ex.: erro de digitação de lote na saída, demonstrado no lote `NPK-99-ERR`), o sistema bloqueia a distorção no saldo global e gera um alerta de **Divergência Física de Lote** na Aba de Auditoria.
- **Alocação de Custos sem Duplicidade:** Compras (`Entrada`) contabilizam recomposição patrimonial no `Almoxarifado Central`. Apenas as retiradas (`Saída`) apropriam custo operacional aos Centros de Custo produtivos dos 500 ha, eliminando qualquer dupla contagem entre compra e aplicação.

---

## 7. Comunicação de Incerteza, Governança e Conformidade Legal (inpEV)

- **Sinalização Obrigatória de Amostra Escassa:** Qualquer insumo com menos de `min_historico_saidas` (padrão: `3` saídas) recebe automaticamente o selo `[Incerteza Alta: Pouco Histórico]` tanto na tabela principal quanto nos alertas gerados.
- **Integridade Semântica de Nulos:** Preços ou validades não informados permanecem como `NaN` (`"Pendente / Ausente"`), jamais sendo substituídos por `0`.
- **Conformidade Ambiental (Lei Federal nº 14.785/2023 / inpEV):** Monitoramento dedicado à devolução obrigatória de embalagens vazias de defensivos com tríplice lavagem.

---

## 8. Guia das 5 Abas da Interface Gráfica Desktop

1. **Aba 1 — Painel de Decisão & Alertas (`dashboard_template.py`):** 5 KPIs executivos, filtros dinâmicos, feed de `AlertBanner` ordenado por score de prioridade com justificativa matemática explícita e Matriz Consolidada de Saldos, CMD, Autonomia, FEFO e Curva ABC.
2. **Aba 2 — Inteligência Visual 500ha (`analytics_template.py`):** 4 gráficos Matplotlib em modo escuro (Série Temporal + Banda Z-Score + Tendência, Autonomia vs. Limiares, Custos por Centro de Custo 500ha e Curva ABC de Pareto).
3. **Aba 3 — Lançamentos & Importação Oficial (`operations_template.py`):** Formulário centralizado de Entrada/Saída com reanálise ao vivo, botão de importação de planilhas `.csv`/`.xlsx` via `ColumnMapper`, exportação executiva `.xlsx` e histórico comparativo Bruto vs. Padronizado.
4. **Aba 4 — Auditoria, Lotes & inpEV (`audit_template.py`):** Trilha completa do `DataCleaner`, tabela de conciliação física por lote e painel de governança e limitações técnicas.
5. **Aba 5 — Mutabilidade & Regras (`settings_template.py`):** Sliders ao vivo para todos os parâmetros do `settings.json`, *checkboxes* para ligar/desligar cada uma das 7 regras do `RuleRegistry` e cadastro instantâneo de novos sinônimos de produtos.

---

## 9. Limitações Técnicas Reconhecidas e Diretrizes de Uso Gerencial

- **Sazonalidade Agrícola:** O cálculo do Consumo Médio Diário (CMD) baseia-se na janela móvel configurável (`janela_consumo_dias`). Em transições abruptas de safra (ex.: início do plantio da soja), recomenda-se ajustar a janela na Aba 5 para refletir o ritmo da operação ativa.
- **Apoio à Decisão:** O AgroZica é um sistema gerencial de inteligência analítica e organização de trilhas de auditoria; decisões de manejo químico/biológico devem seguir estritamente o Receituário Agronômico emitido por Engenheiro Agrônomo responsável.

---

## 10. Instruções de Instalação, Execução e Compilação para `.exe`

### 10.1. Instalação das Dependências
```bash
cd agrozica
pip install -r requirements.txt
```

### 10.2. Execução do Sistema Desktop
```bash
python main.py
```

Para executar o diagnóstico analítico automatizado via linha de comando (sem abrir janela gráfica):
```bash
python main.py --diagnose
```

### 10.3. Compilação em Executável Standalone (`AgroZica.exe`)
Basta executar o script automatizado no Windows:
```cmd
build_exe.bat
```
O executável final será gerado em `dist\AgroZica\AgroZica.exe` acompanhado das pastas `config/` e `data/` editáveis.

