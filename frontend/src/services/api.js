import axios from "axios";

const api = axios.create({
  baseURL: "https://sql-assistant-hla0.onrender.com",
});

export async function getDatabases() {
  const response = await api.get("/api/databases");
  return response.data;
}

export async function uploadDatabase(file) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await api.post(
    "/api/upload",
    formData
  );

  return response.data;
}

export async function askQuestion(database, question) {
  const response = await api.post("/api/ask", {
    database,
    question,
  });

  return response.data;
}

export async function getSchema(database) {
  const response = await api.get(
    `/api/databases/${encodeURIComponent(database)}/schema`
  );

  return response.data;
}