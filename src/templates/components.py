"""
Componentes Visuais Reutilizáveis do AgroZica:
- KPICard: Card de indicador executivo com título, valor principal, subtítulo e barra de cor;
- AlertBanner: Card expansível/detalhado de alerta com justificativa matemática, recomendação e badge de incerteza;
- FilterToolbar: Barra de filtros reutilizável com busca textual e seletores;
- DataGrid: Tabela baseada em ttk.Treeview com barras de rolagem, ordenação por coluna e tags de cor.
"""

import tkinter as tk
from tkinter import ttk
from typing import List, Tuple, Callable, Dict, Any
import customtkinter as ctk

from src.templates.theme import AgroTheme
from src.models.entities import Alert


class KPICard(ctk.CTkFrame):
    """Card executivo para exibição de métricas-chave no topo dos painéis."""

    def __init__(
        self,
        master: Any,
        title: str,
        value: str,
        subtitle: str = "",
        accent_color: str = AgroTheme.ACCENT_EMERALD,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            master,
            fg_color=AgroTheme.BG_CARD,
            corner_radius=10,
            border_width=1,
            border_color=AgroTheme.BORDER_COLOR,
            **kwargs,
        )
        self.grid_columnconfigure(1, weight=1)

        # Barra lateral de destaque
        self.accent_bar = ctk.CTkFrame(
            self, width=6, fg_color=accent_color, corner_radius=4
        )
        self.accent_bar.grid(row=0, column=0, rowspan=3, sticky="ns", padx=(8, 10), pady=10)

        self.lbl_title = ctk.CTkLabel(
            self,
            text=title.upper(),
            font=ctk.CTkFont(family=AgroTheme.FONT_FAMILY, size=11, weight="bold"),
            text_color=AgroTheme.TEXT_SECONDARY,
            anchor="w",
        )
        self.lbl_title.grid(row=0, column=1, sticky="ew", padx=(0, 12), pady=(10, 2))

        self.lbl_value = ctk.CTkLabel(
            self,
            text=value,
            font=ctk.CTkFont(family=AgroTheme.FONT_FAMILY, size=21, weight="bold"),
            text_color=AgroTheme.TEXT_PRIMARY,
            anchor="w",
        )
        self.lbl_value.grid(row=1, column=1, sticky="ew", padx=(0, 12), pady=0)

        self.lbl_subtitle = ctk.CTkLabel(
            self,
            text=subtitle,
            font=ctk.CTkFont(family=AgroTheme.FONT_FAMILY, size=11),
            text_color=accent_color,
            anchor="w",
        )
        self.lbl_subtitle.grid(row=2, column=1, sticky="ew", padx=(0, 12), pady=(2, 10))

    def update_data(self, value: str, subtitle: str | None = None, accent_color: str | None = None) -> None:
        self.lbl_value.configure(text=value)
        if subtitle is not None:
            self.lbl_subtitle.configure(text=subtitle)
        if accent_color is not None:
            self.accent_bar.configure(fg_color=accent_color)
            self.lbl_subtitle.configure(text_color=accent_color)


class AlertBanner(ctk.CTkFrame):
    """
    Componente visual que apresenta um Alerta Priorizado com:
    - Badge de Severidade e Score de Prioridade;
    - Indicador-Chave e Lote afetado;
    - Justificativa Matemática transparente em linguagem natural;
    - Recomendação Gerencial e Aviso de Incerteza Estatística (quando aplicável).
    """

    def __init__(self, master: Any, alert: Alert, **kwargs: Any) -> None:
        color_map = {
            "CRÍTICO": AgroTheme.ACCENT_DANGER,
            "ATENÇÃO": AgroTheme.ACCENT_AMBER,
            "INFORMATIVO": AgroTheme.ACCENT_INFO,
        }
        sev_color = color_map.get(alert.severidade, AgroTheme.ACCENT_EMERALD)

        super().__init__(
            master,
            fg_color=AgroTheme.BG_CARD,
            corner_radius=8,
            border_width=1,
            border_color=sev_color,
            **kwargs,
        )
        self.grid_columnconfigure(0, weight=1)

        # Linha 1: Cabeçalho com Severidade, Título e Indicador
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=12, pady=(8, 4))
        header_frame.grid_columnconfigure(1, weight=1)

        badge = ctk.CTkLabel(
            header_frame,
            text=f" {alert.severidade} • P{alert.score_prioridade} ",
            fg_color=sev_color,
            text_color="#07110B" if alert.severidade != "CRÍTICO" else "#FFFFFF",
            corner_radius=5,
            font=ctk.CTkFont(family=AgroTheme.FONT_FAMILY, size=11, weight="bold"),
        )
        badge.grid(row=0, column=0, padx=(0, 8), sticky="w")

        lbl_title = ctk.CTkLabel(
            header_frame,
            text=f"{alert.titulo}  [{alert.categoria} | Lote: {alert.lote_afetado}]",
            font=ctk.CTkFont(family=AgroTheme.FONT_FAMILY, size=13, weight="bold"),
            text_color=AgroTheme.TEXT_PRIMARY,
            anchor="w",
        )
        lbl_title.grid(row=0, column=1, sticky="ew")

        lbl_kpi = ctk.CTkLabel(
            header_frame,
            text=alert.indicador_chave,
            font=ctk.CTkFont(family=AgroTheme.FONT_FAMILY, size=11, weight="bold"),
            text_color=sev_color,
            anchor="e",
        )
        lbl_kpi.grid(row=0, column=2, padx=(8, 0), sticky="e")

        # Linha 2: Justificativa Matemática Transparente
        lbl_math = ctk.CTkLabel(
            self,
            text=f"📐 Justificativa Analítica: {alert.justificativa_matematica}",
            font=ctk.CTkFont(family=AgroTheme.FONT_FAMILY, size=12),
            text_color=AgroTheme.TEXT_PRIMARY,
            justify="left",
            anchor="w",
            wraplength=980,
        )
        lbl_math.grid(row=1, column=0, sticky="ew", padx=12, pady=(2, 2))

        # Linha 3: Recomendação Gerencial e Incerteza
        rec_text = f"🧭 Ação Recomendada: {alert.recomendacao_gerencial}"
        if alert.aviso_incerteza:
            rec_text += f"   ⚠️ {alert.aviso_incerteza}"

        lbl_rec = ctk.CTkLabel(
            self,
            text=rec_text,
            font=ctk.CTkFont(family=AgroTheme.FONT_FAMILY, size=11),
            text_color=AgroTheme.TEXT_MUTED if not alert.aviso_incerteza else AgroTheme.ACCENT_AMBER,
            justify="left",
            anchor="w",
            wraplength=980,
        )
        lbl_rec.grid(row=2, column=0, sticky="ew", padx=12, pady=(2, 8))


class FilterToolbar(ctk.CTkFrame):
    """Barra de ferramentas com campo de busca rápida e seletores de filtro."""

    def __init__(
        self,
        master: Any,
        search_placeholder: str,
        dropdown_configs: List[Tuple[str, List[str], str]],
        on_filter_change: Callable[[Dict[str, str]], None],
        **kwargs: Any,
    ) -> None:
        super().__init__(
            master,
            fg_color=AgroTheme.BG_CARD,
            corner_radius=8,
            border_width=1,
            border_color=AgroTheme.BORDER_COLOR,
            **kwargs,
        )
        self.on_filter_change = on_filter_change
        self.dropdown_vars: Dict[str, ctk.StringVar] = {}

        lbl_search = ctk.CTkLabel(
            self,
            text="🔎 Buscar:",
            font=ctk.CTkFont(family=AgroTheme.FONT_FAMILY, size=12, weight="bold"),
            text_color=AgroTheme.TEXT_MUTED,
        )
        lbl_search.pack(side="left", padx=(12, 6), pady=8)

        self.search_var = ctk.StringVar(value="")
        self.entry_search = ctk.CTkEntry(
            self,
            textvariable=self.search_var,
            placeholder_text=search_placeholder,
            width=220,
            fg_color=AgroTheme.BG_INPUT,
            border_color=AgroTheme.BORDER_COLOR,
        )
        self.entry_search.pack(side="left", padx=(0, 12), pady=8)
        self.entry_search.bind("<KeyRelease>", lambda _e: self._trigger())

        for key_label, values, default_val in dropdown_configs:
            lbl = ctk.CTkLabel(
                self,
                text=f"{key_label}:",
                font=ctk.CTkFont(family=AgroTheme.FONT_FAMILY, size=12),
                text_color=AgroTheme.TEXT_SECONDARY,
            )
            lbl.pack(side="left", padx=(6, 4), pady=8)

            var = ctk.StringVar(value=default_val)
            self.dropdown_vars[key_label] = var
            combo = ctk.CTkOptionMenu(
                self,
                variable=var,
                values=values,
                width=165,
                fg_color=AgroTheme.BG_SIDEBAR,
                button_color=AgroTheme.ACCENT_EMERALD_DARK,
                button_hover_color=AgroTheme.ACCENT_EMERALD,
                command=lambda _v: self._trigger(),
            )
            combo.pack(side="left", padx=(0, 10), pady=8)

        btn_clear = ctk.CTkButton(
            self,
            text="Limpar Filtros",
            width=105,
            fg_color=AgroTheme.BG_SIDEBAR,
            hover_color=AgroTheme.BG_CARD_HOVER,
            border_width=1,
            border_color=AgroTheme.BORDER_COLOR,
            command=self.reset_filters,
        )
        btn_clear.pack(side="right", padx=12, pady=8)

    def _trigger(self) -> None:
        state = {"busca": self.search_var.get()}
        for k, v in self.dropdown_vars.items():
            state[k] = v.get()
        self.on_filter_change(state)

    def reset_filters(self) -> None:
        self.search_var.set("")
        for k, var in self.dropdown_vars.items():
            var.set("TODOS" if "Status" in k or "Severidade" in k or "Tipo" in k else "TODAS")
        self._trigger()


class DataGrid(ctk.CTkFrame):
    """
    Tabela de alta performance baseada em ttk.Treeview estilizada no tema AgroZica,
    com suporte a ordenação clicável nas colunas e destaque cromático por status/severidade.
    """

    def __init__(
        self,
        master: Any,
        columns: List[Tuple[str, str, int, str]],
        height: int = 12,
        **kwargs: Any,
    ) -> None:
        """
        columns: Lista de tuplas (col_id, titulo_exibicao, largura_px, alinhamento 'w'|'center'|'e')
        """
        super().__init__(
            master,
            fg_color=AgroTheme.BG_CARD,
            corner_radius=8,
            border_width=1,
            border_color=AgroTheme.BORDER_COLOR,
            **kwargs,
        )
        AgroTheme.configure_treeview_style()

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        col_ids = [c[0] for c in columns]
        self.tree = ttk.Treeview(
            self,
            columns=col_ids,
            show="headings",
            height=height,
            style="AgroZica.Treeview",
        )

        vsb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew", padx=(6, 0), pady=(6, 0))
        vsb.grid(row=0, column=1, sticky="ns", padx=(0, 6), pady=(6, 0))
        hsb.grid(row=1, column=0, sticky="ew", padx=(6, 0), pady=(0, 6))

        for col_id, heading_text, width, anchor in columns:
            self.tree.heading(
                col_id,
                text=heading_text,
                command=lambda cid=col_id: self._sort_by_column(cid, False),
            )
            self.tree.column(col_id, width=width, anchor=anchor, stretch=True)

        # Tags de cores para linhas
        self.tree.tag_configure("critico", foreground="#FCA5A5", background="#2A1215")
        self.tree.tag_configure("atencao", foreground="#FDE68A", background="#292111")
        self.tree.tag_configure("normal", foreground=AgroTheme.TEXT_PRIMARY, background=AgroTheme.BG_INPUT)
        self.tree.tag_configure("info", foreground="#93C5FD", background="#102030")
        self.tree.tag_configure("incerteza", foreground="#D8B4FE", background="#1F162B")

    def clear_and_populate(self, rows: List[Tuple[Tuple[Any, ...], str]]) -> None:
        """
        Recebe lista de ((val1, val2, ...), tag_name) e atualiza a tabela.
        """
        for item in self.tree.get_children():
            self.tree.delete(item)
        for values, tag in rows:
            self.tree.insert("", tk.END, values=values, tags=(tag,) if tag else ())

    def _sort_by_column(self, col_id: str, reverse: bool) -> None:
        items = [(self.tree.set(k, col_id), k) for k in self.tree.get_children("")]

        def _parse_val(v: str) -> Any:
            cleaned = (
                v.replace("R$", "")
                .replace("%", "")
                .replace("dias", "")
                .replace(".", "")
                .replace(",", ".")
                .strip()
            )
            try:
                return float(cleaned)
            except ValueError:
                return v.lower()

        items.sort(key=lambda t: _parse_val(t[0]), reverse=reverse)
        for index, (_, k) in enumerate(items):
            self.tree.move(k, "", index)
        self.tree.heading(col_id, command=lambda: self._sort_by_column(col_id, not reverse))

