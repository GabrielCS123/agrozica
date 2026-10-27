"""
Aba 1: Painel de Decisão Executiva, Alertas Priorizados e Conciliação de Saldos (DashboardTemplate).
Apresenta:
- 5 KPICards executivos no topo;
- Barra de filtros dinâmicos por Severidade, Categoria e Busca Textual;
- Feed rolável de AlertBanners com justificativas matemáticas transparentes em linguagem natural;
- Tabela interativa (DataGrid) com Saldos Padronizados, CMD, Autonomia (dias), Lote FEFO,
  Curva ABC e Tag de Confiança Estatística ([Incerteza Alta: Pouco Histórico]).
"""

from typing import Dict, Any, List, Tuple
import customtkinter as ctk

from src.templates.theme import AgroTheme
from src.templates.components import KPICard, AlertBanner, FilterToolbar, DataGrid
from src.controllers.main_controller import MainController


class DashboardTemplate(ctk.CTkFrame):
    """View principal de Apoio à Decisão do Gestor Rural."""

    def __init__(self, master: Any, controller: MainController, **kwargs: Any) -> None:
        super().__init__(master, fg_color="transparent", **kwargs)
        self.controller = controller
        self.filter_state: Dict[str, str] = {
            "busca": "",
            "Severidade": "TODOS",
            "Categoria": "TODAS",
        }

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=5)
        self.grid_rowconfigure(4, weight=4)

        self._build_kpi_row()
        self._build_filter_bar()
        self._build_alerts_section()
        self._build_inventory_table_section()

        self.controller.subscribe(self.refresh_view)
        self.refresh_view()

    def _build_kpi_row(self) -> None:
        kpi_frame = ctk.CTkFrame(self, fg_color="transparent")
        kpi_frame.grid(row=0, column=0, sticky="ew", padx=4, pady=(0, 8))
        for i in range(5):
            kpi_frame.grid_columnconfigure(i, weight=1)

        self.kpi_alertas_crit = KPICard(
            kpi_frame,
            title="Alertas Críticos",
            value="0",
            subtitle="Ruptura / Vencimento / Anomalia",
            accent_color=AgroTheme.ACCENT_DANGER,
        )
        self.kpi_alertas_crit.grid(row=0, column=0, sticky="ew", padx=(0, 6))

        self.kpi_alertas_aten = KPICard(
            kpi_frame,
            title="Alertas de Atenção",
            value="0",
            subtitle="Preventivos e Tendências",
            accent_color=AgroTheme.ACCENT_AMBER,
        )
        self.kpi_alertas_aten.grid(row=0, column=1, sticky="ew", padx=6)

        self.kpi_capital = KPICard(
            kpi_frame,
            title="Capital em Estoque",
            value="R$ 0,00",
            subtitle="Avaliado pelo custo médio auditado",
            accent_color=AgroTheme.ACCENT_EMERALD,
        )
        self.kpi_capital.grid(row=0, column=2, sticky="ew", padx=6)

        self.kpi_consumo = KPICard(
            kpi_frame,
            title="Custo Aplicado (500ha)",
            value="R$ 0,00",
            subtitle="Saídas apropriadas sem duplicidade",
            accent_color=AgroTheme.ACCENT_INFO,
        )
        self.kpi_consumo.grid(row=0, column=3, sticky="ew", padx=6)

        self.kpi_incerteza = KPICard(
            kpi_frame,
            title="Governança & Auditoria",
            value="0",
            subtitle="Itens tratados pelo DataCleaner",
            accent_color=AgroTheme.ACCENT_PURPLE,
        )
        self.kpi_incerteza.grid(row=0, column=4, sticky="ew", padx=(6, 0))

    def _build_filter_bar(self) -> None:
        cats = ["TODAS"] + self.controller.config_model.get_categories()
        sevs = ["TODOS", "CRÍTICO", "ATENÇÃO", "INFORMATIVO"]

        self.toolbar = FilterToolbar(
            self,
            search_placeholder="Produto, lote ou palavra-chave...",
            dropdown_configs=[
                ("Severidade", sevs, "TODOS"),
                ("Categoria", cats, "TODAS"),
            ],
            on_filter_change=self._on_filter_changed,
        )
        self.toolbar.grid(row=1, column=0, sticky="ew", padx=4, pady=(0, 8))

    def _build_alerts_section(self) -> None:
        container = ctk.CTkFrame(
            self,
            fg_color=AgroTheme.BG_SIDEBAR,
            corner_radius=10,
            border_width=1,
            border_color=AgroTheme.BORDER_COLOR,
        )
        container.grid(row=2, column=0, sticky="nsew", padx=4, pady=(0, 8))
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(container, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=12, pady=(8, 4))
        header.grid_columnconfigure(0, weight=1)

        self.lbl_alerts_header = ctk.CTkLabel(
            header,
            text="🚨 Central de Alertas Priorizados com Justificativa Matemática Transparente",
            font=ctk.CTkFont(family=AgroTheme.FONT_FAMILY, size=14, weight="bold"),
            text_color=AgroTheme.TEXT_PRIMARY,
            anchor="w",
        )
        self.lbl_alerts_header.grid(row=0, column=0, sticky="w")

        lbl_hint = ctk.CTkLabel(
            header,
            text="Ordenado automaticamente por Score de Criticidade (P99 → P50)",
            font=ctk.CTkFont(family=AgroTheme.FONT_FAMILY, size=11),
            text_color=AgroTheme.TEXT_MUTED,
            anchor="e",
        )
        lbl_hint.grid(row=0, column=1, sticky="e")

        self.alerts_scroll = ctk.CTkScrollableFrame(
            container,
            fg_color=AgroTheme.BG_ROOT,
            corner_radius=8,
        )
        self.alerts_scroll.grid(row=1, column=0, sticky="nsew", padx=10, pady=(2, 10))
        self.alerts_scroll.grid_columnconfigure(0, weight=1)

    def _build_inventory_table_section(self) -> None:
        lbl_sec = ctk.CTkLabel(
            self,
            text="📦 Matriz Consolidada de Saldos Padronizados, Autonomia (CMD), Validade FEFO, Curva ABC e Nível de Confiança",
            font=ctk.CTkFont(family=AgroTheme.FONT_FAMILY, size=13, weight="bold"),
            text_color=AgroTheme.TEXT_PRIMARY,
            anchor="w",
        )
        lbl_sec.grid(row=3, column=0, sticky="ew", padx=8, pady=(2, 4))

        columns = [
            ("produto", "Insumo Padronizado", 210, "w"),
            ("categoria", "Categoria", 145, "w"),
            ("saldo", "Saldo Atual", 105, "e"),
            ("cmd", "CMD (Giro/Dia)", 105, "e"),
            ("autonomia", "Autonomia Est.", 115, "center"),
            ("fefo", "Lote FEFO (Próx. Venc.)", 175, "center"),
            ("custo_med", "Custo Médio", 105, "e"),
            ("valor_est", "Capital Estoque", 120, "e"),
            ("abc", "Curva ABC", 85, "center"),
            ("confianca", "Confiança Estatística / Status", 220, "w"),
        ]
        self.grid_saldos = DataGrid(self, columns=columns, height=8)
        self.grid_saldos.grid(row=4, column=0, sticky="nsew", padx=4, pady=(0, 4))

    def _on_filter_changed(self, state: Dict[str, str]) -> None:
        self.filter_state = state
        self.refresh_view()

    def refresh_view(self) -> None:
        """Atualiza KPIs, banners de alertas e matriz de saldos em tempo real."""
        kpis = self.controller.get_dashboard_kpis()

        self.kpi_alertas_crit.update_data(
            value=f"{kpis['alertas_criticos']} Críticos",
            subtitle=f"{kpis['itens_ruptura']} insumo(s) em faixa de ruptura",
        )
        self.kpi_alertas_aten.update_data(
            value=f"{kpis['alertas_atencao']} Atenção | {kpis['alertas_info']} Info",
            subtitle=f"Total de {kpis['total_alertas']} alertas ativos no motor",
        )
        self.kpi_capital.update_data(
            value=f"R$ {kpis['valor_estoque_total']:,.2f}",
            subtitle=f"{kpis['total_insumos']} insumos monitorados",
        )
        self.kpi_consumo.update_data(
            value=f"R$ {kpis['valor_consumido_total']:,.2f}",
            subtitle=f"{kpis['total_movimentacoes']} movimentações processadas",
        )
        self.kpi_incerteza.update_data(
            value=f"{kpis['total_auditoria']} Tratamentos",
            subtitle=f"{kpis['itens_incerteza']} c/ Incerteza Alta | {kpis['embalagens_pendentes']} Emb. inpEV",
        )

        # Atualiza Alertas
        alerts = self.controller.get_prioritized_alerts(
            severidade_filter=self.filter_state.get("Severidade", "TODOS"),
            categoria_filter=self.filter_state.get("Categoria", "TODAS"),
            busca_texto=self.filter_state.get("busca", ""),
        )
        self.lbl_alerts_header.configure(
            text=f"🚨 Central de Alertas Priorizados com Justificativa Matemática ({len(alerts)} exibidos)"
        )

        for child in self.alerts_scroll.winfo_children():
            child.destroy()

        if not alerts:
            empty_lbl = ctk.CTkLabel(
                self.alerts_scroll,
                text="✅ Nenhum alerta ativo para os filtros selecionados.",
                font=ctk.CTkFont(family=AgroTheme.FONT_FAMILY, size=13),
                text_color=AgroTheme.TEXT_MUTED,
            )
            empty_lbl.grid(row=0, column=0, pady=24)
        else:
            for idx, alert in enumerate(alerts):
                banner = AlertBanner(self.alerts_scroll, alert=alert)
                banner.grid(row=idx, column=0, sticky="ew", padx=6, pady=5)

        # Atualiza Tabela de Saldos
        summaries = self.controller.get_product_summaries(
            categoria_filter=self.filter_state.get("Categoria", "TODAS"),
            busca_texto=self.filter_state.get("busca", ""),
        )

        rows_data: List[Tuple[Tuple[Any, ...], str]] = []
        for s in summaries:
            aut_str = f"{s.autonomia_dias:.1f} dias" if s.autonomia_dias is not None else "Sem Giro"
            if s.validade_fefo and s.dias_para_vencer_fefo is not None:
                fefo_str = f"{s.lote_fefo} ({s.dias_para_vencer_fefo}d | {s.validade_fefo})"
            else:
                fefo_str = f"{s.lote_fefo} (Pendente / N.A.)"

            custo_str = (
                f"R$ {s.custo_medio_unitario:,.2f}/{s.unidade_padronizada}"
                if s.custo_medio_unitario is not None
                else "Pendente / Ausente"
            )
            abc_str = f"Classe {s.classe_abc} ({s.percentual_valor_abc:.1f}%)"

            if s.status_operacional == "Crítico":
                tag = "critico"
            elif s.status_operacional == "Atenção":
                tag = "atencao"
            elif s.incerteza_alta:
                tag = "incerteza"
            elif s.status_operacional == "Excesso/Parado":
                tag = "info"
            else:
                tag = "normal"

            rows_data.append(
                (
                    (
                        s.produto,
                        s.categoria,
                        f"{s.saldo_atual:g} {s.unidade_padronizada}",
                        f"{s.consumo_medio_diario:.2f} {s.unidade_padronizada}/dia",
                        aut_str,
                        fefo_str,
                        custo_str,
                        f"R$ {s.valor_estoque_atual:,.2f}",
                        abc_str,
                        f"{s.status_operacional} • {s.tag_confianca}",
                    ),
                    tag,
                )
            )

        self.grid_saldos.clear_and_populate(rows_data)

