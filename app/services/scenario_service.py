from copy import deepcopy

from sqlalchemy.orm import Session

from app.repositories.problem_repository import (
    get_problem,
)

from app.repositories.scenario_repository import (
    create_scenario,
)

from app.schemas.scenario import ScenarioCreate

from app.db_models import (
    Execution,
    ResultVariable,
    Scenario
)

def construir_snapshot_base(
    problem,
):

    variables = sorted(
        problem.variables,
        key=lambda item: item.id,
    )

    constraints = sorted(
        problem.constraints,
        key=lambda item: item.id,
    )

    snapshot = {

        "objective_type":
            problem.objective_type,

        "variables": [],

        "constraints": [],
    }

    for variable in variables:

        snapshot["variables"].append({

            "name":
                variable.name,

            "objective_coefficient":
                variable.objective_coefficient,

            "lower_bound":
                variable.lower_bound,

            "upper_bound":
                variable.upper_bound,
        })

    for constraint in constraints:

        coefficients = {}

        for item in constraint.coefficients:

            coefficients[
                item.variable.name
            ] = item.coefficient

        snapshot["constraints"].append({

            "name":
                constraint.name,

            "operator":
                constraint.operator,

            "rhs":
                constraint.rhs,

            "coefficients":
                coefficients,
        })

    return snapshot

def aplicar_overrides(
    snapshot: dict,
    data: ScenarioCreate,
):

    result = deepcopy(
        snapshot
    )

    variables = {

        item["name"]:
            item

        for item
        in result["variables"]
    }

    constraints = {

        item["name"]:
            item

        for item
        in result["constraints"]
    }

    # ========================================================
    # VARIÁVEIS
    # ========================================================

    for override in data.variable_overrides:

        if (
            override.variable_name
            not in variables
        ):

            raise ValueError(
                "Variável desconhecida no cenário: "
                f"{override.variable_name}"
            )

        variable = variables[
            override.variable_name
        ]

        if (
            override.objective_coefficient
            is not None
        ):

            variable[
                "objective_coefficient"
            ] = override.objective_coefficient

        if (
            override.lower_bound
            is not None
        ):

            variable[
                "lower_bound"
            ] = override.lower_bound

        if (
            override.upper_bound
            is not None
        ):

            variable[
                "upper_bound"
            ] = override.upper_bound

    # ========================================================
    # RESTRIÇÕES
    # ========================================================

    for override in data.constraint_overrides:

        if (
            override.constraint_name
            not in constraints
        ):

            raise ValueError(
                "Restrição desconhecida no cenário: "
                f"{override.constraint_name}"
            )

        constraint = constraints[
            override.constraint_name
        ]

        if override.rhs is not None:

            constraint["rhs"] = (
                override.rhs
            )

        if (
            override.operator
            is not None
        ):

            if override.operator not in (
                "<=",
                ">=",
                "=",
            ):

                raise ValueError(
                    "Operador inválido."
                )

            constraint["operator"] = (
                override.operator
            )

        if (
            override.coefficients
            is not None
        ):

            for (
                variable_name,
                coefficient
            ) in (
                override
                .coefficients
                .items()
            ):

                if (
                    variable_name
                    not in variables
                ):

                    raise ValueError(
                        "Variável desconhecida "
                        "no coeficiente: "
                        f"{variable_name}"
                    )

                constraint[
                    "coefficients"
                ][
                    variable_name
                ] = coefficient

    return result

def cadastrar_scenario(
    db: Session,
    problem_id: int,
    data: ScenarioCreate,
):

    problem = get_problem(
        db,
        problem_id,
    )

    if problem is None:

        raise LookupError(
            "Problema não encontrado."
        )

    if data.source_execution_id is not None:
        from app.services.execution_context import stored_model
        source = db.get(Execution, data.source_execution_id)
        if source is None or source.problem_id != problem_id:
            raise LookupError("Execução não encontrada neste problema.")
        base = stored_model(source)
    else:
        base = construir_snapshot_base(problem)

    snapshot = aplicar_overrides(
        base,
        data,
    )

    return create_scenario(

        db=db,

        problem_id=problem_id,

        name=data.name,

        description=data.description,

        model_snapshot=snapshot,
    )

def obter_ultima_execucao(
    scenario,
):

    if not scenario.executions:

        return None

    return max(
        scenario.executions,
        key=lambda item:
            item.created_at
    )

def list_scenarios(
    db: Session,
    problem_id: int,
):

    statement = (
        select(Scenario)
        .where(
            Scenario.problem_id
            ==
            problem_id
        )
        .options(
            selectinload(
                Scenario.executions
            )
            .selectinload(
                Execution.variable_results
            )
            .selectinload(
                ResultVariable.variable
            )
        )
        .order_by(
            Scenario.created_at.asc()
        )
    )

    return list(
        db.scalars(
            statement
        ).all()
    )