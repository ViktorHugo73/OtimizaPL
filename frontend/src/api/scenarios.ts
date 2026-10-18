import {
  apiRequest,
} from "./client";

import type {
  ComparisonResponse,
  Scenario,
  ScenarioCreate,
} from "../types/scenario";

import type {
  SolveResult,
} from "../types/optimization";


export function getScenarios(
  problemId: number
): Promise<Scenario[]> {

  return apiRequest<Scenario[]>(
    `/problems/${problemId}/scenarios`
  );
}


export function createScenario(
  problemId: number,
  data: ScenarioCreate
): Promise<Scenario> {

  return apiRequest<Scenario>(
    `/problems/${problemId}/scenarios`,
    {
      method: "POST",

      body:
        JSON.stringify(data),
    }
  );
}


export function solveScenario(
  scenarioId: number
): Promise<SolveResult> {

  return apiRequest<SolveResult>(
    `/scenarios/${scenarioId}/solve`,
    {
      method: "POST",
    }
  );
}


export function compareScenarios(
  problemId: number
): Promise<ComparisonResponse> {

  return apiRequest<ComparisonResponse>(
    `/problems/${problemId}/scenarios/compare`
  );
}