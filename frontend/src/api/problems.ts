import { apiRequest } from "./client";

import type {
  Problem,
  ProblemCreate,
} from "../types/problem";

import type {
  SolveResult,
} from "../types/optimization";


export function getProblem(
  id: number
): Promise<Problem> {
  return apiRequest<Problem>(
    `/problems/${id}`
  );
}


export function createProblem(
  data: ProblemCreate
): Promise<Problem> {
  return apiRequest<Problem>(
    "/problems",
    {
      method: "POST",
      body: JSON.stringify(data),
    }
  );
}


export function solveProblem(
  id: number
): Promise<SolveResult> {
  return apiRequest<SolveResult>(
    `/problems/${id}/solve`,
    {
      method: "POST",
    }
  );
}