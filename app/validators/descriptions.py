RULE_DESCRIPTIONS = {
    "rules": [
        {
            "id": "test_not_null",
            "display_name": "Columna não nula",
            "description": "Verifica se os valores em uma coluna específica não são nulos.",
            "parameters": {
                "dataset_parameters": {
                    "min_datasets": 1,
                    "max_datasets": 1,
                    "dataset_descriptions": {
                        "dataset1": "O dataset que contém a coluna a ser validada"
                    }
                },
                "validation_parameters": {
                    "column": {
                        "type": "string",
                        "description": "O nome da coluna a ser validada",
                        "required": True
                    }
                }
            }
        },
        {
            "id": "test_unique_generic",
            "display_name": "Valores não repetidos",
            "description": "Verifica se os valores em uma ou mais colunas combinadas não se repetem.",
            "parameters": {
                "dataset_parameters": {
                    "min_datasets": 1,
                    "max_datasets": 1,
                    "dataset_descriptions": {
                        "dataset1": "O dataset que contém a coluna a ser validada"
                    }
                },
                "validation_parameters": {
                    "columns": {
                        "type": "array",
                        "min_items": 2,
                        "items": {
                            "type": "string",
                            "description": "Nome da coluna do dataset ?"
                        },
                        "description": "Lista de colunas que, combinadas, devem ter valores únicos",
                        "required": True
                    }
                }
            }
        },
        {
            "id": "test_length_max",
            "display_name": "Comprimento máximo",
            "description": "Verifica se os valores em uma coluna não excedem um comprimento máximo especificado.",
            "parameters": {
                "dataset_parameters": {
                    "min_datasets": 1,
                    "max_datasets": 1,
                    "dataset_descriptions": {
                        "dataset1": "O dataset que contém a coluna a ser validada"
                    }
                },
                "validation_parameters": {
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
            }
        },
        {
            "id": "test_length_min",
            "display_name": "Comprimento mínimo",
            "description": "Verifica se os valores em uma coluna têm pelo menos um comprimento mínimo especificado.",
            "parameters": {
                "dataset_parameters": {
                    "min_datasets": 1,
                    "max_datasets": 1,
                    "dataset_descriptions": {
                        "dataset1": "O dataset que contém a coluna a ser validada"
                    }
                },
                "validation_parameters": {
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
            }
        },
        {
            "id": "test_length_exact",
            "display_name": "Comprimento exato",
            "description": "Verifica se os valores em uma coluna têm um comprimento exato especificado.",
            "parameters": {
                "dataset_parameters": {
                    "min_datasets": 1,
                    "max_datasets": 1,
                    "dataset_descriptions": {
                        "dataset1": "O dataset que contém a coluna a ser validada"
                    }
                },
                "validation_parameters": {
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
            }
        },
        {
            "id": "test_possible_values",
            "display_name": "Valores permitidos",
            "description": "Verifica se os valores em uma coluna estão dentro de um conjunto permitido de valores.",
            "parameters": {
                "dataset_parameters": {
                    "min_datasets": 1,
                    "max_datasets": 1,
                    "dataset_descriptions": {
                        "dataset1": "O dataset que contém a coluna a ser validada"
                    }
                },
                "validation_parameters": {
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
            }
        },
        {
            "id": "test_percentage_max_decimal_places",
            "display_name": "Porcentagem - Máximo de casas decimais",
            "description": "Verifica se os valores em uma coluna de porcentagens têm no máximo um número específico de casas decimais.",
            "parameters": {
                "dataset_parameters": {
                    "min_datasets": 1,
                    "max_datasets": 1,
                    "dataset_descriptions": {
                        "dataset1": "O dataset que contém a coluna a ser validada"
                    }
                },
                "validation_parameters": {
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
            }
        },
        {
            "id": "test_domains_numeric",
            "display_name": "Domínios numéricos",
            "description": "Verifica se os valores em uma coluna numérica estão dentro de um intervalo permitido (ex: entre 0 e 100 para porcentagens).",
            "parameters": {
                "dataset_parameters": {
                    "min_datasets": 1,
                    "max_datasets": 1,
                    "dataset_descriptions": {
                        "dataset1": "O dataset que contém a coluna a ser validada"
                    }
                },
                "validation_parameters": {
                    "column": {
                        "type": "string",
                        "description": "O nome da coluna a ser validada",
                        "required": True
                    },
                    "min_value": {
                        "type": "numeric",
                        "description": "O valor mínimo permitido",
                        "required": False
                    },
                    "max_value": {
                        "type": "numeric",
                        "description": "O valor máximo permitido",
                        "required": False
                    }
                }
            }
        },
        {
            "id": "test_one_to_one_columns",
            "display_name": "Colunas 1-para-1",
            "description": "Verifica se há uma relação 1-para-1 entre os valores de duas colunas (ex: cada valor em 'ID' corresponde a exatamente um valor em 'Email' e vice-versa).",
            "parameters": {
                "dataset_parameters": {
                    "min_datasets": 1,
                    "max_datasets": 1,
                    "dataset_descriptions": {
                        "dataset1": "O dataset que contém as colunas a serem validadas"
                    }
                },
                "validation_parameters": {
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
        },
        {
            "id": "test_boundaries_extended_table_coherence",
            "display_name": "Coerência entre tabela base e tabela estendida",
            "description": "Verifica se os valores de uma coluna em uma tabela base estão coerentes com os valores de uma coluna em uma tabela estendida, garantindo que não haja valores na tabela estendida que não existam na tabela base.",
            "parameters": {
                "dataset_parameters": {
                    "min_datasets": 2,
                    "max_datasets": 2,
                    "dataset_descriptions": {
                        "dataset1": "A tabela base que contém a coluna de referência",
                        "dataset2": "A tabela estendida que contém a coluna a ser validada em relação à a tabela base"
                    }
                },
                "validation_parameters": {
                    "base_column": {
                        "type": "string",
                        "description": "O nome da coluna na tabela base que serve como referência",
                        "required": True
                    },
                    "extended_column": {
                        "type": "string",
                        "description": "O nome da coluna na tabela estendida que deve ser validada em relação à coluna da tabela base",
                        "required": True
                    }
                }
            }
        },
        {
            "id": "test_domains_only_one_value_across_datasets",
            "display_name": "Somente um valor entre datasets",
            "description": "Valida que o primeiro dataset contêm somente um valor na coluna de referência, e todos os datasets a seguir contêm apenas esse valor nas colunas especificadas.",
            "parameters": {
                "dataset_parameters": {
                    "min_datasets": 2,
                    "max_datasets": None,
                    "dataset_descriptions": {
                        "dataset1": "A tabela base que contém a coluna de referência",
                        "dataset?": "A tabela estendida que contém a coluna a ser validada em relação à tabela base"
                    }
                },
                "validation_parameters": {
                    "base_column": {
                        "type": "string",
                        "description": "O nome da coluna na tabela base que serve como referência",
                        "required": True
                    },
                    "extended_columns": {
                        "type": "array",
                        "min_items": 1,
                        "description": "Lista de colunas estendidas, uma por tabela adicional",
                        "items": {
                            "type": "string",
                            "description": "Nome da coluna na tabela estendida correspondente"
                        },
                        "required": True
                    }
                }
            }
        },
        {
            "id": "test_format_no_leading_whitespace",
            "display_name": "Sem espaço no início dos valores",
            "description": "Verifica se os valores em uma coluna específica não começam com um espaço vazio",
            "parameters": {
                "dataset_parameters": {
                    "min_datasets": 1,
                    "max_datasets": 1,
                    "dataset_descriptions": {
                        "dataset1": "O dataset que contém a coluna a ser validada"
                    }
                },
                "validation_parameters": {
                    "column": {
                        "type": "string",
                        "description": "O nome da coluna a ser validada",
                        "required": True
                    }
                }
            }
        },
        {
            "id": "test_domains_not_zero",
            "display_name": "Nenhum valor igual a zero",
            "description": "Verifica se nenhum dos valores em uma coluna específica é igual a zero",
            "parameters": {
                "dataset_parameters": {
                    "min_datasets": 1,
                    "max_datasets": 1,
                    "dataset_descriptions": {
                        "dataset1": "O dataset que contém a coluna a ser validada"
                    }
                },
                "validation_parameters": {
                    "column": {
                        "type": "string",
                        "description": "O nome da coluna a ser validada",
                        "required": True
                    }
                }
            }
        },
        {
            "id": "test_boundaries_not_all_values_the_same",
            "display_name": "Mais de um valor na coluna",
            "description": "Verifica se existe mais de um valor distinto na coluna, e falha caso seja somente um",
            "parameters": {
                "dataset_parameters": {
                    "min_datasets": 1,
                    "max_datasets": 1,
                    "dataset_descriptions": {
                        "dataset1": "O dataset que contém a coluna a ser validada"
                    }
                },
                "validation_parameters": {
                    "column": {
                        "type": "string",
                        "description": "O nome da coluna a ser validada",
                        "required": True
                    }
                }
            }
        },
        {
            "id": "test_boundaries_sum_equals",
            "display_name": "Soma dos valores igual a um valor específico",
            "description": "Verifica se a soma dos valores em uma coluna numérica é igual a um valor específico, o que pode ser útil para validar distribuições de porcentagens ou proporções.",
            "parameters": {
                "dataset_parameters": {
                    "min_datasets": 1,
                    "max_datasets": 1,
                    "dataset_descriptions": {
                        "dataset1": "O dataset que contém a coluna a ser validada"
                    }
                },
                "validation_parameters": {
                    "column": {
                        "type": "string",
                        "description": "O nome da coluna a ser validada",
                        "required": True
                    },
                    "value": {
                        "type": "numeric",
                        "description": "O valor específico que a soma dos valores na coluna deve igualar",
                        "required": True
                    }
                }
            }
        }
    ]
}