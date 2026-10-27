"""
Aba 4: Auditoria de Dados, Conciliação por Lote, Logística Reversa (inpEV) e Limitações Técnicas (AuditTemplate).
Demonstra os Pilares de Confiabilidade e Governança do AgroZica:
1. Trilha completa de inconsistências diagnosticadas no dado bruto (grafias, conversões de unidades, nulos protegidos);
2. Conciliação Física Auditável por Lote (Saldo Inicial + Entradas - Saídas = Saldo Final);
3. Monitoramento Ambiental de Devolução de Embalagens de Agrotóxicos (Lei 14.785/2023);
4. Transparência sobre Limitações Técnicas e Premissas Estatísticas.
"""

from typing import Any, List, Tuple, Dict
import customtkinter as ctk

from src.templates.theme import AgroTheme
from src.templates.components import FilterToolbar, DataGrid
from src.controllers.main_controller import MainController


class AuditTemplate(ctk.CTkFrame):
    """View de Governança de Dados, Conciliação Rastreável por Lote e Conformidade Ambiental."""

    def __init__(self, master: Any, controller: MainController, **kwargs: Any) -> None:
        super().__init__(master, fg_color="transparent", **kwargs)
        self.controller = controller
        self.filter_state: Dict[str, str] = {"busca": "", "Tipo de Ocorrência": "TODOS"}

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=5)
        self.grid_rowconfigure(2, weight=4)

        self._build_top_filter()
        self._build_inconsistencies_grid()
        self._build_reconciliation_and_governance()

        self.controller.subscribe(self.refresh_view)
        self.refresh_view()

    def _build_top_filter(self) -> None:
        tipos = [
            "TODOS",
            "Divergência de Lote",
            "Grafia Padronizada",
            "Conversão de Unidade",
            "Dado Ausente (NaN)",
            "Logística Reversa (inpEV)",
        ]
        self.toolbar = FilterToolbar(
            self,
            search_placeholder="Filtrar trilha por insumo, lote ou ID...",
            dropdown_configs=[("Tipo de Ocorrência", tipos, "TODOS")],
            on_filter_change=self._on_filter_changed,
        )
        self.toolbar.grid(row=0, column=0, columnspan=2, sticky="ew", padx=4, pady=(0, 8))

    def _build_inconsistencies_grid(self) -> None:
        frame = ctk.CTkFrame(
            self,
            fg_color=AgroTheme.BG_SIDEBAR,
            corner_radius=10,
            border_width=1,
            border_color=AgroTheme.BORDER_COLOR,
        )
        frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=4, pady=(0, 8))
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)

        self.lbl_audit_title = ctk.CTkLabel(
            frame,
            text="🛡️ Trilha de Auditoria de Qualidade de Dados e Tratamentos Semânticos Aplicados",
            font=ctk.CTkFont(family=AgroTheme.FONT_FAMILY, size=13, weight="bold"),
            text_color=AgroTheme.TEXT_PRIMARY,
            anchor="w",
        )
        self.lbl_audit_title.grid(row=0, column=0, sticky="ew", padx=12, pady=(8, 4))

        cols = [
            ("id", "Movimento", 90, "center"),
            ("data", "Data", 90, "center"),
            ("produto", "Insumo Canônico", 185, "w"),
            ("lote", "Lote", 95, "center"),
            ("tipo", "Categoria de Auditoria", 165, "w"),
            ("sev", "Severidade", 85, "center"),
            ("orig", "Dado Bruto Encontrado", 170, "w"),
            ("trat", "Tratamento Auditável Aplicado", 220, "w"),
            ("impacto", "Justificativa de Governança", 310, "w"),
        ]
        self.grid_audit = DataGrid(frame, columns=cols, height=9)
        self.grid_audit.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))

    def _build_reconciliation_and_governance(self) -> None:
        # Painel Esquerdo: Conciliação Rastreável por Lote (Saldo Inicial + Entradas - Saídas = Saldo Final)
        left_frame = ctk.CTkFrame(
            self,
            fg_color=AgroTheme.BG_CARD,
            corner_radius=10,
            border_width=1,
            border_color=AgroTheme.BORDER_COLOR,
        )
        left_frame.grid(row=2, column=0, sticky="nsew", padx=(4, 4), pady=0)
        left_frame.grid_columnconfigure(0, weight=1)
        left_frame.grid_rowconfigure(1, weight=1)

        lbl_conc = ctk.CTkLabel(
            left_frame,
            text="⚖️ Conciliação por Lote: Saldo Inicial + Entradas - Saídas = Saldo Final",
            font=ctk.CTkFont(family=AgroTheme.FONT_FAMILY, size=12, weight="bold"),
            text_color=AgroTheme.TEXT_MUTED,
            anchor="w",
        )
        lbl_conc.grid(row=0, column=0, sticky="ew", padx=12, pady=(8, 4))

        lot_cols = [
            ("produto", "Insumo", 165, "w"),
            ("lote", "Lote", 95, "center"),
            ("ini", "S. Inicial", 75, "e"),
            ("ent", "+ Entradas", 85, "e"),
            ("sai", "- Saídas", 85, "e"),
            ("fin", "= S. Final", 90, "e"),
            ("val", "Validade", 95, "center"),
            ("status", "Status Conciliação", 150, "center"),
        ]
        self.grid_lotes = DataGrid(left_frame, columns=lot_cols, height=7)
        self.grid_lotes.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))

        # Painel Direito: Limitações Técnicas, Incerteza Estatística e Caráter Gerencial
        right_frame = ctk.CTkFrame(
            self,
            fg_color=AgroTheme.BG_CARD,
            corner_radius=10,
            border_width=1,
            border_color=AgroTheme.BORDER_COLOR,
        )
        right_frame.grid(row=2, column=1, sticky="nsew", padx=(4, 4), pady=0)
        right_frame.grid_columnconfigure(0, weight=1)
        right_frame.grid_rowconfigure(1, weight=1)

        lbl_gov = ctk.CTkLabel(
            right_frame,
            text="📜 Declaração de Governança, Comunicação de Incerteza e Limitações Técnicas",
            font=ctk.CTkFont(family=AgroTheme.FONT_FAMILY, size=12, weight="bold"),
            text_color=AgroTheme.ACCENT_AMBER,
            anchor="w",
        )
        lbl_gov.grid(row=0, column=0, sticky="ew", padx=12, pady=(8, 4))

        self.txt_governance = ctk.CTkTextbox(
            right_frame,
            fg_color=AgroTheme.BG_INPUT,
            text_color=AgroTheme.TEXT_PRIMARY,
            font=ctk.CTkFont(family=AgroTheme.FONT_FAMILY, size=12),
            wrap="word",
        )
        self.txt_governance.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))

    def _on_filter_changed(self, state: Dict[str, str]) -> None:
        self.filter_state = state
        self.refresh_view()

    def refresh_view(self) -> None:
        # 1. Trilha de Auditoria
        items = self.controller.get_audit_items(
            tipo_filter=self.filter_state.get("Tipo de Ocorrência", "TODOS"),
            busca_texto=self.filter_state.get("busca", ""),
        )
        self.lbl_audit_title.configure(
            text=f"🛡️ Trilha de Auditoria de Qualidade de Dados e Tratamentos Semânticos ({len(items)} apontamentos)"
        )

        audit_rows: List[Tuple[Tuple[Any, ...], str]] = []
        for it in items:
            tag = "critico" if it.severidade == "ALTA" else ("atencao" if it.severidade == "MÉDIA" else "info")
            audit_rows.append(
                (
                    (
                        it.id_movimento,
                        it.data_movimento,
                        it.produto,
                        it.lote,
                        it.tipo_inconsistencia,
                        it.severidade,
                        it.valor_original,
                        it.tratamento_aplicado,
                        it.impacto_analitico,
                    ),
                    tag,
                )
            )
        self.grid_audit.clear_and_populate(audit_rows)

        # 2. Conciliação por Lote
        lot_rows: List[Tuple[Tuple[Any, ...], str]] = []
        lotes = sorted(
            self.controller.inventory_model.saldos_lote,
            key=lambda l: (not l.divergencia_conciliacao, l.produto, l.lote),
        )
        for lt in lotes:
            status_txt = "⚠️ DIVERGÊNCIA FÍSICA" if lt.divergencia_conciliacao else "✅ CONCILIADO"
            tag = "critico" if lt.divergencia_conciliacao else "normal"
            val_txt = lt.data_validade if lt.data_validade else "Pendente / N.A."
            lot_rows.append(
                (
                    (
                        lt.produto,
                        lt.lote,
                        f"{lt.saldo_inicial:g} {lt.unidade_padronizada}",
                        f"{lt.total_entradas:g} {lt.unidade_padronizada}",
                        f"{lt.total_saidas:g} {lt.unidade_padronizada}",
                        f"{lt.saldo_final:g} {lt.unidade_padronizada}",
                        val_txt,
                        status_txt,
                    ),
                    tag,
                )
            )
        self.grid_lotes.clear_and_populate(lot_rows)

        # 3. Texto de Governança e Limitações Técnicas atualizado dinamicamente
        kpis = self.controller.get_dashboard_kpis()
        min_hist = self.controller.config_model.get_param("min_historico_saidas", 3)
        gov_text = (
            "1. CONCILIAÇÃO RASTREÁVEL E INTEGRIDADE FÍSICA:\n"
            f"   • Todos os lotes são auditados pela identidade: Saldo Inicial + Entradas - Saídas = Saldo Final.\n"
            f"   • Atualmente há {kpis['divergencias_lote']} lote(s) com divergência física (saída lançada maior que a entrada do lote), "
            "destacado(s) em vermelho na tabela ao lado para conferência in loco no almoxarifado.\n\n"
            "2. PROTEÇÃO SEMÂNTICA CONTRA ZEROS ARTIFICIAIS:\n"
            "   • Campos ausentes de 'custo_unitario' ou 'data_validade' NUNCA são convertidos em 0. "
            "São preservados como 'Pendente / Ausente' (NaN) para impedir subestimação artificial do custo médio de aquisição "
            "ou falsas datas de validade.\n\n"
            "3. COMUNICAÇÃO TRANSPARENTE DE INCERTEZA ESTATÍSTICA:\n"
            f"   • Insumos com menos de {min_hist} eventos de saída recebem obrigatoriamente o selo "
            f"'[Incerteza Alta: Pouco Histórico]' ({kpis['itens_incerteza']} insumo(s) atualmente). "
            "Suas projeções de autonomia e Z-Score devem ser interpretadas como indicativas até que a amostra cresça.\n\n"
            "4. LIMITAÇÕES TÉCNICAS E CARÁTER GERENCIAL:\n"
            "   • O Consumo Médio Diário (CMD) reflete o ritmo histórico dentro da janela configurada, podendo sofrer "
            "variações bruscas durante janelas sazonais de plantio/pulverização.\n"
            "   • O AgroZica é uma ferramenta gerencial de apoio à decisão e auditoria: toda aplicação de defensivos, "
            "biológicos ou corretivos deve respeitar o Receituário Agronômico e a Lei 14.785/2023 (logística reversa inpEV)."
        )
        self.txt_governance.configure(state="normal")
        self.txt_governance.delete("1.0", "end")
        self.txt_governance.insert("1.0", gov_text)
        self.txt_governance.configure(state="disabled")
