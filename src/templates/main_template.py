"""
Janela Mestre (MainTemplate) do sistema desktop AgroZica.
Integra o menu lateral de navegação (Dark Mode Verde Floresta), cabeçalho executivo
da propriedade de 500ha, as 5 Views especializadas e a barra de status inferior reativa.
"""

from typing import Dict, Any
import customtkinter as ctk

from src.templates.theme import AgroTheme
from src.templates.dashboard_template import DashboardTemplate
from src.templates.analytics_template import AnalyticsTemplate
from src.templates.operations_template import OperationsTemplate
from src.templates.audit_template import AuditTemplate
from src.templates.settings_template import SettingsTemplate
from src.controllers.main_controller import MainController


class MainTemplate(ctk.CTk):
    """Janela principal CustomTkinter do AgroZica."""

    def __init__(self, controller: MainController) -> None:
        AgroTheme.apply_global_theme()
        super().__init__()

        self.controller = controller
        self.title("AgroZica v2.6 — Inteligência Analítica e Gestão Rastreável de Insumos Rurais (AGROHACK 2026/2)")
        self.geometry("1420x860")
        self.minsize(1200, 740)
        self.configure(fg_color=AgroTheme.BG_ROOT)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.nav_buttons: Dict[str, ctk.CTkButton] = {}
        self.views: Dict[str, ctk.CTkFrame] = {}

        self._build_sidebar()
        self._build_top_header()
        self._build_content_area()
        self._build_statusbar()

        self.controller.subscribe(self._update_statusbar)
        self._update_statusbar()
        self.select_tab("dashboard")

    def _build_sidebar(self) -> None:
        sidebar = ctk.CTkFrame(
            self,
            width=255,
            fg_color=AgroTheme.BG_SIDEBAR,
            corner_radius=0,
            border_width=1,
            border_color=AgroTheme.BORDER_COLOR,
        )
        sidebar.grid(row=0, column=0, rowspan=3, sticky="nsew")
        sidebar.grid_propagate(False)
        sidebar.grid_columnconfigure(0, weight=1)
        sidebar.grid_rowconfigure(8, weight=1)

        # Identidade AgroZica
        brand_frame = ctk.CTkFrame(sidebar, fg_color=AgroTheme.BG_CARD, corner_radius=10)
        brand_frame.grid(row=0, column=0, sticky="ew", padx=14, pady=(18, 14))

        lbl_logo = ctk.CTkLabel(
            brand_frame,
            text="🌱 AGROZICA",
            font=ctk.CTkFont(family=AgroTheme.FONT_FAMILY, size=22, weight="bold"),
            text_color=AgroTheme.ACCENT_EMERALD,
        )
        lbl_logo.pack(padx=12, pady=(10, 0))

        lbl_sub = ctk.CTkLabel(
            brand_frame,
            text="Cérebro Analítico de Almoxarifado\nAGROHACK 2026/2 • IFRO Ariquemes",
            font=ctk.CTkFont(family=AgroTheme.FONT_FAMILY, size=11),
            text_color=AgroTheme.TEXT_SECONDARY,
        )
        lbl_sub.pack(padx=12, pady=(2, 10))

        nav_items = [
            ("dashboard", "🚨  1. Painel de Decisão & Alertas"),
            ("analytics", "📈  2. Inteligência Visual (500ha)"),
            ("operations", "➕  3. Lançamentos & Importação"),
            ("audit", "🛡️  4. Auditoria, Lotes & inpEV"),
            ("settings", "⚙️  5. Mutabilidade & Regras"),
        ]

        for idx, (tab_key, label_text) in enumerate(nav_items):
            btn = ctk.CTkButton(
                sidebar,
                text=label_text,
                anchor="w",
                height=42,
                corner_radius=8,
                font=ctk.CTkFont(family=AgroTheme.FONT_FAMILY, size=12, weight="bold"),
                fg_color="transparent",
                text_color=AgroTheme.TEXT_PRIMARY,
                hover_color=AgroTheme.BG_CARD_HOVER,
                command=lambda k=tab_key: self.select_tab(k),
            )
            btn.grid(row=idx + 1, column=0, sticky="ew", padx=12, pady=4)
            self.nav_buttons[tab_key] = btn

        # Card Resumo da Propriedade Modelo (500ha)
        farm_card = ctk.CTkFrame(
            sidebar,
            fg_color=AgroTheme.BG_CARD,
            corner_radius=8,
            border_width=1,
            border_color=AgroTheme.BORDER_COLOR,
        )
        farm_card.grid(row=9, column=0, sticky="ew", padx=12, pady=14)

        lbl_farm_title = ctk.CTkLabel(
            farm_card,
            text="🗺️ PROPRIEDADE MODELO (500 ha)",
            font=ctk.CTkFont(family=AgroTheme.FONT_FAMILY, size=11, weight="bold"),
            text_color=AgroTheme.ACCENT_AMBER,
        )
        lbl_farm_title.pack(anchor="w", padx=10, pady=(8, 4))

        farm_details = (
            "• Talhão 01: Soja (150 ha)\n"
            "• Talhão 02: Milho Safrinha (120 ha)\n"
            "• 30 Pastos Rotacionados (140 ha)\n"
            "• Semiconfinamento (200 Bovinos)\n"
            "• Silos, Cercas & Manutenção (90 ha)"
        )
        lbl_farm_desc = ctk.CTkLabel(
            farm_card,
            text=farm_details,
            font=ctk.CTkFont(family=AgroTheme.FONT_FAMILY, size=11),
            text_color=AgroTheme.TEXT_PRIMARY,
            justify="left",
        )
        lbl_farm_desc.pack(anchor="w", padx=10, pady=(0, 8))

    def _build_top_header(self) -> None:
        header = ctk.CTkFrame(
            self,
            height=54,
            fg_color=AgroTheme.BG_SIDEBAR,
            corner_radius=0,
            border_width=1,
            border_color=AgroTheme.BORDER_COLOR,
        )
        header.grid(row=0, column=1, sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        self.lbl_page_title = ctk.CTkLabel(
            header,
            text="Painel de Decisão Executiva, Alertas Priorizados e Conciliação Rastreável",
            font=ctk.CTkFont(family=AgroTheme.FONT_FAMILY, size=16, weight="bold"),
            text_color=AgroTheme.TEXT_PRIMARY,
            anchor="w",
        )
        self.lbl_page_title.grid(row=0, column=0, sticky="w", padx=18, pady=12)

        self.lbl_badge_arch = ctk.CTkLabel(
            header,
            text=" Arquitetura MTC • Strategy + Adapter + Observer ",
            fg_color=AgroTheme.BG_CARD,
            text_color=AgroTheme.TEXT_MUTED,
            corner_radius=6,
            font=ctk.CTkFont(family=AgroTheme.FONT_FAMILY, size=11, weight="bold"),
        )
        self.lbl_badge_arch.grid(row=0, column=1, sticky="e", padx=18, pady=12)

    def _build_content_area(self) -> None:
        self.content_container = ctk.CTkFrame(self, fg_color="transparent")
        self.content_container.grid(row=1, column=1, sticky="nsew", padx=12, pady=10)
        self.content_container.grid_rowconfigure(0, weight=1)
        self.content_container.grid_columnconfigure(0, weight=1)

        self.views["dashboard"] = DashboardTemplate(self.content_container, self.controller)
        self.views["analytics"] = AnalyticsTemplate(self.content_container, self.controller)
        self.views["operations"] = OperationsTemplate(self.content_container, self.controller)
        self.views["audit"] = AuditTemplate(self.content_container, self.controller)
        self.views["settings"] = SettingsTemplate(self.content_container, self.controller)

        for view in self.views.values():
            view.grid(row=0, column=0, sticky="nsew")

    def _build_statusbar(self) -> None:
        statusbar = ctk.CTkFrame(
            self,
            height=30,
            fg_color=AgroTheme.BG_SIDEBAR,
            corner_radius=0,
            border_width=1,
            border_color=AgroTheme.BORDER_COLOR,
        )
        statusbar.grid(row=2, column=1, sticky="ew")

        self.lbl_status_left = ctk.CTkLabel(
            statusbar,
            text="🟢 Motor Analítico Ativo",
            font=ctk.CTkFont(family=AgroTheme.FONT_FAMILY, size=11),
            text_color=AgroTheme.TEXT_MUTED,
        )
        self.lbl_status_left.pack(side="left", padx=14, pady=4)

        self.lbl_status_right = ctk.CTkLabel(
            statusbar,
            text="",
            font=ctk.CTkFont(family=AgroTheme.FONT_FAMILY, size=11),
            text_color=AgroTheme.TEXT_SECONDARY,
        )
        self.lbl_status_right.pack(side="right", padx=14, pady=4)

    def select_tab(self, tab_key: str) -> None:
        titles = {
            "dashboard": "🚨 Painel de Decisão Executiva, Alertas Priorizados e Conciliação FEFO",
            "analytics": "📈 Ciência de Dados Aplicada: Séries Temporais, Z-Score, Curva ABC e Custos 500ha",
            "operations": "➕ Central de Lançamentos, Reanálise ao Vivo e Adaptador Oficial (ColumnMapper)",
            "audit": "🛡️ Governança de Dados, Conciliação Rastreável por Lote, Embalagens inpEV e Limitações",
            "settings": "⚙️ Painel de Mutabilidade: Parâmetros Dinâmicos (settings.json) e Motor Plugável",
        }
        self.lbl_page_title.configure(text=titles.get(tab_key, "AgroZica"))

        for k, btn in self.nav_buttons.items():
            if k == tab_key:
                btn.configure(fg_color=AgroTheme.ACCENT_EMERALD_DARK, text_color="#FFFFFF")
            else:
                btn.configure(fg_color="transparent", text_color=AgroTheme.TEXT_PRIMARY)

        target_view = self.views.get(tab_key)
        if target_view:
            target_view.tkraise()

    def _update_statusbar(self) -> None:
        kpis = self.controller.get_dashboard_kpis()
        active_rules = sum(
            1 for r in self.controller.get_all_rules_metadata() if self.controller.config_model.is_rule_active(r.rule_id)
        )
        self.lbl_status_left.configure(
            text=(
                f"🟢 AgroZica Online | Base: {self.controller.inventory_model.csv_path.name} "
                f"({kpis['total_movimentacoes']} lançamentos | {kpis['total_insumos']} insumos)"
            )
        )
        self.lbl_status_right.configure(
            text=(
                f"Regras Ativas: {active_rules}/7  •  Alertas Críticos: {kpis['alertas_criticos']}  •  "
                f"Divergências de Lote: {kpis['divergencias_lote']}  •  Incerteza Alta: {kpis['itens_incerteza']}"
            )
        )
