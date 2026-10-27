"""
Ponto de entrada principal (Entry Point) do sistema desktop AgroZica.
Verifica/gera a base simulada de 500ha, inicializa a arquitetura MTC (Model-Template-Controller)
e inicia a interface gráfica CustomTkinter.
Aceita a flag opcional '--diagnose' para exibir no console o resumo executivo da análise.
"""

from pathlib import Path
import sys

# Garante que o diretório raiz do projeto esteja no sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from generator_seed import generate_seed_csv
from src.controllers.main_controller import MainController


def run_cli_diagnostics(controller: MainController) -> None:
    """Imprime no terminal um resumo executivo completo do motor analítico do AgroZica."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    kpis = controller.get_dashboard_kpis()
    print("=" * 88)
    print("🌱 AGROZICA v2.6 — DIAGNÓSTICO ANALÍTICO AUTOMATIZADO (AGROHACK 2026/2 - IFRO)")
    print("=" * 88)
    print(f"• Insumos Monitorados (Padronizados): {kpis['total_insumos']}")
    print(f"• Movimentações Processadas:          {kpis['total_movimentacoes']}")
    print(f"• Capital Atual em Estoque:           R$ {kpis['valor_estoque_total']:,.2f}")
    print(f"• Custo Apropriado nos 500ha:         R$ {kpis['valor_consumido_total']:,.2f}")
    print(f"• Alertas Ativos no Motor:            {kpis['total_alertas']} "
          f"({kpis['alertas_criticos']} Críticos | {kpis['alertas_atencao']} Atenção | {kpis['alertas_info']} Info)")
    print(f"• Tratamentos de Auditoria Aplicados: {kpis['total_auditoria']}")
    print(f"• Divergências Físicas de Lote:       {kpis['divergencias_lote']}")
    print(f"• Insumos c/ Incerteza Estatística:   {kpis['itens_incerteza']}")
    print("-" * 88)
    print("TOP ALERTAS PRIORIZADOS PELO MOTOR DE REGRAS:")
    for idx, alert in enumerate(controller.alerts[:10], start=1):
        print(f"  {idx:02d}. [{alert.severidade} • P{alert.score_prioridade}] {alert.titulo}")
        print(f"      Indicador: {alert.indicador_chave}")
        print(f"      Justificativa: {alert.justificativa_matematica}")
    print("=" * 88)


def main() -> None:
    """Verifica a base inicial de 500ha e inicializa o aplicativo desktop AgroZica."""
    csv_seed_path = BASE_DIR / "data" / "base_simulada_agrozica.csv"
    if not csv_seed_path.exists():
        generate_seed_csv(csv_seed_path)

    controller = MainController()

    if "--diagnose" in sys.argv:
        run_cli_diagnostics(controller)
        return

    from src.templates.main_template import MainTemplate

    app = MainTemplate(controller=controller)
    app.mainloop()


if __name__ == "__main__":
    main()
