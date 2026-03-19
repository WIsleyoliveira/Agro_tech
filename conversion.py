"""
Conversão de nutrientes do sensor (mg/kg) para kg/ha.

Fórmula simplificada:
- Camada de solo: 20 cm (0,2 m)
- Densidade do solo: 1.250 kg/m³
- Área: 1 hectare = 10.000 m²

Volume: 10.000 m² × 0,2 m = 2.000 m³
Peso: 2.000 m³ × 1.250 kg/m³ = 2.500.000 kg

1 mg/kg × 2.500.000 kg = 2.500.000 mg = 2.500 g = 2,5 kg/ha
→ Fator de conversão: 2,5 kg/ha por 1 mg/kg
"""

# Constantes padrão
SOIL_DEPTH_M = 0.2           # 20 cm
SOIL_DENSITY_KG_M3 = 1_250   # kg/m³ (Franco - padrão)
HECTARE_M2 = 10_000

# Limite do sensor (mg/kg)
SENSOR_MAX_MG_KG = 1999

# Tabela de tipos de solo e densidades (kg/m³)
SOIL_TYPES = [
    {
        "id": "organico_siltoso",
        "label": "Várzea, terra de baixada, que encharca",
        "tipo": "Orgânico/Siltoso",
        "descricao": "Geralmente escura, fofa, encontrada em áreas baixas, pode ser muito ácida.",
        "density_kg_m3": 1100,
    },
    {
        "id": "argiloso",
        "label": "Terra vermelha, forte, que racha quando seca",
        "tipo": "Argiloso",
        "descricao": "Segura muita água, fica pegajosa quando molhada, forma torrões duros.",
        "density_kg_m3": 1150,
    },
    {
        "id": "franco_argiloso",
        "label": "Terra de cultura, preta, boa de trabalhar",
        "tipo": "Franco-argiloso",
        "descricao": "Escura, rica em matéria orgânica, boa estrutura, considerada ideal.",
        "density_kg_m3": 1200,
    },
    {
        "id": "franco",
        "label": "Terra mista, nem muito solta, nem muito dura",
        "tipo": "Franco (Misto)",
        "descricao": "Equilibrada, boa para a maioria das culturas. É o meio-termo.",
        "density_kg_m3": 1250,
    },
    {
        "id": "franco_arenoso",
        "label": "Terra leve, solta, que seca rápido",
        "tipo": "Franco-arenoso",
        "descricao": "Drena bem, fácil de trabalhar, mas não segura muito bem os nutrientes.",
        "density_kg_m3": 1350,
    },
    {
        "id": "arenoso",
        "label": "Terra de areia, arenosa, fraca",
        "tipo": "Arenoso",
        "descricao": "Muito solta, não segura água nem nutrientes, esquenta rápido.",
        "density_kg_m3": 1450,
    },
]


def get_density_by_soil_type(soil_type_id: str | None) -> float:
    """Retorna densidade (kg/m³) pelo id do tipo de solo. Padrão: franco (1250)."""
    if not soil_type_id:
        return SOIL_DENSITY_KG_M3
    for st in SOIL_TYPES:
        if st["id"] == soil_type_id:
            return st["density_kg_m3"]
    return SOIL_DENSITY_KG_M3


def get_conversion_factor(density_kg_m3: float | None = None) -> float:
    """Retorna fator de conversão para a densidade dada."""
    d = density_kg_m3 or SOIL_DENSITY_KG_M3
    return (HECTARE_M2 * SOIL_DEPTH_M * d) / 1_000_000


# Fator padrão (Franco)
CONVERSION_FACTOR = get_conversion_factor(SOIL_DENSITY_KG_M3)  # = 2.5


def mg_kg_to_kg_ha(
    value_mg_kg: float,
    depth_m: float = SOIL_DEPTH_M,
    density_kg_m3: float = SOIL_DENSITY_KG_M3
) -> float:
    """
    Converte leitura do sensor (mg/kg) para kg/ha.

    Args:
        value_mg_kg: Valor medido pelo sensor em mg/kg (0 a 2000)
        depth_m: Profundidade da camada em metros (default: 0.2)
        density_kg_m3: Densidade do solo em kg/m³ (default: 1250)

    Returns:
        Valor convertido em kg/ha
    """
    if value_mg_kg is None:
        return None
    factor = (HECTARE_M2 * depth_m * density_kg_m3) / 1_000_000
    return round(value_mg_kg * factor, 2)


def convert_npk_sensor_to_kg_ha(
    nitrogen_mg_kg: float | None = None,
    phosphorus_mg_kg: float | None = None,
    potassium_mg_kg: float | None = None,
    soil_type_id: str | None = None,
    density_kg_m3: float | None = None,
    **kwargs
) -> dict:
    """
    Converte N, P e K de mg/kg (sensor) para kg/ha.

    Args:
        soil_type_id: Id da tabela SOIL_TYPES (usa densidade correspondente)
        density_kg_m3: Sobrescreve densidade se fornecido (tem prioridade sobre soil_type_id)

    Retorna dicionário com valores convertidos e originais.
    """
    d = density_kg_m3 if density_kg_m3 is not None else get_density_by_soil_type(soil_type_id)
    conv_kw = {"density_kg_m3": d}
    if "depth_m" in kwargs:
        conv_kw["depth_m"] = kwargs["depth_m"]
    result = {"density_kg_m3": d, "conversion_factor": get_conversion_factor(d)}
    if nitrogen_mg_kg is not None:
        result["nitrogen_kg_ha"] = mg_kg_to_kg_ha(nitrogen_mg_kg, **conv_kw)
        result["nitrogen_mg_kg"] = nitrogen_mg_kg
    if phosphorus_mg_kg is not None:
        result["phosphorus_kg_ha"] = mg_kg_to_kg_ha(phosphorus_mg_kg, **conv_kw)
        result["phosphorus_mg_kg"] = phosphorus_mg_kg
    if potassium_mg_kg is not None:
        result["potassium_kg_ha"] = mg_kg_to_kg_ha(potassium_mg_kg, **conv_kw)
        result["potassium_mg_kg"] = potassium_mg_kg
    return result
