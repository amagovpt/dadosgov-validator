from app.models import ValidationRuleset
from app import create_app, db


TITLE = "PT2030 - Regras de Validação"
DESCRIPTION = "Regras de validação para os datasets do PT2030, incluindo dotacoes, avisos, operacoes, operacoes regionalizadas e entidades."
DADOSGOV_DATASET_ID = "600850ac454ae38cbce87116"


"""
================================================================================================================
DOTACOES
================================================================================================================
"""
dotacoes_resource_id = "6399d7170781907341452aad"

dotacoes_dataframe_id = "dataframe_" + DADOSGOV_DATASET_ID + "_" + dotacoes_resource_id

dotacoes_rules = [
   { "dataframe_ids": [dotacoes_dataframe_id], "type": "test_not_null", "column": "dt_referencia" },
   { "dataframe_ids": [dotacoes_dataframe_id], "type": "test_not_null", "column": "cd_programa_operacional" },
   { "dataframe_ids": [dotacoes_dataframe_id], "type": "test_not_null", "column": "ds_programa_operacional" },
   { "dataframe_ids": [dotacoes_dataframe_id], "type": "test_not_null", "column": "ds_tipologia_objetivo" },
   { "dataframe_ids": [dotacoes_dataframe_id], "type": "test_not_null", "column": "cd_objetivo_estrategico" },
   { "dataframe_ids": [dotacoes_dataframe_id], "type": "test_not_null", "column": "ds_objetivo_estrategico" },
   { "dataframe_ids": [dotacoes_dataframe_id], "type": "test_not_null", "column": "cd_objetivo_especifico" },
   { "dataframe_ids": [dotacoes_dataframe_id], "type": "test_not_null", "column": "sigla_objetivo_especifico" },
   { "dataframe_ids": [dotacoes_dataframe_id], "type": "test_not_null", "column": "ds_objetivo_especifico" },
   { "dataframe_ids": [dotacoes_dataframe_id], "type": "test_not_null", "column": "cd_fundo" },
   { "dataframe_ids": [dotacoes_dataframe_id], "type": "test_not_null", "column": "sg_fundo" },
   { "dataframe_ids": [dotacoes_dataframe_id], "type": "test_not_null", "column": "ds_fundo" },
   { "dataframe_ids": [dotacoes_dataframe_id], "type": "test_not_null", "column": "montante_programado" },

   { "dataframe_ids": [dotacoes_dataframe_id], "type": "test_possible_values", "column": "sg_fundo", "possible_values": ['FEDER', 'FSE+', 'FC', 'FEAMPA', 'FTJ'] }

    # TODO: implement the "test_domains_pt2030_cd_ds_objetivo_estrategico" test
]

"""
================================================================================================================
AVISOS
================================================================================================================
"""
avisos_resource_id = "65afddb4bca3f3b9c6aac069"

avisos_dataframe_id = "dataframe_" + DADOSGOV_DATASET_ID + "_" + avisos_resource_id

avisoes_rules = [
    { "dataframe_ids": [avisos_dataframe_id], "type": "test_not_null", "column": "dt_referencia" },
    { "dataframe_ids": [avisos_dataframe_id], "type": "test_not_null", "column": "cd_aviso" },
    { "dataframe_ids": [avisos_dataframe_id], "type": "test_not_null", "column": "ds_aviso" },
    { "dataframe_ids": [avisos_dataframe_id], "type": "test_not_null", "column": "estado_aviso" },
    { "dataframe_ids": [avisos_dataframe_id], "type": "test_not_null", "column": "cd_programa" },
    { "dataframe_ids": [avisos_dataframe_id], "type": "test_not_null", "column": "ds_programa" },
    { "dataframe_ids": [avisos_dataframe_id], "type": "test_not_null", "column": "marca_programa" },
    { "dataframe_ids": [avisos_dataframe_id], "type": "test_not_null", "column": "cd_objetivo_estrategico" },
    { "dataframe_ids": [avisos_dataframe_id], "type": "test_not_null", "column": "ds_objetivo_estrategico" },
    { "dataframe_ids": [avisos_dataframe_id], "type": "test_not_null", "column": "cd_objetivo_especifico" },
    { "dataframe_ids": [avisos_dataframe_id], "type": "test_not_null", "column": "sg_objetivo_especifico" },
    { "dataframe_ids": [avisos_dataframe_id], "type": "test_not_null", "column": "ds_objetivo_especifico" },
    { "dataframe_ids": [avisos_dataframe_id], "type": "test_not_null", "column": "cd_fundo" },
    { "dataframe_ids": [avisos_dataframe_id], "type": "test_not_null", "column": "sg_fundo" },
    { "dataframe_ids": [avisos_dataframe_id], "type": "test_not_null", "column": "ds_fundo" },
    { "dataframe_ids": [avisos_dataframe_id], "type": "test_not_null", "column": "montante_colocado_concurso" },

    { "dataframe_ids": [avisos_dataframe_id], "type": "test_possible_values", "column": "estado_aviso", "possible_values": ['Aberto', 'Fechado'] },
    { "dataframe_ids": [avisos_dataframe_id], "type": "test_possible_values", "column": "sg_fundo", "possible_values": ['FEDER', 'FSE+', 'FC', 'FEAMPA', 'FTJ'] },
    { "dataframe_ids": [avisos_dataframe_id], "type": "test_possible_values", "column": "enquadramento", "possible_values": ['PT2030'] }

    # TODO: implement the "test_domains_pt2030_cd_ds_objetivo_estrategico" test
]

"""
================================================================================================================
OPERACOES
================================================================================================================
"""
operacoes_resource_id = "672265cd9e435b9467b89ded"

operacoes_dataframe_id = "dataframe_" + DADOSGOV_DATASET_ID + "_" + operacoes_resource_id

operacoes_rules = [
    { "dataframe_ids": [operacoes_dataframe_id], "type": "test_not_null", "column": "dt_referencia" },
    { "dataframe_ids": [operacoes_dataframe_id], "type": "test_not_null", "column": "cd_operacao" },
    { "dataframe_ids": [operacoes_dataframe_id], "type": "test_not_null", "column": "nome_operacao" },
    { "dataframe_ids": [operacoes_dataframe_id], "type": "test_not_null", "column": "finalidade", "warning_only": True },
    { "dataframe_ids": [operacoes_dataframe_id], "type": "test_not_null", "column": "cd_programa" },
    { "dataframe_ids": [operacoes_dataframe_id], "type": "test_not_null", "column": "ds_programa" },
    { "dataframe_ids": [operacoes_dataframe_id], "type": "test_not_null", "column": "cd_objetivo_estrategico" },
    { "dataframe_ids": [operacoes_dataframe_id], "type": "test_not_null", "column": "ds_objetivo_estrategico" },
    { "dataframe_ids": [operacoes_dataframe_id], "type": "test_not_null", "column": "cd_objetivo_especifico" },
    { "dataframe_ids": [operacoes_dataframe_id], "type": "test_not_null", "column": "sg_objetivo_especifico" },
    { "dataframe_ids": [operacoes_dataframe_id], "type": "test_not_null", "column": "cd_area_tematica" },
    { "dataframe_ids": [operacoes_dataframe_id], "type": "test_not_null", "column": "ds_area_tematica" },
    { "dataframe_ids": [operacoes_dataframe_id], "type": "test_not_null", "column": "pc_cofinanciamento" },
    { "dataframe_ids": [operacoes_dataframe_id], "type": "test_not_null", "column": "nif_beneficiario" },
    { "dataframe_ids": [operacoes_dataframe_id], "type": "test_not_null", "column": "nome_beneficiario" },
    { "dataframe_ids": [operacoes_dataframe_id], "type": "test_not_null", "column": "cd_fundo" },
    { "dataframe_ids": [operacoes_dataframe_id], "type": "test_not_null", "column": "ds_fundo" },
    { "dataframe_ids": [operacoes_dataframe_id], "type": "test_not_null", "column": "total_elegivel_aprovado" },
    { "dataframe_ids": [operacoes_dataframe_id], "type": "test_not_null", "column": "fundo_aprovado" },
    { "dataframe_ids": [operacoes_dataframe_id], "type": "test_not_null", "column": "total_elegivel_executado" },
    { "dataframe_ids": [operacoes_dataframe_id], "type": "test_not_null", "column": "fundo_executado" },
    { "dataframe_ids": [operacoes_dataframe_id], "type": "test_not_null", "column": "modalidade" },
    { "dataframe_ids": [operacoes_dataframe_id], "type": "test_not_null", "column": "cd_cae_operacao" },
    { "dataframe_ids": [operacoes_dataframe_id], "type": "test_not_null", "column": "ds_cae_operacao" },
    { "dataframe_ids": [operacoes_dataframe_id], "type": "test_not_null", "column": "cd_estado_operacao" },
    { "dataframe_ids": [operacoes_dataframe_id], "type": "test_not_null", "column": "ds_estado_operacao" },
    { "dataframe_ids": [operacoes_dataframe_id], "type": "test_not_null", "column": "cd_aviso_operacao" },
    { "dataframe_ids": [operacoes_dataframe_id], "type": "test_not_null", "column": "ds_aviso_operacao" },
    { "dataframe_ids": [operacoes_dataframe_id], "type": "test_not_null", "column": "enquadramento" },
    { "dataframe_ids": [operacoes_dataframe_id], "type": "test_not_null", "column": "dt_inicio_prevista" },
    { "dataframe_ids": [operacoes_dataframe_id], "type": "test_not_null", "column": "dt_conclusao_prevista" },

    { "dataframe_ids": [operacoes_dataframe_id], "type": "test_possible_values", "column": "sg_fundo", "possible_values": ['FEDER', 'FSE+', 'FC', 'FEAMPA', 'FTJ'] },
    { "dataframe_ids": [operacoes_dataframe_id], "type": "test_possible_values", "column": "enquadramento", "possible_values": ['PT2030'] },

    { "dataframe_ids": [operacoes_dataframe_id], "type": "test_percentage_max_decimal_places", "column": "pc_cofinanciamento", "max_decimal_places": 2, "warning_only": True }, 

    # TODO: implement the "test_domains_pt2030_cd_ds_objetivo_estrategico" test

    { "dataframe_ids": [operacoes_dataframe_id], "type": "test_domains_numeric", "column": "pc_cofinanciamento", "min_value": 0, "max_value": 100 },

    { "dataframe_ids": [operacoes_dataframe_id], "type": "test_boundaries_sum_equals", "column": "pc_localizacao_operacao", "value": 100, "warning_only": True },
]

"""
================================================================================================================
OPERACOES REGIONALIZADAS
================================================================================================================
"""
operacoes_regionalizadas_resource_id = "6776b1f30b2fe06be472fcd4"

operacoes_regionalizadas_dataframe_id = "dataframe_" + DADOSGOV_DATASET_ID + "_" + operacoes_regionalizadas_resource_id

operacoes_regionalizadas_rules = [
    { "dataframe_ids": [operacoes_regionalizadas_dataframe_id], "type": "test_not_null", "column": "dt_referencia" },
    { "dataframe_ids": [operacoes_regionalizadas_dataframe_id], "type": "test_not_null", "column": "cd_programa" },
    { "dataframe_ids": [operacoes_regionalizadas_dataframe_id], "type": "test_not_null", "column": "ds_programa" },
    { "dataframe_ids": [operacoes_regionalizadas_dataframe_id], "type": "test_not_null", "column": "cd_fundo" },
    { "dataframe_ids": [operacoes_regionalizadas_dataframe_id], "type": "test_not_null", "column": "cd_operacao" },
    { "dataframe_ids": [operacoes_regionalizadas_dataframe_id], "type": "test_not_null", "column": "cd_nutsii_operacao" },
    { "dataframe_ids": [operacoes_regionalizadas_dataframe_id], "type": "test_not_null", "column": "ds_nutsii_operacao" },
    { "dataframe_ids": [operacoes_regionalizadas_dataframe_id], "type": "test_not_null", "column": "cd_nutsiii_operacao" },
    { "dataframe_ids": [operacoes_regionalizadas_dataframe_id], "type": "test_not_null", "column": "ds_nutsiii_operacao" },
    { "dataframe_ids": [operacoes_regionalizadas_dataframe_id], "type": "test_not_null", "column": "cd_distrito_operacao" },
    { "dataframe_ids": [operacoes_regionalizadas_dataframe_id], "type": "test_not_null", "column": "ds_distrito_operacao" },
    { "dataframe_ids": [operacoes_regionalizadas_dataframe_id], "type": "test_not_null", "column": "cd_concelho_operacao" },
    { "dataframe_ids": [operacoes_regionalizadas_dataframe_id], "type": "test_not_null", "column": "ds_concelho_operacao" },
    { "dataframe_ids": [operacoes_regionalizadas_dataframe_id], "type": "test_not_null", "column": "pc_localizacao_operacao", "warning_only": True },
    { "dataframe_ids": [operacoes_regionalizadas_dataframe_id], "type": "test_not_null", "column": "total_elegivel_aprovado", "warning_only": True },
    { "dataframe_ids": [operacoes_regionalizadas_dataframe_id], "type": "test_not_null", "column": "fundo_aprovado", "warning_only": True },
    { "dataframe_ids": [operacoes_regionalizadas_dataframe_id], "type": "test_not_null", "column": "total_elegivel_executado", "warning_only": True },
    { "dataframe_ids": [operacoes_regionalizadas_dataframe_id], "type": "test_not_null", "column": "fundo_executado", "warning_only": True },
    { "dataframe_ids": [operacoes_regionalizadas_dataframe_id], "type": "test_not_null", "column": "enquadramento" },

    { "dataframe_ids": [operacoes_regionalizadas_dataframe_id], "type": "test_possible_values", "column": "sg_fundo", "possible_values": ['FEDER', 'FSE+', 'FC', 'FEAMPA', 'FTJ'] },
    { "dataframe_ids": [operacoes_regionalizadas_dataframe_id], "type": "test_possible_values", "column": "enquadramento", "possible_values": ['PT2030'] },

    { "dataframe_ids": [operacoes_regionalizadas_dataframe_id], "type": "test_percentage_max_decimal_places", "column": "pc_localizacao_operacao", "max_decimal_places": 4, "warning_only": True },

    { "dataframe_ids": [operacoes_regionalizadas_dataframe_id], "type": "test_domains_numeric", "column": "pc_localizacao_operacao", "min_value": 0, "max_value": 100 }

    # TODO: include "test_admin_units" tests
]

"""
================================================================================================================
ENTIDADES
================================================================================================================
"""
entidades_resource_id = "672266469e435b9467b89dee"
entidades_dataframe_id = "dataframe_" + DADOSGOV_DATASET_ID + "_" + entidades_resource_id

entidades_rules = [
    { "dataframe_ids": [entidades_dataframe_id], "type": "test_not_null", "column": "dt_referencia" },
    { "dataframe_ids": [entidades_dataframe_id], "type": "test_not_null", "column": "cd_operacao" },
    { "dataframe_ids": [entidades_dataframe_id], "type": "test_not_null", "column": "nif_entidade" },
    { "dataframe_ids": [entidades_dataframe_id], "type": "test_not_null", "column": "ds_entidade" },
    { "dataframe_ids": [entidades_dataframe_id], "type": "test_not_null", "column": "papel_entidade" },
    { "dataframe_ids": [entidades_dataframe_id], "type": "test_not_null", "column": "pc_beneficiario_operacao" },
    { "dataframe_ids": [entidades_dataframe_id], "type": "test_not_null", "column": "valor_contratualizado" },
    { "dataframe_ids": [entidades_dataframe_id], "type": "test_not_null", "column": "enquadramento" },
    { "dataframe_ids": [entidades_dataframe_id], "type": "test_not_null", "column": "fundo_aprovado" },
    { "dataframe_ids": [entidades_dataframe_id], "type": "test_not_null", "column": "fundo_executado" },

    { "dataframe_ids": [entidades_dataframe_id], "type": "test_possible_values", "column": "papel_entidade", "possible_values": ['Beneficiário Principal', 'Outros Beneficiários', 'Fornecedor'] },
    { "dataframe_ids": [entidades_dataframe_id], "type": "test_possible_values", "column": "enquadramento", "possible_values": ['PT2030'] },

    { "dataframe_ids": [entidades_dataframe_id], "type": "test_percentage_max_decimal_places", "column": "pc_beneficiario_operacao", "max_decimal_places": 2, "warning_only": True },

    { "dataframe_ids": [entidades_dataframe_id], "type": "test_domains_numeric", "column": "pc_beneficiario_operacao", "min_value": 0, "max_value": 100 },
]

"""
================================================================================================================
MULTIPLE RESOURCES
================================================================================================================
"""
multiple_resource_rules = [
    {
        "dataframe_ids": [entidades_dataframe_id, operacoes_dataframe_id, operacoes_regionalizadas_dataframe_id], 
        "type": "test_domains_only_one_value_across_datasets",
        "base_column": "dt_referencia",
        "extended_columns": [
            "dt_referencia",
            "dt_referencia"
        ], 
        "warning_only": True
    },

    { 
        "dataframe_ids": [operacoes_dataframe_id, entidades_dataframe_id], 
        "type": "test_boundaries_extended_table_coherence", 
        "base_column": "cd_operacao", 
        "extended_column": "cd_operacao",
        "warning_only": True 
    },
    { 
        "dataframe_ids": [operacoes_dataframe_id, operacoes_regionalizadas_dataframe_id], 
        "type": "test_boundaries_extended_table_coherence", 
        "base_column": "cd_operacao", 
        "extended_column": "cd_operacao",
        "warning_only": True
    },

]


"""
###############################################################################################
DB INTERACTION 
###############################################################################################
"""

DADOSGOV_RESOURCE_ID_LIST = [
    dotacoes_resource_id,
    avisos_resource_id,
    operacoes_resource_id,
    operacoes_regionalizadas_resource_id,
    entidades_resource_id
]
ALL_RULES = dotacoes_rules + avisoes_rules + operacoes_rules + operacoes_regionalizadas_rules + entidades_rules + multiple_resource_rules


def main():
    app = create_app()

    with app.app_context():
        validation_ruleset = ValidationRuleset(
            title=TITLE,
            description=DESCRIPTION,
            dadosgov_dataset_id=DADOSGOV_DATASET_ID,
            dadosgov_resource_id_list=DADOSGOV_RESOURCE_ID_LIST,
            rules=ALL_RULES
        )

        db.session.add(validation_ruleset)
        db.session.commit()


if __name__ == "__main__":
    main()