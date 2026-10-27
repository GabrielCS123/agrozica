"""
Motor de Regras Plugável do AgroZica (Strategy Pattern + RuleRegistry).
Implementa a classe abstrata BaseAlertRule e as 7 classes analíticas independentes:
1. StockAutonomyAlertRule (RULE_ESTOQUE_CRITICO)
2. ExpirationVsTurnoverAlertRule (RULE_VALIDADE_GIRO)
3. WithdrawalAnomalyAlertRule (RULE_ANOMALIA_RETIRADA)
4. ProgressiveDemandTrendAlertRule (RULE_TENDENCIA_ALTA)
5. PriceInflationAlertRule (RULE_VARIACAO_PRECO)
6. IdleCapitalAlertRule (RULE_CAPITAL_PARADO)
7. PesticidePackagingAlertRule (RULE_EMBALAGENS_DEFENSIVOS)

Novas regras podem ser adicionadas apenas herdando de BaseAlertRule e registrando no RuleRegistry.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
import numpy as np
import pandas as pd

from src.models.entities import Alert


class BaseAlertRule(ABC):
    """Interface abstrata (Strategy) para todas as regras analíticas do AgroZica."""

    rule_id: str = "BASE_RULE"
    rule_name: str = "Regra Base"
    description: str = "Descrição da regra analítica."

    @abstractmethod
    def evaluate(
        self, df_movs: pd.DataFrame, df_saldos: pd.DataFrame, config: Dict[str, Any]
    ) -> List[Alert]:
        """Avalia o histórico e saldos e retorna uma lista de alertas justificados."""


class StockAutonomyAlertRule(BaseAlertRule):
    """Regra 1: Antecipa rupturas calculando a autonomia estimada em dias com base no CMD."""

    rule_id = "RULE_ESTOQUE_CRITICO"
    rule_name = "Ruptura e Autonomia de Estoque (CMD)"
    description = "Monitora insumos cuja autonomia estimada (Saldo / CMD) está abaixo do limiar crítico ou de atenção."

    def evaluate(
        self, df_movs: pd.DataFrame, df_saldos: pd.DataFrame, config: Dict[str, Any]
    ) -> List[Alert]:
        alerts: List[Alert] = []
        if df_saldos.empty:
            return alerts

        params = config.get("parametros_regras", {})
        lim_critico = float(params.get("dias_estoque_critico", 8))
        lim_atencao = float(params.get("dias_estoque_atencao", 20))

        for _, row in df_saldos.iterrows():
            autonomia = row.get("autonomia_dias")
            if autonomia is None or pd.isna(autonomia):
                continue

            prod = str(row["produto"])
            cat = str(row["categoria"])
            unid = str(row["unidade_padronizada"])
            saldo = float(row["saldo_atual"])
            cmd = float(row["consumo_medio_diario"])
            lote = str(row["lote_fefo"])
            tag_conf = str(row["tag_confianca"])
            incerteza = bool(row["incerteza_alta"])

            if autonomia <= lim_critico:
                qtd_sugerida = round(max(0.0, (cmd * 30.0) - saldo), 1)
                alerts.append(
                    Alert(
                        rule_id=self.rule_id,
                        titulo=f"Ruptura Iminente de Estoque: {prod}",
                        severidade="CRÍTICO",
                        score_prioridade=98,
                        produto=prod,
                        categoria=cat,
                        lote_afetado=lote,
                        indicador_chave=f"Autonomia: {autonomia:.1f} dias (Limiar Crítico: <= {lim_critico:g} dias)",
                        justificativa_matematica=(
                            f"Saldo físico atual de {saldo:g} {unid} dividido pelo Consumo Médio Diário (CMD) "
                            f"de {cmd:.2f} {unid}/dia resulta em autonomia de apenas {autonomia:.1f} dias "
                            f"(abaixo do limite crítico de {lim_critico:g} dias). {tag_conf}"
                        ),
                        recomendacao_gerencial=(
                            f"Emitir pedido emergencial de compra. Para recompor cobertura de 30 dias no ritmo atual, "
                            f"adquirir no mínimo {qtd_sugerida:g} {unid} (conferir estoque físico antes do pedido)."
                        ),
                        aviso_incerteza=tag_conf if incerteza else "",
                    )
                )
            elif autonomia <= lim_atencao:
                qtd_sugerida = round(max(0.0, (cmd * 30.0) - saldo), 1)
                alerts.append(
                    Alert(
                        rule_id=self.rule_id,
                        titulo=f"Estoque em Faixa de Atenção: {prod}",
                        severidade="ATENÇÃO",
                        score_prioridade=72,
                        produto=prod,
                        categoria=cat,
                        lote_afetado=lote,
                        indicador_chave=f"Autonomia: {autonomia:.1f} dias (Faixa Atenção: <= {lim_atencao:g} dias)",
                        justificativa_matematica=(
                            f"Saldo atual de {saldo:g} {unid} frente ao CMD de {cmd:.2f} {unid}/dia garante "
                            f"suprimento por {autonomia:.1f} dias (dentro da janela de alerta preventivo de {lim_atencao:g} dias). "
                            f"{tag_conf}"
                        ),
                        recomendacao_gerencial=(
                            f"Programar cotação com fornecedores para reposição estimada de {qtd_sugerida:g} {unid} "
                            f"para os próximos 30 dias de operação."
                        ),
                        aviso_incerteza=tag_conf if incerteza else "",
                    )
                )

        return alerts


class ExpirationVsTurnoverAlertRule(BaseAlertRule):
    """Regra 2: Cruza a validade de cada lote (FEFO) com a velocidade de consumo (CMD)."""

    rule_id = "RULE_VALIDADE_GIRO"
    rule_name = "Risco de Vencimento vs. Velocidade de Giro (FEFO)"
    description = "Cruza os dias até o vencimento do lote com o tempo necessário para consumi-lo no ritmo atual."

    def evaluate(
        self, df_movs: pd.DataFrame, df_saldos: pd.DataFrame, config: Dict[str, Any]
    ) -> List[Alert]:
        alerts: List[Alert] = []
        if df_saldos.empty:
            return alerts

        params = config.get("parametros_regras", {})
        lim_validade = int(params.get("dias_alerta_validade", 45))

        for _, row in df_saldos.iterrows():
            dias_vencer = row.get("dias_para_vencer_fefo")
            if dias_vencer is None or pd.isna(dias_vencer):
                continue
            dias_vencer = int(dias_vencer)
            if dias_vencer > lim_validade:
                continue

            prod = str(row["produto"])
            cat = str(row["categoria"])
            unid = str(row["unidade_padronizada"])
            lote = str(row["lote_fefo"])
            dt_val = str(row["validade_fefo"])
            qtd_lote = float(row["qtd_lote_fefo"])
            cmd = float(row["consumo_medio_diario"])
            custo_med = float(row["custo_medio_unitario"]) if pd.notna(row["custo_medio_unitario"]) else 0.0
            tag_conf = str(row["tag_confianca"])
            incerteza = bool(row["incerteza_alta"])

            dias_para_esgotar_lote = round(qtd_lote / cmd, 1) if cmd > 0 else 999.0
            consumo_ate_vencer = max(0.0, cmd * max(0, dias_vencer))
            sobra_vencida = round(max(0.0, qtd_lote - consumo_ate_vencer), 2)
            perda_financeira = round(sobra_vencida * custo_med, 2)

            if dias_vencer <= 0:
                alerts.append(
                    Alert(
                        rule_id=self.rule_id,
                        titulo=f"Lote Vencido no Almoxarifado: {prod}",
                        severidade="CRÍTICO",
                        score_prioridade=99,
                        produto=prod,
                        categoria=cat,
                        lote_afetado=lote,
                        indicador_chave=f"Vencido há {abs(dias_vencer)} dias ({dt_val}) | Saldo: {qtd_lote:g} {unid}",
                        justificativa_matematica=(
                            f"O lote {lote} ({qtd_lote:g} {unid}) atingiu a data de validade em {dt_val}. "
                            f"Perda potencial estimada em R$ {qtd_lote * custo_med:,.2f}."
                        ),
                        recomendacao_gerencial=(
                            "Segregar imediatamente o lote físico no almoxarifado para impedir aplicação indevida "
                            "e acionar orientação agronômica/fabricante para descarte seguro."
                        ),
                        aviso_incerteza=tag_conf if incerteza else "",
                    )
                )
            elif sobra_vencida > 0:
                alerts.append(
                    Alert(
                        rule_id=self.rule_id,
                        titulo=f"Risco de Perda por Validade vs. Giro Lento: {prod}",
                        severidade="CRÍTICO",
                        score_prioridade=95,
                        produto=prod,
                        categoria=cat,
                        lote_afetado=lote,
                        indicador_chave=(
                            f"Vence em {dias_vencer} dias ({dt_val}) | Giro exige {dias_para_esgotar_lote:.1f} dias"
                        ),
                        justificativa_matematica=(
                            f"O lote FEFO {lote} possui {qtd_lote:g} {unid} e vence em {dias_vencer} dias ({dt_val}), "
                            f"mas com o CMD atual de {cmd:.2f} {unid}/dia serão necessários {dias_para_esgotar_lote:.1f} dias "
                            f"para esgotá-lo. Estimativa de perda na prateleira: {sobra_vencida:g} {unid} "
                            f"(R$ {perda_financeira:,.2f}). {tag_conf}"
                        ),
                        recomendacao_gerencial=(
                            f"Priorizar saída imediata do lote {lote} (regra FEFO) nas próximas ordens de manejo "
                            f"dos talhões compatíveis, respeitando rigorosamente o receituário agronômico."
                        ),
                        aviso_incerteza=tag_conf if incerteza else "",
                    )
                )
            else:
                alerts.append(
                    Alert(
                        rule_id=self.rule_id,
                        titulo=f"Validade Próxima Monitorada (FEFO): {prod}",
                        severidade="ATENÇÃO",
                        score_prioridade=68,
                        produto=prod,
                        categoria=cat,
                        lote_afetado=lote,
                        indicador_chave=f"Vence em {dias_vencer} dias ({dt_val}) | Giro esgota em {dias_para_esgotar_lote:.1f} dias",
                        justificativa_matematica=(
                            f"O lote {lote} vence em {dias_vencer} dias (<= {lim_validade} dias). O giro atual "
                            f"({cmd:.2f} {unid}/dia) consome o saldo em {dias_para_esgotar_lote:.1f} dias, antes do vencimento."
                        ),
                        recomendacao_gerencial=f"Garantir que toda retirada utilize primeiro o lote {lote} (FEFO).",
                        aviso_incerteza=tag_conf if incerteza else "",
                    )
                )

        return alerts


class WithdrawalAnomalyAlertRule(BaseAlertRule):
    """Regra 3: Detecta retiradas estatisticamente fora do padrão via Z-Score."""

    rule_id = "RULE_ANOMALIA_RETIRADA"
    rule_name = "Anomalia Estatística de Retirada (Z-Score)"
    description = "Identifica retiradas pontuais cujo volume destoa significativamente da média e desvio padrão do insumo."

    def evaluate(
        self, df_movs: pd.DataFrame, df_saldos: pd.DataFrame, config: Dict[str, Any]
    ) -> List[Alert]:
        alerts: List[Alert] = []
        if df_movs.empty:
            return alerts

        params = config.get("parametros_regras", {})
        z_limiar = float(params.get("z_score_anomalia", 2.0))
        min_hist = int(params.get("min_historico_saidas", 3))

        df_saidas = df_movs[df_movs["tipo_movimento"] == "Saída"]
        for prod, grp in df_saidas.groupby("produto", sort=False):
            if len(grp) < max(3, min_hist):
                continue

            vals = grp["quantidade_padronizada"].astype(float).values
            media = float(np.mean(vals))
            desvio = float(np.std(vals, ddof=0))
            if desvio <= 1e-6:
                continue

            for _, row in grp.iterrows():
                qtd = float(row["quantidade_padronizada"])
                z_score = (qtd - media) / desvio
                if z_score >= z_limiar and qtd > media * 1.4:
                    unid = str(row["unidade_padronizada"])
                    cat = str(row["categoria"])
                    lote = str(row["lote"])
                    mov_id = str(row["id_movimento"])
                    dt_mov = str(row["data_movimento"])
                    dest = str(row["destino_centro_custo"])
                    resp = str(row["responsavel"])

                    alerts.append(
                        Alert(
                            rule_id=self.rule_id,
                            titulo=f"Retirada Fora do Padrão Detectada: {prod}",
                            severidade="CRÍTICO" if z_score >= 2.4 else "ATENÇÃO",
                            score_prioridade=91 if z_score >= 2.4 else 78,
                            produto=str(prod),
                            categoria=cat,
                            lote_afetado=f"{lote} ({mov_id})",
                            indicador_chave=(
                                f"Retirada: {qtd:g} {unid} | Z-Score: +{z_score:.2f}σ (Média: {media:.1f} {unid})"
                            ),
                            justificativa_matematica=(
                                f"O lançamento {mov_id} em {dt_mov} registrou saída de {qtd:g} {unid} para "
                                f"'{dest}' (Resp.: {resp}), situando-se a +{z_score:.2f} desvios-padrão acima da "
                                f"média histórica de {media:.1f} ± {desvio:.1f} {unid} (Limiar Z >= {z_limiar:.1f})."
                            ),
                            recomendacao_gerencial=(
                                f"Auditar com {resp} se a retirada de {qtd:g} {unid} em '{dest}' corresponde "
                                f"a uma operação extraordinária autorizada, erro de digitação de unidade ou desvio físico."
                            ),
                        )
                    )

        return alerts


class ProgressiveDemandTrendAlertRule(BaseAlertRule):
    """Regra 4: Detecta tendência de aumento progressivo de consumo entre janelas consecutivas."""

    rule_id = "RULE_TENDENCIA_ALTA"
    rule_name = "Aumento Progressivo de Demanda"
    description = "Detecta aceleração consistente no ritmo de consumo de um insumo ao longo do tempo."

    def evaluate(
        self, df_movs: pd.DataFrame, df_saldos: pd.DataFrame, config: Dict[str, Any]
    ) -> List[Alert]:
        alerts: List[Alert] = []
        if df_movs.empty:
            return alerts

        params = config.get("parametros_regras", {})
        cresc_limiar = float(params.get("crescimento_progressivo_pct", 30.0))
        min_hist = int(params.get("min_historico_saidas", 3))

        df_saidas = df_movs[df_movs["tipo_movimento"] == "Saída"].sort_values("data_movimento_dt")
        for prod, grp in df_saidas.groupby("produto", sort=False):
            if len(grp) < max(4, min_hist):
                continue

            vals = grp["quantidade_padronizada"].astype(float).values
            meio = len(vals) // 2
            media_inicial = float(np.mean(vals[:meio]))
            media_recente = float(np.mean(vals[meio:]))
            if media_inicial <= 0:
                continue

            crescimento_pct = ((media_recente - media_inicial) / media_inicial) * 100.0
            # Verifica também se a tendência linear (slope) é positiva
            x = np.arange(len(vals), dtype=float)
            slope = float(np.polyfit(x, vals, 1)[0])

            if crescimento_pct >= cresc_limiar and slope > 0:
                unid = str(grp["unidade_padronizada"].iloc[0])
                cat = str(grp["categoria"].iloc[0])
                lote = str(grp["lote"].iloc[-1])

                alerts.append(
                    Alert(
                        rule_id=self.rule_id,
                        titulo=f"Crescimento Progressivo de Demanda: {prod}",
                        severidade="ATENÇÃO",
                        score_prioridade=76,
                        produto=str(prod),
                        categoria=cat,
                        lote_afetado=lote,
                        indicador_chave=f"Alta de +{crescimento_pct:.1f}% no volume por retirada (Limiar: {cresc_limiar:g}%)",
                        justificativa_matematica=(
                            f"A média das retiradas recentes subiu para {media_recente:.1f} {unid} contra "
                            f"{media_inicial:.1f} {unid} no período inicial (+{crescimento_pct:.1f}%, "
                            f"taxa de inclinação +{slope:.1f} {unid}/evento)."
                        ),
                        recomendacao_gerencial=(
                            "Revisar o estoque de segurança para cima ou verificar se houve aumento de lotação/dose "
                            "aplicada nos pastos e semiconfinamento."
                        ),
                    )
                )

        return alerts


class PriceInflationAlertRule(BaseAlertRule):
    """Regra 5: Detecta inflação abrupta no custo unitário de aquisição entre compras."""

    rule_id = "RULE_VARIACAO_PRECO"
    rule_name = "Inflação Abrupta de Preço de Aquisição"
    description = "Monitora variações percentuais de custo unitário nas entradas em relação à média histórica."

    def evaluate(
        self, df_movs: pd.DataFrame, df_saldos: pd.DataFrame, config: Dict[str, Any]
    ) -> List[Alert]:
        alerts: List[Alert] = []
        if df_movs.empty:
            return alerts

        params = config.get("parametros_regras", {})
        var_limiar = float(params.get("variacao_preco_pct", 20.0))

        df_ent = df_movs[df_movs["tipo_movimento"] == "Entrada"].dropna(subset=["custo_unitario_padronizado"])
        df_ent = df_ent.sort_values("data_movimento_dt")

        for prod, grp in df_ent.groupby("produto", sort=False):
            if len(grp) < 2:
                continue

            custos = grp["custo_unitario_padronizado"].astype(float).values
            custo_ultimo = float(custos[-1])
            media_anterior = float(np.mean(custos[:-1]))
            if media_anterior <= 0:
                continue

            variacao_pct = ((custo_ultimo - media_anterior) / media_anterior) * 100.0
            if variacao_pct >= var_limiar:
                ult_row = grp.iloc[-1]
                unid = str(ult_row["unidade_padronizada"])
                cat = str(ult_row["categoria"])
                lote = str(ult_row["lote"])
                dt_compra = str(ult_row["data_movimento"])

                alerts.append(
                    Alert(
                        rule_id=self.rule_id,
                        titulo=f"Alta Abrupta no Preço de Compra: {prod}",
                        severidade="ATENÇÃO",
                        score_prioridade=74,
                        produto=str(prod),
                        categoria=cat,
                        lote_afetado=lote,
                        indicador_chave=(
                            f"Variação: +{variacao_pct:.1f}% (R$ {media_anterior:.2f} -> R$ {custo_ultimo:.2f}/{unid})"
                        ),
                        justificativa_matematica=(
                            f"A entrada do lote {lote} em {dt_compra} foi registrada a R$ {custo_ultimo:.2f}/{unid}, "
                            f"representando aumento de +{variacao_pct:.1f}% sobre o custo médio anterior de "
                            f"R$ {media_anterior:.2f}/{unid} (Limiar configurado: {var_limiar:g}%)."
                        ),
                        recomendacao_gerencial=(
                            "Diversificar cotação com novos fornecedores ou avaliar compras conjuntas/antecipadas "
                            "para proteger a margem operacional da safra."
                        ),
                    )
                )

        return alerts


class IdleCapitalAlertRule(BaseAlertRule):
    """Regra 6: Identifica itens com alto capital financeiro imobilizado / sem giro."""

    rule_id = "RULE_CAPITAL_PARADO"
    rule_name = "Capital Imobilizado e Excesso de Estoque"
    description = "Detecta produtos parados há muitos dias sem saída ou com autonomia excessiva."

    def evaluate(
        self, df_movs: pd.DataFrame, df_saldos: pd.DataFrame, config: Dict[str, Any]
    ) -> List[Alert]:
        alerts: List[Alert] = []
        if df_saldos.empty:
            return alerts

        params = config.get("parametros_regras", {})
        dias_parado_lim = int(params.get("dias_capital_parado", 45))
        autonomia_exc_lim = float(params.get("autonomia_excesso_dias", 180))

        for _, row in df_saldos.iterrows():
            saldo = float(row["saldo_atual"])
            if saldo <= 0:
                continue

            prod = str(row["produto"])
            cat = str(row["categoria"])
            unid = str(row["unidade_padronizada"])
            lote = str(row["lote_fefo"])
            valor_est = float(row["valor_estoque_atual"])
            dias_sem_saida = row.get("dias_sem_saida")
            autonomia = row.get("autonomia_dias")
            tag_conf = str(row["tag_confianca"])
            incerteza = bool(row["incerteza_alta"])

            parado_por_tempo = (
                dias_sem_saida is not None and pd.notna(dias_sem_saida) and int(dias_sem_saida) >= dias_parado_lim
            )
            parado_por_autonomia = (
                autonomia is not None and pd.notna(autonomia) and float(autonomia) >= autonomia_exc_lim
            )

            if parado_por_tempo or parado_por_autonomia:
                dias_str = f"{int(dias_sem_saida)} dias sem saída" if pd.notna(dias_sem_saida) else "Sem saídas"
                aut_str = f"Autonomia: {float(autonomia):.0f} dias" if pd.notna(autonomia) else "Giro Nulo"
                alerts.append(
                    Alert(
                        rule_id=self.rule_id,
                        titulo=f"Capital Imobilizado em Estoque Parado: {prod}",
                        severidade="INFORMATIVO" if valor_est < 8000 else "ATENÇÃO",
                        score_prioridade=64 if valor_est >= 8000 else 55,
                        produto=prod,
                        categoria=cat,
                        lote_afetado=lote,
                        indicador_chave=f"Capital Parado: R$ {valor_est:,.2f} | {dias_str} ({aut_str})",
                        justificativa_matematica=(
                            f"O insumo acumula saldo de {saldo:g} {unid} avaliado em R$ {valor_est:,.2f}, "
                            f"permanecendo {dias_str} (limiar de imobilização: {dias_parado_lim} dias; "
                            f"{aut_str}, limiar de excesso: {autonomia_exc_lim:g} dias). {tag_conf}"
                        ),
                        recomendacao_gerencial=(
                            "Suspender novas aquisições deste item e verificar cronograma técnico de aplicação "
                            "nos talhões ou manutenção para liberar fluxo de caixa."
                        ),
                        aviso_incerteza=tag_conf if incerteza else "",
                    )
                )

        return alerts


class PesticidePackagingAlertRule(BaseAlertRule):
    """Regra 7: Monitora a logística reversa de embalagens vazias de agrotóxicos e biológicos."""

    rule_id = "RULE_EMBALAGENS_DEFENSIVOS"
    rule_name = "Conformidade Legal de Embalagens (inpEV)"
    description = "Rastreia retiradas de defensivos químicos e biológicos com devolução de embalagem pendente ou vencida."

    def evaluate(
        self, df_movs: pd.DataFrame, df_saldos: pd.DataFrame, config: Dict[str, Any]
    ) -> List[Alert]:
        alerts: List[Alert] = []
        if df_movs.empty:
            return alerts

        df_def = df_movs[
            (df_movs["tipo_movimento"] == "Saída")
            & (df_movs["categoria"].isin(["Defensivos Químicos", "Defensivos Biológicos"]))
            & (df_movs["devolucao_embalagem"].isin(["Pendente", "Prazo Vencido"]))
        ]

        if df_def.empty:
            return alerts

        for prod, grp in df_def.groupby("produto", sort=False):
            qtd_vencidas = int((grp["devolucao_embalagem"] == "Prazo Vencido").sum())
            qtd_pendentes = int((grp["devolucao_embalagem"] == "Pendente").sum())
            vol_total = float(grp["quantidade_padronizada"].sum())
            unid = str(grp["unidade_padronizada"].iloc[0])
            cat = str(grp["categoria"].iloc[0])
            lotes = ", ".join(sorted(grp["lote"].astype(str).unique()))

            severidade = "CRÍTICO" if qtd_vencidas > 0 else "ATENÇÃO"
            score = 92 if qtd_vencidas > 0 else 70

            alerts.append(
                Alert(
                    rule_id=self.rule_id,
                    titulo=f"Logística Reversa de Embalagens Pendente: {prod}",
                    severidade=severidade,
                    score_prioridade=score,
                    produto=str(prod),
                    categoria=cat,
                    lote_afetado=lotes,
                    indicador_chave=(
                        f"{qtd_vencidas} Prazo Vencido | {qtd_pendentes} Pendente(s) ({vol_total:g} {unid} aplicados)"
                    ),
                    justificativa_matematica=(
                        f"Foram identificadas {qtd_vencidas + qtd_pendentes} retiradas de '{prod}' (Lotes: {lotes}) "
                        f"totalizando {vol_total:g} {unid} aplicados sem comprovante de devolução das embalagens vazias "
                        f"({qtd_vencidas} com prazo vencido e {qtd_pendentes} aguardando entrega)."
                    ),
                    recomendacao_gerencial=(
                        "Realizar tríplice lavagem/pressurização, armazenar temporariamente no depósito de embalagens "
                        "vazias e agendar entrega imediata na central inpEV de Ariquemes/RO (Lei 14.785/2023)."
                    ),
                )
            )

        return alerts


class RuleRegistry:
    """
    Registro central de regras analíticas do AgroZica.
    Permite plugar novas regras ou ativar/desativar regras existentes dinamicamente via settings.json.
    """

    def __init__(self) -> None:
        self._rules: Dict[str, BaseAlertRule] = {}
        self._register_default_rules()

    def _register_default_rules(self) -> None:
        default_rules: List[BaseAlertRule] = [
            StockAutonomyAlertRule(),
            ExpirationVsTurnoverAlertRule(),
            WithdrawalAnomalyAlertRule(),
            ProgressiveDemandTrendAlertRule(),
            PriceInflationAlertRule(),
            IdleCapitalAlertRule(),
            PesticidePackagingAlertRule(),
        ]
        for rule in default_rules:
            self.register(rule)

    def register(self, rule: BaseAlertRule) -> None:
        """Pluga uma nova instância de BaseAlertRule no motor."""
        self._rules[rule.rule_id] = rule

    def get_all_rules(self) -> List[BaseAlertRule]:
        return list(self._rules.values())

    def evaluate_all(
        self, df_movs: pd.DataFrame, df_saldos: pd.DataFrame, config: Dict[str, Any]
    ) -> List[Alert]:
        """Executa todas as regras ativas e retorna a lista de alertas ordenada por prioridade."""
        active_map = config.get("regras_ativas", {})
        all_alerts: List[Alert] = []

        for rule_id, rule in self._rules.items():
            if active_map.get(rule_id, True):
                rule_alerts = rule.evaluate(df_movs, df_saldos, config)
                all_alerts.extend(rule_alerts)

        # Ordena por score_prioridade decrescente
        all_alerts.sort(key=lambda a: a.score_prioridade, reverse=True)
        return all_alerts

