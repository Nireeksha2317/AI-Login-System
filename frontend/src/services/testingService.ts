const API_BASE_URL = "http://127.0.0.1:8000";


// =========================================================
// TYPES
// =========================================================

export interface TestSummary {
  baseline_scenarios: number;
  baseline_total: number;
  baseline_passed: number;
  baseline_failed: number;

  ai_scenarios_generated: number;
  ai_executable: number;
  coverage_gaps: number;
  unmapped_scenarios: number;

  ai_total_executed: number;
  ai_passed: number;
  ai_failed: number;
  ai_errors: number;
  ai_not_executed: number;
}

export interface ExecutiveSummary {
  final_status: string;
  summary: string;
}

export interface ReportMetadata {
  project: string;
  report_type: string;
  generated_at: string;
  ai_provider: string;
  ai_model: string;
}

export interface AIExecutionResult {
  name?: string;
  status?: string;
  actual_status?: number | string;
  expected_status?: number | string;
  reason?: string;
}

export interface AIExecution {
  summary: {
    total: number;
    passed: number;
    failed: number;
    errors: number;
    not_executed: number;
  };
  results: AIExecutionResult[];
}

export interface CoverageGap {
  name?: string;
  objective?: string;
  priority?: string;
  category?: string;
  execution_status?: string;
  reason?: string;
}

export interface TestingReport {
  report_metadata: ReportMetadata;

  executive_summary: ExecutiveSummary;

  test_summary: TestSummary;

  ai_analysis: {
    provider: string;
    model: string;
    analysis: string;
  };

  baseline_results: {
    status: string;
    total: number;
    passed: number;
    failed: number;
    return_code: number;
    recommendation: string;
  };

  ai_execution: AIExecution;

  approved_ai_scenarios: CoverageGap[];

  coverage_gaps: CoverageGap[];

  unmapped_scenarios: CoverageGap[];

  recommendations: string[];
}


// =========================================================
// RESPONSE PARSER
// =========================================================

async function parseResponse<T>(
  response: Response,
): Promise<T> {

  const data = await response.json();

  if (!response.ok) {

    throw new Error(
      data.detail ||
      "Testing request failed.",
    );
  }

  return data as T;
}


// =========================================================
// GET LATEST REPORT
// =========================================================

export async function getLatestTestingReport():
  Promise<TestingReport> {

  const response = await fetch(
    `${API_BASE_URL}/testing/report`,
  );

  return parseResponse<TestingReport>(
    response,
  );
}


// =========================================================
// RUN AI TESTING
// =========================================================

export async function runAITests():
  Promise<TestingReport> {

  const response = await fetch(
    `${API_BASE_URL}/testing/run`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    },
  );

  const data = await parseResponse<{
    status: string;
    message: string;
    report: TestingReport;
  }>(response);

  return data.report;
}