import {
  useEffect,
  useState,
} from "react";

import {
  getProblem,
  solveProblem,
} from "../api/problems";

import type {
  Problem,
} from "../types/problem";



import {
  Link,
  useParams,
  useNavigate,
} from "react-router-dom";

export default function ProblemPage() {
  const navigate = useNavigate();
  const [problem, setProblem] =
    useState<Problem | null>(null);

  const [error, setError] =
    useState<string | null>(null);

  const [loading, setLoading] =
    useState(false);

    const {
  problemId
} = useParams();

const id =
  Number(problemId);

  useEffect(() => {

  if (
    !Number.isInteger(id)
    ||
    id <= 0
  ) {

    setError(
      "Identificador do problema inválido."
    );

    return;
  }


  getProblem(id)
    .then(
      setProblem
    )
    .catch(
      (error) =>
        setError(
          error.message
        )
    );

}, [id]);


  async function handleSolve() {
    try {
      setLoading(true);
      setError(null);

      const response =
        await solveProblem(id);

      navigate(`/problems/${id}/executions?execution=${response.execution_id}`);

    } catch (error) {
      if (error instanceof Error) {
        setError(error.message);
      }

    } finally {
      setLoading(false);
    }
  }


  if (error) {
    return (
      <p>Erro: {error}</p>
    );
  }


  if (!problem) {
    return (
      <p>Carregando...</p>
    );
  }


  return (
    <main>
      <Link to={`/problems/${id}/executions`}>Histórico de execuções</Link>
      <h1>{problem.name}</h1>

     <nav>

        <Link
            to={
                `/problems/${id}/scenarios`
            }
        >     
            Cenários
        </Link>

     </nav>

      <p>
        Tipo:
        {" "}
        {problem.objective_type}
      </p>

      <h2>Variáveis</h2>

      <table>
        <thead>
          <tr>
            <th>Variável</th>
            <th>Coeficiente</th>
          </tr>
        </thead>

        <tbody>
          {problem.variables.map(
            (variable) => (
              <tr key={variable.id}>
                <td>{variable.name}</td>

                <td>
                  {
                    variable
                      .objective_coefficient
                  }
                </td>
              </tr>
            )
          )}
        </tbody>
      </table>

      <button
        onClick={handleSolve}
        disabled={loading}
      >
        {
          loading
            ? "Resolvendo..."
            : "Resolver"
        }
      </button>

    </main>
  );
}