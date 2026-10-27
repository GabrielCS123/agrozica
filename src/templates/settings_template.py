"""
Aba 5: Painel de Mutabilidade em Tempo Real (SettingsTemplate).
Garante que nenhum parâmetro matemático fique fixo no código (hardcoded):
- Sliders interativos para todos os limiares analíticos de config/settings.json;
- Checkboxes de ativação/desativação individual das 7 classes do RuleRegistry;
- Cadastro a quente de novos sinônimos/grafias de produtos para o DataCleaner;
- Recálculo instantâneo de todas as abas via Observer Pattern.
"""

from typing import Any, Dict, Tuple
import customtkinter as ctk

from src.templates.theme import AgroTheme
from src.controllers.main_controller import MainController


class SettingsTemplate(ctk.CTkFrame):
    """View de Parametrização Dinâmica e Mutabilidade do Motor Analítico AgroZica."""

    def __init__(self, master: Any, controller: MainController, **kwargs: Any) -> None:
        super().__init__(master, fg_color="transparent", **kwargs)
        self.controller = controller
        self.sliders: Dict[str, Tuple[ctk.CTkSlider, ctk.CTkLabel, type]] = {}
        self.rule_vars: Dict[str, ctk.BooleanVar] = {}

        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(1, weight=1)

        self._build_header()
        self._build_sliders_panel()
        self._build_rules_and_synonyms_panel()

    def _build_header(self) -> None:
        bar = ctk.CTkFrame(
            self,
            fg_color=AgroTheme.BG_SIDEBAR,
            corner_radius=10,
            border_width=1,
            border_color=AgroTheme.BORDER_COLOR,
        )
        bar.grid(row=0, column=0, columnspan=2, sticky="ew", padx=4, pady=(0, 8))

        lbl = ctk.CTkLabel(
            bar,
            text="⚙️ Engenharia de Mutabilidade (Hot-Reload de config/settings.json e RuleRegistry)",
            font=ctk.CTkFont(family=AgroTheme.FONT_FAMILY, size=14, weight="bold"),
            text_color=AgroTheme.TEXT_PRIMARY,
        )
        lbl.pack(side="left", padx=14, pady=10)

        self.lbl_status = ctk.CTkLabel(
            bar,
            text="Alterações aplicadas recalcularão KPIs, Alertas e Gráficos instantaneamente.",
            font=ctk.CTkFont(family=AgroTheme.FONT_FAMILY, size=11),
            text_color=AgroTheme.TEXT_MUTED,
        )
        self.lbl_status.pack(side="left", padx=12, pady=10)

        btn_reset = ctk.CTkButton(
            bar,
            text="🔄 Restaurar Padrões Recomendados",
            width=215,
            fg_color=AgroTheme.BG_CARD,
            hover_color=AgroTheme.BG_CARD_HOVER,
            border_width=1,
            border_color=AgroTheme.BORDER_COLOR,
            command=self._on_reset_defaults,
        )
        btn_reset.pack(side="right", padx=(6, 12), pady=10)

        btn_save = ctk.CTkButton(
            bar,
            text="⚡ Aplicar Parâmetros & Recalcular Agora",
            width=255,
            fg_color=AgroTheme.ACCENT_EMERALD_DARK,
            hover_color=AgroTheme.ACCENT_EMERALD,
            font=ctk.CTkFont(family=AgroTheme.FONT_FAMILY, size=12, weight="bold"),
            command=self._on_apply_changes,
        )
        btn_save.pack(side="right", padx=6, pady=10)

    def _build_sliders_panel(self) -> None:
        panel = ctk.CTkScrollableFrame(
            self,
            fg_color=AgroTheme.BG_CARD,
            corner_radius=10,
            border_width=1,
            border_color=AgroTheme.BORDER_COLOR,
            label_text="🎚️ Limiares Matemáticos e Estatísticos (Externalizados em settings.json)",
            label_font=ctk.CTkFont(family=AgroTheme.FONT_FAMILY, size=13, weight="bold"),
            label_text_color=AgroTheme.TEXT_MUTED,
        )
        panel.grid(row=1, column=0, sticky="nsew", padx=(4, 6), pady=0)
        panel.grid_columnconfigure(0, weight=1)

        param_specs = [
            ("dias_estoque_critico", "Limiar de Estoque Crítico (dias de autonomia)", 1, 30, 29, int, "dias"),
            ("dias_estoque_atencao", "Limiar de Estoque em Atenção (dias de autonomia)", 5, 60, 55, int, "dias"),
            ("dias_alerta_validade", "Janela de Alerta Preventivo de Validade (FEFO)", 10, 120, 110, int, "dias"),
            ("z_score_anomalia", "Limiar Estatístico Z-Score para Retirada Anômala", 1.0, 3.5, 25, float, "σ"),
            ("crescimento_progressivo_pct", "Taxa de Crescimento Progressivo de Demanda", 10.0, 100.0, 18, float, "%"),
            ("variacao_preco_pct", "Limiar de Inflação Abrupta de Preço de Compra", 5.0, 80.0, 15, float, "%"),
            ("dias_capital_parado", "Dias Sem Saída para Alerta de Capital Parado", 15, 120, 21, int, "dias"),
            ("autonomia_excesso_dias", "Autonomia para Excesso de Estoque Imobilizado", 60, 360, 30, int, "dias"),
            ("min_historico_saidas", "Mínimo de Saídas p/ Confiança Estatística", 2, 10, 8, int, "saídas"),
            ("janela_consumo_dias", "Janela Temporal para Cálculo do CMD", 15, 120, 21, int, "dias"),
        ]

        for idx, (key, title, min_v, max_v, steps, v_type, unit) in enumerate(param_specs):
            curr_val = self.controller.config_model.get_param(key, min_v)
            row_frame = ctk.CTkFrame(panel, fg_color=AgroTheme.BG_INPUT, corner_radius=8)
            row_frame.grid(row=idx, column=0, sticky="ew", padx=8, pady=5)
            row_frame.grid_columnconfigure(0, weight=1)

            top_r = ctk.CTkFrame(row_frame, fg_color="transparent")
            top_r.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=(6, 2))
            top_r.grid_columnconfigure(0, weight=1)

            lbl_name = ctk.CTkLabel(
                top_r,
                text=f"{title} ({key})",
                font=ctk.CTkFont(family=AgroTheme.FONT_FAMILY, size=12, weight="bold"),
                text_color=AgroTheme.TEXT_PRIMARY,
                anchor="w",
            )
            lbl_name.grid(row=0, column=0, sticky="w")

            fmt_val = f"{curr_val:.1f} {unit}" if v_type is float else f"{int(curr_val)} {unit}"
            lbl_val = ctk.CTkLabel(
                top_r,
                text=fmt_val,
                font=ctk.CTkFont(family=AgroTheme.FONT_FAMILY, size=12, weight="bold"),
                text_color=AgroTheme.ACCENT_EMERALD,
                anchor="e",
            )
            lbl_val.grid(row=0, column=1, sticky="e")

            slider = ctk.CTkSlider(
                row_frame,
                from_=min_v,
                to=max_v,
                number_of_steps=steps,
                button_color=AgroTheme.ACCENT_EMERALD,
                progress_color=AgroTheme.ACCENT_EMERALD_DARK,
            )
            slider.set(float(curr_val))
            slider.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=(2, 8))

            def _make_cb(lbl_w: ctk.CTkLabel, t: type, u: str) -> Any:
                def _on_slide(v: float) -> None:
                    txt = f"{v:.1f} {u}" if t is float else f"{int(round(v))} {u}"
                    lbl_w.configure(text=txt)
                return _on_slide

            slider.configure(command=_make_cb(lbl_val, v_type, unit))
            self.sliders[key] = (slider, lbl_val, v_type)

    def _build_rules_and_synonyms_panel(self) -> None:
        right_col = ctk.CTkFrame(self, fg_color="transparent")
        right_col.grid(row=1, column=1, sticky="nsew", padx=(6, 4), pady=0)
        right_col.grid_columnconfigure(0, weight=1)
        right_col.grid_rowconfigure(0, weight=3)
        right_col.grid_rowconfigure(1, weight=2)

        # Card 1: Ativação Individual de Regras (Strategy Pattern)
        rules_card = ctk.CTkFrame(
            right_col,
            fg_color=AgroTheme.BG_CARD,
            corner_radius=10,
            border_width=1,
            border_color=AgroTheme.BORDER_COLOR,
        )
        rules_card.grid(row=0, column=0, sticky="nsew", pady=(0, 8))
        rules_card.grid_columnconfigure(0, weight=1)

        lbl_r = ctk.CTkLabel(
            rules_card,
            text="🔌 Motor de Regras Plugável (RuleRegistry — Strategy Pattern)",
            font=ctk.CTkFont(family=AgroTheme.FONT_FAMILY, size=13, weight="bold"),
            text_color=AgroTheme.TEXT_MUTED,
            anchor="w",
        )
        lbl_r.grid(row=0, column=0, sticky="ew", padx=14, pady=(10, 6))

        for idx, rule in enumerate(self.controller.get_all_rules_metadata()):
            is_act = self.controller.config_model.is_rule_active(rule.rule_id)
            var = ctk.BooleanVar(value=is_act)
            self.rule_vars[rule.rule_id] = var

            r_box = ctk.CTkFrame(rules_card, fg_color=AgroTheme.BG_INPUT, corner_radius=6)
            r_box.grid(row=idx + 1, column=0, sticky="ew", padx=12, pady=4)
            r_box.grid_columnconfigure(0, weight=1)

            chk = ctk.CTkCheckBox(
                r_box,
                text=f"{rule.rule_name} [{rule.rule_id}]",
                variable=var,
                font=ctk.CTkFont(family=AgroTheme.FONT_FAMILY, size=12, weight="bold"),
                text_color=AgroTheme.TEXT_PRIMARY,
                fg_color=AgroTheme.ACCENT_EMERALD_DARK,
                hover_color=AgroTheme.ACCENT_EMERALD,
                command=self._on_apply_changes,
            )
            chk.grid(row=0, column=0, sticky="w", padx=10, pady=(6, 2))

            desc_lbl = ctk.CTkLabel(
                r_box,
                text=rule.description,
                font=ctk.CTkFont(family=AgroTheme.FONT_FAMILY, size=11),
                text_color=AgroTheme.TEXT_SECONDARY,
                anchor="w",
                wraplength=420,
            )
            desc_lbl.grid(row=1, column=0, sticky="w", padx=34, pady=(0, 6))

        # Card 2: Dicionário Dinâmico de Sinônimos de Produtos
        syn_card = ctk.CTkFrame(
            right_col,
            fg_color=AgroTheme.BG_CARD,
            corner_radius=10,
            border_width=1,
            border_color=AgroTheme.BORDER_COLOR,
        )
        syn_card.grid(row=1, column=0, sticky="nsew")
        syn_card.grid_columnconfigure(0, weight=1)

        lbl_syn = ctk.CTkLabel(
            syn_card,
            text="🔤 Adicionar Sinônimo / Grafia Divergente ao DataCleaner",
            font=ctk.CTkFont(family=AgroTheme.FONT_FAMILY, size=13, weight="bold"),
            text_color=AgroTheme.ACCENT_AMBER,
            anchor="w",
        )
        lbl_syn.grid(row=0, column=0, sticky="ew", padx=14, pady=(10, 4))

        canonical_list = sorted(list(self.controller.config_model.data.get("sinonimos_produtos", {}).keys()))
        self.var_syn_target = ctk.StringVar(value=canonical_list[0] if canonical_list else "Glifosato 480 SL")
        self.var_syn_new = ctk.StringVar(value="")

        lbl_c1 = ctk.CTkLabel(syn_card, text="Insumo Canônico Destino:", text_color=AgroTheme.TEXT_SECONDARY)
        lbl_c1.grid(row=1, column=0, sticky="w", padx=14, pady=(2, 2))

        self.combo_syn = ctk.CTkOptionMenu(
            syn_card,
            variable=self.var_syn_target,
            values=canonical_list or ["Glifosato 480 SL"],
            fg_color=AgroTheme.BG_SIDEBAR,
            button_color=AgroTheme.ACCENT_EMERALD_DARK,
        )
        self.combo_syn.grid(row=2, column=0, sticky="ew", padx=14, pady=(0, 6))

        lbl_c2 = ctk.CTkLabel(syn_card, text="Nova Grafia / Apelido na Planilha:", text_color=AgroTheme.TEXT_SECONDARY)
        lbl_c2.grid(row=3, column=0, sticky="w", padx=14, pady=(2, 2))

        entry_syn = ctk.CTkEntry(
            syn_card,
            textvariable=self.var_syn_new,
            placeholder_text="Ex: glifosato concentrado 480",
            fg_color=AgroTheme.BG_INPUT,
        )
        entry_syn.grid(row=4, column=0, sticky="ew", padx=14, pady=(0, 8))

        btn_add_syn = ctk.CTkButton(
            syn_card,
            text="➕ Cadastrar Sinônimo & Reprocessar Base",
            fg_color=AgroTheme.ACCENT_EMERALD_DARK,
            hover_color=AgroTheme.ACCENT_EMERALD,
            command=self._on_add_synonym,
        )
        btn_add_syn.grid(row=5, column=0, sticky="ew", padx=14, pady=(0, 10))

    def _on_apply_changes(self) -> None:
        new_params: Dict[str, Any] = {}
        for k, (slider, _lbl, v_type) in self.sliders.items():
            raw = slider.get()
            new_params[k] = round(float(raw), 2) if v_type is float else int(round(raw))

        active_rules: Dict[str, bool] = {r_id: var.get() for r_id, var in self.rule_vars.items()}
        ok, msg = self.controller.update_parameters_batch(new_params, active_rules)
        self.lbl_status.configure(
            text=f"{'✅' if ok else '❌'} {msg}",
            text_color=AgroTheme.ACCENT_EMERALD if ok else AgroTheme.ACCENT_DANGER,
        )

    def _on_reset_defaults(self) -> None:
        ok, msg = self.controller.reset_parameters_to_default()
        for k, (slider, lbl_val, v_type) in self.sliders.items():
            val = self.controller.config_model.get_param(k)
            slider.set(float(val))
            unit_txt = lbl_val.cget("text").split(" ")[-1]
            lbl_val.configure(text=f"{val:.1f} {unit_txt}" if v_type is float else f"{int(val)} {unit_txt}")
        for r_id, var in self.rule_vars.items():
            var.set(True)
        self.lbl_status.configure(text=f"✅ {msg}", text_color=AgroTheme.ACCENT_EMERALD)

    def _on_add_synonym(self) -> None:
        syn = self.var_syn_new.get().strip()
        target = self.var_syn_target.get().strip()
        if not syn:
            self.lbl_status.configure(text="⚠️ Digite uma grafia para cadastrar.", text_color=AgroTheme.ACCENT_AMBER)
            return
        self.controller.config_model.add_product_synonym(target, syn, auto_save=True)
        self.var_syn_new.set("")
        self.controller.refresh_analysis(notify=True)
        self.lbl_status.configure(
            text=f"✅ Sinônimo '{syn}' vinculado a '{target}' e base reanalisada!",
            text_color=AgroTheme.ACCENT_EMERALD,
        )
