"""
Adaptador Inteligente de Colunas (ColumnMapper - Adapter Pattern).
Permite importar planilhas externas (.csv ou .xlsx) disponibilizadas pela organização
do AGROHACK mesmo quando os nomes das colunas divergem do esquema interno,
traduzindo-as automaticamente para as 13 colunas canônicas do AgroZica.
"""

from typing import Dict, List, Tuple
import unicodedata
import re
import pandas as pd


CANONICAL_COLUMNS: List[str] = [
    "id_movimento",
    "data_movimento",
    "tipo_movimento",
    "produto",
    "categoria",
    "lote",
    "quantidade",
    "unidade",
    "custo_unitario",
    "data_validade",
    "destino_centro_custo",
    "responsavel",
    "devolucao_embalagem",
]


def normalize_token(text: str) -> str:
    """Remove acentos, caracteres especiais e converte para snake_case minúsculo."""
    if not text:
        return ""
    text_str = str(text).strip().lower()
    nfkd = unicodedata.normalize("NFKD", text_str)
    without_accents = "".join([c for c in nfkd if not unicodedata.combining(c)])
    cleaned = re.sub(r"[^a-z0-9]+", "_", without_accents).strip("_")
    return cleaned


class ColumnMapper:
    """
    Aplica o padrão Adapter sobre qualquer DataFrame bruto importado,
    mapeando cabeçalhos variados para as 13 colunas canônicas do AgroZica.
    """

    def __init__(self, mapping_config: Dict[str, List[str]] | None = None) -> None:
        self.mapping_config = mapping_config or {}

    def adapt_dataframe(self, df_raw: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, str], List[str]]:
        """
        Recebe um DataFrame bruto e retorna:
        1. DataFrame padronizado com as 13 colunas canônicas;
        2. Dicionário de tradução aplicada {coluna_original: coluna_canonica};
        3. Lista de colunas canônicas que não existiam na planilha e foram preenchidas com padrão seguro.
        """
        df = df_raw.copy()
        reverse_lookup: Dict[str, str] = {}

        # Constrói índice reverso normalizado a partir do settings.json
        for canonical_col in CANONICAL_COLUMNS:
            reverse_lookup[normalize_token(canonical_col)] = canonical_col
            aliases = self.mapping_config.get(canonical_col, [])
            for alias in aliases:
                reverse_lookup[normalize_token(alias)] = canonical_col

        applied_mapping: Dict[str, str] = {}
        rename_dict: Dict[str, str] = {}
        used_canonicals = set()

        for raw_col in df.columns:
            norm_raw = normalize_token(str(raw_col))
            target_canonical = reverse_lookup.get(norm_raw)

            # Fallback por substring se não houver match exato
            if not target_canonical:
                for alias_norm, can_col in reverse_lookup.items():
                    if alias_norm and (alias_norm in norm_raw or norm_raw in alias_norm):
                        if can_col not in used_canonicals:
                            target_canonical = can_col
                            break

            if target_canonical and target_canonical not in used_canonicals:
                rename_dict[raw_col] = target_canonical
                applied_mapping[str(raw_col)] = target_canonical
                used_canonicals.add(target_canonical)

        df = df.rename(columns=rename_dict)

        missing_columns: List[str] = []
        for idx, can_col in enumerate(CANONICAL_COLUMNS):
            if can_col not in df.columns:
                missing_columns.append(can_col)
                if can_col == "id_movimento":
                    df[can_col] = [f"IMP-{i + 1:04d}" for i in range(len(df))]
                elif can_col == "tipo_movimento":
                    df[can_col] = "Saída"
                elif can_col == "categoria":
                    df[can_col] = "Fertilizantes"
                elif can_col == "lote":
                    df[can_col] = "LOTE-UNICO"
                elif can_col == "unidade":
                    df[can_col] = "un"
                elif can_col in ("custo_unitario", "data_validade"):
                    df[can_col] = None  # Nunca 0!
                elif can_col == "destino_centro_custo":
                    df[can_col] = "Talhão 01 - Soja (150ha)"
                elif can_col == "responsavel":
                    df[can_col] = "Operador Não Informado"
                elif can_col == "devolucao_embalagem":
                    df[can_col] = "Não Aplicável"
                else:
                    df[can_col] = ""

        # Garante a ordem exata das 13 colunas canônicas
        df = df[CANONICAL_COLUMNS].copy()
        return df, applied_mapping, missing_columns

