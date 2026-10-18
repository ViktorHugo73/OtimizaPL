import ComparisonCharts from "../components/ComparisonCharts";
import ResourceComparison from "../components/ResourceComparison";
import {
  useEffect,
  useState,
} from "react";

import {
  Link,
  useParams,
} from "react-router-dom";

import {
  compareScenarios,
} from "../api/scenarios";

import type {
  ComparisonResponse,
} from "../types/scenario";


export default function ComparisonPage() {

  const {
    problemId,
  } = useParams();


  const id =
    Number(problemId);


  const [
    comparison,
    setComparison,
  ] = useState<
    ComparisonResponse | null
  >(null);


  const [
    error,
    setError,
  ] = useState<
    string | null
  >(null);


  useEffect(() => {

    if (
      !Number.isInteger(id)
      ||
      id <= 0
    ) {

      setError(
        "Problema inválido."
      );

      return;
    }


    compareScenarios(id)
      .then(
        setComparison
      )
      .catch(
        (error) => {

          if (
            error instanceof Error
          ) {

            setError(
              error.message
            );
          }
        }
      );

  }, [id]);


  if (error) {

    return (
      <main>
        <p>{error}</p>
      </main>
    );
  }


  if (!comparison) {

    return (
      <main>
        <p>
          Carregando comparação...
        </p>
      </main>
    );
  }


  return (

    <main>

      <Link to={`/problems/${id}/executions`}>Histórico de execuções</Link>
      <h1>
        Comparação de cenários
      </h1>


      <Link
        to={
          `/problems/${id}/scenarios`
        }
      >
        Voltar aos cenários
      </Link>


      {
        comparison
          .scenarios
          .length
        === 0
          ?
        (
          <p>
            Nenhum cenário resolvido.
          </p>
        )
          :
        (
          <table>

            <thead>

              <tr>

                <th>
                  Cenário
                </th>

                <th>
                  Status
                </th>

                <th>
                  Função objetivo
                </th>

                {
                  Object.keys(
                    comparison
                      .scenarios[0]
                      .variables
                  ).map(
                    (name) => (

                      <th key={name}>
                        {name}
                      </th>
                    )
                  )
                }

              </tr>

            </thead>


            <tbody>

              {
                comparison
                  .scenarios
                  .map(
                    (scenario) => (

                      <tr
                        key={
                          scenario
                            .scenario_id
                        }
                      >

                        <td>
                          {
                            scenario
                              .scenario_name
                          }
                        </td>


                        <td>
                          {
                            scenario.status
                          }
                        </td>


                        <td>
                          {
                            scenario
                              .objective_value
                          }
                        </td>


                        {
                          Object.values(
                            scenario.variables
                          ).map(
                            (
                              value,
                              index
                            ) => (

                              <td
                                key={
                                  index
                                }
                              >
                                {value}
                              </td>
                            )
                          )
                        }

                      </tr>
                    )
                  )
              }

            </tbody>

          </table>
        )
      }

      <ComparisonCharts key={`${id}-${comparison.scenarios.map(s => s.execution_id).join("-")}`} scenarios={comparison.scenarios} />
      <ResourceComparison key={id} problemId={id} scenarios={comparison.scenarios} />
    </main>
  );
}