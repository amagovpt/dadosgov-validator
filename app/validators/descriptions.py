RULE_DESCRIPTIONS = {
    "rules": [
        {
            "id": "test_not_null",
            "display_name": "Columna não nula",
            "description": "Verifica se os valores em uma coluna específica não são nulos.",
            "parameters": {
                "column": {
                    "type": "string",
                    "description": "O nome da coluna a ser validada",
                    "required": True
                }
            }
        },
        {
            "id": "test_unique_generic",
            "display_name": "Valores não repetidos",
            "description": "Verifica se os valores em uma ou mais colunas combinadas não se repetem.",
            "parameters": {
                "columns": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Lista de colunas que, combinadas, devem ter valores únicos",
                    "required": True
                }
            }
        },
        {
            "id": "test_length_max",
            "display_name": "Comprimento máximo",
            "description": "Verifica se os valores em uma coluna não excedem um comprimento máximo especificado.",
            "parameters": {
                "column": {
                    "type": "string",
                    "description": "O nome da coluna a ser validada",
                    "required": True
                },
                "max_length": {
                    "type": "integer",
                    "description": "O comprimento máximo permitido",
                    "required": True
                }
            }
        },
        {
            "id": "test_length_min",
            "display_name": "Comprimento mínimo",
            "description": "Verifica se os valores em uma coluna têm pelo menos um comprimento mínimo especificado.",
            "parameters": {
                "column": {
                    "type": "string",
                    "description": "O nome da coluna a ser validada",
                    "required": True
                },
                "min_length": {
                    "type": "integer",
                    "description": "O comprimento mínimo permitido",
                    "required": True
                }
            }
        },
        {
            "id": "test_length_exact",
            "display_name": "Comprimento exato",
            "description": "Verifica se os valores em uma coluna têm um comprimento exato especificado.",
            "parameters": {
                "column": {
                    "type": "string",
                    "description": "O nome da coluna a ser validada",
                    "required": True
                },
                "exact_length": {
                    "type": "integer",
                    "description": "O comprimento exato permitido",
                    "required": True
                }
            }
        },
        {
            "id": "test_possible_values",
            "display_name": "Valores permitidos",
            "description": "Verifica se os valores em uma coluna estão dentro de um conjunto permitido de valores.",
            "parameters": {
                "column": {
                    "type": "string",
                    "description": "O nome da coluna a ser validada",
                    "required": True
                },
                "possible_values": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Lista de valores permitidos para a coluna",
                    "required": True
                }
            }
        },
        {
            "id": "test_percentage_max_decimal_places",
            "display_name": "Porcentagem - Máximo de casas decimais",
            "description": "Verifica se os valores em uma coluna de porcentagens têm no máximo um número específico de casas decimais.",
            "parameters": {
                "column": {
                    "type": "string",
                    "description": "O nome da coluna a ser validada",
                    "required": True
                },
                "max_decimal_places": {
                    "type": "integer",
                    "description": "O número máximo de casas decimais permitido",
                    "required": True
                }
            }
        },
        {
            "id": "test_domains_numeric",
            "display_name": "Domínios numéricos",
            "description": "Verifica se os valores em uma coluna numérica estão dentro de um intervalo permitido (ex: entre 0 e 100 para porcentagens).",
            "parameters": {
                "column": {
                    "type": "string",
                    "description": "O nome da coluna a ser validada",
                    "required": True
                },
                "min_value": {
                    "type": "number",
                    "description": "O valor mínimo permitido",
                    "required": False
                },
                "max_value": {
                    "type": "number",
                    "description": "O valor máximo permitido",
                    "required": False
                }
            }
        },
        {
            "id": "test_one_to_one_columns",
            "display_name": "Colunas 1-para-1",
            "description": "Verifica se há uma relação 1-para-1 entre os valores de duas colunas (ex: cada valor em 'ID' corresponde a exatamente um valor em 'Email' e vice-versa).",
            "parameters": {
                "column1": {
                    "type": "string",
                    "description": "O nome da primeira coluna",
                    "required": True
                },
                "column2": {
                    "type": "string",
                    "description": "O nome da segunda coluna",
                    "required": True
                }
            }
        }
    ]
}