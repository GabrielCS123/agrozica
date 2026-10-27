"""
Orquestrador Central MTC (MainController) do AgroZica.
Implementa o padrão Observer para notificar automaticamente todas as abas (Templates)
sempre que:
1. Um novo lançamento de Entrada/Saída é registrado;
2. Uma planilha oficial do AGROHACK (.csv ou .xlsx) é importada via ColumnMapper;
3. Qualquer limiar matemático ou checkbox de regra é alterado na Aba de Configurações.
"""

from pathlib import Path
from typing import Callable, List, Dict, Any, Tuple
import pandas as pd

from src.models.config_model import ConfigModel
from src.models.inventory_model import InventoryModel
from src.models.rules_engine import RuleRegistry, BaseAlertRule
from src.models.entities import Alert, ResumoProduto, SaldoLote, ItemAuditoria
from generator_seed import generate_seed_csv


class MainController:
    """Controlador central do padrão MTC com suporte reativo (Observer Pattern)."""

    def __init__(self) -> None:
        self.config_model = ConfigModel()
        self.inventory_model = InventoryModel(self.config_model)
        self.rule_registry = RuleRegistry()
        self._observers: List[Callable[[], None]] = []
        self.alerts: List[Alert] = []
        self.refresh_analysis(notify=False)

    # =========================================================================
    # OBSERVER PATTERN (ATUALIZAÇÃO REATIVA EM TEMPO REAL)
    # =========================================================================
    def subscribe(self, callback: Callable[[], None]) -> None:
        """Registra uma View/Template para receber atualizações automáticas de estado."""
        if callback not in self._observers:
            self._observers.append(callback)

    def notify_observers(self) -> None:
        """Notifica todas as Views inscritas para redesenhar KPIs, tabelas e gráficos."""
        for callback in self._observers:
            try:
                callback()
            except Exception as exc:
                print(f"[AgroZica Controller] Aviso ao atualizar observer: {exc}")

    def refresh_analysis(self, notify: bool = True) -> None:
        """Recalcula saldos, conciliação por lote, FEFO e executa todas as regras ativas."""
        self.inventory_model.recalculate_all()
        self.alerts = self.rule_registry.evaluate_all(
            self.inventory_model.df_clean,
            self.inventory_model.df_saldos,
            self.config_model.data,
        )
        if notify:
            self.notify_observers()

    # =========================================================================
    # CONSULTAS PARA OS TEMPLATES (DASHBOARD, ANALYTICS, AUDIT)
    # =========================================================================
    def get_dashboard_kpis(self) -> Dict[str, Any]:
        """Retorna os indicadores executivos consolidados para os KPICards e Status Bar."""
        resumos = self.inventory_model.resumos_produto
        df_clean = self.inventory_model.df_clean

        valor_estoque_total = sum(r.valor_estoque_atual for r in resumos)
        valor_consumido_total = sum(r.valor_consumido_total for r in resumos)

        alertas_criticos = sum(1 for a in self.alerts if a.severidade == "CRÍTICO")
        alertas_atencao = sum(1 for a in self.alerts if a.severidade == "ATENÇÃO")
        alertas_info = sum(1 for a in self.alerts if a.severidade == "INFORMATIVO")

        itens_ruptura = sum(1 for r in resumos if r.status_operacional == "Crítico")
        itens_incerteza = sum(1 for r in resumos if r.incerteza_alta)
        divergencias_lote = sum(1 for l in self.inventory_model.saldos_lote if l.divergencia_conciliacao)

        emb_pendentes = 0
        if not df_clean.empty:
            emb_pendentes = int(
                df_clean[
                    (df_clean["tipo_movimento"] == "Saída")
                    & (df_clean["devolucao_embalagem"].isin(["Pendente", "Prazo Vencido"]))
                ].shape[0]
            )

        return {
            "total_insumos": len(resumos),
            "total_movimentacoes": len(df_clean),
            "valor_estoque_total": round(valor_estoque_total, 2),
            "valor_consumido_total": round(valor_consumido_total, 2),
            "total_alertas": len(self.alerts),
            "alertas_criticos": alertas_criticos,
            "alertas_atencao": alertas_atencao,
            "alertas_info": alertas_info,
            "itens_ruptura": itens_ruptura,
            "itens_incerteza": itens_incerteza,
            "divergencias_lote": divergencias_lote,
            "embalagens_pendentes": emb_pendentes,
            "total_auditoria": len(self.inventory_model.itens_auditoria),
        }

    def get_prioritized_alerts(
        self,
        severidade_filter: str = "TODOS",
        categoria_filter: str = "TODAS",
        busca_texto: str = "",
    ) -> List[Alert]:
        """Filtra a lista de alertas priorizados conforme seleção do usuário."""
        result = self.alerts
        if severidade_filter and severidade_filter != "TODOS":
            result = [a for a in result if a.severidade == severidade_filter]
        if categoria_filter and categoria_filter != "TODAS":
            result = [a for a in result if a.categoria == categoria_filter]
        if busca_texto.strip():
            q = busca_texto.strip().lower()
            result = [
                a
                for a in result
                if q in a.produto.lower()
                or q in a.titulo.lower()
                or q in a.justificativa_matematica.lower()
                or q in a.lote_afetado.lower()
            ]
        return result

    def get_product_summaries(
        self,
        categoria_filter: str = "TODAS",
        status_filter: str = "TODOS",
        busca_texto: str = "",
    ) -> List[ResumoProduto]:
        """Retorna a lista de ResumoProduto filtrada para as tabelas de decisão."""
        res = list(self.inventory_model.resumos_produto)
        if categoria_filter and categoria_filter != "TODAS":
            res = [r for r in res if r.categoria == categoria_filter]
        if status_filter and status_filter != "TODOS":
            res = [r for r in res if r.status_operacional == status_filter]
        if busca_texto.strip():
            q = busca_texto.strip().lower()
            res = [r for r in res if q in r.produto.lower() or q in r.lote_fefo.lower()]
        # Ordena por menor autonomia primeiro
        res.sort(key=lambda r: (r.autonomia_dias if r.autonomia_dias is not None else 9999.0))
        return res

    def get_audit_items(self, tipo_filter: str = "TODOS", busca_texto: str = "") -> List[ItemAuditoria]:
        """Filtra os apontamentos de governança e auditoria de dados."""
        items = list(self.inventory_model.itens_auditoria)
        if tipo_filter and tipo_filter != "TODOS":
            items = [i for i in items if i.tipo_inconsistencia == tipo_filter]
        if busca_texto.strip():
            q = busca_texto.strip().lower()
            items = [
                i
                for i in items
                if q in i.produto.lower()
                or q in i.valor_original.lower()
                or q in i.tratamento_aplicado.lower()
                or q in i.id_movimento.lower()
            ]
        return items

    def get_packaging_records(self) -> pd.DataFrame:
        """Retorna todas as saídas de defensivos químicos e biológicos para rastreamento inpEV."""
        df = self.inventory_model.df_clean
        if df.empty:
            return pd.DataFrame()
        return df[
            (df["tipo_movimento"] == "Saída")
            & (df["categoria"].isin(["Defensivos Químicos", "Defensivos Biológicos"]))
        ].copy()

    # =========================================================================
    # OPERAÇÕES DE LANÇAMENTO, IMPORTAÇÃO OFICIAL E EXPORTAÇÃO
    # =========================================================================
    def register_new_movement(self, form_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Valida e registra uma nova Entrada ou Saída com reanálise instantânea."""
        try:
            produto = str(form_data.get("produto", "")).strip()
            if not produto:
                return False, "Informe o nome do insumo/produto."

            qtd_str = str(form_data.get("quantidade", "")).replace(",", ".").strip()
            try:
                qtd = float(qtd_str)
                if qtd <= 0:
                    return False, "A quantidade deve ser maior que zero."
            except ValueError:
                return False, "Quantidade inválida. Informe um número positivo."

            record = {
                "id_movimento": str(form_data.get("id_movimento", "")).strip(),
                "data_movimento": str(form_data.get("data_movimento", "2026-10-27")).strip(),
                "tipo_movimento": str(form_data.get("tipo_movimento", "Saída")).strip(),
                "produto": produto,
                "categoria": str(form_data.get("categoria", "Fertilizantes")).strip(),
                "lote": str(form_data.get("lote", "LOTE-2026")).strip() or "LOTE-2026",
                "quantidade": qtd,
                "unidade": str(form_data.get("unidade", "kg")).strip() or "kg",
                "custo_unitario": str(form_data.get("custo_unitario", "")).strip(),
                "data_validade": str(form_data.get("data_validade", "")).strip(),
                "destino_centro_custo": str(form_data.get("destino_centro_custo", "")).strip(),
                "responsavel": str(form_data.get("responsavel", "Operador AgroZica")).strip() or "Operador AgroZica",
                "devolucao_embalagem": str(form_data.get("devolucao_embalagem", "Não Aplicável")).strip(),
            }

            mov_id = self.inventory_model.add_movement(record, persist=True)
            self.refresh_analysis(notify=True)
            return True, f"Movimentação {mov_id} registrada e analisada em tempo real!"
        except Exception as exc:
            return False, f"Erro ao registrar movimentação: {exc}"

    def import_external_spreadsheet(self, file_path: str | Path) -> Tuple[bool, str]:
        """
        Importa uma planilha oficial do AGROHACK (.csv ou .xlsx), aplica o ColumnMapper,
        executa o DataCleaner e atualiza todas as abas.
        """
        try:
            self.inventory_model.load_from_file(file_path)
            self.refresh_analysis(notify=True)
            mapped_count = len(self.inventory_model.ultimo_mapeamento_colunas)
            total_rows = len(self.inventory_model.df_clean)
            return (
                True,
                f"Planilha importada com sucesso ({total_rows} registros, {mapped_count} colunas mapeadas pelo ColumnMapper).",
            )
        except Exception as exc:
            return False, f"Falha ao importar planilha: {exc}"

    def export_consolidated_report(self, target_path: str | Path) -> Tuple[bool, str]:
        """Exporta o relatório analítico consolidado de saldos, alertas e auditoria em CSV ou XLSX."""
        try:
            path = Path(target_path)
            if path.suffix.lower() == ".xlsx":
                with pd.ExcelWriter(path, engine="openpyxl") as writer:
                    self.inventory_model.df_saldos.to_excel(writer, sheet_name="Saldos_FEFO_ABC", index=False)
                    pd.DataFrame([a.__dict__ for a in self.alerts]).to_excel(
                        writer, sheet_name="Alertas_Priorizados", index=False
                    )
                    pd.DataFrame([i.__dict__ for i in self.inventory_model.itens_auditoria]).to_excel(
                        writer, sheet_name="Trilha_Auditoria", index=False
                    )
                    self.inventory_model.df_clean.drop(columns=["data_movimento_dt"], errors="ignore").to_excel(
                        writer, sheet_name="Movimentos_Higienizados", index=False
                    )
            else:
                self.inventory_model.df_saldos.to_csv(path, index=False, encoding="utf-8-sig")
            return True, f"Relatório consolidado exportado em: {path.name}"
        except Exception as exc:
            return False, f"Erro ao exportar relatório: {exc}"

    def reload_simulated_seed(self) -> Tuple[bool, str]:
        """Regenera a base simulada de 500ha padrão e recalcula todos os indicadores."""
        try:
            out_path = generate_seed_csv(self.inventory_model.csv_path)
            self.inventory_model.load_from_file(out_path)
            self.refresh_analysis(notify=True)
            return True, "Base simulada oficial (500ha) restaurada e reanalisada com sucesso!"
        except Exception as exc:
            return False, f"Erro ao restaurar base simulada: {exc}"

    # =========================================================================
    # MUTABILIDADE EM TEMPO REAL (ABA DE CONFIGURAÇÕES)
    # =========================================================================
    def update_parameters_batch(self, new_params: Dict[str, Any], active_rules: Dict[str, bool]) -> Tuple[bool, str]:
        """Salva novos parâmetros matemáticos e estados de regras no settings.json e recalcula tudo."""
        try:
            for k, v in new_params.items():
                self.config_model.set_param(k, v, auto_save=False)
            for r_id, state in active_rules.items():
                self.config_model.set_rule_active(r_id, state, auto_save=False)
            self.config_model.save()
            self.refresh_analysis(notify=True)
            return True, "Parâmetros e regras aplicados ao vivo! Painéis e alertas recalculados."
        except Exception as exc:
            return False, f"Erro ao salvar configurações: {exc}"

    def reset_parameters_to_default(self) -> Tuple[bool, str]:
        """Restaura parâmetros recomendados de fábrica e recalcula."""
        self.config_model.reset_to_defaults()
        self.refresh_analysis(notify=True)
        return True, "Parâmetros restaurados para os valores de referência AgroZica 500ha."

    def get_all_rules_metadata(self) -> List[BaseAlertRule]:
        return self.rule_registry.get_all_rules()

