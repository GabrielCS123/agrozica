"""
Gerador determinístico da base simulada oficial do AgroZica (AGROHACK 2026/2 - IFRO Ariquemes).
Modela uma propriedade de 500 hectares (Soja, Milho, 30 Pastos Rotacionados, Semiconfinamento de 200 Bovinos,
Silos e Manutenção) com mais de 100 movimentações cobrindo todos os casos de análise e auditoria do edital.
"""

from pathlib import Path
import csv
from typing import List, Dict, Any


def build_simulated_records() -> List[Dict[str, Any]]:
    """
    Constrói de forma determinística os registros brutos de movimentação do almoxarifado rural.
    Inclui propositalmente:
    - Grafias divergentes para teste do DataCleaner (ex: 'Glifosato 480', 'roundup glifosato', 'Uréia')
    - Unidades misturadas para o mesmo insumo (ex: 'galao' e 'L', 'ton', 'saco' e 'kg', 'tambor' e 'L')
    - Preços de aquisição e datas de validade ausentes ('') para validar proteção contra zero
    - Ruptura crítica (<= 8 dias) e atenção (<= 20 dias)
    - Lotes de biológicos/defensivos que vencem antes do consumo estimado (FEFO vs Giro)
    - Anomalia estatística de retirada (Z-Score > 2.0)
    - Crescimento progressivo de demanda (> 30%)
    - Inflação abrupta no preço de aquisição (> 20%)
    - Capital imobilizado / estoque parado (> 45 dias sem giro e autonomia > 180 dias)
    - Embalagens de agrotóxicos pendentes e com prazo vencido
    - Produtos com histórico escasso (< 3 saídas) para sinalização de Incerteza Alta
    - Divergência de conciliação de lote para demonstração de Auditoria Rastreável
    """
    rows: List[Dict[str, Any]] = [
        # =========================================================================
        # 1. ÓLEO DIESEL S10 -> Estoque Crítico (<= 8 dias), unidades misturadas (tambor/L) e grafias divergentes
        # =========================================================================
        {
            "id_movimento": "MOV-0001", "data_movimento": "2026-09-01", "tipo_movimento": "Entrada",
            "produto": "Óleo Diesel S10", "categoria": "Combustíveis e Lubrificantes", "lote": "DSL-2609A",
            "quantidade": 15, "unidade": "tambor", "custo_unitario": 1220.00, "data_validade": "2027-09-01",
            "destino_centro_custo": "Almoxarifado Central (Entrada)", "responsavel": "Marcos Souza",
            "devolucao_embalagem": "Não Aplicável"
        },
        {
            "id_movimento": "MOV-0002", "data_movimento": "2026-09-08", "tipo_movimento": "Saída",
            "produto": "diesel s10", "categoria": "Combustíveis e Lubrificantes", "lote": "DSL-2609A",
            "quantidade": 650, "unidade": "L", "custo_unitario": 6.10, "data_validade": "2027-09-01",
            "destino_centro_custo": "Manutenção de Máquinas e Frota", "responsavel": "João Tratorista",
            "devolucao_embalagem": "Não Aplicável"
        },
        {
            "id_movimento": "MOV-0003", "data_movimento": "2026-09-18", "tipo_movimento": "Saída",
            "produto": "oleo diesel s10", "categoria": "Combustíveis e Lubrificantes", "lote": "DSL-2609A",
            "quantidade": 720, "unidade": "litros", "custo_unitario": 6.10, "data_validade": "2027-09-01",
            "destino_centro_custo": "Talhão 01 - Soja (150ha)", "responsavel": "João Tratorista",
            "devolucao_embalagem": "Não Aplicável"
        },
        {
            "id_movimento": "MOV-0004", "data_movimento": "2026-09-29", "tipo_movimento": "Saída",
            "produto": "Óleo Diesel S10", "categoria": "Combustíveis e Lubrificantes", "lote": "DSL-2609A",
            "quantidade": 680, "unidade": "L", "custo_unitario": 6.10, "data_validade": "2027-09-01",
            "destino_centro_custo": "Talhão 01 - Soja (150ha)", "responsavel": "Pedro Operador",
            "devolucao_embalagem": "Não Aplicável"
        },
        {
            "id_movimento": "MOV-0005", "data_movimento": "2026-10-05", "tipo_movimento": "Entrada",
            "produto": "Óleo Diesel S10", "categoria": "Combustíveis e Lubrificantes", "lote": "DSL-2610B",
            "quantidade": 1200, "unidade": "L", "custo_unitario": 6.35, "data_validade": "2027-10-05",
            "destino_centro_custo": "Almoxarifado Central (Entrada)", "responsavel": "Marcos Souza",
            "devolucao_embalagem": "Não Aplicável"
        },
        {
            "id_movimento": "MOV-0006", "data_movimento": "2026-10-10", "tipo_movimento": "Saída",
            "produto": "Diesel S10", "categoria": "Combustíveis e Lubrificantes", "lote": "DSL-2609A",
            "quantidade": 750, "unidade": "L", "custo_unitario": 6.10, "data_validade": "2027-09-01",
            "destino_centro_custo": "Talhão 02 - Milho Safrinha (120ha)", "responsavel": "João Tratorista",
            "devolucao_embalagem": "Não Aplicável"
        },
        {
            "id_movimento": "MOV-0007", "data_movimento": "2026-10-18", "tipo_movimento": "Saída",
            "produto": "Óleo Diesel S10", "categoria": "Combustíveis e Lubrificantes", "lote": "DSL-2610B",
            "quantidade": 520, "unidade": "L", "custo_unitario": 6.35, "data_validade": "2027-10-05",
            "destino_centro_custo": "Semiconfinamento (200 Bovinos)", "responsavel": "Pedro Operador",
            "devolucao_embalagem": "Não Aplicável"
        },
        {
            "id_movimento": "MOV-0008", "data_movimento": "2026-10-25", "tipo_movimento": "Saída",
            "produto": "Óleo Diesel S10", "categoria": "Combustíveis e Lubrificantes", "lote": "DSL-2610B",
            "quantidade": 540, "unidade": "L", "custo_unitario": 6.35, "data_validade": "2027-10-05",
            "destino_centro_custo": "Talhão 01 - Soja (150ha)", "responsavel": "João Tratorista",
            "devolucao_embalagem": "Não Aplicável"
        },

        # =========================================================================
        # 2. GLIFOSATO 480 SL -> Anomalia de Retirada (Z-score > 2), embalagens pendentes/vencidas, galao vs L
        # =========================================================================
        {
            "id_movimento": "MOV-0009", "data_movimento": "2026-08-28", "tipo_movimento": "Entrada",
            "produto": "Glifosato 480 SL", "categoria": "Defensivos Químicos", "lote": "GLI-4401",
            "quantidade": 35, "unidade": "galao", "custo_unitario": 480.00, "data_validade": "2027-08-28",
            "destino_centro_custo": "Almoxarifado Central (Entrada)", "responsavel": "Marcos Souza",
            "devolucao_embalagem": "Não Aplicável"
        },
        {
            "id_movimento": "MOV-0010", "data_movimento": "2026-09-03", "tipo_movimento": "Saída",
            "produto": "glifosato 480", "categoria": "Defensivos Químicos", "lote": "GLI-4401",
            "quantidade": 2, "unidade": "galao", "custo_unitario": 480.00, "data_validade": "2027-08-28",
            "destino_centro_custo": "Talhão 01 - Soja (150ha)", "responsavel": "Carlos Agrônomo",
            "devolucao_embalagem": "Devolvida"
        },
        {
            "id_movimento": "MOV-0011", "data_movimento": "2026-09-09", "tipo_movimento": "Saída",
            "produto": "roundup glifosato", "categoria": "Defensivos Químicos", "lote": "GLI-4401",
            "quantidade": 45, "unidade": "L", "custo_unitario": 24.00, "data_validade": "2027-08-28",
            "destino_centro_custo": "Talhão 01 - Soja (150ha)", "responsavel": "Carlos Agrônomo",
            "devolucao_embalagem": "Devolvida"
        },
        {
            "id_movimento": "MOV-0012", "data_movimento": "2026-09-15", "tipo_movimento": "Saída",
            "produto": "Glifosato 480 SL", "categoria": "Defensivos Químicos", "lote": "GLI-4401",
            "quantidade": 40, "unidade": "L", "custo_unitario": 24.00, "data_validade": "2027-08-28",
            "destino_centro_custo": "Talhão 02 - Milho Safrinha (120ha)", "responsavel": "Carlos Agrônomo",
            "devolucao_embalagem": "Prazo Vencido"
        },
        {
            "id_movimento": "MOV-0013", "data_movimento": "2026-09-22", "tipo_movimento": "Saída",
            "produto": "glifozato 480", "categoria": "Defensivos Químicos", "lote": "GLI-4401",
            "quantidade": 50, "unidade": "L", "custo_unitario": 24.00, "data_validade": "2027-08-28",
            "destino_centro_custo": "Talhão 02 - Milho Safrinha (120ha)", "responsavel": "Pedro Operador",
            "devolucao_embalagem": "Pendente"
        },
        {
            "id_movimento": "MOV-0014", "data_movimento": "2026-09-30", "tipo_movimento": "Saída",
            "produto": "Glifosato 480 SL", "categoria": "Defensivos Químicos", "lote": "GLI-4401",
            "quantidade": 2, "unidade": "galão", "custo_unitario": 480.00, "data_validade": "2027-08-28",
            "destino_centro_custo": "Pastos Rotacionados (30 Piquetes - 140ha)", "responsavel": "Carlos Agrônomo",
            "devolucao_embalagem": "Devolvida"
        },
        {
            "id_movimento": "MOV-0015", "data_movimento": "2026-10-07", "tipo_movimento": "Saída",
            "produto": "Glifosato 480 SL", "categoria": "Defensivos Químicos", "lote": "GLI-4401",
            "quantidade": 42, "unidade": "L", "custo_unitario": 24.00, "data_validade": "2027-08-28",
            "destino_centro_custo": "Talhão 01 - Soja (150ha)", "responsavel": "Carlos Agrônomo",
            "devolucao_embalagem": "Pendente"
        },
        {
            "id_movimento": "MOV-0016", "data_movimento": "2026-10-14", "tipo_movimento": "Saída",
            "produto": "Glifosato 480 SL", "categoria": "Defensivos Químicos", "lote": "GLI-4401",
            "quantidade": 48, "unidade": "L", "custo_unitario": 24.00, "data_validade": "2027-08-28",
            "destino_centro_custo": "Talhão 01 - Soja (150ha)", "responsavel": "Carlos Agrônomo",
            "devolucao_embalagem": "Pendente"
        },
        {
            "id_movimento": "MOV-0017", "data_movimento": "2026-10-19", "tipo_movimento": "Saída",
            "produto": "Glifosato 480 SL", "categoria": "Defensivos Químicos", "lote": "GLI-4401",
            "quantidade": 44, "unidade": "L", "custo_unitario": 24.00, "data_validade": "2027-08-28",
            "destino_centro_custo": "Talhão 02 - Milho Safrinha (120ha)", "responsavel": "Carlos Agrônomo",
            "devolucao_embalagem": "Devolvida"
        },
        {
            "id_movimento": "MOV-0018", "data_movimento": "2026-10-24", "tipo_movimento": "Saída",
            "produto": "Glifosato 480 SL", "categoria": "Defensivos Químicos", "lote": "GLI-4401",
            "quantidade": 260, "unidade": "L", "custo_unitario": 24.00, "data_validade": "2027-08-28",
            "destino_centro_custo": "Manutenção de Cercas e Infraestrutura", "responsavel": "Pedro Operador",
            "devolucao_embalagem": "Pendente"
        },

        # =========================================================================
        # 3. INOCULANTE BRADYRHIZOBIUM LÍQUIDO -> Risco de Vencimento vs Giro (FEFO Crítico!)
        # =========================================================================
        {
            "id_movimento": "MOV-0019", "data_movimento": "2026-09-02", "tipo_movimento": "Entrada",
            "produto": "Inoculante Bradyrhizobium Líquido", "categoria": "Defensivos Biológicos", "lote": "BIO-2026A",
            "quantidade": 120, "unidade": "L", "custo_unitario": 85.00, "data_validade": "2026-11-12",
            "destino_centro_custo": "Almoxarifado Central (Entrada)", "responsavel": "Marcos Souza",
            "devolucao_embalagem": "Não Aplicável"
        },
        {
            "id_movimento": "MOV-0020", "data_movimento": "2026-09-12", "tipo_movimento": "Saída",
            "produto": "inoculante soja", "categoria": "Defensivos Biológicos", "lote": "BIO-2026A",
            "quantidade": 12, "unidade": "L", "custo_unitario": 85.00, "data_validade": "2026-11-12",
            "destino_centro_custo": "Talhão 01 - Soja (150ha)", "responsavel": "Carlos Agrônomo",
            "devolucao_embalagem": "Devolvida"
        },
        {
            "id_movimento": "MOV-0021", "data_movimento": "2026-09-25", "tipo_movimento": "Saída",
            "produto": "bradyrhizobium liquido", "categoria": "Defensivos Biológicos", "lote": "BIO-2026A",
            "quantidade": 14, "unidade": "L", "custo_unitario": 85.00, "data_validade": "2026-11-12",
            "destino_centro_custo": "Talhão 01 - Soja (150ha)", "responsavel": "Carlos Agrônomo",
            "devolucao_embalagem": "Devolvida"
        },
        {
            "id_movimento": "MOV-0022", "data_movimento": "2026-10-08", "tipo_movimento": "Saída",
            "produto": "Inoculante Bradyrhizobium Líquido", "categoria": "Defensivos Biológicos", "lote": "BIO-2026A",
            "quantidade": 10, "unidade": "L", "custo_unitario": 85.00, "data_validade": "2026-11-12",
            "destino_centro_custo": "Talhão 01 - Soja (150ha)", "responsavel": "Carlos Agrônomo",
            "devolucao_embalagem": "Devolvida"
        },
        {
            "id_movimento": "MOV-0023", "data_movimento": "2026-10-19", "tipo_movimento": "Saída",
            "produto": "Inoculante Bradyrhizobium Líquido", "categoria": "Defensivos Biológicos", "lote": "BIO-2026A",
            "quantidade": 12, "unidade": "L", "custo_unitario": 85.00, "data_validade": "2026-11-12",
            "destino_centro_custo": "Talhão 01 - Soja (150ha)", "responsavel": "Carlos Agrônomo",
            "devolucao_embalagem": "Pendente"
        },
        {
            "id_movimento": "MOV-0024", "data_movimento": "2026-10-20", "tipo_movimento": "Entrada",
            "produto": "Inoculante Bradyrhizobium Líquido", "categoria": "Defensivos Biológicos", "lote": "BIO-2026B",
            "quantidade": 40, "unidade": "L", "custo_unitario": 88.00, "data_validade": "2027-04-30",
            "destino_centro_custo": "Almoxarifado Central (Entrada)", "responsavel": "Marcos Souza",
            "devolucao_embalagem": "Não Aplicável"
        },

        # =========================================================================
        # 4. TRICHODERMA HARZIANUM BIOFUNGICIDA -> Validade curta vs giro lento + unidade mL e L
        # =========================================================================
        {
            "id_movimento": "MOV-0025", "data_movimento": "2026-09-05", "tipo_movimento": "Entrada",
            "produto": "Trichoderma harzianum Biofungicida", "categoria": "Defensivos Biológicos", "lote": "TRI-88",
            "quantidade": 60, "unidade": "L", "custo_unitario": 135.00, "data_validade": "2026-11-28",
            "destino_centro_custo": "Almoxarifado Central (Entrada)", "responsavel": "Marcos Souza",
            "devolucao_embalagem": "Não Aplicável"
        },
        {
            "id_movimento": "MOV-0026", "data_movimento": "2026-09-16", "tipo_movimento": "Saída",
            "produto": "tricoderma", "categoria": "Defensivos Biológicos", "lote": "TRI-88",
            "quantidade": 5000, "unidade": "ml", "custo_unitario": 0.135, "data_validade": "2026-11-28",
            "destino_centro_custo": "Talhão 01 - Soja (150ha)", "responsavel": "Carlos Agrônomo",
            "devolucao_embalagem": "Devolvida"
        },
        {
            "id_movimento": "MOV-0027", "data_movimento": "2026-10-01", "tipo_movimento": "Saída",
            "produto": "Trichoderma harzianum Biofungicida", "categoria": "Defensivos Biológicos", "lote": "TRI-88",
            "quantidade": 6, "unidade": "L", "custo_unitario": 135.00, "data_validade": "2026-11-28",
            "destino_centro_custo": "Talhão 01 - Soja (150ha)", "responsavel": "Carlos Agrônomo",
            "devolucao_embalagem": "Devolvida"
        },
        {
            "id_movimento": "MOV-0028", "data_movimento": "2026-10-17", "tipo_movimento": "Saída",
            "produto": "biofungicida trichoderma", "categoria": "Defensivos Biológicos", "lote": "TRI-88",
            "quantidade": 5, "unidade": "L", "custo_unitario": 135.00, "data_validade": "2026-11-28",
            "destino_centro_custo": "Talhão 02 - Milho Safrinha (120ha)", "responsavel": "Carlos Agrônomo",
            "devolucao_embalagem": "Pendente"
        },

        # =========================================================================
        # 5. UREIA AGRÍCOLA 45% N -> Estoque em Atenção (<= 20 dias), mistura ton/saco/kg e grafia 'Uréia'
        # =========================================================================
        {
            "id_movimento": "MOV-0029", "data_movimento": "2026-09-01", "tipo_movimento": "Entrada",
            "produto": "Ureia Agrícola 45% N", "categoria": "Fertilizantes", "lote": "URE-101",
            "quantidade": 6, "unidade": "ton", "custo_unitario": 3400.00, "data_validade": "2028-03-01",
            "destino_centro_custo": "Almoxarifado Central (Entrada)", "responsavel": "Marcos Souza",
            "devolucao_embalagem": "Não Aplicável"
        },
        {
            "id_movimento": "MOV-0030", "data_movimento": "2026-09-10", "tipo_movimento": "Saída",
            "produto": "uréia", "categoria": "Fertilizantes", "lote": "URE-101",
            "quantidade": 25, "unidade": "saco", "custo_unitario": 170.00, "data_validade": "2028-03-01",
            "destino_centro_custo": "Pastos Rotacionados (30 Piquetes - 140ha)", "responsavel": "Antônio Campeiro",
            "devolucao_embalagem": "Não Aplicável"
        },
        {
            "id_movimento": "MOV-0031", "data_movimento": "2026-09-21", "tipo_movimento": "Saída",
            "produto": "ureia agricola", "categoria": "Fertilizantes", "lote": "URE-101",
            "quantidade": 1300, "unidade": "kg", "custo_unitario": 3.40, "data_validade": "2028-03-01",
            "destino_centro_custo": "Talhão 02 - Milho Safrinha (120ha)", "responsavel": "João Tratorista",
            "devolucao_embalagem": "Não Aplicável"
        },
        {
            "id_movimento": "MOV-0032", "data_movimento": "2026-10-04", "tipo_movimento": "Saída",
            "produto": "Ureia Agrícola 45% N", "categoria": "Fertilizantes", "lote": "URE-101",
            "quantidade": 28, "unidade": "saco", "custo_unitario": 170.00, "data_validade": "2028-03-01",
            "destino_centro_custo": "Pastos Rotacionados (30 Piquetes - 140ha)", "responsavel": "Antônio Campeiro",
            "devolucao_embalagem": "Não Aplicável"
        },
        {
            "id_movimento": "MOV-0033", "data_movimento": "2026-10-16", "tipo_movimento": "Saída",
            "produto": "Uréia Agrícola", "categoria": "Fertilizantes", "lote": "URE-101",
            "quantidade": 1000, "unidade": "kg", "custo_unitario": 3.40, "data_validade": "2028-03-01",
            "destino_centro_custo": "Talhão 02 - Milho Safrinha (120ha)", "responsavel": "João Tratorista",
            "devolucao_embalagem": "Não Aplicável"
        },

        # =========================================================================
        # 6. SAL MINERAL BOVINOS 80G FÓSFORO -> Crescimento Progressivo de Demanda (> 30%)
        # =========================================================================
        {
            "id_movimento": "MOV-0034", "data_movimento": "2026-08-30", "tipo_movimento": "Entrada",
            "produto": "Sal Mineral Bovinos 80g Fósforo", "categoria": "Fertilizantes", "lote": "SAL-200",
            "quantidade": 120, "unidade": "saco", "custo_unitario": 145.00, "data_validade": "2027-12-30",
            "destino_centro_custo": "Almoxarifado Central (Entrada)", "responsavel": "Marcos Souza",
            "devolucao_embalagem": "Não Aplicável"
        },
        {
            "id_movimento": "MOV-0035", "data_movimento": "2026-09-04", "tipo_movimento": "Saída",
            "produto": "sal mineral 80", "categoria": "Fertilizantes", "lote": "SAL-200",
            "quantidade": 6, "unidade": "saco", "custo_unitario": 145.00, "data_validade": "2027-12-30",
            "destino_centro_custo": "Pastos Rotacionados (30 Piquetes - 140ha)", "responsavel": "Antônio Campeiro",
            "devolucao_embalagem": "Não Aplicável"
        },
        {
            "id_movimento": "MOV-0036", "data_movimento": "2026-09-14", "tipo_movimento": "Saída",
            "produto": "Sal Mineral Bovinos 80g Fósforo", "categoria": "Fertilizantes", "lote": "SAL-200",
            "quantidade": 7, "unidade": "saco", "custo_unitario": 145.00, "data_validade": "2027-12-30",
            "destino_centro_custo": "Semiconfinamento (200 Bovinos)", "responsavel": "Antônio Campeiro",
            "devolucao_embalagem": "Não Aplicável"
        },
        {
            "id_movimento": "MOV-0037", "data_movimento": "2026-09-24", "tipo_movimento": "Saída",
            "produto": "sal mineral bovinos", "categoria": "Fertilizantes", "lote": "SAL-200",
            "quantidade": 8, "unidade": "saco", "custo_unitario": 145.00, "data_validade": "2027-12-30",
            "destino_centro_custo": "Semiconfinamento (200 Bovinos)", "responsavel": "Antônio Campeiro",
            "devolucao_embalagem": "Não Aplicável"
        },
        {
            "id_movimento": "MOV-0038", "data_movimento": "2026-10-03", "tipo_movimento": "Saída",
            "produto": "Sal Mineral Bovinos 80g Fósforo", "categoria": "Fertilizantes", "lote": "SAL-200",
            "quantidade": 11, "unidade": "saco", "custo_unitario": 145.00, "data_validade": "2027-12-30",
            "destino_centro_custo": "Semiconfinamento (200 Bovinos)", "responsavel": "Antônio Campeiro",
            "devolucao_embalagem": "Não Aplicável"
        },
        {
            "id_movimento": "MOV-0039", "data_movimento": "2026-10-13", "tipo_movimento": "Saída",
            "produto": "Sal Mineral Bovinos 80g Fósforo", "categoria": "Fertilizantes", "lote": "SAL-200",
            "quantidade": 13, "unidade": "saco", "custo_unitario": 145.00, "data_validade": "2027-12-30",
            "destino_centro_custo": "Pastos Rotacionados (30 Piquetes - 140ha)", "responsavel": "Antônio Campeiro",
            "devolucao_embalagem": "Não Aplicável"
        },
        {
            "id_movimento": "MOV-0040", "data_movimento": "2026-10-23", "tipo_movimento": "Saída",
            "produto": "Sal Mineral Bovinos 80g Fósforo", "categoria": "Fertilizantes", "lote": "SAL-200",
            "quantidade": 16, "unidade": "saco", "custo_unitario": 145.00, "data_validade": "2027-12-30",
            "destino_centro_custo": "Semiconfinamento (200 Bovinos)", "responsavel": "Antônio Campeiro",
            "devolucao_embalagem": "Não Aplicável"
        },

        # =========================================================================
        # 7. CLORETO DE POTÁSSIO (KCl) -> Inflação de Preço (> 20%) e falta de custo em uma saída
        # =========================================================================
        {
            "id_movimento": "MOV-0041", "data_movimento": "2026-08-15", "tipo_movimento": "Entrada",
            "produto": "Cloreto de Potássio (KCl)", "categoria": "Fertilizantes", "lote": "KCL-01",
            "quantidade": 4000, "unidade": "kg", "custo_unitario": 2.80, "data_validade": "2028-08-15",
            "destino_centro_custo": "Almoxarifado Central (Entrada)", "responsavel": "Marcos Souza",
            "devolucao_embalagem": "Não Aplicável"
        },
        {
            "id_movimento": "MOV-0042", "data_movimento": "2026-09-10", "tipo_movimento": "Entrada",
            "produto": "kcl", "categoria": "Fertilizantes", "lote": "KCL-02",
            "quantidade": 3000, "unidade": "kg", "custo_unitario": 2.90, "data_validade": "2028-09-10",
            "destino_centro_custo": "Almoxarifado Central (Entrada)", "responsavel": "Marcos Souza",
            "devolucao_embalagem": "Não Aplicável"
        },
        {
            "id_movimento": "MOV-0043", "data_movimento": "2026-09-18", "tipo_movimento": "Saída",
            "produto": "cloreto de potassio", "categoria": "Fertilizantes", "lote": "KCL-01",
            "quantidade": 1500, "unidade": "kg", "custo_unitario": 2.80, "data_validade": "2028-08-15",
            "destino_centro_custo": "Talhão 01 - Soja (150ha)", "responsavel": "João Tratorista",
            "devolucao_embalagem": "Não Aplicável"
        },
        {
            "id_movimento": "MOV-0044", "data_movimento": "2026-10-02", "tipo_movimento": "Saída",
            "produto": "Cloreto de Potássio (KCl)", "categoria": "Fertilizantes", "lote": "KCL-01",
            "quantidade": 1200, "unidade": "kg", "custo_unitario": "", "data_validade": "2028-08-15",
            "destino_centro_custo": "Talhão 01 - Soja (150ha)", "responsavel": "João Tratorista",
            "devolucao_embalagem": "Não Aplicável"
        },
        {
            "id_movimento": "MOV-0045", "data_movimento": "2026-10-15", "tipo_movimento": "Entrada",
            "produto": "Cloreto de Potássio (KCl)", "categoria": "Fertilizantes", "lote": "KCL-03",
            "quantidade": 4000, "unidade": "kg", "custo_unitario": 3.85, "data_validade": "2028-10-15",
            "destino_centro_custo": "Almoxarifado Central (Entrada)", "responsavel": "Marcos Souza",
            "devolucao_embalagem": "Não Aplicável"
        },
        {
            "id_movimento": "MOV-0046", "data_movimento": "2026-10-21", "tipo_movimento": "Saída",
            "produto": "Cloreto de Potássio (KCl)", "categoria": "Fertilizantes", "lote": "KCL-02",
            "quantidade": 1400, "unidade": "kg", "custo_unitario": 2.90, "data_validade": "2028-09-10",
            "destino_centro_custo": "Talhão 02 - Milho Safrinha (120ha)", "responsavel": "João Tratorista",
            "devolucao_embalagem": "Não Aplicável"
        },

        # =========================================================================
        # 8. TUBO GOTEJADOR 16MM -> Capital Parado (> 45 dias sem saída) e Excesso de Estoque
        # =========================================================================
        {
            "id_movimento": "MOV-0047", "data_movimento": "2026-07-10", "tipo_movimento": "Entrada",
            "produto": "Tubo Gotejador 16mm", "categoria": "Irrigação", "lote": "IRR-701",
            "quantidade": 30, "unidade": "rolo_100m", "custo_unitario": 420.00, "data_validade": "",
            "destino_centro_custo": "Almoxarifado Central (Entrada)", "responsavel": "Marcos Souza",
            "devolucao_embalagem": "Não Aplicável"
        },
        {
            "id_movimento": "MOV-0048", "data_movimento": "2026-08-05", "tipo_movimento": "Saída",
            "produto": "mangueira gotejamento 16mm", "categoria": "Irrigação", "lote": "IRR-701",
            "quantidade": 200, "unidade": "m", "custo_unitario": 4.20, "data_validade": "",
            "destino_centro_custo": "Manutenção de Cercas e Infraestrutura", "responsavel": "Pedro Operador",
            "devolucao_embalagem": "Não Aplicável"
        },

        # =========================================================================
        # 9. CALCÁRIO DOLOMÍTICO PRNT 85% -> Capital Parado (> 45 dias sem movimentação recente)
        # =========================================================================
        {
            "id_movimento": "MOV-0049", "data_movimento": "2026-07-20", "tipo_movimento": "Entrada",
            "produto": "Calcário Dolomítico PRNT 85%", "categoria": "Corretivos", "lote": "CAL-500",
            "quantidade": 80, "unidade": "ton", "custo_unitario": 260.00, "data_validade": "",
            "destino_centro_custo": "Almoxarifado Central (Entrada)", "responsavel": "Marcos Souza",
            "devolucao_embalagem": "Não Aplicável"
        },
        {
            "id_movimento": "MOV-0050", "data_movimento": "2026-08-12", "tipo_movimento": "Saída",
            "produto": "calcario dolomitico", "categoria": "Corretivos", "lote": "CAL-500",
            "quantidade": 25, "unidade": "ton", "custo_unitario": 260.00, "data_validade": "",
            "destino_centro_custo": "Talhão 01 - Soja (150ha)", "responsavel": "João Tratorista",
            "devolucao_embalagem": "Não Aplicável"
        },
        {
            "id_movimento": "MOV-0051", "data_movimento": "2026-08-25", "tipo_movimento": "Saída",
            "produto": "calcário", "categoria": "Corretivos", "lote": "CAL-500",
            "quantidade": 15000, "unidade": "kg", "custo_unitario": 0.26, "data_validade": "",
            "destino_centro_custo": "Pastos Rotacionados (30 Piquetes - 140ha)", "responsavel": "João Tratorista",
            "devolucao_embalagem": "Não Aplicável"
        },

        # =========================================================================
        # 10. FUNGICIDA FOX XPRO -> Variação de Preço (> 20%) + Embalagens Pendentes/Vencidas
        # =========================================================================
        {
            "id_movimento": "MOV-0052", "data_movimento": "2026-08-20", "tipo_movimento": "Entrada",
            "produto": "Fungicida Fox Xpro", "categoria": "Defensivos Químicos", "lote": "FOX-11",
            "quantidade": 60, "unidade": "L", "custo_unitario": 240.00, "data_validade": "2027-06-30",
            "destino_centro_custo": "Almoxarifado Central (Entrada)", "responsavel": "Marcos Souza",
            "devolucao_embalagem": "Não Aplicável"
        },
        {
            "id_movimento": "MOV-0053", "data_movimento": "2026-09-07", "tipo_movimento": "Saída",
            "produto": "fox xpro", "categoria": "Defensivos Químicos", "lote": "FOX-11",
            "quantidade": 15, "unidade": "L", "custo_unitario": 240.00, "data_validade": "2027-06-30",
            "destino_centro_custo": "Talhão 01 - Soja (150ha)", "responsavel": "Carlos Agrônomo",
            "devolucao_embalagem": "Prazo Vencido"
        },
        {
            "id_movimento": "MOV-0054", "data_movimento": "2026-09-23", "tipo_movimento": "Saída",
            "produto": "Fungicida Fox Xpro", "categoria": "Defensivos Químicos", "lote": "FOX-11",
            "quantidade": 15, "unidade": "L", "custo_unitario": 240.00, "data_validade": "2027-06-30",
            "destino_centro_custo": "Talhão 01 - Soja (150ha)", "responsavel": "Carlos Agrônomo",
            "devolucao_embalagem": "Devolvida"
        },
        {
            "id_movimento": "MOV-0055", "data_movimento": "2026-10-11", "tipo_movimento": "Entrada",
            "produto": "Fungicida Fox Xpro", "categoria": "Defensivos Químicos", "lote": "FOX-12",
            "quantidade": 40, "unidade": "L", "custo_unitario": 310.00, "data_validade": "2027-11-30",
            "destino_centro_custo": "Almoxarifado Central (Entrada)", "responsavel": "Marcos Souza",
            "devolucao_embalagem": "Não Aplicável"
        },
        {
            "id_movimento": "MOV-0056", "data_movimento": "2026-10-20", "tipo_movimento": "Saída",
            "produto": "fungicida fox", "categoria": "Defensivos Químicos", "lote": "FOX-11",
            "quantidade": 12, "unidade": "L", "custo_unitario": 240.00, "data_validade": "2027-06-30",
            "destino_centro_custo": "Talhão 01 - Soja (150ha)", "responsavel": "Carlos Agrônomo",
            "devolucao_embalagem": "Pendente"
        },

        # =========================================================================
        # 11. INSETICIDA ENGEO PLENO S -> Embalagens Pendentes e Validade Ausente num lote
        # =========================================================================
        {
            "id_movimento": "MOV-0057", "data_movimento": "2026-09-03", "tipo_movimento": "Entrada",
            "produto": "Inseticida Engeo Pleno S", "categoria": "Defensivos Químicos", "lote": "ENG-301",
            "quantidade": 50, "unidade": "L", "custo_unitario": 175.00, "data_validade": "2027-05-15",
            "destino_centro_custo": "Almoxarifado Central (Entrada)", "responsavel": "Marcos Souza",
            "devolucao_embalagem": "Não Aplicável"
        },
        {
            "id_movimento": "MOV-0058", "data_movimento": "2026-09-14", "tipo_movimento": "Saída",
            "produto": "engeo pleno", "categoria": "Defensivos Químicos", "lote": "ENG-301",
            "quantidade": 10, "unidade": "L", "custo_unitario": 175.00, "data_validade": "2027-05-15",
            "destino_centro_custo": "Talhão 02 - Milho Safrinha (120ha)", "responsavel": "Carlos Agrônomo",
            "devolucao_embalagem": "Devolvida"
        },
        {
            "id_movimento": "MOV-0059", "data_movimento": "2026-10-01", "tipo_movimento": "Saída",
            "produto": "Inseticida Engeo Pleno S", "categoria": "Defensivos Químicos", "lote": "ENG-301",
            "quantidade": 12, "unidade": "L", "custo_unitario": 175.00, "data_validade": "",
            "destino_centro_custo": "Talhão 02 - Milho Safrinha (120ha)", "responsavel": "Carlos Agrônomo",
            "devolucao_embalagem": "Pendente"
        },
        {
            "id_movimento": "MOV-0060", "data_movimento": "2026-10-18", "tipo_movimento": "Saída",
            "produto": "inseticida engeo", "categoria": "Defensivos Químicos", "lote": "ENG-301",
            "quantidade": 11, "unidade": "L", "custo_unitario": 175.00, "data_validade": "2027-05-15",
            "destino_centro_custo": "Silos e Armazenagem", "responsavel": "Carlos Agrônomo",
            "devolucao_embalagem": "Pendente"
        },

        # =========================================================================
        # 12. SEMENTE SOJA INTACTA RR2 -> Conversão específica (saco 40kg vs kg) e Alto Valor ABC
        # =========================================================================
        {
            "id_movimento": "MOV-0061", "data_movimento": "2026-09-05", "tipo_movimento": "Entrada",
            "produto": "Semente Soja Intacta RR2", "categoria": "Sementes", "lote": "SOJ-2026",
            "quantidade": 220, "unidade": "saco_40kg", "custo_unitario": 460.00, "data_validade": "2027-03-30",
            "destino_centro_custo": "Almoxarifado Central (Entrada)", "responsavel": "Marcos Souza",
            "devolucao_embalagem": "Não Aplicável"
        },
        {
            "id_movimento": "MOV-0062", "data_movimento": "2026-09-20", "tipo_movimento": "Saída",
            "produto": "semente soja", "categoria": "Sementes", "lote": "SOJ-2026",
            "quantidade": 60, "unidade": "saco_40kg", "custo_unitario": 460.00, "data_validade": "2027-03-30",
            "destino_centro_custo": "Talhão 01 - Soja (150ha)", "responsavel": "Carlos Agrônomo",
            "devolucao_embalagem": "Não Aplicável"
        },
        {
            "id_movimento": "MOV-0063", "data_movimento": "2026-10-05", "tipo_movimento": "Saída",
            "produto": "soja intacta", "categoria": "Sementes", "lote": "SOJ-2026",
            "quantidade": 2400, "unidade": "kg", "custo_unitario": 11.50, "data_validade": "2027-03-30",
            "destino_centro_custo": "Talhão 01 - Soja (150ha)", "responsavel": "Carlos Agrônomo",
            "devolucao_embalagem": "Não Aplicável"
        },
        {
            "id_movimento": "MOV-0064", "data_movimento": "2026-10-19", "tipo_movimento": "Saída",
            "produto": "Semente Soja Intacta RR2", "categoria": "Sementes", "lote": "SOJ-2026",
            "quantidade": 55, "unidade": "saco_40kg", "custo_unitario": 460.00, "data_validade": "2027-03-30",
            "destino_centro_custo": "Talhão 01 - Soja (150ha)", "responsavel": "Carlos Agrônomo",
            "devolucao_embalagem": "Não Aplicável"
        },

        # =========================================================================
        # 13. SEMENTE MILHO HÍBRIDO VT PRO3 -> Plantio Talhão 02
        # =========================================================================
        {
            "id_movimento": "MOV-0065", "data_movimento": "2026-09-08", "tipo_movimento": "Entrada",
            "produto": "Semente Milho Híbrido VT PRO3", "categoria": "Sementes", "lote": "MIL-880",
            "quantidade": 150, "unidade": "saco", "custo_unitario": 780.00, "data_validade": "2027-05-01",
            "destino_centro_custo": "Almoxarifado Central (Entrada)", "responsavel": "Marcos Souza",
            "devolucao_embalagem": "Não Aplicável"
        },
        {
            "id_movimento": "MOV-0066", "data_movimento": "2026-09-25", "tipo_movimento": "Saída",
            "produto": "semente milho", "categoria": "Sementes", "lote": "MIL-880",
            "quantidade": 40, "unidade": "saco", "custo_unitario": 780.00, "data_validade": "2027-05-01",
            "destino_centro_custo": "Talhão 02 - Milho Safrinha (120ha)", "responsavel": "Carlos Agrônomo",
            "devolucao_embalagem": "Não Aplicável"
        },
        {
            "id_movimento": "MOV-0067", "data_movimento": "2026-10-09", "tipo_movimento": "Saída",
            "produto": "milho vt pro3", "categoria": "Sementes", "lote": "MIL-880",
            "quantidade": 35, "unidade": "saco", "custo_unitario": 780.00, "data_validade": "2027-05-01",
            "destino_centro_custo": "Talhão 02 - Milho Safrinha (120ha)", "responsavel": "Carlos Agrônomo",
            "devolucao_embalagem": "Não Aplicável"
        },
        {
            "id_movimento": "MOV-0068", "data_movimento": "2026-10-22", "tipo_movimento": "Saída",
            "produto": "Semente Milho Híbrido VT PRO3", "categoria": "Sementes", "lote": "MIL-880",
            "quantidade": 38, "unidade": "saco", "custo_unitario": 780.00, "data_validade": "2027-05-01",
            "destino_centro_custo": "Talhão 02 - Milho Safrinha (120ha)", "responsavel": "Carlos Agrônomo",
            "devolucao_embalagem": "Não Aplicável"
        },

        # =========================================================================
        # 14. NPK 04-14-08 -> Inclui Divergência de Conciliação por Lote (Auditoria Rastreável!)
        # Lote NPK-99-ERR tem entrada de 500 kg e saída lançada de 650 kg (saldo negativo no lote!)
        # =========================================================================
        {
            "id_movimento": "MOV-0069", "data_movimento": "2026-09-01", "tipo_movimento": "Entrada",
            "produto": "NPK 04-14-08", "categoria": "Fertilizantes", "lote": "NPK-98-OK",
            "quantidade": 5000, "unidade": "kg", "custo_unitario": 3.10, "data_validade": "2028-09-01",
            "destino_centro_custo": "Almoxarifado Central (Entrada)", "responsavel": "Marcos Souza",
            "devolucao_embalagem": "Não Aplicável"
        },
        {
            "id_movimento": "MOV-0070", "data_movimento": "2026-09-12", "tipo_movimento": "Entrada",
            "produto": "npk 4-14-8", "categoria": "Fertilizantes", "lote": "NPK-99-ERR",
            "quantidade": 10, "unidade": "saco", "custo_unitario": 155.00, "data_validade": "2028-09-12",
            "destino_centro_custo": "Almoxarifado Central (Entrada)", "responsavel": "Marcos Souza",
            "devolucao_embalagem": "Não Aplicável"
        },
        {
            "id_movimento": "MOV-0071", "data_movimento": "2026-09-19", "tipo_movimento": "Saída",
            "produto": "NPK 04-14-08", "categoria": "Fertilizantes", "lote": "NPK-98-OK",
            "quantidade": 1500, "unidade": "kg", "custo_unitario": 3.10, "data_validade": "2028-09-01",
            "destino_centro_custo": "Talhão 02 - Milho Safrinha (120ha)", "responsavel": "João Tratorista",
            "devolucao_embalagem": "Não Aplicável"
        },
        {
            "id_movimento": "MOV-0072", "data_movimento": "2026-10-06", "tipo_movimento": "Saída",
            "produto": "adubo npk 04 14 08", "categoria": "Fertilizantes", "lote": "NPK-99-ERR",
            "quantidade": 650, "unidade": "kg", "custo_unitario": 3.10, "data_validade": "2028-09-12",
            "destino_centro_custo": "Pastos Rotacionados (30 Piquetes - 140ha)", "responsavel": "João Tratorista",
            "devolucao_embalagem": "Não Aplicável"
        },
        {
            "id_movimento": "MOV-0073", "data_movimento": "2026-10-18", "tipo_movimento": "Saída",
            "produto": "NPK 04-14-08", "categoria": "Fertilizantes", "lote": "NPK-98-OK",
            "quantidade": 1200, "unidade": "kg", "custo_unitario": 3.10, "data_validade": "2028-09-01",
            "destino_centro_custo": "Talhão 02 - Milho Safrinha (120ha)", "responsavel": "João Tratorista",
            "devolucao_embalagem": "Não Aplicável"
        },

        # =========================================================================
        # 15. ÓLEO LUBRIFICANTE 15W40 -> Manutenção de Máquinas + Custo Ausente em 1 entrada
        # =========================================================================
        {
            "id_movimento": "MOV-0074", "data_movimento": "2026-09-02", "tipo_movimento": "Entrada",
            "produto": "Óleo Lubrificante 15W40", "categoria": "Combustíveis e Lubrificantes", "lote": "LUB-401",
            "quantidade": 5, "unidade": "bombona", "custo_unitario": 520.00, "data_validade": "2029-09-02",
            "destino_centro_custo": "Almoxarifado Central (Entrada)", "responsavel": "Marcos Souza",
            "devolucao_embalagem": "Não Aplicável"
        },
        {
            "id_movimento": "MOV-0075", "data_movimento": "2026-09-15", "tipo_movimento": "Saída",
            "produto": "lubrificante 15w40", "categoria": "Combustíveis e Lubrificantes", "lote": "LUB-401",
            "quantidade": 20, "unidade": "L", "custo_unitario": 26.00, "data_validade": "2029-09-02",
            "destino_centro_custo": "Manutenção de Máquinas e Frota", "responsavel": "Pedro Operador",
            "devolucao_embalagem": "Não Aplicável"
        },
        {
            "id_movimento": "MOV-0076", "data_movimento": "2026-09-28", "tipo_movimento": "Saída",
            "produto": "oleo 15w40", "categoria": "Combustíveis e Lubrificantes", "lote": "LUB-401",
            "quantidade": 18, "unidade": "L", "custo_unitario": 26.00, "data_validade": "2029-09-02",
            "destino_centro_custo": "Manutenção de Máquinas e Frota", "responsavel": "Pedro Operador",
            "devolucao_embalagem": "Não Aplicável"
        },
        {
            "id_movimento": "MOV-0077", "data_movimento": "2026-10-12", "tipo_movimento": "Entrada",
            "produto": "Óleo Lubrificante 15W40", "categoria": "Combustíveis e Lubrificantes", "lote": "LUB-402",
            "quantidade": 40, "unidade": "L", "custo_unitario": "", "data_validade": "2029-10-12",
            "destino_centro_custo": "Almoxarifado Central (Entrada)", "responsavel": "Marcos Souza",
            "devolucao_embalagem": "Não Aplicável"
        },
        {
            "id_movimento": "MOV-0078", "data_movimento": "2026-10-21", "tipo_movimento": "Saída",
            "produto": "Óleo Lubrificante 15W40", "categoria": "Combustíveis e Lubrificantes", "lote": "LUB-401",
            "quantidade": 22, "unidade": "L", "custo_unitario": 26.00, "data_validade": "2029-09-02",
            "destino_centro_custo": "Manutenção de Máquinas e Frota", "responsavel": "Pedro Operador",
            "devolucao_embalagem": "Não Aplicável"
        },

        # =========================================================================
        # 16. ROLAMENTO CÔNICO GRADE ARADORA -> Pouco Histórico (< 3 saídas -> Incerteza Alta!)
        # =========================================================================
        {
            "id_movimento": "MOV-0079", "data_movimento": "2026-09-10", "tipo_movimento": "Entrada",
            "produto": "Rolamento Cônico Grade Aradora", "categoria": "Peças e Manutenção", "lote": "PEC-901",
            "quantidade": 12, "unidade": "un", "custo_unitario": 290.00, "data_validade": "",
            "destino_centro_custo": "Almoxarifado Central (Entrada)", "responsavel": "Marcos Souza",
            "devolucao_embalagem": "Não Aplicável"
        },
        {
            "id_movimento": "MOV-0080", "data_movimento": "2026-09-27", "tipo_movimento": "Saída",
            "produto": "rolamento grade", "categoria": "Peças e Manutenção", "lote": "PEC-901",
            "quantidade": 4, "unidade": "peca", "custo_unitario": 290.00, "data_validade": "",
            "destino_centro_custo": "Manutenção de Máquinas e Frota", "responsavel": "Pedro Operador",
            "devolucao_embalagem": "Não Aplicável"
        },
        {
            "id_movimento": "MOV-0081", "data_movimento": "2026-10-24", "tipo_movimento": "Saída",
            "produto": "Rolamento Cônico Grade Aradora", "categoria": "Peças e Manutenção", "lote": "PEC-901",
            "quantidade": 6, "unidade": "un", "custo_unitario": 290.00, "data_validade": "",
            "destino_centro_custo": "Manutenção de Máquinas e Frota", "responsavel": "Pedro Operador",
            "devolucao_embalagem": "Não Aplicável"
        },

        # =========================================================================
        # 17. KIT EPI APLICAÇÃO DEFENSIVOS -> Pouco Histórico (< 3 saídas -> Incerteza Alta!)
        # =========================================================================
        {
            "id_movimento": "MOV-0082", "data_movimento": "2026-09-05", "tipo_movimento": "Entrada",
            "produto": "Kit EPI Aplicação Defensivos", "categoria": "EPIs", "lote": "EPI-2026",
            "quantidade": 15, "unidade": "un", "custo_unitario": 185.00, "data_validade": "2028-09-05",
            "destino_centro_custo": "Almoxarifado Central (Entrada)", "responsavel": "Marcos Souza",
            "devolucao_embalagem": "Não Aplicável"
        },
        {
            "id_movimento": "MOV-0083", "data_movimento": "2026-09-22", "tipo_movimento": "Saída",
            "produto": "kit epi", "categoria": "EPIs", "lote": "EPI-2026",
            "quantidade": 5, "unidade": "unidade", "custo_unitario": 185.00, "data_validade": "2028-09-05",
            "destino_centro_custo": "Talhão 01 - Soja (150ha)", "responsavel": "Carlos Agrônomo",
            "devolucao_embalagem": "Não Aplicável"
        },
        {
            "id_movimento": "MOV-0084", "data_movimento": "2026-10-16", "tipo_movimento": "Saída",
            "produto": "epi defensivo", "categoria": "EPIs", "lote": "EPI-2026",
            "quantidade": 4, "unidade": "un", "custo_unitario": 185.00, "data_validade": "2028-09-05",
            "destino_centro_custo": "Talhão 02 - Milho Safrinha (120ha)", "responsavel": "Carlos Agrônomo",
            "devolucao_embalagem": "Não Aplicável"
        },

        # =========================================================================
        # 18. ARAME LISO OVALADO ZN3 -> Manutenção de Cercas e Piquetes Rotacionados
        # =========================================================================
        {
            "id_movimento": "MOV-0085", "data_movimento": "2026-09-01", "tipo_movimento": "Entrada",
            "produto": "Arame Liso Ovalado ZN3", "categoria": "Peças e Manutenção", "lote": "ARA-55",
            "quantidade": 20, "unidade": "un", "custo_unitario": 640.00, "data_validade": "",
            "destino_centro_custo": "Almoxarifado Central (Entrada)", "responsavel": "Marcos Souza",
            "devolucao_embalagem": "Não Aplicável"
        },
        {
            "id_movimento": "MOV-0086", "data_movimento": "2026-09-11", "tipo_movimento": "Saída",
            "produto": "arame liso", "categoria": "Peças e Manutenção", "lote": "ARA-55",
            "quantidade": 4, "unidade": "un", "custo_unitario": 640.00, "data_validade": "",
            "destino_centro_custo": "Manutenção de Cercas e Infraestrutura", "responsavel": "Antônio Campeiro",
            "devolucao_embalagem": "Não Aplicável"
        },
        {
            "id_movimento": "MOV-0087", "data_movimento": "2026-09-26", "tipo_movimento": "Saída",
            "produto": "arame ovalado", "categoria": "Peças e Manutenção", "lote": "ARA-55",
            "quantidade": 3, "unidade": "un", "custo_unitario": 640.00, "data_validade": "",
            "destino_centro_custo": "Pastos Rotacionados (30 Piquetes - 140ha)", "responsavel": "Antônio Campeiro",
            "devolucao_embalagem": "Não Aplicável"
        },
        {
            "id_movimento": "MOV-0088", "data_movimento": "2026-10-08", "tipo_movimento": "Saída",
            "produto": "Arame Liso Ovalado ZN3", "categoria": "Peças e Manutenção", "lote": "ARA-55",
            "quantidade": 4, "unidade": "un", "custo_unitario": 640.00, "data_validade": "",
            "destino_centro_custo": "Manutenção de Cercas e Infraestrutura", "responsavel": "Antônio Campeiro",
            "devolucao_embalagem": "Não Aplicável"
        },
        {
            "id_movimento": "MOV-0089", "data_movimento": "2026-10-20", "tipo_movimento": "Saída",
            "produto": "Arame Liso Ovalado ZN3", "categoria": "Peças e Manutenção", "lote": "ARA-55",
            "quantidade": 3, "unidade": "un", "custo_unitario": 640.00, "data_validade": "",
            "destino_centro_custo": "Pastos Rotacionados (30 Piquetes - 140ha)", "responsavel": "Antônio Campeiro",
            "devolucao_embalagem": "Não Aplicável"
        },

        # =========================================================================
        # MOVIMENTAÇÕES COMPLEMENTARES (Silos, Semiconfinamento, Talhões) -> 95+ registros
        # =========================================================================
        {
            "id_movimento": "MOV-0090", "data_movimento": "2026-09-15", "tipo_movimento": "Entrada",
            "produto": "Glifosato 480 SL", "categoria": "Defensivos Químicos", "lote": "GLI-4402",
            "quantidade": 200, "unidade": "L", "custo_unitario": 24.50, "data_validade": "2027-09-15",
            "destino_centro_custo": "Almoxarifado Central (Entrada)", "responsavel": "Marcos Souza",
            "devolucao_embalagem": "Não Aplicável"
        },
        {
            "id_movimento": "MOV-0091", "data_movimento": "2026-09-29", "tipo_movimento": "Saída",
            "produto": "Inseticida Engeo Pleno S", "categoria": "Defensivos Químicos", "lote": "ENG-301",
            "quantidade": 8, "unidade": "L", "custo_unitario": 175.00, "data_validade": "2027-05-15",
            "destino_centro_custo": "Silos e Armazenagem", "responsavel": "Carlos Agrônomo",
            "devolucao_embalagem": "Prazo Vencido"
        },
        {
            "id_movimento": "MOV-0092", "data_movimento": "2026-10-03", "tipo_movimento": "Saída",
            "produto": "Óleo Diesel S10", "categoria": "Combustíveis e Lubrificantes", "lote": "DSL-2609A",
            "quantidade": 120, "unidade": "L", "custo_unitario": 6.10, "data_validade": "2027-09-01",
            "destino_centro_custo": "Silos e Armazenagem", "responsavel": "Pedro Operador",
            "devolucao_embalagem": "Não Aplicável"
        },
        {
            "id_movimento": "MOV-0093", "data_movimento": "2026-10-11", "tipo_movimento": "Saída",
            "produto": "Ureia Agrícola 45% N", "categoria": "Fertilizantes", "lote": "URE-101",
            "quantidade": 400, "unidade": "kg", "custo_unitario": 3.40, "data_validade": "2028-03-01",
            "destino_centro_custo": "Semiconfinamento (200 Bovinos)", "responsavel": "Antônio Campeiro",
            "devolucao_embalagem": "Não Aplicável"
        },
        {
            "id_movimento": "MOV-0094", "data_movimento": "2026-10-14", "tipo_movimento": "Saída",
            "produto": "NPK 04-14-08", "categoria": "Fertilizantes", "lote": "NPK-98-OK",
            "quantidade": 18, "unidade": "saco", "custo_unitario": 155.00, "data_validade": "2028-09-01",
            "destino_centro_custo": "Talhão 01 - Soja (150ha)", "responsavel": "João Tratorista",
            "devolucao_embalagem": "Não Aplicável"
        },
        {
            "id_movimento": "MOV-0095", "data_movimento": "2026-10-22", "tipo_movimento": "Saída",
            "produto": "Fungicida Fox Xpro", "categoria": "Defensivos Químicos", "lote": "FOX-12",
            "quantidade": 14, "unidade": "L", "custo_unitario": 310.00, "data_validade": "2027-11-30",
            "destino_centro_custo": "Talhão 01 - Soja (150ha)", "responsavel": "Carlos Agrônomo",
            "devolucao_embalagem": "Pendente"
        },
        {
            "id_movimento": "MOV-0096", "data_movimento": "2026-10-25", "tipo_movimento": "Saída",
            "produto": "Cloreto de Potássio (KCl)", "categoria": "Fertilizantes", "lote": "KCL-03",
            "quantidade": 30, "unidade": "saco", "custo_unitario": 192.50, "data_validade": "2028-10-15",
            "destino_centro_custo": "Talhão 02 - Milho Safrinha (120ha)", "responsavel": "João Tratorista",
            "devolucao_embalagem": "Não Aplicável"
        }
    ]
    return rows


def generate_seed_csv(target_path: Path | str | None = None) -> Path:
    """Gera o arquivo CSV da base simulada com as 13 colunas canônicas do AgroZica."""
    base_dir = Path(__file__).resolve().parent
    csv_path = Path(target_path) if target_path else (base_dir / "data" / "base_simulada_agrozica.csv")
    csv_path.parent.mkdir(parents=True, exist_ok=True)

    records = build_simulated_records()
    fieldnames = [
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

    with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    return csv_path


if __name__ == "__main__":
    out = generate_seed_csv()
    print(f"[AgroZica Seed] Base simulada gerada com sucesso em: {out}")

