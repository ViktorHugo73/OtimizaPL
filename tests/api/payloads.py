ARTIGO_V1_PAYLOAD = {

    "name":
        "Oficina de feixes - artigo v1.0",

    "description":
        "Modelo auditado utilizado "
        "na validação do sistema.",

    "objective_type":
        "min",

    "variables": [

        {
            "name":
                "XR",

            "description":
                "Feixes reformados",

            "objective_coefficient":
                450,

            "lower_bound":
                0
        },

        {
            "name":
                "XS",

            "description":
                "Feixes substituídos",

            "objective_coefficient":
                800,

            "lower_bound":
                0
        }
    ],

    "constraints": [

        {
            "name":
                "Demanda",

            "operator":
                ">=",

            "rhs":
                20,

            "terms": [

                {
                    "variable_name":
                        "XR",

                    "coefficient":
                        1
                },

                {
                    "variable_name":
                        "XS",

                    "coefficient":
                        1
                }
            ]
        },

        {
            "name":
                "Horas",

            "operator":
                "<=",

            "rhs":
                80,

            "terms": [

                {
                    "variable_name":
                        "XR",

                    "coefficient":
                        3
                },

                {
                    "variable_name":
                        "XS",

                    "coefficient":
                        1.5
                }
            ]
        },

        {
            "name":
                "Mão de obra",

            "operator":
                "<=",

            "rhs":
                40,

            "terms": [

                {
                    "variable_name":
                        "XR",

                    "coefficient":
                        2
                },

                {
                    "variable_name":
                        "XS",

                    "coefficient":
                        1
                }
            ]
        },

        {
            "name":
                "Estoque",

            "operator":
                "<=",

            "rhs":
                25,

            "terms": [

                {
                    "variable_name":
                        "XS",

                    "coefficient":
                        1
                }
            ]
        },

        {
            "name":
                "Percentual mínimo de reformas",

            "operator":
                ">=",

            "rhs":
                0,

            "terms": [

                {
                    "variable_name":
                        "XR",

                    "coefficient":
                        0.7
                },

                {
                    "variable_name":
                        "XS",

                    "coefficient":
                        -0.3
                }
            ]
        },

        {
            "name":
                "Capacidade do forno",

            "operator":
                "<=",

            "rhs":
                8,

            "terms": [

                {
                    "variable_name":
                        "XR",

                    "coefficient":
                        1
                }
            ]
        }
    ]
}