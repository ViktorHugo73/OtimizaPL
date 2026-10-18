import HomePage from "./pages/HomePage";
import ProblemsPage from "./pages/ProblemsPage";
import ExecutionHistoryPage from "./pages/ExecutionHistoryPage";
import {
  BrowserRouter,
  Link,
  Route,
  Routes,
} from "react-router-dom";

import CreateProblemPage
  from "./pages/CreateProblemPage";

import ProblemPage
  from "./pages/ProblemPage";

import ScenariosPage
  from "./pages/ScenariosPage";

import ComparisonPage
  from "./pages/ComparisonPage";

function App() {

  return (

    <BrowserRouter>

      <header>

        <h1>
          OtimizaPL
        </h1>

        <nav>
          <Link to="/">Como usar?</Link>{" | "}
          <Link to="/problems">Problemas cadastrados</Link>{" | "}

          <Link
            to="/problems/new"
          >
            Novo problema
          </Link>

        </nav>

      </header>


      <Routes>
        <Route path="/problems" element={<ProblemsPage />} />
        <Route path="/problems/:problemId/executions" element={<ExecutionHistoryPage />} />

        <Route
          path="/"
          element={
            <HomePage />
          }
        />


        <Route
          path="/problems/new"
          element={
            <CreateProblemPage />
          }
        />


        <Route
          path="/problems/:problemId"
          element={
            <ProblemPage />
          }
        />

        <Route
          path="/problems/:problemId/scenarios"
          element={
            <ScenariosPage />
          }
        />

        <Route
          path="/problems/:problemId/comparison"
          element={
            <ComparisonPage />
          }
        />

      </Routes>

    </BrowserRouter>
  );
}


export default App;