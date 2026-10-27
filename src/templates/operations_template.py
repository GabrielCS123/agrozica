"""
Aba 3: Central Operacional de Lançamentos, Reanálise ao Vivo e Importação Oficial (OperationsTemplate).
Permite:
- Registrar novas Entradas e Saídas com validação, proteção de campos vazios (NaN) e conversão automática de unidades;
- Importar qualquer planilha externa (.csv ou .xlsx) do AGROHACK com adaptação automática via ColumnMapper;
- Exportar relatórios analíticos consolidados (.xlsx / .csv);
- Visualizar todo o histórico de movimentações comparando o dado original (bruto) com o padronizado.
"""

from tkinter import filedialog, messagebox
from typing import Any, List, Tuple
import customtkinter as ctk

from src.templates.theme import AgroTheme
from src.templates.components import DataGrid
from src.controllers.main_controller import MainController


class OperationsTemplate(ctk.CTkFrame):
    """View de Lançamento Centralizado, Importação Resiliente e Histórico Rastreável."""

    def __init__(self, master: Any, controller: MainController, **kwargs: Any) -> None:
        super().__init__(master, fg_color="transparent", **kwargs)
        self.controller = controller

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._build_import_export_bar()
        self._build_movement_form()
        self._build_history_grid()

        self.controller.subscribe(self.refresh_view)
        self.refresh_view()

    def _build_import_export_bar(self) -> None:
        bar = ctk.CTkFrame(
            self,
            fg_color=AgroTheme.BG_SIDEBAR,
            corner_radius=10,
            border_width=1,
            border_color=AgroTheme.BORDER_COLOR,
        )
        bar.grid(row=0, column=0, sticky="ew", padx=4, pady=(0, 8))

        lbl_info = ctk.CTkLabel(
            bar,
            text="📂 Adaptador Oficial AGROHACK (ColumnMapper): Importe planilhas .CSV ou .XLSX com mapeamento automático para as 13 colunas canônicas",
            font=ctk.CTkFont(family=AgroTheme.FONT_FAMILY, size=12, weight="bold"),
            text_color=AgroTheme.TEXT_PRIMARY,
        )
        lbl_info.pack(side="left", padx=14, pady=10)

        btn_seed = ctk.CTkButton(
            bar,
            text="♻️ Restaurar Base Simulada (500ha)",
            width=205,
            fg_color=AgroTheme.BG_CARD,
            hover_color=AgroTheme.BG_CARD_HOVER,
            border_width=1,
            border_color=AgroTheme.BORDER_COLOR,
            command=self._on_restore_seed,
        )
        btn_seed.pack(side="right", padx=(6, 12), pady=10)

        btn_export = ctk.CTkButton(
            bar,
            text="📤 Exportar Relatório (.XLSX/.CSV)",
            width=205,
            fg_color=AgroTheme.BG_CARD,
            hover_color=AgroTheme.BG_CARD_HOVER,
            border_width=1,
            border_color=AgroTheme.ACCENT_EMERALD,
            command=self._on_export_report,
        )
        btn_export.pack(side="right", padx=6, pady=10)

        btn_import = ctk.CTkButton(
            bar,
            text="📥 Importar Base Oficial (.CSV/.XLSX)",
            width=225,
            fg_color=AgroTheme.ACCENT_EMERALD_DARK,
            hover_color=AgroTheme.ACCENT_EMERALD,
            font=ctk.CTkFont(family=AgroTheme.FONT_FAMILY, size=12, weight="bold"),
            command=self._on_import_file,
        )
        btn_import.pack(side="right", padx=6, pady=10)

    def _build_movement_form(self) -> None:
        form = ctk.CTkFrame(
            self,
            fg_color=AgroTheme.BG_CARD,
            corner_radius=10,
            border_width=1,
            border_color=AgroTheme.BORDER_COLOR,
        )
        form.grid(row=1, column=0, sticky="ew", padx=4, pady=(0, 8))
        for col_idx in range(6):
            form.grid_columnconfigure(col_idx, weight=1)

        title_lbl = ctk.CTkLabel(
            form,
            text="➕ Novo Lançamento Rastreável (Aciona Higienização, Conversão de Unidades e Reanálise em Tempo Real)",
            font=ctk.CTkFont(family=AgroTheme.FONT_FAMILY, size=13, weight="bold"),
            text_color=AgroTheme.TEXT_MUTED,
            anchor="w",
        )
        title_lbl.grid(row=0, column=0, columnspan=6, sticky="ew", padx=14, pady=(10, 6))

        # Linha 1 de campos
        self.var_data = ctk.StringVar(value="2026-10-27")
        self.var_tipo = ctk.StringVar(value="Saída")
        self.var_produto = ctk.StringVar(value="Óleo Diesel S10")
        self.var_categoria = ctk.StringVar(value="Combustíveis e Lubrificantes")
        self.var_lote = ctk.StringVar(value="DSL-2610B")
        self.var_qtd = ctk.StringVar(value="150")

        self._add_field(form, 1, 0, "Data (AAAA-MM-DD):", ctk.CTkEntry(form, textvariable=self.var_data, fg_color=AgroTheme.BG_INPUT))
        self._add_field(
            form,
            1,
            1,
            "Tipo de Movimento:",
            ctk.CTkOptionMenu(
                form,
                variable=self.var_tipo,
                values=["Entrada", "Saída"],
                fg_color=AgroTheme.BG_SIDEBAR,
                button_color=AgroTheme.ACCENT_EMERALD_DARK,
            ),
        )
        self._add_field(
            form,
            1,
            2,
            "Produto (Aceita Sinônimos):",
            ctk.CTkEntry(form, textvariable=self.var_produto, fg_color=AgroTheme.BG_INPUT),
        )
        self._add_field(
            form,
            1,
            3,
            "Categoria do Insumo:",
            ctk.CTkOptionMenu(
                form,
                variable=self.var_categoria,
                values=self.controller.config_model.get_categories(),
                fg_color=AgroTheme.BG_SIDEBAR,
                button_color=AgroTheme.ACCENT_EMERALD_DARK,
            ),
        )
        self._add_field(
            form,
            1,
            4,
            "Código do Lote (FEFO):",
            ctk.CTkEntry(form, textvariable=self.var_lote, fg_color=AgroTheme.BG_INPUT),
        )
        self._add_field(
            form,
            1,
            5,
            "Quantidade:",
            ctk.CTkEntry(form, textvariable=self.var_qtd, fg_color=AgroTheme.BG_INPUT),
        )

        # Linha 2 de campos
        self.var_unidade = ctk.StringVar(value="L")
        self.var_custo = ctk.StringVar(value="6.35")
        self.var_validade = ctk.StringVar(value="2027-10-05")
        self.var_destino = ctk.StringVar(value="Talhão 01 - Soja (150ha)")
        self.var_resp = ctk.StringVar(value="João Tratorista")
        self.var_embalagem = ctk.StringVar(value="Não Aplicável")

        unidades_disp = ["kg", "saco", "saco_40kg", "ton", "L", "ml", "galao", "bombona", "tambor", "un", "m", "rolo_100m"]
        self._add_field(
            form,
            3,
            0,
            "Unidade Informada:",
            ctk.CTkOptionMenu(
                form,
                variable=self.var_unidade,
                values=unidades_disp,
                fg_color=AgroTheme.BG_SIDEBAR,
                button_color=AgroTheme.ACCENT_EMERALD_DARK,
            ),
        )
        self._add_field(
            form,
            3,
            1,
            "Custo Unit. R$ (Vazio = NaN):",
            ctk.CTkEntry(form, textvariable=self.var_custo, placeholder_text="Opcional (Nunca vira 0)", fg_color=AgroTheme.BG_INPUT),
        )
        self._add_field(
            form,
            3,
            2,
            "Validade (Vazio = NaN):",
            ctk.CTkEntry(form, textvariable=self.var_validade, placeholder_text="AAAA-MM-DD ou vazio", fg_color=AgroTheme.BG_INPUT),
        )
        self._add_field(
            form,
            3,
            3,
            "Destino / Centro de Custo (500ha):",
            ctk.CTkOptionMenu(
                form,
                variable=self.var_destino,
                values=self.controller.config_model.get_cost_centers(),
                fg_color=AgroTheme.BG_SIDEBAR,
                button_color=AgroTheme.ACCENT_EMERALD_DARK,
            ),
        )
        self._add_field(
            form,
            3,
            4,
            "Responsável Operacional:",
            ctk.CTkEntry(form, textvariable=self.var_resp, fg_color=AgroTheme.BG_INPUT),
        )
        self._add_field(
            form,
            3,
            5,
            "Embalagem Defensivo (inpEV):",
            ctk.CTkOptionMenu(
                form,
                variable=self.var_embalagem,
                values=["Não Aplicável", "Pendente", "Devolvida", "Prazo Vencido"],
                fg_color=AgroTheme.BG_SIDEBAR,
                button_color=AgroTheme.ACCENT_EMERALD_DARK,
            ),
        )

        # Linha de Ações e Feedback
        action_frame = ctk.CTkFrame(form, fg_color="transparent")
        action_frame.grid(row=5, column=0, columnspan=6, sticky="ew", padx=14, pady=(8, 10))

        self.lbl_feedback = ctk.CTkLabel(
            action_frame,
            text="💡 Dica: Você pode digitar grafias como 'glifosato 480' ou unidades em 'galao'/'saco' para testar a higienização ao vivo.",
            font=ctk.CTkFont(family=AgroTheme.FONT_FAMILY, size=11),
            text_color=AgroTheme.TEXT_SECONDARY,
        )
        self.lbl_feedback.pack(side="left")

        btn_submit = ctk.CTkButton(
            action_frame,
            text="✅ Registrar Movimentação & Recalcular Inteligência",
            width=310,
            height=34,
            fg_color=AgroTheme.ACCENT_EMERALD_DARK,
            hover_color=AgroTheme.ACCENT_EMERALD,
            font=ctk.CTkFont(family=AgroTheme.FONT_FAMILY, size=12, weight="bold"),
            command=self._on_submit_movement,
        )
        btn_submit.pack(side="right")

    def _add_field(self, parent: Any, row_lbl: int, col: int, label_text: str, widget: Any) -> None:
        lbl = ctk.CTkLabel(
            parent,
            text=label_text,
            font=ctk.CTkFont(family=AgroTheme.FONT_FAMILY, size=11),
            text_color=AgroTheme.TEXT_SECONDARY,
            anchor="w",
        )
        lbl.grid(row=row_lbl, column=col, sticky="ew", padx=8, pady=(4, 1))
        widget.grid(row=row_lbl + 1, column=col, sticky="ew", padx=8, pady=(0, 4))

    def _build_history_grid(self) -> None:
        hist_frame = ctk.CTkFrame(self, fg_color="transparent")
        hist_frame.grid(row=2, column=0, sticky="nsew", padx=4, pady=0)
        hist_frame.grid_columnconfigure(0, weight=1)
        hist_frame.grid_rowconfigure(1, weight=1)

        self.lbl_hist_title = ctk.CTkLabel(
            hist_frame,
            text="📋 Histórico Auditado de Movimentações (Comparativo Bruto vs. Padronizado)",
            font=ctk.CTkFont(family=AgroTheme.FONT_FAMILY, size=13, weight="bold"),
            text_color=AgroTheme.TEXT_PRIMARY,
            anchor="w",
        )
        self.lbl_hist_title.grid(row=0, column=0, sticky="ew", padx=4, pady=(0, 4))

        columns = [
            ("id", "ID", 85, "center"),
            ("data", "Data", 90, "center"),
            ("tipo", "Tipo", 75, "center"),
            ("prod_orig", "Grafia Bruta", 155, "w"),
            ("prod_pad", "Insumo Padronizado", 185, "w"),
            ("lote", "Lote", 95, "center"),
            ("qtd_orig", "Qtd. Bruta", 95, "e"),
            ("qtd_pad", "Qtd. Padronizada", 115, "e"),
            ("custo", "Custo Unit. Base", 115, "e"),
            ("validade", "Validade", 95, "center"),
            ("destino", "Centro de Custo (500ha)", 190, "w"),
            ("tratamento", "Diagnóstico DataCleaner", 240, "w"),
        ]
        self.grid_history = DataGrid(hist_frame, columns=columns, height=13)
        self.grid_history.grid(row=1, column=0, sticky="nsew")

    def _on_submit_movement(self) -> None:
        data = {
            "data_movimento": self.var_data.get(),
            "tipo_movimento": self.var_tipo.get(),
            "produto": self.var_produto.get(),
            "categoria": self.var_categoria.get(),
            "lote": self.var_lote.get(),
            "quantidade": self.var_qtd.get(),
            "unidade": self.var_unidade.get(),
            "custo_unitario": self.var_custo.get(),
            "data_validade": self.var_validade.get(),
            "destino_centro_custo": self.var_destino.get(),
            "responsavel": self.var_resp.get(),
            "devolucao_embalagem": self.var_embalagem.get(),
        }
        ok, msg = self.controller.register_new_movement(data)
        self.lbl_feedback.configure(
            text=f"{'✅' if ok else '❌'} {msg}",
            text_color=AgroTheme.ACCENT_EMERALD if ok else AgroTheme.ACCENT_DANGER,
        )

    def _on_import_file(self) -> None:
        file_path = filedialog.askopenfilename(
            title="Importar Planilha Oficial AGROHACK (.CSV ou .XLSX)",
            filetypes=[("Planilhas de Dados", "*.csv *.xlsx *.xls"), ("Todos os Arquivos", "*.*")],
        )
        if not file_path:
            return
        ok, msg = self.controller.import_external_spreadsheet(file_path)
        self.lbl_feedback.configure(
            text=f"{'✅' if ok else '❌'} {msg}",
            text_color=AgroTheme.ACCENT_EMERALD if ok else AgroTheme.ACCENT_DANGER,
        )
        if ok:
            messagebox.showinfo("Importação Concluída (ColumnMapper)", msg)
        else:
            messagebox.showerror("Erro na Importação", msg)

    def _on_export_report(self) -> None:
        file_path = filedialog.asksaveasfilename(
            title="Exportar Relatório Analítico AgroZica",
            defaultextension=".xlsx",
            initialfile="Relatorio_Executivo_AgroZica.xlsx",
            filetypes=[("Excel Workbook (.xlsx)", "*.xlsx"), ("CSV (.csv)", "*.csv")],
        )
        if not file_path:
            return
        ok, msg = self.controller.export_consolidated_report(file_path)
        self.lbl_feedback.configure(
            text=f"{'✅' if ok else '❌'} {msg}",
            text_color=AgroTheme.ACCENT_EMERALD if ok else AgroTheme.ACCENT_DANGER,
        )

    def _on_restore_seed(self) -> None:
        ok, msg = self.controller.reload_simulated_seed()
        self.lbl_feedback.configure(
            text=f"{'✅' if ok else '❌'} {msg}",
            text_color=AgroTheme.ACCENT_EMERALD if ok else AgroTheme.ACCENT_DANGER,
        )

    def refresh_view(self) -> None:
        df = self.controller.inventory_model.df_clean
        self.lbl_hist_title.configure(
            text=f"📋 Histórico Auditado de Movimentações ({len(df)} registros processados — mais recentes no topo)"
        )
        if df.empty:
            self.grid_history.clear_and_populate([])
            return

        rows: List[Tuple[Tuple[Any, ...], str]] = []
        df_rev = df.iloc[::-1]
        for _, r in df_rev.iterrows():
            custo_pad = r.get("custo_unitario_padronizado")
            custo_str = (
                f"R$ {float(custo_pad):,.2f}/{r['unidade_padronizada']}"
                if custo_pad is not None and str(custo_pad) != "nan"
                else "Pendente / Ausente"
            )
            val_str = str(r["data_validade"]) if r["data_validade"] is not None else "Pendente / N.A."
            incons = str(r.get("inconsistencias_detectadas", "OK"))

            if "Preço de aquisição ausente" in incons:
                tag = "atencao"
            elif incons != "OK":
                tag = "info"
            else:
                tag = "normal"

            rows.append(
                (
                    (
                        r["id_movimento"],
                        r["data_movimento"],
                        r["tipo_movimento"],
                        r["produto_original"],
                        r["produto"],
                        r["lote"],
                        f"{float(r['quantidade_original']):g} {r['unidade_original']}",
                        f"{float(r['quantidade_padronizada']):g} {r['unidade_padronizada']}",
                        custo_str,
                        val_str,
                        r["destino_centro_custo"],
                        incons,
                    ),
                    tag,
                )
            )
        self.grid_history.clear_and_populate(rows)

