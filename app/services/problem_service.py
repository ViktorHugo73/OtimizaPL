from sqlalchemy.orm import Session

from app.repositories.problem_repository import (
    create_problem,
)

from app.schemas.problem import (
    ProblemCreate,
    ProblemRead,
)


def validar_problem_create(
    data: ProblemCreate,
):

    nomes = [
        variable.name
        for variable
        in data.variables
    ]

    if len(set(nomes)) != len(nomes):

        raise ValueError(
            "Os nomes das variáveis devem ser únicos."
        )

    nomes_restricoes = [
        constraint.name
        for constraint
        in data.constraints
    ]

    if len(
        set(nomes_restricoes)
    ) != len(
        nomes_restricoes
    ):
        raise ValueError(
            "Os nomes das restrições devem ser únicos."
        )

    conjunto_variaveis = set(
        nomes
    )

    for constraint in data.constraints:

        termos = [
            term.variable_name
            for term
            in constraint.terms
        ]

        if len(termos) != len(set(termos)):

            raise ValueError(
                f"A restrição '{constraint.name}' "
                "possui variável repetida."
            )

        desconhecidas = (
            set(termos)
            -
            conjunto_variaveis
        )

        if desconhecidas:

            raise ValueError(
                "Variáveis desconhecidas na restrição "
                f"'{constraint.name}': "
                f"{sorted(desconhecidas)}"
            )


def serializar_problem(
    problem,
):

    return ProblemRead(

        id=problem.id,

        name=problem.name,

        description=problem.description,

        objective_type=(
            problem.objective_type
        ),

        variables=[

            {
                "id":
                    variable.id,

                "name":
                    variable.name,

                "description":
                    variable.description,

                "objective_coefficient":
                    variable.objective_coefficient,

                "lower_bound":
                    variable.lower_bound,

                "upper_bound":
                    variable.upper_bound,
            }

            for variable
            in problem.variables
        ],

        constraints=[

            {
                "id":
                    constraint.id,

                "name":
                    constraint.name,

                "operator":
                    constraint.operator,

                "rhs":
                    constraint.rhs,

                "terms": [

                    {
                        "variable_id":
                            item.variable_id,

                        "variable_name":
                            item.variable.name,

                        "coefficient":
                            item.coefficient,
                    }

                    for item
                    in constraint.coefficients
                ],
            }

            for constraint
            in problem.constraints
        ],
    )


def cadastrar_problem(
    db: Session,
    data: ProblemCreate,
):

    validar_problem_create(
        data
        
    )

    

    return create_problem(
        db,
        data,
    )