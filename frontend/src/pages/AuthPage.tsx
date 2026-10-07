import { useEffect, useState, type FormEvent } from "react";
import "./AuthPage.css";

import {
  login,
  signup,
  type LoginData,
  type SignupData,
} from "../services/authService";

import {
  getLatestTestingReport,
  runAITests,
  type TestingReport,
} from "../services/testingService";

type AuthMode = "signin" | "signup";

const TESTING_REPORT_HTML_URL =
  "http://127.0.0.1:8000/testing/report/html";

const passwordRequirements = [
  {
    key: "length",
    label: "At least 8 characters",
    check: (value: string) => value.length >= 8,
  },
  {
    key: "lowercase",
    label: "Lowercase letter",
    check: (value: string) => /[a-z]/.test(value),
  },
  {
    key: "uppercase",
    label: "Uppercase letter",
    check: (value: string) => /[A-Z]/.test(value),
  },
  {
    key: "number",
    label: "Number",
    check: (value: string) => /\d/.test(value),
  },
  {
    key: "special",
    label: "Special character",
    check: (value: string) => /[^A-Za-z0-9]/.test(value),
  },
];

function AuthPage() {
  // ==========================================================================
  // AUTH STATE
  // ==========================================================================

  const [mode, setMode] = useState<AuthMode>("signin");

  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const [rememberMe, setRememberMe] = useState(false);

  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  // ==========================================================================
  // AI TESTING STATE
  // ==========================================================================

  const [testingReport, setTestingReport] =
    useState<TestingReport | null>(null);

  const [testingLoading, setTestingLoading] = useState(false);
  const [testingError, setTestingError] = useState("");

  // Expandable dashboard sections
  const [showAIAnalysis, setShowAIAnalysis] = useState(false);
  const [showCoverageGaps, setShowCoverageGaps] = useState(false);
  const [showUnmapped, setShowUnmapped] = useState(false);

  // ==========================================================================
  // LOAD LATEST TESTING REPORT
  // ==========================================================================

  useEffect(() => {
    const loadLatestReport = async () => {
      try {
        const report = await getLatestTestingReport();

        setTestingReport(report);
        setTestingError("");
      } catch {
        // No report is normal before the agent runs for the first time.
        setTestingReport(null);
      }
    };

    loadLatestReport();
  }, []);

  // ==========================================================================
  // RUN AI TESTS
  // ==========================================================================

  const handleRunAITests = async () => {
    setTestingLoading(true);
    setTestingError("");

    try {
      const report = await runAITests();

      setTestingReport(report);

      // Reset expanded sections after a new report.
      setShowAIAnalysis(false);
      setShowCoverageGaps(false);
      setShowUnmapped(false);
    } catch (error) {
      setTestingError(
        error instanceof Error
          ? error.message
          : "AI testing failed. Please try again.",
      );
    } finally {
      setTestingLoading(false);
    }
  };

  // ==========================================================================
  // PASSWORD REQUIREMENTS
  // ==========================================================================

  const passwordChecks = passwordRequirements.map((requirement) => ({
    ...requirement,
    satisfied: requirement.check(password),
  }));

  const passwordScore = passwordChecks.filter(
    (requirement) => requirement.satisfied,
  ).length;

  const passwordsMatch =
    password.length > 0 &&
    confirmPassword.length > 0 &&
    password === confirmPassword;

  // ==========================================================================
  // FORM VALIDATION
  // ==========================================================================

  const validateForm = (): string | null => {
    if (!email.trim()) {
      return "Please enter your email address.";
    }

    if (mode === "signup" && !username.trim()) {
      return "Please enter a username.";
    }

    if (!password) {
      return "Please enter your password.";
    }

    if (mode === "signup") {
      if (username.trim().length < 3) {
        return "Username must contain at least 3 characters.";
      }

      if (passwordScore < passwordRequirements.length) {
        return "Please satisfy all password requirements.";
      }

      if (!confirmPassword) {
        return "Please confirm your password.";
      }

      if (password !== confirmPassword) {
        return "Passwords do not match.";
      }
    }

    return null;
  };

  // ==========================================================================
  // AUTH SUBMIT
  // ==========================================================================

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    setError("");
    setSuccess("");

    const validationError = validateForm();

    if (validationError) {
      setError(validationError);
      return;
    }

    setLoading(true);

    try {
      // ----------------------------------------------------------------------
      // SIGN UP
      // ----------------------------------------------------------------------

      if (mode === "signup") {
        const signupData: SignupData = {
          username: username.trim(),
          email: email.trim(),
          password,
          confirm_password: confirmPassword,
        };

        const user = await signup(signupData);

        setSuccess(
          `Account created successfully. Welcome, ${user.username}.`,
        );

        setMode("signin");

        setUsername("");
        setPassword("");
        setConfirmPassword("");

        setShowPassword(false);
        setShowConfirmPassword(false);
      }

      // ----------------------------------------------------------------------
      // SIGN IN
      // ----------------------------------------------------------------------

      else {
        const loginData: LoginData = {
          email: email.trim(),
          password,
        };

        const response = await login(loginData);

        if (rememberMe) {
          localStorage.setItem(
            "access_token",
            response.access_token,
          );

          sessionStorage.removeItem("access_token");
        } else {
          sessionStorage.setItem(
            "access_token",
            response.access_token,
          );

          localStorage.removeItem("access_token");
        }

        setSuccess(
          `Welcome back, ${response.user.username}.`,
        );

        setPassword("");
      }
    } catch (error) {
      setError(
        error instanceof Error
          ? error.message
          : "Something went wrong. Please try again.",
      );
    } finally {
      setLoading(false);
    }
  };

  // ==========================================================================
  // SWITCH AUTH MODE
  // ==========================================================================

  const handleModeChange = (newMode: AuthMode) => {
    setMode(newMode);

    setError("");
    setSuccess("");

    setUsername("");
    setEmail("");
    setPassword("");
    setConfirmPassword("");

    setShowPassword(false);
    setShowConfirmPassword(false);
  };

  // ==========================================================================
  // TESTING REPORT DATA
  // ==========================================================================

  const finalStatus =
    testingReport?.executive_summary?.final_status ||
    "NO REPORT";

  const baselinePassed =
    testingReport?.test_summary?.baseline_passed ?? 0;

  const baselineTotal =
    testingReport?.test_summary?.baseline_total ?? 0;

  const aiPassed =
    testingReport?.test_summary?.ai_passed ?? 0;

  const aiTotal =
    testingReport?.test_summary?.ai_total_executed ?? 0;

  const coverageGaps =
    testingReport?.test_summary?.coverage_gaps ?? 0;

  const unmappedScenarios =
    testingReport?.test_summary?.unmapped_scenarios ?? 0;

  const aiAnalysis =
    testingReport?.ai_analysis?.analysis || "";

  const coverageGapItems =
    testingReport?.coverage_gaps ?? [];

  const unmappedItems =
    testingReport?.unmapped_scenarios ?? [];

  const recommendations =
    testingReport?.recommendations ?? [];

  const totalPassed =
    baselinePassed + aiPassed;

  // ==========================================================================
  // RENDER
  // ==========================================================================

  return (
    <main className="auth-page">

      {/* ==================================================================== */}
      {/* LEFT SIDE                                                           */}
      {/* ==================================================================== */}

      <section className="auth-intro">

        {/* ------------------------------------------------------------------ */}
        {/* TOP LINE                                                           */}
        {/* ------------------------------------------------------------------ */}

        <div className="intro-topline">
          <span>NEXA / AUTH</span>

          <span>
            SECURE ACCESS SYSTEM
          </span>
        </div>

        {/* ------------------------------------------------------------------ */}
        {/* INTRO CONTENT                                                      */}
        {/* ------------------------------------------------------------------ */}

        <div className="intro-content">

          <div className="intro-index">
            01 / 02
          </div>

          <h1>
            Secure
            <br />
            access.
            <br />
            <span>
              Intelligently tested.
            </span>
          </h1>

          <p className="intro-description">
            A production-minded authentication system
            designed with secure credential handling,
            JWT authentication, validation, and
            AI-assisted testing.
          </p>

          <div className="intro-meta">

            <div>
              <span className="meta-label">
                AUTHENTICATION
              </span>

              <strong>
                JWT / ARGON2
              </strong>
            </div>

            <div>
              <span className="meta-label">
                DATABASE
              </span>

              <strong>
                SQLITE
              </strong>
            </div>

            <div>
              <span className="meta-label">
                TEST ENGINE
              </span>

              <strong>
                GEMINI + PYTEST
              </strong>
            </div>

          </div>

        </div>

        {/* ================================================================== */}
        {/* AI TESTING AGENT                                                  */}
        {/* ================================================================== */}

        <div className="agent-status">

          {/* ---------------------------------------------------------------- */}
          {/* AGENT HEADER                                                     */}
          {/* ---------------------------------------------------------------- */}

          <div className="status-header">

            <div>

              <span className="agent-label">
                AI TESTING AGENT
              </span>

              <div
                className={`agent-title ${
                  testingLoading
                    ? "status-running"
                    : ""
                }`}
              >

                <span className="pulse-dot" />

                {testingLoading
                  ? "ANALYZING SYSTEM"
                  : testingReport
                    ? "LATEST TEST REPORT"
                    : "READY TO TEST"}

              </div>

            </div>

            {testingReport && (
              <div className="test-summary">

                <span className="test-summary-number">
                  {totalPassed}
                </span>

                <span className="test-summary-label">
                  TESTS PASSED
                </span>

              </div>
            )}

          </div>

          {/* ================================================================ */}
          {/* REPORT AVAILABLE                                                */}
          {/* ================================================================ */}

          {testingReport ? (
            <>

              {/* ------------------------------------------------------------ */}
              {/* CORE TEST METRICS                                            */}
              {/* ------------------------------------------------------------ */}

              <div className="test-list">

                {/* BASELINE */}
                <div className="test-item">

                  <div className="test-check">
                    {baselinePassed === baselineTotal
                      ? "✓"
                      : "!"}
                  </div>

                  <div className="test-info">

                    <span className="test-name">
                      Baseline authentication suite
                    </span>

                    <span className="test-detail">
                      {baselinePassed}/{baselineTotal}{" "}
                      passed
                    </span>

                  </div>

                  <span className="test-metric">
                    {baselineTotal > 0
                      ? Math.round(
                          (baselinePassed /
                            baselineTotal) *
                            100,
                        )
                      : 0}
                    %
                  </span>

                </div>

                {/* AI TESTS */}
                <div className="test-item">

                  <div className="test-check">
                    {aiPassed === aiTotal
                      ? "✓"
                      : "!"}
                  </div>

                  <div className="test-info">

                    <span className="test-name">
                      AI-generated security tests
                    </span>

                    <span className="test-detail">
                      {aiPassed}/{aiTotal} passed
                    </span>

                  </div>

                  <span className="test-metric">
                    {aiTotal > 0
                      ? Math.round(
                          (aiPassed / aiTotal) *
                            100,
                        )
                      : 0}
                    %
                  </span>

                </div>

                {/* COVERAGE */}
                <div className="test-item">

                  <div className="test-check">
                    {coverageGaps === 0
                      ? "✓"
                      : "!"}
                  </div>

                  <div className="test-info">

                    <span className="test-name">
                      Security & coverage analysis
                    </span>

                    <span className="test-detail">
                      {coverageGaps} coverage gap
                      {coverageGaps === 1
                        ? ""
                        : "s"}{" "}
                      identified
                    </span>

                  </div>

                  <span className="test-metric">
                    {coverageGaps}
                  </span>

                </div>

                {/* UNMAPPED */}
                <div className="test-item">

                  <div className="test-check">
                    {unmappedScenarios === 0
                      ? "✓"
                      : "!"}
                  </div>

                  <div className="test-info">

                    <span className="test-name">
                      Scenario mapping
                    </span>

                    <span className="test-detail">
                      {unmappedScenarios} unmapped
                      scenario
                      {unmappedScenarios === 1
                        ? ""
                        : "s"}
                    </span>

                  </div>

                  <span className="test-metric">
                    {unmappedScenarios}
                  </span>

                </div>

              </div>

              {/* ============================================================ */}
              {/* AI ANALYSIS                                                   */}
              {/* ============================================================ */}

              <div className="testing-section">

                <button
                  type="button"
                  className="testing-section-header"
                  onClick={() =>
                    setShowAIAnalysis(
                      (current) => !current,
                    )
                  }
                >

                  <div>

                    <span className="section-number">
                      01
                    </span>

                    <span className="section-title">
                      AI ANALYSIS
                    </span>

                  </div>

                  <span className="section-toggle">
                    {showAIAnalysis
                      ? "−"
                      : "+"}
                  </span>

                </button>

                {showAIAnalysis && (
                  <div className="testing-section-content">

                    {aiAnalysis ? (
                      <p className="ai-analysis-text">
                        {aiAnalysis}
                      </p>
                    ) : (
                      <p className="empty-testing-message">
                        No AI analysis is available
                        in this report.
                      </p>
                    )}

                    {testingReport.ai_analysis?.model && (
                      <div className="ai-provider">

                        <span>
                          MODEL
                        </span>

                        <strong>
                          {testingReport.ai_analysis.model}
                        </strong>

                      </div>
                    )}

                  </div>
                )}

              </div>

              {/* ============================================================ */}
              {/* SECURITY & COVERAGE                                          */}
              {/* ============================================================ */}

              <div className="testing-section">

                <button
                  type="button"
                  className="testing-section-header"
                  onClick={() =>
                    setShowCoverageGaps(
                      (current) => !current,
                    )
                  }
                >

                  <div>

                    <span className="section-number">
                      02
                    </span>

                    <span className="section-title">
                      SECURITY & COVERAGE
                    </span>

                    <span className="section-count">
                      {coverageGapItems.length}
                    </span>

                  </div>

                  <span className="section-toggle">
                    {showCoverageGaps
                      ? "−"
                      : "+"}
                  </span>

                </button>

                {showCoverageGaps && (
                  <div className="testing-section-content">

                    {coverageGapItems.length > 0 ? (

                      <div className="scenario-list">

                        {coverageGapItems.map(
                          (scenario, index) => (
                            <div
                              className="scenario-card"
                              key={`${scenario.name}-${index}`}
                            >

                              <div className="scenario-top">

                                <span className="scenario-index">
                                  {String(
                                    index + 1,
                                  ).padStart(2, "0")}
                                </span>

                                <span className="scenario-priority">
                                  {scenario.priority ||
                                    "REVIEW"}
                                </span>

                              </div>

                              <strong>
                                {scenario.name}
                              </strong>

                              {scenario.objective && (
                                <p>
                                  {scenario.objective}
                                </p>
                              )}

                              {scenario.reason && (
                                <span className="scenario-reason">
                                  {scenario.reason}
                                </span>
                              )}

                            </div>
                          ),
                        )}

                      </div>

                    ) : (
                      <p className="empty-testing-message">
                        No coverage gaps identified.
                      </p>
                    )}

                  </div>
                )}

              </div>

              {/* ============================================================ */}
              {/* UNMAPPED SCENARIOS                                           */}
              {/* ============================================================ */}

              <div className="testing-section">

                <button
                  type="button"
                  className="testing-section-header"
                  onClick={() =>
                    setShowUnmapped(
                      (current) => !current,
                    )
                  }
                >

                  <div>

                    <span className="section-number">
                      03
                    </span>

                    <span className="section-title">
                      UNMAPPED SCENARIOS
                    </span>

                    <span className="section-count">
                      {unmappedItems.length}
                    </span>

                  </div>

                  <span className="section-toggle">
                    {showUnmapped
                      ? "−"
                      : "+"}
                  </span>

                </button>

                {showUnmapped && (
                  <div className="testing-section-content">

                    {unmappedItems.length > 0 ? (

                      <div className="unmapped-list">

                        {unmappedItems.map(
                          (scenario, index) => (
                            <div
                              className="unmapped-item"
                              key={`${scenario.name}-${index}`}
                            >

                              <span>
                                {String(
                                  index + 1,
                                ).padStart(2, "0")}
                              </span>

                              <strong>
                                {scenario.name}
                              </strong>

                            </div>
                          ),
                        )}

                      </div>

                    ) : (
                      <p className="empty-testing-message">
                        All AI scenarios are mapped.
                      </p>
                    )}

                  </div>
                )}

              </div>

              {/* ============================================================ */}
              {/* AI RECOMMENDATIONS                                           */}
              {/* ============================================================ */}

              {recommendations.length > 0 && (
                <div className="testing-recommendations">

                  <span className="recommendation-label">
                    AI RECOMMENDATIONS
                  </span>

                  <ul>

                    {recommendations.map(
                      (recommendation, index) => (
                        <li key={index}>
                          {recommendation}
                        </li>
                      ),
                    )}

                  </ul>

                </div>
              )}

              {/* ============================================================ */}
              {/* FINAL STATUS                                                 */}
              {/* ============================================================ */}

              <div className="agent-final-status">

                <div>
                  <span>
                    FINAL STATUS
                  </span>
                </div>

                <strong>
                  {finalStatus}
                </strong>

              </div>

              {/* ============================================================ */}
              {/* FULL HTML REPORT                                             */}
              {/* ============================================================ */}

              <a
                href={TESTING_REPORT_HTML_URL}
                target="_blank"
                rel="noreferrer"
                className="view-report-button"
              >

                <span>
                  View full HTML report
                </span>

                <span>
                  ↗
                </span>

              </a>

              {/* ============================================================ */}
              {/* RUN AGAIN                                                    */}
              {/* ============================================================ */}

              <button
                type="button"
                className="run-tests-button"
                onClick={handleRunAITests}
                disabled={testingLoading}
              >

                <span>
                  {testingLoading
                    ? "Running AI tests..."
                    : "Run AI tests again"}
                </span>

                <span>
                  ↗
                </span>

              </button>

              {/* REPORT TIMESTAMP */}
              {testingReport.report_metadata
                ?.generated_at && (
                <div className="report-timestamp">

                  Last report:{" "}
                  {new Date(
                    testingReport.report_metadata
                      .generated_at,
                  ).toLocaleString()}

                </div>
              )}

            </>
          ) : (

            /* ================================================================ */
            /* NO REPORT                                                      */
            /* ================================================================ */

            <div className="agent-empty">

              <p>
                No testing report available yet.
              </p>

              <span>
                Run the AI testing agent to analyze
                the authentication system, execute
                approved scenarios, and generate a
                security report.
              </span>

              <button
                type="button"
                className="run-tests-button"
                onClick={handleRunAITests}
                disabled={testingLoading}
              >

                <span>
                  {testingLoading
                    ? "Running AI tests..."
                    : "Run AI tests"}
                </span>

                <span>
                  ↗
                </span>

              </button>

            </div>
          )}

          {/* TESTING ERROR */}
          {testingError && (
            <p className="testing-error">
              {testingError}
            </p>
          )}

        </div>

      </section>

      {/* ==================================================================== */}
      {/* RIGHT SIDE — AUTHENTICATION                                         */}
      {/* ==================================================================== */}

      <section className="auth-panel">

        <div className="auth-card">

          {/* ---------------------------------------------------------------- */}
          {/* HEADER                                                           */}
          {/* ---------------------------------------------------------------- */}

          <div className="auth-header">

            <div>

              <span className="auth-eyebrow">
                {mode === "signin"
                  ? "WELCOME BACK"
                  : "NEW ACCOUNT"}
              </span>

              <h2>
                {mode === "signin"
                  ? "Sign in."
                  : "Create account."}
              </h2>

            </div>

            <span className="auth-version">
              v1.0
            </span>

          </div>

          {/* ---------------------------------------------------------------- */}
          {/* MODE SWITCH                                                      */}
          {/* ---------------------------------------------------------------- */}

          <div className="auth-switch">

            <button
              type="button"
              className={
                mode === "signin"
                  ? "active"
                  : ""
              }
              onClick={() =>
                handleModeChange("signin")
              }
            >
              Sign in
            </button>

            <button
              type="button"
              className={
                mode === "signup"
                  ? "active"
                  : ""
              }
              onClick={() =>
                handleModeChange("signup")
              }
            >
              Create account
            </button>

          </div>

          {/* ---------------------------------------------------------------- */}
          {/* ERROR                                                            */}
          {/* ---------------------------------------------------------------- */}

          {error && (
            <div className="form-message form-error">

              <span>
                !
              </span>

              <p>
                {error}
              </p>

            </div>
          )}

          {/* ---------------------------------------------------------------- */}
          {/* SUCCESS                                                          */}
          {/* ---------------------------------------------------------------- */}

          {success && (
            <div className="form-message form-success">

              <span>
                ✓
              </span>

              <p>
                {success}
              </p>

            </div>
          )}

          {/* ================================================================= */}
          {/* AUTH FORM                                                        */}
          {/* ================================================================= */}

          <form
            onSubmit={handleSubmit}
            noValidate
          >

            {/* =============================================================== */}
            {/* USERNAME                                                        */}
            {/* =============================================================== */}

            {mode === "signup" && (
              <div className="form-group">

                <label htmlFor="username">
                  Username
                </label>

                <input
                  id="username"
                  type="text"
                  value={username}
                  onChange={(event) =>
                    setUsername(
                      event.target.value,
                    )
                  }
                  placeholder="Choose a username"
                  autoComplete="username"
                  disabled={loading}
                />

                <span className="field-hint">
                  Minimum 3 characters
                </span>

              </div>
            )}

            {/* =============================================================== */}
            {/* EMAIL                                                           */}
            {/* =============================================================== */}

            <div className="form-group">

              <label htmlFor="email">
                Email address
              </label>

              <input
                id="email"
                type="email"
                value={email}
                onChange={(event) =>
                  setEmail(
                    event.target.value,
                  )
                }
                placeholder="you@example.com"
                autoComplete="email"
                disabled={loading}
              />

            </div>

            {/* =============================================================== */}
            {/* PASSWORD                                                        */}
            {/* =============================================================== */}

            <div className="form-group">

              <div className="field-label-row">

                <label htmlFor="password">
                  Password
                </label>

                {mode === "signin" && (
                  <button
                    type="button"
                    className="forgot-button"
                    onClick={() =>
                      setError(
                        "Password reset is not available yet.",
                      )
                    }
                  >
                    Forgot password?
                  </button>
                )}

              </div>

              <div className="password-input">

                <input
                  id="password"
                  type={
                    showPassword
                      ? "text"
                      : "password"
                  }
                  value={password}
                  onChange={(event) =>
                    setPassword(
                      event.target.value,
                    )
                  }
                  placeholder="Enter your password"
                  autoComplete={
                    mode === "signin"
                      ? "current-password"
                      : "new-password"
                  }
                  disabled={loading}
                />

                <button
                  type="button"
                  className="password-toggle"
                  onClick={() =>
                    setShowPassword(
                      (current) =>
                        !current,
                    )
                  }
                  aria-label={
                    showPassword
                      ? "Hide password"
                      : "Show password"
                  }
                >
                  {showPassword
                    ? "HIDE"
                    : "SHOW"}
                </button>

              </div>

            </div>

            {/* =============================================================== */}
            {/* PASSWORD REQUIREMENTS                                           */}
            {/* =============================================================== */}

            {mode === "signup" && (
              <div className="password-requirements">

                <div className="requirements-heading">

                  <span>
                    PASSWORD REQUIREMENTS
                  </span>

                  <strong>
                    {passwordScore}/
                    {passwordRequirements.length}
                  </strong>

                </div>

                <div className="requirements-list">

                  {passwordChecks.map(
                    (requirement) => (
                      <div
                        className={`requirement ${
                          requirement.satisfied
                            ? "satisfied"
                            : ""
                        }`}
                        key={requirement.key}
                      >

                        <span className="requirement-icon">
                          {requirement.satisfied
                            ? "✓"
                            : "○"}
                        </span>

                        <span>
                          {requirement.label}
                        </span>

                      </div>
                    ),
                  )}

                </div>

              </div>
            )}

            {/* =============================================================== */}
            {/* CONFIRM PASSWORD                                               */}
            {/* =============================================================== */}

            {mode === "signup" && (
              <div className="form-group">

                <label htmlFor="confirm-password">
                  Confirm password
                </label>

                <div className="password-input">

                  <input
                    id="confirm-password"
                    type={
                      showConfirmPassword
                        ? "text"
                        : "password"
                    }
                    value={confirmPassword}
                    onChange={(event) =>
                      setConfirmPassword(
                        event.target.value,
                      )
                    }
                    placeholder="Repeat your password"
                    autoComplete="new-password"
                    disabled={loading}
                  />

                  <button
                    type="button"
                    className="password-toggle"
                    onClick={() =>
                      setShowConfirmPassword(
                        (current) =>
                          !current,
                      )
                    }
                    aria-label={
                      showConfirmPassword
                        ? "Hide confirm password"
                        : "Show confirm password"
                    }
                  >
                    {showConfirmPassword
                      ? "HIDE"
                      : "SHOW"}
                  </button>

                </div>

                {confirmPassword.length > 0 && (
                  <span
                    className={`field-hint ${
                      passwordsMatch
                        ? "hint-success"
                        : "hint-error"
                    }`}
                  >
                    {passwordsMatch
                      ? "Passwords match."
                      : "Passwords do not match."}
                  </span>
                )}

              </div>
            )}

            {/* =============================================================== */}
            {/* REMEMBER ME                                                    */}
            {/* =============================================================== */}

            {mode === "signin" && (
              <div className="remember-row">

                <label className="checkbox-label">

                  <input
                    type="checkbox"
                    checked={rememberMe}
                    onChange={(event) =>
                      setRememberMe(
                        event.target.checked,
                      )
                    }
                    disabled={loading}
                  />

                  <span className="custom-checkbox" />

                  <span>
                    Remember me
                  </span>

                </label>

              </div>
            )}

            {/* =============================================================== */}
            {/* SUBMIT                                                          */}
            {/* =============================================================== */}

            <button
              type="submit"
              className="submit-button"
              disabled={loading}
            >

              <span>
                {loading
                  ? mode === "signin"
                    ? "Signing in..."
                    : "Creating account..."
                  : mode === "signin"
                    ? "Sign in"
                    : "Create account"}
              </span>

              <span className="submit-arrow">
                →
              </span>

            </button>

          </form>

          {/* ================================================================= */}
          {/* AUTH FOOTER                                                      */}
          {/* ================================================================= */}

          <div className="auth-footer">

            <span>
              {mode === "signin"
                ? "Don't have an account?"
                : "Already have an account?"}
            </span>

            <button
              type="button"
              onClick={() =>
                handleModeChange(
                  mode === "signin"
                    ? "signup"
                    : "signin",
                )
              }
            >
              {mode === "signin"
                ? "Create account"
                : "Sign in"}
            </button>

          </div>

          {/* ================================================================= */}
          {/* SECURITY NOTE                                                    */}
          {/* ================================================================= */}

          <div className="security-note">

            <span className="security-icon">
              ◈
            </span>

            <p>
              Your credentials are protected using
              secure password hashing and JWT-based
              authentication.
            </p>

          </div>

        </div>

        {/* ================================================================== */}
        {/* PANEL FOOTER                                                      */}
        {/* ================================================================== */}

        <div className="panel-footer">

          <span>
            © 2026 NEXA / AUTH
          </span>

          <span>
            SECURE • TESTED • AI-ASSISTED
          </span>

        </div>

      </section>

    </main>
  );
}

export default AuthPage;