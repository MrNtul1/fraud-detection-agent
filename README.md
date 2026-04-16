# fraud-detection-agent
this is AI-powered fraud detection system using MCP agents

# 🛡️ Fraud Detection Agent System (MCP + Multi-Agent AI)

## 📌 Overview

This project is an **AI-powered fraud detection system** built using a **multi-agent architecture** with MCP (Model Context Protocol) tools and LLM orchestration.

The system simulates real-world banking fraud detection by combining:
- Rule-based scoring
- Behavioral analysis
- Anomaly detection (unsupervised ML)
- LLM-based decision orchestration

---

## 🧠 Core Idea

Instead of using one AI model, this system uses **multiple specialized agents**:

- Amount Risk Agent → detects unusually large transactions
- Country Risk Agent → detects location anomalies
- Anomaly Agent → detects unusual patterns using ML
- Orchestrator Agent → decides which tools to use and makes final fraud decision

The LLM acts as the **brain that coordinates everything**, not just a classifier.

---

## ⚙️ Architecture
