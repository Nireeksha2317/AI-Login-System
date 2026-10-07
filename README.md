# NEXA/AUTH — AI-Powered Authentication & Testing Platform

> A production-style full-stack authentication system built with React, FastAPI, JWT, Argon2 password hashing, and an AI-powered testing agent using Google Gemini.

NEXA/AUTH is a secure authentication platform designed with a modern frontend, a structured FastAPI backend, automated testing, and an AI testing agent capable of analyzing requirements, generating test scenarios, identifying coverage gaps, executing controlled test cases, and producing detailed testing reports.

---

## 🚀 Project Overview

Modern authentication systems need more than just a login form.

NEXA/AUTH combines:

- Secure user registration and login
- Password hashing using Argon2
- JWT-based authentication
- Backend validation with Pydantic
- React + TypeScript frontend
- Automated Pytest testing
- AI-assisted test scenario generation
- Security and edge-case analysis
- Coverage-gap detection
- Automated JSON and HTML testing reports

The project demonstrates how an AI agent can work alongside conventional software testing rather than simply generating code.

---

## ✨ Key Features

### 🔐 Secure Authentication

- User registration
- User login
- Email validation
- Username validation
- Password strength validation
- Password confirmation
- Duplicate username detection
- Duplicate email detection
- JWT access tokens
- Configurable token expiration
- Account active/inactive validation
- Argon2 password hashing

### 🧪 Automated Testing

The backend includes a Pytest test suite covering important authentication scenarios.

Current baseline scenarios include:

- Successful registration
- Duplicate email
- Duplicate username
- Invalid email
- Weak password
- Password mismatch
- Successful login
- Incorrect password
- Unknown email

### 🤖 AI Testing Agent

The project includes an AI-powered testing agent using Google Gemini.

The agent can:

1. Analyze authentication requirements
2. Understand the available API endpoints
3. Generate additional test scenarios
4. Identify security and edge cases
5. Detect potential coverage gaps
6. Classify scenarios based on executability
7. Execute approved controlled scenarios
8. Analyze test results
9. Generate recommendations
10. Produce JSON and HTML testing reports

### 📊 Testing Dashboard

The frontend provides a testing dashboard showing:

- Baseline test results
- AI-generated scenarios
- Passed and failed scenarios
- Coverage gaps
- Unmapped scenarios
- AI analysis
- Security recommendations
- Final testing status
- Full HTML testing report

### 🎨 Modern Authentication UI

The frontend follows a clean editorial/security-inspired design with:

- Responsive layout
- Sign in / Sign up modes
- Password visibility toggle
- Remember-me functionality
- Inline validation
- Loading states
- Error handling
- AI testing dashboard
- Responsive mobile layout

---

## 🏗️ System Architecture

```text
                         ┌─────────────────────────┐
                         │        React UI         │
                         │   React + TypeScript    │
                         └────────────┬────────────┘
                                      │
                                      │ HTTP / JSON
                                      ▼
                         ┌─────────────────────────┐
                         │       FastAPI API       │
                         │      Python Backend     │
                         └────────────┬────────────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    │                 │                 │
                    ▼                 ▼                 ▼
             ┌────────────┐   ┌─────────────┐   ┌──────────────┐
             │  Security  │   │ SQLAlchemy  │   │    Pytest    │
             │ JWT/Argon2 │   │   + SQLite  │   │    Tests     │
             └────────────┘   └─────────────┘   └──────┬───────┘
                                                       │
                                                       ▼
                                           ┌─────────────────────┐
                                           │   AI Testing Agent  │
                                           │    Google Gemini    │
                                           └──────────┬──────────┘
                                                      │
                              ┌───────────────────────┼───────────────────────┐
                              │                       │                       │
                              ▼                       ▼                       ▼
                       Test Scenarios          Coverage Gaps          Recommendations
                              │                       │                       │
                              └───────────────────────┼───────────────────────┘
                                                      │
                                                      ▼
                                           ┌─────────────────────┐
                                           │  JSON / HTML Report │
                                           └─────────────────────┘
