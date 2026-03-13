import axios from "axios";

const API_BASE_URL = "http://localhost:8000";

export const getDashboardStats = async () => {
  return {
    prompts: 1254,
    violations: 32,
    highRisk: 5,
    users: 14
  };
};

export const getViolationLogs = async () => {
  return [
    {
      time: "10:32",
      user: "emp_21",
      tool: "ChatGPT",
      risk: "High"
    },
    {
      time: "10:40",
      user: "emp_08",
      tool: "Gemini",
      risk: "Medium"
    }
  ];
};