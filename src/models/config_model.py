"""
Gerenciador de Configuração Dinâmica (ConfigModel) do AgroZica.
Permite leitura e gravação a quente ('hot-reload') do arquivo config/settings.json,
garantindo que nenhum parâmetro matemático fique fixo (hardcoded) no código-fonte.
"""

from pathlib import Path
import json
import sys
from typing import Dict, Any, List


def get_base_dir() -> Path:
    """
    Retorna o diretório raiz do aplicativo AgroZica, funcionando tanto em modo
    desenvolvimento Python quanto compilado em executável (.exe) via PyInstaller.
    """
    if getattr(sys, "frozen", False):
        exe_dir = Path(sys.executable).resolve().parent
        if (exe_dir / "config" / "settings.json").exists():
            return exe_dir
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            return Path(meipass)
        return exe_dir
    return Path(__file__).resolve().parent.parent.parent


class ConfigModel:
    """Gerencia acesso, atualização ao vivo e persistência de config/settings.json."""

    def __init__(self, config_path: Path | None = None) -> None:
        self.base_dir = get_base_dir()
        self.config_path = config_path or (self.base_dir / "config" / "settings.json")
        self._data: Dict[str, Any] = {}
        self.load()

    def load(self) -> Dict[str, Any]:
        """Carrega o arquivo JSON de configurações ou restaura padrões seguros."""
        if self.config_path.exists():
            with open(self.config_path, mode="r", encoding="utf-8") as f:
                self._data = json.load(f)
        else:
            self._data = self._default_settings()
            self.save()
        return self._data

    def save(self) -> None:
        """Persiste imediatamente o estado atual das configurações em settings.json."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, mode="w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2, ensure_ascii=False)

    @property
    def data(self) -> Dict[str, Any]:
        return self._data

    def get_param(self, key: str, default: Any = None) -> Any:
        """Obtém um parâmetro numérico do motor de regras."""
        return self._data.get("parametros_regras", {}).get(key, default)

    def set_param(self, key: str, value: Any, auto_save: bool = True) -> None:
        """Atualiza um limiar matemático do motor de regras em tempo real."""
        if "parametros_regras" not in self._data:
            self._data["parametros_regras"] = {}
        self._data["parametros_regras"][key] = value
        if auto_save:
            self.save()

    def is_rule_active(self, rule_id: str) -> bool:
        """Verifica se uma regra do motor está habilitada na interface."""
        return bool(self._data.get("regras_ativas", {}).get(rule_id, True))

    def set_rule_active(self, rule_id: str, active: bool, auto_save: bool = True) -> None:
        """Ativa ou desativa uma regra específica sem reiniciar o sistema."""
        if "regras_ativas" not in self._data:
            self._data["regras_ativas"] = {}
        self._data["regras_ativas"][rule_id] = bool(active)
        if auto_save:
            self.save()

    def add_product_synonym(self, canonical_name: str, synonym: str, auto_save: bool = True) -> None:
        """Adiciona dinamicamente uma nova grafia/sinônimo de produto ao dicionário."""
        sinonimos = self._data.setdefault("sinonimos_produtos", {})
        lista = sinonimos.setdefault(canonical_name, [])
        norm = synonym.strip().lower()
        if norm and norm not in [s.lower() for s in lista]:
            lista.append(norm)
            if auto_save:
                self.save()

    def get_cost_centers(self) -> List[str]:
        """Retorna os centros de custo configurados para a propriedade de 500ha."""
        return self._data.get("centros_custo_500ha", [
            "Almoxarifado Central (Entrada)",
            "Talhão 01 - Soja (150ha)",
            "Talhão 02 - Milho Safrinha (120ha)",
            "Pastos Rotacionados (30 Piquetes - 140ha)",
            "Semiconfinamento (200 Bovinos)",
            "Silos e Armazenagem",
            "Manutenção de Cercas e Infraestrutura",
            "Manutenção de Máquinas e Frota",
        ])

    def get_categories(self) -> List[str]:
        """Retorna as categorias oficiais de insumos."""
        return self._data.get("categorias_insumos", [
            "Fertilizantes",
            "Corretivos",
            "Sementes",
            "Defensivos Químicos",
            "Defensivos Biológicos",
            "Combustíveis e Lubrificantes",
            "Peças e Manutenção",
            "Irrigação",
            "EPIs",
        ])

    def reset_to_defaults(self) -> None:
        """Restaura os limiares recomendados de fábrica para a propriedade de 500ha."""
        self._data["parametros_regras"] = {
            "dias_estoque_critico": 8,
            "dias_estoque_atencao": 20,
            "dias_alerta_validade": 45,
            "z_score_anomalia": 2.0,
            "crescimento_progressivo_pct": 30.0,
            "variacao_preco_pct": 20.0,
            "dias_capital_parado": 45,
            "autonomia_excesso_dias": 180,
            "min_historico_saidas": 3,
            "janela_consumo_dias": 60,
            "prazo_legal_embalagem_dias": 90,
        }
        for k in list(self._data.get("regras_ativas", {}).keys()):
            self._data["regras_ativas"][k] = True
        self.save()

    @staticmethod
    def _default_settings() -> Dict[str, Any]:
        return {
            "sistema": {
                "nome": "AgroZica - Inteligência Analítica e Gestão Rastreável de Insumos Rurais",
                "versao": "2.6.0-AGROHACK",
                "propriedade_modelo": "Fazenda Experimental AgroZica (500 ha - Ariquemes/RO)",
                "area_total_ha": 500,
                "moeda": "BRL",
                "data_referencia_simulacao": "2026-10-27",
            },
            "parametros_regras": {
                "dias_estoque_critico": 8,
                "dias_estoque_atencao": 20,
                "dias_alerta_validade": 45,
                "z_score_anomalia": 2.0,
                "crescimento_progressivo_pct": 30.0,
                "variacao_preco_pct": 20.0,
                "dias_capital_parado": 45,
                "autonomia_excesso_dias": 180,
                "min_historico_saidas": 3,
                "janela_consumo_dias": 60,
                "prazo_legal_embalagem_dias": 90,
            },
            "regras_ativas": {
                "RULE_ESTOQUE_CRITICO": True,
                "RULE_VALIDADE_GIRO": True,
                "RULE_ANOMALIA_RETIRADA": True,
                "RULE_TENDENCIA_ALTA": True,
                "RULE_VARIACAO_PRECO": True,
                "RULE_CAPITAL_PARADO": True,
                "RULE_EMBALAGENS_DEFENSIVOS": True,
            },
        }

