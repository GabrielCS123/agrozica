"""
Aba 2: Inteligência Visual e Gráficos Analíticos (AnalyticsTemplate).
Integra gráficos Matplotlib estilizados no tema Dark Mode Verde Floresta do AgroZica:
1. Série Temporal de Consumo por Insumo com Banda de Anomalia (Z-Score) e Linha de Tendência;
2. Autonomia Estimada em Dias vs. Limiares Configurados (Crítico / Atenção);
3. Curva ABC de Valor de Insumos (Pareto 80/15/5);
4. Alocação de Custos Operacionais por Centro de Custo dos 500 hectares (sem duplicidade).
"""

from typing import Any, List
import numpy as np
import pandas as pd
import customtkinter as ctk
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from src.templates.theme import AgroTheme
from src.controllers.main_controller import MainController


class AnalyticsTemplate(ctk.CTkFrame):
    """View de Ciência de Dados Visual e Rastreabilidade de Custos 500ha."""

    def __init__(self, master: Any, controller: MainController, **kwargs: Any) -> None:
        super().__init__(master, fg_color="transparent", **kwargs)
        self.controller = controller

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_top_controls()
        self._build_charts_canvas()

        self.controller.subscribe(self.refresh_view)
        self.refresh_view()

    def _build_top_controls(self) -> None:
        bar = ctk.CTkFrame(
            self,
            fg_color=AgroTheme.BG_CARD,
            corner_radius=8,
            border_width=1,
            border_color=AgroTheme.BORDER_COLOR,
        )
        bar.grid(row=0, column=0, sticky="ew", padx=4, pady=(0, 8))

        lbl_title = ctk.CTkLabel(
            bar,
            text="📈 Diagnóstico Estatístico Visual & Rastreabilidade dos 500 Hectares",
            font=ctk.CTkFont(family=AgroTheme.FONT_FAMILY, size=14, weight="bold"),
            text_color=AgroTheme.TEXT_PRIMARY,
        )
        lbl_title.pack(side="left", padx=14, pady=10)

        lbl_sel = ctk.CTkLabel(
            bar,
            text="Insumo para Série Temporal (Z-Score & Tendência):",
            font=ctk.CTkFont(family=AgroTheme.FONT_FAMILY, size=12),
            text_color=AgroTheme.TEXT_MUTED,
        )
        lbl_sel.pack(side="left", padx=(20, 8), pady=10)

        self.selected_product_var = ctk.StringVar(value="Glifosato 480 SL")
        self.combo_product = ctk.CTkOptionMenu(
            bar,
            variable=self.selected_product_var,
            values=["Glifosato 480 SL"],
            width=250,
            fg_color=AgroTheme.BG_SIDEBAR,
            button_color=AgroTheme.ACCENT_EMERALD_DARK,
            button_hover_color=AgroTheme.ACCENT_EMERALD,
            command=lambda _v: self.refresh_view(),
        )
        self.combo_product.pack(side="left", padx=(0, 12), pady=10)

        btn_refresh = ctk.CTkButton(
            bar,
            text="🔄 Recalcular Gráficos",
            width=150,
            fg_color=AgroTheme.ACCENT_EMERALD_DARK,
            hover_color=AgroTheme.ACCENT_EMERALD,
            command=self.refresh_view,
        )
        btn_refresh.pack(side="right", padx=14, pady=10)

    def _build_charts_canvas(self) -> None:
        chart_frame = ctk.CTkFrame(
            self,
            fg_color=AgroTheme.BG_CARD,
            corner_radius=10,
            border_width=1,
            border_color=AgroTheme.BORDER_COLOR,
        )
        chart_frame.grid(row=1, column=0, sticky="nsew", padx=4, pady=0)
        chart_frame.grid_rowconfigure(0, weight=1)
        chart_frame.grid_columnconfigure(0, weight=1)

        self.fig = Figure(figsize=(12, 7.2), dpi=96, facecolor=AgroTheme.BG_CARD)
        self.canvas = FigureCanvasTkAgg(self.fig, master=chart_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)

    def _style_axis(self, ax: Any, title: str) -> None:
        ax.set_facecolor(AgroTheme.BG_INPUT)
        ax.set_title(title, color=AgroTheme.TEXT_PRIMARY, fontsize=10.5, fontweight="bold", pad=8)
        ax.tick_params(colors=AgroTheme.TEXT_SECONDARY, labelsize=8.5)
        for spine in ax.spines.values():
            spine.set_color(AgroTheme.BORDER_COLOR)
        ax.grid(True, linestyle="--", alpha=0.22, color=AgroTheme.TEXT_MUTED)

    def refresh_view(self) -> None:
        """Redesenha os 4 quadrantes analíticos Matplotlib sincronizados com os Models."""
        df_clean = self.controller.inventory_model.df_clean
        summaries = self.controller.inventory_model.resumos_produto

        # Atualiza lista de produtos no seletor
        if summaries:
            prod_names: List[str] = sorted([s.produto for s in summaries])
            self.combo_product.configure(values=prod_names)
            if self.selected_product_var.get() not in prod_names:
                self.selected_product_var.set(prod_names[0])

        self.fig.clear()
        gs = self.fig.add_gridspec(2, 2, hspace=0.38, wspace=0.26, left=0.07, right=0.97, top=0.93, bottom=0.09)

        ax_temporal = self.fig.add_subplot(gs[0, 0])
        ax_autonomia = self.fig.add_subplot(gs[0, 1])
        ax_centros = self.fig.add_subplot(gs[1, 0])
        ax_abc = self.fig.add_subplot(gs[1, 1])

        self._plot_temporal_series(ax_temporal, df_clean)
        self._plot_autonomy_bars(ax_autonomia, summaries)
        self._plot_cost_centers_500ha(ax_centros)
        self._plot_abc_pareto(ax_abc, summaries)

        self.canvas.draw_idle()

    def _plot_temporal_series(self, ax: Any, df_clean: pd.DataFrame) -> None:
        prod_sel = self.selected_product_var.get()
        z_lim = float(self.controller.config_model.get_param("z_score_anomalia", 2.0))

        if df_clean.empty:
            self._style_axis(ax, "1. Série Temporal de Consumo e Detecção de Anomalia")
            return

        df_prod = df_clean[
            (df_clean["produto"] == prod_sel) & (df_clean["tipo_movimento"] == "Saída")
        ].sort_values("data_movimento_dt")

        unid = str(df_prod["unidade_padronizada"].iloc[0]) if not df_prod.empty else "un"
        self._style_axis(ax, f"1. Consumo Temporal & Limiar Z-Score ({z_lim:.1f}σ): {prod_sel}")

        if df_prod.empty:
            ax.text(0.5, 0.5, "Sem saídas registradas", color=AgroTheme.TEXT_SECONDARY, ha="center", va="center")
            return

        dates = df_prod["data_movimento"].astype(str).tolist()
        vals = df_prod["quantidade_padronizada"].astype(float).values
        x = np.arange(len(vals))

        ax.plot(x, vals, marker="o", color=AgroTheme.ACCENT_EMERALD, linewidth=2, label=f"Saída ({unid})")

        if len(vals) >= 2:
            media = float(np.mean(vals))
            std = float(np.std(vals, ddof=0))
            limiar_sup = media + z_lim * std

            ax.axhline(media, color=AgroTheme.ACCENT_INFO, linestyle="--", linewidth=1.2, label=f"Média ({media:.1f})")
            if std > 0:
                ax.axhline(
                    limiar_sup,
                    color=AgroTheme.ACCENT_DANGER,
                    linestyle=":",
                    linewidth=1.4,
                    label=f"Limiar Z={z_lim:.1f}σ ({limiar_sup:.1f})",
                )
                # Destaca pontos anômalos em vermelho
                for idx_pt, val_pt in enumerate(vals):
                    if val_pt >= limiar_sup and val_pt > media * 1.3:
                        ax.scatter(
                            [idx_pt],
                            [val_pt],
                            color=AgroTheme.ACCENT_DANGER,
                            s=90,
                            zorder=5,
                            label="Anomalia Detectada",
                        )

            # Linha de tendência linear
            slope, intercept = np.polyfit(x, vals, 1)
            ax.plot(
                x,
                slope * x + intercept,
                color=AgroTheme.ACCENT_AMBER,
                linestyle="-.",
                linewidth=1.3,
                label="Tendência",
            )

        ax.set_xticks(x)
        ax.set_xticklabels([d[5:] for d in dates], rotation=25)
        ax.set_ylabel(f"Volume ({unid})", color=AgroTheme.TEXT_SECONDARY, fontsize=8.5)
        ax.legend(facecolor=AgroTheme.BG_SIDEBAR, edgecolor=AgroTheme.BORDER_COLOR, labelcolor=AgroTheme.TEXT_PRIMARY, fontsize=7.5)

    def _plot_autonomy_bars(self, ax: Any, summaries: List[Any]) -> None:
        lim_crit = float(self.controller.config_model.get_param("dias_estoque_critico", 8))
        lim_aten = float(self.controller.config_model.get_param("dias_estoque_atencao", 20))
        self._style_axis(ax, "2. Autonomia Estimada de Estoque (Dias) vs. Limiares")

        valid_items = [s for s in summaries if s.autonomia_dias is not None and s.autonomia_dias < 150]
        valid_items.sort(key=lambda s: float(s.autonomia_dias or 999))
        top_items = valid_items[:8]

        if not top_items:
            ax.text(0.5, 0.5, "Sem dados de autonomia", color=AgroTheme.TEXT_SECONDARY, ha="center", va="center")
            return

        names = [s.produto[:22] for s in top_items]
        vals = [float(s.autonomia_dias or 0) for s in top_items]
        colors = [
            AgroTheme.ACCENT_DANGER if v <= lim_crit else (AgroTheme.ACCENT_AMBER if v <= lim_aten else AgroTheme.ACCENT_EMERALD)
            for v in vals
        ]

        y_pos = np.arange(len(names))
        bars = ax.barh(y_pos, vals, color=colors, height=0.62)
        ax.axvline(lim_crit, color=AgroTheme.ACCENT_DANGER, linestyle="--", linewidth=1.3, label=f"Crítico ({lim_crit:g}d)")
        ax.axvline(lim_aten, color=AgroTheme.ACCENT_AMBER, linestyle=":", linewidth=1.3, label=f"Atenção ({lim_aten:g}d)")

        ax.set_yticks(y_pos)
        ax.set_yticklabels(names)
        ax.invert_yaxis()
        ax.set_xlabel("Autonomia Estimada (Saldo / CMD em dias)", color=AgroTheme.TEXT_SECONDARY, fontsize=8.5)

        for bar, v in zip(bars, vals):
            ax.text(
                bar.get_width() + 0.8,
                bar.get_y() + bar.get_height() / 2,
                f"{v:.1f}d",
                va="center",
                color=AgroTheme.TEXT_PRIMARY,
                fontsize=8,
            )
        ax.legend(facecolor=AgroTheme.BG_SIDEBAR, edgecolor=AgroTheme.BORDER_COLOR, labelcolor=AgroTheme.TEXT_PRIMARY, fontsize=7.5)

    def _plot_cost_centers_500ha(self, ax: Any) -> None:
        self._style_axis(ax, "3. Custo Operacional Aplicado nos 500ha (Sem Duplicidade)")
        df_cc = self.controller.inventory_model.get_cost_center_breakdown()

        if df_cc.empty:
            ax.text(0.5, 0.5, "Sem saídas apropriadas", color=AgroTheme.TEXT_SECONDARY, ha="center", va="center")
            return

        labels = [str(c)[:26] for c in df_cc["destino_centro_custo"]]
        valores = df_cc["custo_operacional"].astype(float).values
        pcts = df_cc["percentual"].astype(float).values

        y_pos = np.arange(len(labels))
        bars = ax.barh(y_pos, valores, color=AgroTheme.ACCENT_EMERALD_DARK, edgecolor=AgroTheme.ACCENT_EMERALD, height=0.6)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(labels)
        ax.invert_yaxis()
        ax.set_xlabel("Custo Apropriado nas Saídas (R$)", color=AgroTheme.TEXT_SECONDARY, fontsize=8.5)

        for bar, val, pct in zip(bars, valores, pcts):
            ax.text(
                bar.get_width() + (max(valores) * 0.01),
                bar.get_y() + bar.get_height() / 2,
                f"R$ {val:,.0f} ({pct:.1f}%)",
                va="center",
                color=AgroTheme.TEXT_PRIMARY,
                fontsize=7.8,
            )
        ax.set_xlim(0, max(valores) * 1.25 if len(valores) > 0 else 100)

    def _plot_abc_pareto(self, ax: Any, summaries: List[Any]) -> None:
        self._style_axis(ax, "4. Curva ABC de Valor de Insumos (Pareto Financeiro)")
        if not summaries:
            return

        sorted_abc = sorted(
            summaries,
            key=lambda s: (s.valor_consumido_total + s.valor_estoque_atual),
            reverse=True,
        )[:8]

        names = [s.produto[:15] for s in sorted_abc]
        vals = [(s.valor_consumido_total + s.valor_estoque_atual) / 1000.0 for s in sorted_abc]
        classes = [s.classe_abc for s in sorted_abc]

        color_map = {"A": AgroTheme.ACCENT_EMERALD, "B": AgroTheme.ACCENT_AMBER, "C": AgroTheme.ACCENT_INFO}
        bar_colors = [color_map.get(c, AgroTheme.ACCENT_EMERALD) for c in classes]

        x_pos = np.arange(len(names))
        bars = ax.bar(x_pos, vals, color=bar_colors, width=0.58)
        ax.set_xticks(x_pos)
        ax.set_xticklabels(names, rotation=22, ha="right")
        ax.set_ylabel("Valor Movimentado (R$ Mil)", color=AgroTheme.TEXT_SECONDARY, fontsize=8.5)

        for bar, cls_name in zip(bars, classes):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.5,
                f"[{cls_name}]",
                ha="center",
                color=AgroTheme.TEXT_PRIMARY,
                fontsize=8,
                fontweight="bold",
            )

