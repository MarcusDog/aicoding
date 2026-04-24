import request from "../utils/request";

export function getDashboard() {
  return request.get("/admin/dashboard");
}

export function getUsers(params) {
  return request.get("/admin/users", { params });
}

export function createUser(payload) {
  return request.post("/admin/users", payload);
}

export function updateUser(id, payload) {
  return request.put(`/admin/users/${id}`, payload);
}

export function disableUser(id) {
  return request.delete(`/admin/users/${id}`);
}

export function getAttendance(params) {
  return request.get("/admin/attendance", { params });
}

export function getRules() {
  return request.get("/admin/rules");
}

export function createRule(payload) {
  return request.post("/admin/rules", payload);
}

export function updateRule(id, payload) {
  return request.put(`/admin/rules/${id}`, payload);
}

export function deleteRule(id) {
  return request.delete(`/admin/rules/${id}`);
}

export function getMonthlyReport(params) {
  return request.get("/statistics/monthly", { params });
}

export function getFaces(params) {
  return request.get("/admin/faces", { params });
}

export function getLogs(params) {
  return request.get("/admin/logs", { params });
}
