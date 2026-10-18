from copy import deepcopy
from app.services.scenario_service import construir_snapshot_base
from time import perf_counter_ns

from sqlalchemy.orm import Session

from app.db_models import (
    Execution,
    ResultVariable,
)

from app.schemas.optimization import (
    ExecutionHistoryItem,
    SolveResponse,
)

from motor import (
    SimplexDuasFases,
    VERSION,
)


def resolver_problem(
    db: Session,
    problem,
):

    variables = sorted(
        problem.variables,
        key=lambda item: item.id,
    )

    index = {

        variable.id: position

        for position, variable
        in enumerate(
            variables
        )
    }


    # ========================================================
    # FUNÇÃO OBJETIVO
    # ========================================================

    c = [

        variable.objective_coefficient

        for variable
        in variables
    ]


    A = []

    b = []

    operadores = []


    # ========================================================
    # RESTRIÇÕES DO USUÁRIO
    # ========================================================

    for constraint in problem.constraints:

        row = [
            0.0
        ] * len(
            variables
        )

        for item in constraint.coefficients:

            position = index[
                item.variable_id
            ]

            row[position] = (
                item.coefficient
            )

        A.append(
            row
        )

        b.append(
            constraint.rhs
        )

        operadores.append(
            constraint.operator
        )


    # ========================================================
    # LIMITES DAS VARIÁVEIS
    # ========================================================

    for position, variable in enumerate(
        variables
    ):

        if variable.lower_bound > 0:

            row = [
                0.0
            ] * len(
                variables
            )

            row[position] = 1.0

            A.append(
                row
            )

            b.append(
                variable.lower_bound
            )

            operadores.append(
                ">="
            )


        if variable.upper_bound is not None:

            row = [
                0.0
            ] * len(
                variables
            )

            row[position] = 1.0

            A.append(
                row
            )

            b.append(
                variable.upper_bound
            )

            operadores.append(
                "<="
            )


    solver = SimplexDuasFases()


    inicio = perf_counter_ns()


    resultado = solver.resolver(
        A=A,
        b=b,
        c=c,
        operadores=operadores,
        objetivo=problem.objective_type,
    )


    fim = perf_counter_ns()


    duration_ms = (
        fim - inicio
    ) / 1_000_000.0


    # ========================================================
    # SALVA EXECUÇÃO
    # ========================================================

    execution = Execution(
        problem_id=problem.id,
        status=resultado.status,
        objective_value=(
            resultado.valor_objetivo
        ),
        iterations_phase1=(
            resultado.iteracoes_fase1
        ),
        iterations_phase2=(
            resultado.iteracoes_fase2
        ),
        duration_ms=duration_ms,
        solver_version=VERSION,
    )


    db.add(execution)

    db.flush()


    variable_results = []


    if (
        resultado.status == "optimal"
        and
        resultado.x is not None
    ):

        for variable, value in zip(
            variables,
            resultado.x,
        ):

            item = ResultVariable(
                execution_id=execution.id,
                variable_id=variable.id,
                value=float(value),
            )

            db.add(item)

            variable_results.append(

                {
                    "variable_id":
                        variable.id,

                    "variable_name":
                        variable.name,

                    "value":
                        float(value),
                }
            )


    execution.analysis_snapshot = {
        "model": construir_snapshot_base(problem),
        "values": {item["variable_name"]: item["value"] for item in variable_results},
    }

    db.commit()

    db.refresh(
        execution
    )


    return SolveResponse(

        execution_id=execution.id,

        problem_id=problem.id,

        status=resultado.status,

        objective_value=(
            resultado.valor_objetivo
        ),

        iterations_phase1=(
            resultado.iteracoes_fase1
        ),

        iterations_phase2=(
            resultado.iteracoes_fase2
        ),

        duration_ms=duration_ms,

        solver_version=VERSION,

        variables=variable_results,
    )

def serializar_execution(
    execution,
):

    from app.services.execution_context import execution_context

    return ExecutionHistoryItem(
        **execution_context(execution),

        execution_id=execution.id,

        problem_id=execution.problem_id,

        status=execution.status,

        objective_value=(
            execution.objective_value
        ),

        iterations_phase1=(
            execution.iterations_phase1
        ),

        iterations_phase2=(
            execution.iterations_phase2
        ),

        duration_ms=(
            execution.duration_ms
        ),

        solver_version=(
            execution.solver_version
        ),

        created_at=(
            execution.created_at
        ),

        variables=[
            {
                "variable_id":
                    result.variable_id,

                "variable_name":
                    result.variable.name,

                "value":
                    result.value,
            }

            for result
            in execution.variable_results
        ],
    )

def snapshot_para_modelo(
    snapshot: dict,
):

    variables = (
        snapshot["variables"]
    )

    constraints = (
        snapshot["constraints"]
    )

    variable_index = {

        item["name"]: index

        for index, item
        in enumerate(
            variables
        )
    }

    c = [

        item[
            "objective_coefficient"
        ]

        for item
        in variables
    ]

    A = []

    b = []

    operadores = []

    for constraint in constraints:

        row = [
            0.0
        ] * len(
            variables
        )

        for (
            variable_name,
            coefficient
        ) in (
            constraint[
                "coefficients"
            ].items()
        ):

            position = (
                variable_index[
                    variable_name
                ]
            )

            row[position] = coefficient

        A.append(
            row
        )

        b.append(
            constraint["rhs"]
        )

        operadores.append(
            constraint["operator"]
        )

    # ========================================================
    # LIMITES DAS VARIÁVEIS
    # ========================================================

    for (
        position,
        variable
    ) in enumerate(
        variables
    ):

        lower_bound = (
            variable.get(
                "lower_bound",
                0.0
            )
        )

        upper_bound = (
            variable.get(
                "upper_bound"
            )
        )

        if (
            lower_bound is not None
            and
            lower_bound > 0
        ):

            row = [
                0.0
            ] * len(
                variables
            )

            row[position] = 1.0

            A.append(
                row
            )

            b.append(
                lower_bound
            )

            operadores.append(
                ">="
            )

        if (
            upper_bound
            is not None
        ):

            row = [
                0.0
            ] * len(
                variables
            )

            row[position] = 1.0

            A.append(
                row
            )

            b.append(
                upper_bound
            )

            operadores.append(
                "<="
            )

    return {

        "variable_names": [
            item["name"]
            for item
            in variables
        ],

        "c":
            c,

        "A":
            A,

        "b":
            b,

        "operadores":
            operadores,

        "objetivo":
            snapshot[
                "objective_type"
            ],
    }

def resolver_scenario(
    db: Session,
    scenario,
):

    modelo = snapshot_para_modelo(
        scenario.model_snapshot
    )

    solver = SimplexDuasFases()

    inicio = perf_counter_ns()

    resultado = solver.resolver(

        A=modelo["A"],

        b=modelo["b"],

        c=modelo["c"],

        operadores=(
            modelo["operadores"]
        ),

        objetivo=(
            modelo["objetivo"]
        ),
    )

    fim = perf_counter_ns()

    duration_ms = (
        fim - inicio
    ) / 1_000_000.0

    execution = Execution(

        problem_id=scenario.problem_id,

        scenario_id=scenario.id,

        status=resultado.status,

        objective_value=(
            resultado.valor_objetivo
        ),

        iterations_phase1=(
            resultado.iteracoes_fase1
        ),

        iterations_phase2=(
            resultado.iteracoes_fase2
        ),

        duration_ms=duration_ms,

        solver_version=VERSION,
    )

    db.add(
        execution
    )

    db.flush()

    variable_results = []

    # Precisamos localizar as variáveis reais
    # do problema pelo nome.

    problem_variables = {

        variable.name:
            variable

        for variable
        in scenario.problem.variables
    }

    if (
        resultado.status == "optimal"
        and
        resultado.x is not None
    ):

        for (
            variable_name,
            value
        ) in zip(

            modelo[
                "variable_names"
            ],

            resultado.x
        ):

            variable = (
                problem_variables[
                    variable_name
                ]
            )

            item = ResultVariable(

                execution_id=(
                    execution.id
                ),

                variable_id=(
                    variable.id
                ),

                value=float(
                    value
                ),
            )

            db.add(
                item
            )

            variable_results.append({

                "variable_id":
                    variable.id,

                "variable_name":
                    variable_name,

                "value":
                    float(value),
            })

    execution.analysis_snapshot = {
        "model": deepcopy(scenario.model_snapshot),
        "values": {item["variable_name"]: item["value"] for item in variable_results},
    }

    db.commit()

    db.refresh(
        execution
    )

    return SolveResponse(

        execution_id=(
            execution.id
        ),

        problem_id=(
            scenario.problem_id
        ),

        status=(
            resultado.status
        ),

        objective_value=(
            resultado.valor_objetivo
        ),

        iterations_phase1=(
            resultado.iteracoes_fase1
        ),

        iterations_phase2=(
            resultado.iteracoes_fase2
        ),

        duration_ms=duration_ms,

        solver_version=VERSION,

        variables=(
            variable_results
        ),
    )