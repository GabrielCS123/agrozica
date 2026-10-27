"""
Higienizador Semântico e Conversor Auditável de Dados (DataCleaner).
Implementa os Pilares de Confiabilidade e Governança do AgroZica:
1. Padronização automática de grafias divergentes de insumos;
2. Conversão auditável de unidades heterogêneas (kg, saco, ton, L, galao, tambor, mL, rolo_100m);
3. Integridade Semântica: ausência de custo_unitario ou data_validade é preservada como NaN
   ('Pendente / Ausente'), jamais sendo distorcida como zero (0).
"""

from typing import Dict, Any, List, Tuple, Optional
import unicodedata
import difflib
import numpy as np
import pandas as pd

from src.models.entities import ItemAuditoria


def _strip_accents_lower(text: str) -> str:
    if not text:
        return ""
    s = str(text).strip().lower()
    nfkd = unicodedata.normalize("NFKD", s)
    return "".join([c for c in nfkd if not unicodedata.combining(c)])


class DataCleaner:
    """Realiza limpeza, padronização de grafia, conversão de unidades e geração de trilha de auditoria."""

    def __init__(self, config_data: Dict[str, Any]) -> None:
        self.config_data = config_data

    def update_config(self, config_data: Dict[str, Any]) -> None:
        self.config_data = config_data

    def _build_synonym_map(self) -> Dict[str, str]:
        """Mapeia grafia normalizada -> nome canônico do insumo."""
        syn_cfg: Dict[str, List[str]] = self.config_data.get("sinonimos_produtos", {})
        lookup: Dict[str, str] = {}
        for canonical, aliases in syn_cfg.items():
            lookup[_strip_accents_lower(canonical)] = canonical
            for alias in aliases:
                lookup[_strip_accents_lower(alias)] = canonical
        return lookup

    def resolve_product_name(self, raw_name: str, lookup: Dict[str, str]) -> Tuple[str, bool]:
        """
        Retorna (nome_canonico, foi_corrigido).
        Utiliza busca exata sem acento e fallback por similaridade textual (SequenceMatcher).
        """
        clean_raw = str(raw_name).strip()
        norm = _strip_accents_lower(clean_raw)
        if norm in lookup:
            canonical = lookup[norm]
            return canonical, (clean_raw != canonical)

        # Fallback por similaridade caso surja erro de digitação inédito na base oficial
        candidates = list(lookup.keys())
        matches = difflib.get_close_matches(norm, candidates, n=1, cutoff=0.78)
        if matches:
            canonical = lookup[matches[0]]
            return canonical, (clean_raw != canonical)

        return clean_raw, False

    def resolve_unit_conversion(
        self, raw_unit: str, canonical_product: str, category: str
    ) -> Tuple[str, float, bool]:
        """
        Determina (unidade_base, fator_conversao, houve_conversao) a partir do settings.json.
        Respeita fatores específicos por produto (ex: saco de semente de soja = 40kg, milho = 20kg)
        e fatores gerais de conversão.
        """
        conv_cfg = self.config_data.get("conversao_unidades", {})
        base_by_cat = conv_cfg.get("unidades_base_por_categoria", {})
        factors_map = conv_cfg.get("fatores_para_base", {})
        prod_specific = conv_cfg.get("fatores_especificos_produto", {})

        u_raw = str(raw_unit).strip()
        u_norm = u_raw.lower()

        default_base = base_by_cat.get(category, "un")

        # 1. Verifica fator específico do produto (ex: saco de semente 40kg vs saco adubo 50kg)
        if canonical_product in prod_specific:
            prod_rules = prod_specific[canonical_product]
            if u_norm in prod_rules:
                factor = float(prod_rules[u_norm])
                return default_base, factor, True

        # 2. Verifica tabela geral de fatores
        if u_norm in factors_map:
            entry = factors_map[u_norm]
            target_base = str(entry.get("unidade_base", default_base))
            factor = float(entry.get("fator", 1.0))
            converted = (factor != 1.0) or (u_raw != target_base)
            return target_base, factor, converted

        return u_raw or default_base, 1.0, False

    def clean_and_audit(self, df_canonical: pd.DataFrame) -> Tuple[pd.DataFrame, List[ItemAuditoria]]:
        """
        Processa o DataFrame com as 13 colunas canônicas, adicionando colunas analíticas
        padronizadas e retornando a lista detalhada de ocorrências para a Aba de Auditoria.
        """
        df = df_canonical.copy()
        audit_items: List[ItemAuditoria] = []
        syn_lookup = self._build_synonym_map()

        produtos_originais: List[str] = []
        produtos_canonicos: List[str] = []
        unidades_originais: List[str] = []
        unidades_padronizadas: List[str] = []
        fatores_conversao: List[float] = []
        qtds_originais: List[float] = []
        qtds_padronizadas: List[float] = []
        custos_originais: List[Optional[float]] = []
        custos_unit_padronizados: List[Optional[float]] = []
        validades_limpas: List[Optional[str]] = []
        tipos_padronizados: List[str] = []
        inconsistencias_por_linha: List[str] = []

        for idx, row in df.iterrows():
            mov_id = str(row.get("id_movimento", f"MOV-{idx + 1:04d}")).strip()
            dt_mov = str(row.get("data_movimento", "")).strip()
            raw_tipo = str(row.get("tipo_movimento", "Saída")).strip()
            norm_tipo = _strip_accents_lower(raw_tipo)
            tipo = "Entrada" if norm_tipo.startswith("ent") or norm_tipo == "compra" else "Saída"
            tipos_padronizados.append(tipo)

            raw_prod = str(row.get("produto", "Insumo Não Identificado")).strip()
            cat = str(row.get("categoria", "Fertilizantes")).strip()
            lote = str(row.get("lote", "SEM-LOTE")).strip() or "SEM-LOTE"

            row_issues: List[str] = []

            # 1. Padronização de grafia do produto
            can_prod, was_renamed = self.resolve_product_name(raw_prod, syn_lookup)
            produtos_originais.append(raw_prod)
            produtos_canonicos.append(can_prod)
            if was_renamed:
                row_issues.append(f"Grafia unificada: '{raw_prod}' -> '{can_prod}'")
                audit_items.append(
                    ItemAuditoria(
                        id_movimento=mov_id,
                        data_movimento=dt_mov,
                        produto=can_prod,
                        lote=lote,
                        tipo_inconsistencia="Grafia Padronizada",
                        severidade="MÉDIA",
                        valor_original=raw_prod,
                        tratamento_aplicado=f"Padronizado para '{can_prod}'",
                        impacto_analitico="Evita fragmentação de saldo e histórico de consumo do mesmo insumo.",
                    )
                )

            # 2. Quantidade e conversão de unidade de medida
            raw_qtd_val = row.get("quantidade", 0.0)
            try:
                qtd_orig = float(str(raw_qtd_val).replace(",", "."))
            except (ValueError, TypeError):
                qtd_orig = 0.0
            qtds_originais.append(qtd_orig)

            raw_unit = str(row.get("unidade", "un")).strip()
            unidades_originais.append(raw_unit)
            base_unit, factor, unit_converted = self.resolve_unit_conversion(raw_unit, can_prod, cat)
            qtd_pad = round(qtd_orig * factor, 4)

            unidades_padronizadas.append(base_unit)
            fatores_conversao.append(factor)
            qtds_padronizadas.append(qtd_pad)

            if unit_converted:
                row_issues.append(f"Unidade convertida: {qtd_orig:g} {raw_unit} -> {qtd_pad:g} {base_unit} (x{factor:g})")
                audit_items.append(
                    ItemAuditoria(
                        id_movimento=mov_id,
                        data_movimento=dt_mov,
                        produto=can_prod,
                        lote=lote,
                        tipo_inconsistencia="Conversão de Unidade",
                        severidade="BAIXA" if factor == 1.0 else "MÉDIA",
                        valor_original=f"{qtd_orig:g} {raw_unit}",
                        tratamento_aplicado=f"{qtd_pad:g} {base_unit} (Fator: {factor:g})",
                        impacto_analitico="Impede soma direta de grandezas distintas (ex: sacos/galões com kg/L).",
                    )
                )

            # 3. Proteção semântica de custo_unitario (ausência NUNCA é tratada como 0)
            raw_custo = row.get("custo_unitario", None)
            custo_orig: Optional[float] = None
            if pd.notna(raw_custo) and str(raw_custo).strip() not in ("", "nan", "None", "null", "Pendente / Ausente"):
                try:
                    val_c = float(str(raw_custo).replace("R$", "").replace(",", ".").strip())
                    if val_c > 0:
                        custo_orig = val_c
                except (ValueError, TypeError):
                    custo_orig = None

            custos_originais.append(custo_orig)
            if custo_orig is None:
                custos_unit_padronizados.append(None)
                row_issues.append("Preço de aquisição ausente (mantido como NaN / Pendente)")
                audit_items.append(
                    ItemAuditoria(
                        id_movimento=mov_id,
                        data_movimento=dt_mov,
                        produto=can_prod,
                        lote=lote,
                        tipo_inconsistencia="Dado Ausente (NaN)",
                        severidade="MÉDIA",
                        valor_original="Custo Unitário Vazio",
                        tratamento_aplicado="Marcado como 'Pendente / Ausente' (NaN)",
                        impacto_analitico="Não contamina a média histórica de preços com zero artificial.",
                    )
                )
            else:
                custo_pad = round(custo_orig / factor, 4) if factor > 0 else custo_orig
                custos_unit_padronizados.append(custo_pad)

            # 4. Proteção semântica de data_validade (ausência preservada como None/NaN)
            raw_val = row.get("data_validade", None)
            val_str: Optional[str] = None
            if pd.notna(raw_val) and str(raw_val).strip() not in ("", "nan", "None", "null", "0", "Pendente / Ausente"):
                parsed_dt = pd.to_datetime(str(raw_val).strip(), errors="coerce")
                if pd.notna(parsed_dt):
                    val_str = parsed_dt.strftime("%Y-%m-%d")

            validades_limpas.append(val_str)
            if val_str is None and cat in ("Defensivos Químicos", "Defensivos Biológicos", "Sementes", "Fertilizantes"):
                row_issues.append("Data de validade não informada no registro")
                audit_items.append(
                    ItemAuditoria(
                        id_movimento=mov_id,
                        data_movimento=dt_mov,
                        produto=can_prod,
                        lote=lote,
                        tipo_inconsistencia="Dado Ausente (NaN)",
                        severidade="MÉDIA" if cat in ("Defensivos Químicos", "Defensivos Biológicos") else "BAIXA",
                        valor_original="Validade Ausente",
                        tratamento_aplicado="Preservado como 'Pendente / Ausente' (NaN)",
                        impacto_analitico="Sinaliza necessidade de conferência física do rótulo do lote no almoxarifado.",
                    )
                )

            # 5. Verificação de logística reversa de embalagens de defensivos
            dev_status = str(row.get("devolucao_embalagem", "Não Aplicável")).strip()
            if tipo == "Saída" and cat in ("Defensivos Químicos", "Defensivos Biológicos"):
                if dev_status in ("Pendente", "Prazo Vencido"):
                    sev_emb = "ALTA" if dev_status == "Prazo Vencido" else "MÉDIA"
                    audit_items.append(
                        ItemAuditoria(
                            id_movimento=mov_id,
                            data_movimento=dt_mov,
                            produto=can_prod,
                            lote=lote,
                            tipo_inconsistencia="Logística Reversa (inpEV)",
                            severidade=sev_emb,
                            valor_original=f"Embalagem: {dev_status}",
                            tratamento_aplicado="Monitoramento ambiental ativo (Lei 14.785/2023)",
                            impacto_analitico="Exige tríplice lavagem e devolução ao posto de recebimento credenciado.",
                        )
                    )

            inconsistencias_por_linha.append(" | ".join(row_issues) if row_issues else "OK")

        # Atualiza colunas higienizadas e enriquece o DataFrame
        df["tipo_movimento"] = tipos_padronizados
        df["produto_original"] = produtos_originais
        df["produto"] = produtos_canonicos
        df["quantidade_original"] = qtds_originais
        df["unidade_original"] = unidades_originais
        df["quantidade_padronizada"] = qtds_padronizadas
        df["unidade_padronizada"] = unidades_padronizadas
        df["fator_conversao"] = fatores_conversao
        df["custo_unitario_original"] = pd.Series(custos_originais, dtype="float64")
        df["custo_unitario_padronizado"] = pd.Series(custos_unit_padronizados, dtype="float64")
        df["data_validade"] = validades_limpas
        df["inconsistencias_detectadas"] = inconsistencias_por_linha

        # Cálculo do custo total do movimento usando custo padronizado ou média histórica auditada do produto
        medias_por_produto = (
            df.groupby("produto")["custo_unitario_padronizado"]
            .transform(lambda s: s.dropna().mean() if len(s.dropna()) > 0 else np.nan)
        )
        custo_efetivo = df["custo_unitario_padronizado"].fillna(medias_por_produto).fillna(0.0)
        df["custo_total_movimento"] = (df["quantidade_padronizada"] * custo_efetivo).round(2)

        # Garante ordenação temporal consistente
        df["data_movimento_dt"] = pd.to_datetime(df["data_movimento"], errors="coerce")
        df = df.sort_values(by=["data_movimento_dt", "id_movimento"], ascending=[True, True]).reset_index(drop=True)

        return df, audit_items

