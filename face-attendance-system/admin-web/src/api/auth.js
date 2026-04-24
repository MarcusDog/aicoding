import request from "../utils/request";

export function adminLogin(payload) {
  return request.post("/auth/admin-login", payload);
}

export function getProfile() {
  return request.get("/auth/profile");
}
