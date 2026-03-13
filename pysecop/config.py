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
        "uid", "anno_cargue_secop", "anno_firma_contrato", "nivel_entidad", 
        "orden_entidad", "nombre_entidad", "nit_de_la_entidad", "c_digo_de_la_entidad", 
        "id_modalidad", "modalidad_de_contratacion", "estado_del_proceso", 
        "causal_de_otras_formas_de", "id_regimen_de_contratacion", "nombre_regimen_de_contratacion", 
        "id_objeto_a_contratar", "objeto_a_contratar", "detalle_del_objeto_a_contratar", 
        "tipo_de_contrato", "municipio_de_obtencion", "municipio_de_entrega", 
        "municipios_ejecucion", "fecha_de_cargue_en_el_secop", "numero_de_constancia", 
        "numero_de_proceso", "numero_de_contrato", "cuantia_proceso", "id_grupo", 
        "nombre_grupo", "id_familia", "nombre_familia", "id_clase", "nombre_clase", 
        "id_adjudicacion", "tipo_identifi_del_contratista", "identificacion_del_contratista", 
        "nom_razon_social_contratista", "dpto_y_muni_contratista", "tipo_doc_representante_legal", 
        "identific_representante_legal", "nombre_del_represen_legal", "fecha_de_firma_del_contrato", 
        "fecha_ini_ejec_contrato", "plazo_de_ejec_del_contrato", "rango_de_ejec_del_contrato", 
        "tiempo_adiciones_en_dias", "tiempo_adiciones_en_meses", "fecha_fin_ejec_contrato", 
        "compromiso_presupuestal", "cuantia_contrato", "valor_total_de_adiciones", 
        "valor_contrato_con_adiciones", "objeto_del_contrato_a_la", "proponentes_seleccionados", 
        "calificacion_definitiva", "id_sub_unidad_ejecutora", "nombre_sub_unidad_ejecutora", 
        "ruta_proceso_en_secop_i", "moneda", "es_postconflicto", "marcacion_adiciones", 
        "posicion_rubro", "nombre_rubro", "valor_rubro", "sexo_replegal", "pilar_acuerdo_paz", 
        "punto_acuerdo_paz", "municipio_entidad", "departamento_entidad", "ultima_actualizacion", 
        "fecha_liquidacion", "cumpledecreto248", "incluyebienesdecreto248", "cumple_sentencia_t302", 
        "es_mipyme", "tama_o_mipyme", "codigo_bpin", "destino_gasto", "pliegos_tipo", "sector_pliegos_tipo"
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
        "objeto_a_contratar", "dpto_y_muni_contratista"
    ],
    categorical_columns=[
        "cumpledecreto248", "incluyebienesdecreto248", "cumple_sentencia_t302", 
        "es_postconflicto", "es_mipyme", "pliegos_tipo"
    ]
)

# SECOP II Contratos
SECOP_II_CONTRATOS = DatasetConfig(
    id="jbjy-vk9h",
    name="SECOP II Contratos",
    description="Contratos estatales SECOP II",
    id_column="id_contrato",
    columns=[
        "nombre_entidad", "nit_entidad", "departamento", "ciudad", "localizaci_n", 
        "orden", "sector", "rama", "entidad_centralizada", "proceso_de_compra", 
        "id_contrato", "referencia_del_contrato", "estado_contrato", 
        "codigo_de_categoria_principal", "descripcion_del_proceso", "tipo_de_contrato", 
        "modalidad_de_contratacion", "justificacion_modalidad_de", "fecha_de_firma", 
        "fecha_de_inicio_del_contrato", "fecha_de_fin_del_contrato", "condiciones_de_entrega", 
        "tipodocproveedor", "documento_proveedor", "proveedor_adjudicado", "es_grupo", 
        "es_pyme", "habilita_pago_adelantado", "liquidaci_n", "obligaci_n_ambiental", 
        "obligaciones_postconsumo", "reversion", "origen_de_los_recursos", "destino_gasto", 
        "valor_del_contrato", "valor_de_pago_adelantado", "valor_facturado", 
        "valor_pendiente_de_pago", "valor_pagado", "valor_amortizado", "valor_pendiente_de", 
        "valor_pendiente_de_ejecucion", "saldo_cdp", "saldo_vigencia", "espostconflicto", 
        "dias_adicionados", "puntos_del_acuerdo", "pilares_del_acuerdo", "urlproceso", 
        "nombre_representante_legal", "nacionalidad_representante_legal", 
        "domicilio_representante_legal", "tipo_de_identificaci_n_representante_legal", 
        "identificaci_n_representante_legal", "g_nero_representante_legal", 
        "presupuesto_general_de_la_nacion_pgn", "sistema_general_de_participaciones", 
        "sistema_general_de_regal_as", "recursos_propios_alcald_as_gobernaciones_y_resguardos_ind_genas_", 
        "recursos_de_credito", "recursos_propios", "ultima_actualizacion", "codigo_entidad", 
        "codigo_proveedor", "fecha_inicio_liquidacion", "fecha_fin_liquidacion", 
        "objeto_del_contrato", "duraci_n_del_contrato", "nombre_del_banco", "tipo_de_cuenta", 
        "n_mero_de_cuenta", "el_contrato_puede_ser_prorrogado", 
        "fecha_de_notificaci_n_de_prorrogaci_n", "nombre_ordenador_del_gasto", 
        "tipo_de_documento_ordenador_del_gasto", "n_mero_de_documento_ordenador_del_gasto", 
        "nombre_supervisor", "tipo_de_documento_supervisor", "n_mero_de_documento_supervisor", 
        "nombre_ordenador_de_pago", "tipo_de_documento_ordenador_de_pago", 
        "n_mero_de_documento_ordenador_de_pago", "documentos_tipo", "descripcion_documentos_tipo"
    ],
    date_columns=[
        "fecha_de_firma", "fecha_de_inicio_del_contrato", "fecha_de_fin_del_contrato", 
        "ultima_actualizacion", "fecha_inicio_liquidacion", "fecha_fin_liquidacion",
        "fecha_de_notificaci_n_de_prorrogaci_n"
    ],
    url_columns=["urlproceso"],
    text_columns=[
        "descripcion_del_proceso", "condiciones_de_entrega", "objeto_del_contrato",
        "justificacion_modalidad_de", "descripcion_documentos_tipo"
    ],
    categorical_columns=[
        "liquidaci_n", "obligaci_n_ambiental", "obligaciones_postconsumo", 
        "reversion", "espostconflicto", "el_contrato_puede_ser_prorrogado",
        "es_pyme", "habilita_pago_adelantado", "entidad_centralizada"
    ]
)

DATASETS = {
    "SECOP_I": SECOP_I_CONTRATOS,
    "SECOP_II": SECOP_II_CONTRATOS,
    "TVEC": DatasetConfig(id="rgxm-mmea", name="TVEC", description="Tienda Virtual del Estado Colombiano")
}

DEFAULT_DOMAIN = "www.datos.gov.co"
