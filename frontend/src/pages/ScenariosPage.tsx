import { parseCoefficients } from "../components/constraintCoefficients";
import MetadataActions from "../components/MetadataActions";
import ResourcePanel from "../components/ResourceAnalysis";
import {
  useEffect,
  useState,
} from "react";

import {
  Link,
  useParams,
} from "react-router-dom";

import {
  getProblem,
} from "../api/problems";

import {
  createScenario,
  getScenarios,
  solveScenario,
} from "../api/scenarios";

import type {
  Problem,
} from "../types/problem";

import type {
  Scenario,
  ScenarioCreate,
} from "../types/scenario";

import type {
  SolveResult,
} from "../types/optimization";


interface VariableForm {
  enabled: boolean;

  objectiveCoefficient:
    string;

  lowerBound:
    string;

  upperBound:
    string;
}


interface ConstraintForm {
  coefficients: Record<string, string>;
  enabled: boolean;

  rhs: string;

  operator:
    "<="
    | ">="
    | "=";
}


export default function ScenariosPage() {

  const {
    problemId,
  } = useParams();


  const id =
    Number(problemId);


  const [
    problem,
    setProblem,
  ] = useState<
    Problem | null
  >(null);


  const [
    scenarios,
    setScenarios,
  ] = useState<
    Scenario[]
  >([]);


  const [
    name,
    setName,
  ] = useState("");


  const [
    description,
    setDescription,
  ] = useState("");


  const [
    variableForms,
    setVariableForms,
  ] = useState<
    Record<
      string,
      VariableForm
    >
  >({});


  const [
    constraintForms,
    setConstraintForms,
  ] = useState<
    Record<
      string,
      ConstraintForm
    >
  >({});


  const [
    results,
    setResults,
  ] = useState<
    Record<
      number,
      SolveResult
    >
  >({});


  const [
    error,
    setError,
  ] = useState<
    string | null
  >(null);


  const [
    saving,
    setSaving,
  ] = useState(false);


  // ========================================================
  // CARREGAMENTO
  // ========================================================

  async function loadData() {

    try {

      setError(null);

      const [
        problemData,
        scenarioData,
      ] = await Promise.all([

        getProblem(id),

        getScenarios(id),
      ]);


      setProblem(
        problemData
      );


      setScenarios(
        scenarioData
      );


      const variables:
        Record<
          string,
          VariableForm
        > = {};


      for (
        const variable
        of problemData.variables
      ) {

        variables[
          variable.name
        ] = {

          enabled:
            false,

          objectiveCoefficient:
            String(
              variable
                .objective_coefficient
            ),

          lowerBound:
            String(
              variable
                .lower_bound
            ),

          upperBound:
            variable
              .upper_bound
              ===
              null
                ?
              ""
                :
              String(
                variable
                  .upper_bound
              ),
        };
      }


      setVariableForms(
        variables
      );


      const constraints:
        Record<
          string,
          ConstraintForm
        > = {};


      for (
        const constraint
        of problemData.constraints
      ) {

        constraints[
          constraint.name
        ] = {

          enabled:
            false,

          rhs:
            String(
              constraint.rhs
            ),

          operator:
            constraint.operator,
          coefficients: Object.fromEntries(problemData.variables.map(variable => [variable.name, String(constraint.terms.find(term => term.variable_name === variable.name)?.coefficient ?? 0)])),
        };
      }


      setConstraintForms(
        constraints
      );


    } catch (error) {

      if (
        error instanceof Error
      ) {

        setError(
          error.message
        );

      } else {

        setError(
          "Erro ao carregar cenários."
        );
      }
    }
  }


  useEffect(() => {

    if (
      Number.isInteger(id)
      &&
      id > 0
    ) {

      loadData();
    }

  }, [id]);


  // ========================================================
  // VARIÁVEIS
  // ========================================================

  function updateVariable(
    variableName: string,
    field:
      keyof VariableForm,
    value:
      string | boolean
  ) {

    setVariableForms(
      (previous) => ({

        ...previous,

        [variableName]: {

          ...previous[
            variableName
          ],

          [field]:
            value,
        },
      })
    );
  }


  // ========================================================
  // RESTRIÇÕES
  // ========================================================

  function updateConstraint(
    constraintName: string,
    field:
      keyof ConstraintForm,
    value:
      string | boolean
  ) {

    setConstraintForms(
      (previous) => ({

        ...previous,

        [constraintName]: {

          ...previous[
            constraintName
          ],

          [field]:
            value,
        },
      })
    );
  }


  // ========================================================
  // CRIAÇÃO DO PAYLOAD
  // ========================================================

  function buildPayload():
    ScenarioCreate {

    if (!problem) {

      throw new Error(
        "Problema não carregado."
      );
    }


    const variableOverrides =
      problem.variables
        .filter(
          (variable) =>
            variableForms[
              variable.name
            ]?.enabled
        )
        .map(
          (variable) => {

            const form =
              variableForms[
                variable.name
              ];


            return {

              variable_name:
                variable.name,

              objective_coefficient:
                Number(
                  form
                    .objectiveCoefficient
                ),

              lower_bound:
                Number(
                  form
                    .lowerBound
                ),

              upper_bound:
                form
                  .upperBound
                  .trim()
                  ===
                ""
                  ?
                null
                  :
                Number(
                  form
                    .upperBound
                ),
            };
          }
        );


    const constraintOverrides =
      problem.constraints
        .filter(
          (constraint) =>
            constraintForms[
              constraint.name
            ]?.enabled
        )
        .map(
          (constraint) => {

            const form =
              constraintForms[
                constraint.name
              ];


            return {

              constraint_name:
                constraint.name,

              rhs:
                Number(
                  form.rhs
                ),

              operator:
                form.operator,
              coefficients: parseCoefficients(form.coefficients, constraint.name),
            };
          }
        );


    return {

      name:
        name.trim(),

      description:
        description
          .trim()
          ||
        null,

      variable_overrides:
        variableOverrides,

      constraint_overrides:
        constraintOverrides,
    };
  }


  // ========================================================
  // CRIAR CENÁRIO
  // ========================================================

  async function handleCreate() {

    if (!name.trim()) {

      setError(
        "Informe o nome do cenário."
      );

      return;
    }


    try {

      setSaving(true);

      setError(null);


      const payload =
        buildPayload();


      await createScenario(
        id,
        payload
      );


      setName("");

      setDescription("");


      await loadData();


    } catch (error) {

      if (
        error instanceof Error
      ) {

        setError(
          error.message
        );

      } else {

        setError(
          "Erro ao criar cenário."
        );
      }


    } finally {

      setSaving(false);
    }
  }


  // ========================================================
  // RESOLVER
  // ========================================================

  async function handleSolve(
    scenarioId: number
  ) {

    try {

      setError(null);


      const result =
        await solveScenario(
          scenarioId
        );


      setResults(
        (previous) => ({

          ...previous,

          [scenarioId]:
            result,
        })
      );


    } catch (error) {

      if (
        error instanceof Error
      ) {

        setError(
          error.message
        );
      }
    }
  }


  // ========================================================
  // RENDER
  // ========================================================

  if (!problem) {

    return (
      <main>

        {
          error
            ?
          <p>{error}</p>
            :
          <p>
            Carregando...
          </p>
        }

      </main>
    );
  }


  return (

    <main>

      <Link to={`/problems/${id}/executions`}>Histórico de execuções</Link>
      <h1>
        Cenários
      </h1>


      <p>
        Problema:
        {" "}
        <strong>
          {problem.name}
        </strong>
      </p>


      <nav>

        <Link
          to={
            `/problems/${id}`
          }
        >
          Voltar ao problema
        </Link>

        {" | "}

        <Link
          to={
            `/problems/${id}/comparison`
          }
        >
          Comparar cenários
        </Link>

      </nav>


      <hr />


      <section>

        <h2>
          Novo cenário
        </h2>


        <label>

          Nome

          <input
            value={name}
            onChange={
              (event) =>
                setName(
                  event.target.value
                )
            }
          />

        </label>


        <label>

          Descrição

          <textarea
            value={
              description
            }
            onChange={
              (event) =>
                setDescription(
                  event.target.value
                )
            }
          />

        </label>


        <h3>
          Alterações nas variáveis
        </h3>


        {problem.variables.map(
          (variable) => {

            const form =
              variableForms[
                variable.name
              ];


            if (!form) {
              return null;
            }


            return (

              <div
                key={
                  variable.id
                }
              >

                <label>

                  <input
                    type="checkbox"
                    checked={
                      form.enabled
                    }
                    onChange={
                      (event) =>
                        updateVariable(
                          variable.name,
                          "enabled",
                          event
                            .target
                            .checked
                        )
                    }
                  />

                  Alterar
                  {" "}
                  {variable.name}

                </label>


                {form.enabled && (

                  <div>

                    <label>

                      Coeficiente objetivo

                      <input
                        type="number"
                        step="any"
                        value={
                          form
                            .objectiveCoefficient
                        }
                        onChange={
                          (event) =>
                            updateVariable(
                              variable.name,
                              "objectiveCoefficient",
                              event
                                .target
                                .value
                            )
                        }
                      />

                    </label>


                    <label>

                      Limite inferior

                      <input
                        type="number"
                        step="any"
                        value={
                          form
                            .lowerBound
                        }
                        onChange={
                          (event) =>
                            updateVariable(
                              variable.name,
                              "lowerBound",
                              event
                                .target
                                .value
                            )
                        }
                      />

                    </label>


                    <label>

                      Limite superior

                      <input
                        type="number"
                        step="any"
                        value={
                          form
                            .upperBound
                        }
                        onChange={
                          (event) =>
                            updateVariable(
                              variable.name,
                              "upperBound",
                              event
                                .target
                                .value
                            )
                        }
                      />

                    </label>

                  </div>
                )}

              </div>
            );
          }
        )}


        <h3>
          Alterações nas restrições
        </h3>


        {problem.constraints.map(
          (constraint) => {

            const form =
              constraintForms[
                constraint.name
              ];


            if (!form) {
              return null;
            }


            return (

              <div
                key={
                  constraint.id
                }
              >

                <label>

                  <input
                    type="checkbox"
                    checked={
                      form.enabled
                    }
                    onChange={
                      (event) =>
                        updateConstraint(
                          constraint.name,
                          "enabled",
                          event
                            .target
                            .checked
                        )
                    }
                  />

                  Alterar
                  {" "}
                  {constraint.name}

                </label>


                {form.enabled && (

                  <div>

                    <label>

                      Operador

                      <select
                        value={
                          form.operator
                        }
                        onChange={
                          (event) => {

                            const value =
                              event
                                .target
                                .value;


                            if (
                              value === "<="
                              ||
                              value === ">="
                              ||
                              value === "="
                            ) {

                              updateConstraint(
                                constraint.name,
                                "operator",
                                value
                              );
                            }
                          }
                        }
                      >

                        <option value="<=">
                          ≤
                        </option>

                        <option value=">=">
                          ≥
                        </option>

                        <option value="=">
                          =
                        </option>

                      </select>

                    </label>


                    <fieldset>
                      <legend>Coeficientes da restrição (aᵢⱼ)</legend>
                      <p>Valores usados nesta restrição para cada variável. Zero remove sua contribuição. A alteração será salva em um novo cenário.</p>
                      {problem.variables.map(variable => (
                        <label key={variable.id}>
                          {variable.name} em {constraint.name}
                          <input type="number" step="any" required
                            value={form.coefficients[variable.name] ?? "0"}
                            onChange={event => {
                              const value = event.target.value;
                              setConstraintForms(previous => ({
                                ...previous,
                                [constraint.name]: {
                                  ...previous[constraint.name],
                                  coefficients: { ...previous[constraint.name].coefficients, [variable.name]: value },
                                },
                              }));
                            }} />
                        </label>
                      ))}
                    </fieldset>

                    <label>

                      RHS

                      <input
                        type="number"
                        step="any"
                        value={
                          form.rhs
                        }
                        onChange={
                          (event) =>
                            updateConstraint(
                              constraint.name,
                              "rhs",
                              event
                                .target
                                .value
                            )
                        }
                      />

                    </label>

                  </div>
                )}

              </div>
            );
          }
        )}


        {error && (
          <p>
            {error}
          </p>
        )}


        <button
          type="button"
          disabled={
            saving
          }
          onClick={
            handleCreate
          }
        >

          {
            saving
              ?
            "Criando..."
              :
            "Criar cenário"
          }

        </button>

      </section>


      <hr />


      <section>

        <h2>
          Cenários cadastrados
        </h2>


        {
          scenarios.length === 0
            ?
          (
            <p>
              Nenhum cenário cadastrado.
            </p>
          )
            :
          scenarios.map(
            (scenario) => {

              const result =
                results[
                  scenario.id
                ];


              return (

                <article
                  key={
                    scenario.id
                  }
                >

                  <h3>
                    {scenario.name}
                  </h3>


                  <p>
                    {
                      scenario.description
                      ||
                      "Sem descrição."
                    }
                  </p>


                  <button
                    onClick={() =>
                      handleSolve(
                        scenario.id
                      )
                    }
                  >
                    Resolver cenário
                  </button>


                  {result && <Link to={`/problems/${id}/executions?execution=${result.execution_id}`}>Visualizar resultado da execução #{result.execution_id}</Link>}
                  <MetadataActions kind="scenarios" item={scenario} onChanged={() => { getScenarios(id).then(setScenarios).catch(error => setError(error.message)); }} />
                  <ResourcePanel scenarioId={scenario.id} executionId={result?.execution_id} />
                </article>
              );
            }
          )
        }

      </section>

    </main>
  );
}