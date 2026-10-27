"""
Identidade Visual e Paleta de Cores do AgroZica (Dark Mode Verde Floresta, Esmeralda e Âmbar).
Configura temas do CustomTkinter, estilos do ttk.Treeview e paleta para gráficos Matplotlib.
"""

from tkinter import ttk
import customtkinter as ctk


class AgroTheme:
    """Constantes de cores, tipografia e estilização visual do AgroZica."""

    # Cores de Fundo (Dark Forest Palette)
    BG_ROOT = "#0B1610"          # Verde floresta profundo (fundo mestre)
    BG_SIDEBAR = "#0F2017"       # Menu lateral verde escuro
    BG_CARD = "#14291E"          # Superfície de cards e painéis
    BG_CARD_HOVER = "#1B3728"    # Card hover / destaque
    BG_INPUT = "#0D1C14"         # Fundo de campos de entrada e tabelas
    BORDER_COLOR = "#234734"     # Borda sutil esmeralda escuro

    # Cores de Destaque e Semântica
    ACCENT_EMERALD = "#10B981"   # Verde Esmeralda principal
    ACCENT_EMERALD_DARK = "#059669"
    ACCENT_AMBER = "#F59E0B"     # Âmbar / Ouro safra (Atenção / Destaque)
    ACCENT_DANGER = "#EF4444"    # Vermelho Coral (Crítico / Ruptura / Vencido)
    ACCENT_INFO = "#38BDF8"      # Azul Céu (Informativo / Rastreabilidade)
    ACCENT_PURPLE = "#A855F7"    # Roxo (Incerteza / Estatística)

    # Tipografia / Texto
    TEXT_PRIMARY = "#ECFDF5"     # Branco esverdeado suave
    TEXT_SECONDARY = "#9CA3AF"   # Cinza claro
    TEXT_MUTED = "#6EE7B7"       # Verde menta suave para subtítulos

    # Fontes
    FONT_FAMILY = "Segoe UI"

    @classmethod
    def apply_global_theme(cls) -> None:
        """Aplica o modo escuro do CustomTkinter."""
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")

    @classmethod
    def configure_treeview_style(cls) -> None:
        """Estiliza o ttk.Treeview para harmonizar com o Dark Mode Verde Floresta do AgroZica."""
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass

        style.configure(
            "AgroZica.Treeview",
            background=cls.BG_INPUT,
            foreground=cls.TEXT_PRIMARY,
            fieldbackground=cls.BG_INPUT,
            bordercolor=cls.BORDER_COLOR,
            borderwidth=0,
            rowheight=29,
            font=(cls.FONT_FAMILY, 10),
        )
        style.configure(
            "AgroZica.Treeview.Heading",
            background=cls.BG_SIDEBAR,
            foreground=cls.TEXT_MUTED,
            relief="flat",
            font=(cls.FONT_FAMILY, 10, "bold"),
            padding=(6, 6),
        )
        style.map(
            "AgroZica.Treeview",
            background=[("selected", cls.ACCENT_EMERALD_DARK)],
            foreground=[("selected", "#FFFFFF")],
        )
        style.map(
            "AgroZica.Treeview.Heading",
            background=[("active", cls.BG_CARD_HOVER)],
        )

