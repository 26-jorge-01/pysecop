from dataclasses import dataclass, field
from typing import Dict, List, Optional

@dataclass
class DatasetConfig:
    id: str
    name: str
    description: str
    columns: List[str] = field(default_factory=list)
    date_columns: List[str] = field(default_factory=list)
    url_columns: List[str] = field(default_factory=list)
    text_columns: List[str] = field(default_factory=list)
    categorical_columns: List[str] = field(default_factory=list)
    id_column: str = "uid"  # Default for SECOP I

# SECOP I Contratos
SECOP_I_CONTRATOS = DatasetConfig(
    id="f789-7hwg",
    name="SECOP I Contratos",
    description="Contratos estatales de régimen general SECOP I",
    id_column="uid",
    columns=[
        "uid", "numero_de_contrato", "id_adjudicacion", "anno_cargue_secop", 
        "fecha_de_cargue_en_el_secop", "anno_firma_contrato", "fecha_de_firma_del_contrato",
        "fecha_fin_ejec_contrato", "tipo_de_contrato", "modalidad_de_contratacion", 
        "causal_de_otras_formas_de", "estado_del_proceso", "objeto_del_contrato_a_la", 
        "detalle_del_objeto_a_contratar", "tipo_identifi_del_contratista", 
        "identificacion_del_contratista", "nom_razon_social_contratista", 
        "tipo_doc_representante_legal", "identific_representante_legal", 
        "nombre_del_represen_legal", "nombre_entidad", "nit_de_la_entidad", 
        "departamento_entidad", "municipio_entidad", "valor_contrato_con_adiciones", 
        "ruta_proceso_en_secop_i"
    ],
    date_columns=[
        "fecha_de_cargue_en_el_secop", "fecha_de_firma_del_contrato", 
        "fecha_ini_ejec_contrato", "fecha_fin_ejec_contrato", 
        "fecha_liquidacion", "ultima_actualizacion"
    ],
    url_columns=["ruta_proceso_en_secop_i"],
    text_columns=[
        "causal_de_otras_formas_de", "detalle_del_objeto_a_contratar", 
        "compromiso_presupuestal", "objeto_del_contrato_a_la", 
        "proponentes_seleccionados", "calificacion_definitiva", "posicion_rubro", 
        "nombre_rubro", "pilar_acuerdo_paz", "punto_acuerdo_paz", 
        "cumpledecreto248", "incluyebienesdecreto248"
    ],
    categorical_columns=["cumple_sentencia_t302"]
)

# SECOP II Contratos
SECOP_II_CONTRATOS = DatasetConfig(
    id="jbjy-vk9h",
    name="SECOP II Contratos",
    description="Contratos estatales SECOP II",
    id_column="id_contrato",
    columns=[
        "id_contrato", "fecha_de_firma", "tipo_de_contrato", 
        "modalidad_de_contratacion", "estado_contrato", "objeto_del_contrato", 
        "tipodocproveedor", "documento_proveedor", "proveedor_adjudicado", 
        "tipo_de_identificaci_n_representante_legal", "identificaci_n_representante_legal", 
        "nombre_representante_legal", "nombre_entidad", "nit_entidad", "departamento", "ciudad", 
        "valor_del_contrato", "urlproceso"
    ],
    date_columns=[
        "fecha_de_firma", "fecha_de_inicio_del_contrato", "fecha_de_fin_del_contrato", 
        "ultima_actualizacion", "fecha_de_inicio_de_ejecucion", "fecha_de_fin_de_ejecucion", 
        "fecha_de_notificaci_n_de_prorrogaci_n", "fecha_inicio_liquidacion", "fecha_fin_liquidacion"
    ],
    url_columns=["urlproceso"],
    text_columns=[
        "descripcion_del_proceso", "condiciones_de_entrega", "habilita_pago_adelantado", 
        "origen_de_los_recursos", "destino_gasto", "objeto_del_contrato"
    ],
    categorical_columns=[
        "liquidaci_n", "obligaci_n_ambiental", "obligaciones_postconsumo", 
        "reversion", "espostconflicto", "el_contrato_puede_ser_prorrogado"
    ]
)

DATASETS = {
    "SECOP_I": SECOP_I_CONTRATOS,
    "SECOP_II": SECOP_II_CONTRATOS,
    "TVEC": DatasetConfig(id="rgxm-mmea", name="TVEC", description="Tienda Virtual del Estado Colombiano")
}

DEFAULT_DOMAIN = "www.datos.gov.co"
