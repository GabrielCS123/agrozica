"""
Modelo de Inventário, Conciliação Rastreável por Lote/FEFO e Inteligência de Saldos (InventoryModel).
Implementa:
- Conciliação auditável: Saldo Inicial + Entradas - Saídas = Saldo Final;
- Rastreabilidade por lote e priorização FEFO (First Expired, First Out);
- Cálculo de Consumo Médio Diário (CMD), Autonomia em dias e Curva ABC de Pareto;
- Alocação de custos aos Centros de Custo de 500ha sem duplicidade contábil;
- Persistência imediata em CSV e importação de bases externas (.csv / .xlsx).
"""

from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
import numpy as np
import pandas as pd

from src.models.config_model import ConfigModel, get_base_dir
from src.models.column_mapper import ColumnMapper, CANONICAL_COLUMNS
from src.models.data_cleaner import DataCleaner
from src.models.entities import ResumoProduto, SaldoLote, ItemAuditoria
from generator_seed import generate_seed_csv


class InventoryModel:
    """Núcleo de cálculo de saldos, conciliação física, FEFO e indicadores de estoque do AgroZica."""

    def __init__(self, config_model: ConfigModel, csv_path: Path | None = None) -> None:
        self.config_model = config_model
        base_dir = get_base_dir()
        self.csv_path = csv_path or (base_dir / "data" / "base_simulada_agrozica.csv")
        self.column_mapper = ColumnMapper(self.config_model.data.get("mapeamento_colunas", {}))
        self.data_cleaner = DataCleaner(self.config_model.data)

        self.df_raw: pd.DataFrame = pd.DataFrame()
        self.df_clean: pd.DataFrame = pd.DataFrame()
        self.saldos_lote: List[SaldoLote] = []
        self.resumos_produto: List[ResumoProduto] = []
        self.df_saldos: pd.DataFrame = pd.DataFrame()
        self.itens_auditoria: List[ItemAuditoria] = []
        self.ultimo_mapeamento_colunas: Dict[str, str] = {}
        self.colunas_ausentes_importacao: List[str] = []

        self.ensure_and_load()

    def ensure_and_load(self) -> None:
        """Garante que a base CSV inicial exista e carrega todo o pipeline analítico."""
        if not self.csv_path.exists():
            generate_seed_csv(self.csv_path)
        self.load_from_file(self.csv_path)

    def load_from_file(self, file_path: Path | str) -> None:
        """Lê um arquivo .csv ou .xlsx, aplica o ColumnMapper (Adapter) e executa a reanálise completa."""
        path = Path(file_path)
        if path.suffix.lower() in (".xlsx", ".xls"):
            df_loaded = pd.read_excel(path)
        else:
            try:
                df_loaded = pd.read_csv(path, encoding="utf-8")
            except UnicodeDecodeError:
                df_loaded = pd.read_csv(path, encoding="latin-1", sep=None, engine="python")

        self.column_mapper.mapping_config = self.config_model.data.get("mapeamento_colunas", {})
        df_adapted, applied_map, missing_cols = self.column_mapper.adapt_dataframe(df_loaded)
        self.df_raw = df_adapted
        self.ultimo_mapeamento_colunas = applied_map
        self.colunas_ausentes_importacao = missing_cols
        self.recalculate_all()

    def recalculate_all(self) -> None:
        """Reprocessa higienização, conciliação por lote, FEFO, CMD, autonomia e Curva ABC."""
        self.data_cleaner.update_config(self.config_model.data)
        self.df_clean, audit_cleaner = self.data_cleaner.clean_and_audit(self.df_raw)

        # Data de referência da análise: maior data da base ou data configurada
        max_dt = self.df_clean["data_movimento_dt"].dropna().max()
        if pd.isna(max_dt):
            ref_date = pd.Timestamp("2026-10-27")
        else:
            ref_date = max_dt

        self.saldos_lote, audit_lotes = self._compute_lot_balances(self.df_clean, ref_date)
        self.itens_auditoria = audit_cleaner + audit_lotes
        self.resumos_produto, self.df_saldos = self._compute_product_summaries(
            self.df_clean, self.saldos_lote, ref_date
        )

    def _compute_lot_balances(
        self, df: pd.DataFrame, ref_date: pd.Timestamp
    ) -> Tuple[List[SaldoLote], List[ItemAuditoria]]:
        """
        Audita cada lote individualmente pela fórmula:
        Saldo Inicial (0) + Entradas - Saídas = Saldo Final.
        Detecta divergências onde Saídas > Entradas no lote.
        """
        lot_list: List[SaldoLote] = []
        lot_audits: List[ItemAuditoria] = []

        if df.empty:
            return lot_list, lot_audits

        grouped = df.groupby(["produto", "lote"], sort=False)
        for (prod, lote), grp in grouped:
            cat = str(grp["categoria"].iloc[0])
            unid = str(grp["unidade_padronizada"].iloc[0])
            saldo_ini = 0.0
            entradas = float(grp.loc[grp["tipo_movimento"] == "Entrada", "quantidade_padronizada"].sum())
            saidas = float(grp.loc[grp["tipo_movimento"] == "Saída", "quantidade_padronizada"].sum())
            saldo_fin = round(saldo_ini + entradas - saidas, 4)

            vals_validade = grp["data_validade"].dropna().unique()
            dt_val_str: Optional[str] = str(vals_validade[0]) if len(vals_validade) > 0 else None
            dias_val: Optional[int] = None
            if dt_val_str:
                dt_parsed = pd.to_datetime(dt_val_str, errors="coerce")
                if pd.notna(dt_parsed):
                    dias_val = int((dt_parsed - ref_date).days)

            divergencia = saldo_fin < -1e-6
            detalhe = ""
            if divergencia:
                detalhe = (
                    f"Divergência de Conciliação no lote {lote}: "
                    f"Saldo Inicial (0) + Entradas ({entradas:g} {unid}) - Saídas ({saidas:g} {unid}) "
                    f"= {saldo_fin:g} {unid} (Saldo Físico Negativo no Lote!)."
                )
                lot_audits.append(
                    ItemAuditoria(
                        id_movimento=str(grp["id_movimento"].iloc[-1]),
                        data_movimento=str(grp["data_movimento"].iloc[-1]),
                        produto=str(prod),
                        lote=str(lote),
                        tipo_inconsistencia="Divergência de Lote",
                        severidade="ALTA",
                        valor_original=f"Entradas: {entradas:g} | Saídas: {saidas:g} {unid}",
                        tratamento_aplicado=f"Saldo do lote = {saldo_fin:g} {unid} (Bloqueio para conferência)",
                        impacto_analitico=detalhe,
                    )
                )

            lot_list.append(
                SaldoLote(
                    produto=str(prod),
                    categoria=cat,
                    lote=str(lote),
                    unidade_padronizada=unid,
                    saldo_inicial=saldo_ini,
                    total_entradas=round(entradas, 4),
                    total_saidas=round(saidas, 4),
                    saldo_final=saldo_fin,
                    data_validade=dt_val_str,
                    dias_ate_validade=dias_val,
                    divergencia_conciliacao=divergencia,
                    detalhe_divergencia=detalhe,
                )
            )

        return lot_list, lot_audits

    def _compute_product_summaries(
        self, df: pd.DataFrame, lots: List[SaldoLote], ref_date: pd.Timestamp
    ) -> Tuple[List[ResumoProduto], pd.DataFrame]:
        """Calcula indicadores analíticos consolidados por produto, FEFO, CMD, autonomia e Curva ABC."""
        summaries: List[ResumoProduto] = []
        if df.empty:
            return summaries, pd.DataFrame()

        min_hist = int(self.config_model.get_param("min_historico_saidas", 3))
        dias_critico = float(self.config_model.get_param("dias_estoque_critico", 8))
        dias_atencao = float(self.config_model.get_param("dias_estoque_atencao", 20))
        dias_parado_lim = float(self.config_model.get_param("dias_capital_parado", 45))
        autonomia_exc_lim = float(self.config_model.get_param("autonomia_excesso_dias", 180))
        janela_padrao = float(self.config_model.get_param("janela_consumo_dias", 60))

        lots_by_prod: Dict[str, List[SaldoLote]] = {}
        for l_item in lots:
            lots_by_prod.setdefault(l_item.produto, []).append(l_item)

        for prod, grp in df.groupby("produto", sort=False):
            cat = str(grp["categoria"].iloc[0])
            unid = str(grp["unidade_padronizada"].iloc[0])

            df_ent = grp[grp["tipo_movimento"] == "Entrada"]
            df_sai = grp[grp["tipo_movimento"] == "Saída"]

            saldo_ini = 0.0
            tot_ent = round(float(df_ent["quantidade_padronizada"].sum()), 4)
            tot_sai = round(float(df_sai["quantidade_padronizada"].sum()), 4)
            saldo_atual = round(max(0.0, saldo_ini + tot_ent - tot_sai), 4)

            # Custo médio unitário (ignorando NaNs sem tratá-los como zero!)
            custos_validos = grp["custo_unitario_padronizado"].dropna()
            custo_medio: Optional[float] = (
                round(float(custos_validos.mean()), 4) if len(custos_validos) > 0 else None
            )

            valor_estoque = round(saldo_atual * (custo_medio or 0.0), 2)
            valor_consumido = round(tot_sai * (custo_medio or 0.0), 2)

            # Cálculo do Consumo Médio Diário (CMD) na janela efetiva do insumo
            qtd_eventos_saida = len(df_sai)
            dt_min_prod = grp["data_movimento_dt"].dropna().min()
            if pd.notna(dt_min_prod):
                span_dias = max(14.0, float((ref_date - dt_min_prod).days) + 1.0)
                janela_efetiva = min(janela_padrao, span_dias)
            else:
                janela_efetiva = janela_padrao

            # Filtra saídas dentro da janela_padrao a partir de ref_date
            corte_janela = ref_date - pd.Timedelta(days=janela_padrao)
            saidas_janela = df_sai[df_sai["data_movimento_dt"] >= corte_janela]
            soma_saidas_janela = float(saidas_janela["quantidade_padronizada"].sum())

            if soma_saidas_janela > 0:
                cmd = round(soma_saidas_janela / janela_efetiva, 4)
            elif tot_sai > 0 and pd.notna(dt_min_prod):
                dias_totais = max(1.0, float((ref_date - dt_min_prod).days))
                cmd = round(tot_sai / dias_totais, 4)
            else:
                cmd = 0.0

            autonomia: Optional[float] = round(saldo_atual / cmd, 1) if cmd > 0 else None

            # Dias desde a última saída
            dt_ult_saida = df_sai["data_movimento_dt"].dropna().max()
            dias_sem_saida: Optional[int] = (
                int((ref_date - dt_ult_saida).days) if pd.notna(dt_ult_saida) else None
            )

            # Lote FEFO (First Expired, First Out) entre lotes com saldo > 0
            prod_lots = [lt for lt in lots_by_prod.get(str(prod), []) if lt.saldo_final > 0]
            prod_lots_with_val = [lt for lt in prod_lots if lt.dias_ate_validade is not None]
            if prod_lots_with_val:
                prod_lots_with_val.sort(key=lambda x: x.dias_ate_validade if x.dias_ate_validade is not None else 99999)
                fefo = prod_lots_with_val[0]
            elif prod_lots:
                fefo = prod_lots[0]
            else:
                fefo = SaldoLote(
                    produto=str(prod), categoria=cat, lote="SEM SALDO", unidade_padronizada=unid,
                    saldo_inicial=0, total_entradas=0, total_saidas=0, saldo_final=0,
                    data_validade=None, dias_ate_validade=None
                )

            incerteza_alta = qtd_eventos_saida < min_hist
            tag_conf = (
                "[Incerteza Alta: Pouco Histórico]"
                if incerteza_alta
                else f"[Confiança Adequada: {qtd_eventos_saida} saídas]"
            )

            # Status operacional
            if autonomia is not None and autonomia <= dias_critico:
                status_op = "Crítico"
            elif autonomia is not None and autonomia <= dias_atencao:
                status_op = "Atenção"
            elif (dias_sem_saida is not None and dias_sem_saida >= dias_parado_lim) or (
                autonomia is not None and autonomia >= autonomia_exc_lim
            ):
                status_op = "Excesso/Parado"
            else:
                status_op = "Normal"

            summaries.append(
                ResumoProduto(
                    produto=str(prod),
                    categoria=cat,
                    unidade_padronizada=unid,
                    saldo_inicial=saldo_ini,
                    total_entradas=tot_ent,
                    total_saidas=tot_sai,
                    saldo_atual=saldo_atual,
                    custo_medio_unitario=custo_medio,
                    valor_estoque_atual=valor_estoque,
                    valor_consumido_total=valor_consumido,
                    consumo_medio_diario=cmd,
                    autonomia_dias=autonomia,
                    lote_fefo=fefo.lote,
                    validade_fefo=fefo.data_validade,
                    dias_para_vencer_fefo=fefo.dias_ate_validade,
                    qtd_lote_fefo=fefo.saldo_final,
                    dias_sem_saida=dias_sem_saida,
                    qtd_eventos_saida=qtd_eventos_saida,
                    incerteza_alta=incerteza_alta,
                    tag_confianca=tag_conf,
                    status_operacional=status_op,
                )
            )

        # Cálculo da Curva ABC (critério: Valor Total Movimentado = Consumo + Estoque Atual)
        total_valor_global = sum(
            (s.valor_consumido_total + s.valor_estoque_atual) for s in summaries
        )
        summaries.sort(key=lambda s: (s.valor_consumido_total + s.valor_estoque_atual), reverse=True)

        acumulado = 0.0
        for s in summaries:
            peso = (
                ((s.valor_consumido_total + s.valor_estoque_atual) / total_valor_global) * 100.0
                if total_valor_global > 0
                else 0.0
            )
            s.percentual_valor_abc = round(peso, 2)
            if acumulado < 75.0:
                s.classe_abc = "A"
            elif acumulado < 93.0:
                s.classe_abc = "B"
            else:
                s.classe_abc = "C"
            acumulado += peso

        # Ordena por criticidade de autonomia para exibição padrão
        df_saldos = pd.DataFrame([s.__dict__ for s in summaries])
        return summaries, df_saldos

    def add_movement(self, record: Dict[str, Any], persist: bool = True) -> str:
        """
        Insere uma nova movimentação (Entrada ou Saída), gera ID incremental se necessário,
        persiste no CSV e dispara reanálise completa em tempo real.
        """
        new_row = {col: record.get(col, "") for col in CANONICAL_COLUMNS}
        if not str(new_row.get("id_movimento", "")).strip():
            next_num = len(self.df_raw) + 1
            new_row["id_movimento"] = f"MOV-{next_num:04d}"

        # Proteção semântica: campos vazios ficam None/vazio, nunca zero!
        if str(new_row.get("custo_unitario", "")).strip() in ("", "None"):
            new_row["custo_unitario"] = ""
        if str(new_row.get("data_validade", "")).strip() in ("", "None"):
            new_row["data_validade"] = ""

        self.df_raw = pd.concat([self.df_raw, pd.DataFrame([new_row])], ignore_index=True)
        if persist:
            self.save_to_csv()
        self.recalculate_all()
        return str(new_row["id_movimento"])

    def save_to_csv(self, target_path: Path | None = None) -> Path:
        """Salva o DataFrame de 13 colunas canônicas no arquivo CSV."""
        out_path = target_path or self.csv_path
        out_path.parent.mkdir(parents=True, exist_ok=True)
        df_to_save = self.df_raw[CANONICAL_COLUMNS].copy()
        df_to_save.to_csv(out_path, index=False, encoding="utf-8")
        return out_path

    def get_cost_center_breakdown(self) -> pd.DataFrame:
        """
        Retorna os custos operacionais por Centro de Custo dos 500ha SEM DUPLICIDADE:
        Apenas as SAÍDAS para aplicação nos talhões, pastos, semiconfinamento, silos e manutenção
        são apropriadas como custo operacional; ENTRADAS representam compras para o almoxarifado.
        """
        if self.df_clean.empty:
            return pd.DataFrame(columns=["destino_centro_custo", "custo_operacional", "qtd_movimentos", "percentual"])

        df_saidas = self.df_clean[self.df_clean["tipo_movimento"] == "Saída"].copy()
        if df_saidas.empty:
            return pd.DataFrame(columns=["destino_centro_custo", "custo_operacional", "qtd_movimentos", "percentual"])

        grp = (
            df_saidas.groupby("destino_centro_custo", as_index=False)
            .agg(
                custo_operacional=("custo_total_movimento", "sum"),
                qtd_movimentos=("id_movimento", "count"),
            )
            .sort_values(by="custo_operacional", ascending=False)
        )
        total = float(grp["custo_operacional"].sum())
        grp["percentual"] = grp["custo_operacional"].apply(lambda v: round((v / total) * 100.0, 1) if total > 0 else 0.0)
        return grp

