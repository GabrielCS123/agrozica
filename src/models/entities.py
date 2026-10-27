"""
Entidades de domínio (Dataclasses) do AgroZica.
Representam registros de movimentação, saldos consolidados por produto e lote,
alertas priorizados pelo motor de regras e ocorrências de auditoria de dados.
"""

from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class RegistroMovimento:
    """Representa uma movimentação individual já higienizada e padronizada pelo AgroZica."""
    id_movimento: str
    data_movimento: str
    tipo_movimento: str          # 'Entrada' ou 'Saída'
    produto_original: str        # Grafia exata informada no dado bruto
    produto: str                 # Nome canônico padronizado pelo DataCleaner
    categoria: str
    lote: str
    quantidade_original: float
    unidade_original: str
    quantidade_padronizada: float
    unidade_padronizada: str
    fator_conversao: float
    custo_unitario_original: Optional[float]  # None se ausente no bruto (nunca zero artificial!)
    custo_unitario_padronizado: Optional[float]
    custo_total_estimado: float
    data_validade: Optional[str]              # None se ausente/não aplicável
    destino_centro_custo: str
    responsavel: str
    devolucao_embalagem: str
    inconsistencias: List[str] = field(default_factory=list)


@dataclass
class SaldoLote:
    """Representa o saldo rastreável de um lote específico (suporte a FEFO e conciliação)."""
    produto: str
    categoria: str
    lote: str
    unidade_padronizada: str
    saldo_inicial: float
    total_entradas: float
    total_saidas: float
    saldo_final: float
    data_validade: Optional[str]
    dias_ate_validade: Optional[int]
    divergencia_conciliacao: bool = False
    detalhe_divergencia: str = ""


@dataclass
class ResumoProduto:
    """
    Consolida a inteligência analítica de um insumo no almoxarifado:
    conciliação física, consumo médio diário (CMD), autonomia estimada,
    validade FEFO, classificação ABC e nível de confiança estatística.
    """
    produto: str
    categoria: str
    unidade_padronizada: str
    saldo_inicial: float
    total_entradas: float
    total_saidas: float
    saldo_atual: float
    custo_medio_unitario: Optional[float]
    valor_estoque_atual: float
    valor_consumido_total: float
    consumo_medio_diario: float              # CMD na janela de análise
    autonomia_dias: Optional[float]          # Saldo Atual / CMD (None se CMD == 0)
    lote_fefo: str                           # Lote com vencimento mais próximo e saldo > 0
    validade_fefo: Optional[str]
    dias_para_vencer_fefo: Optional[int]
    qtd_lote_fefo: float
    dias_sem_saida: Optional[int]
    qtd_eventos_saida: int
    incerteza_alta: bool                     # True se qtd_eventos_saida < min_historico_saidas
    tag_confianca: str                       # '[Confiança Adequada]' ou '[Incerteza Alta: Pouco Histórico]'
    classe_abc: str = "C"                    # 'A', 'B' ou 'C'
    percentual_valor_abc: float = 0.0
    status_operacional: str = "Normal"       # 'Crítico', 'Atenção', 'Normal', 'Excesso/Parado'


@dataclass
class Alert:
    """
    Alerta priorizado gerado por uma subclasse de BaseAlertRule no motor de regras.
    Contém justificativa matemática transparente em linguagem natural e recomendação.
    """
    rule_id: str
    titulo: str
    severidade: str              # 'CRÍTICO', 'ATENÇÃO', 'INFORMATIVO'
    score_prioridade: int        # 1 a 100 para ordenação determinística no painel de decisão
    produto: str
    categoria: str
    lote_afetado: str
    indicador_chave: str         # Ex: 'Autonomia: 5.6 dias | CMD: 75.0 L/dia'
    justificativa_matematica: str
    recomendacao_gerencial: str
    aviso_incerteza: str = ""


@dataclass
class ItemAuditoria:
    """
    Representa um apontamento de governança e qualidade de dados:
    grafia corrigida, unidade convertida, campo ausente protegido ou divergência de lote.
    """
    id_movimento: str
    data_movimento: str
    produto: str
    lote: str
    tipo_inconsistencia: str     # 'Grafia Padronizada', 'Conversão de Unidade', 'Dado Ausente (NaN)', 'Divergência de Lote', 'Logística Reversa'
    severidade: str              # 'ALTA', 'MÉDIA', 'BAIXA'
    valor_original: str
    tratamento_aplicado: str
    impacto_analitico: str

