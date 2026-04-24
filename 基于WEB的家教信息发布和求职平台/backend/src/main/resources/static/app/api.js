function buildErrorMessage(payload) {
  if (!payload) return '请求失败';
  if (typeof payload === 'string') return payload;
  return payload.message || payload.error || '请求失败';
}

async function request(path, options = {}) {
  const response = await fetch(path, {
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {})
    },
    ...options
  });

  if (!response.ok) {
    const payload = await response.json().catch(() => null);
    throw new Error(buildErrorMessage(payload));
  }

  return response.status === 204 ? null : response.json();
}

export const api = {
  request,
  login(username, password) {
    return request('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password })
    });
  },
  register(payload) {
    return request('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  },
  dashboard() {
    return request('/api/dashboard');
  },
  catalogDemands() {
    return request('/api/catalog/demands/open');
  },
  demandDetail(id) {
    return request(`/api/catalog/demands/${id}`);
  },
  approvedTutors() {
    return request('/api/catalog/tutors');
  },
  tutorProfileDetail(id) {
    return request(`/api/catalog/tutors/${id}`);
  },
  tutorProfileByUser(userId) {
    return request(`/api/catalog/tutor-users/${userId}/profile`);
  },
  parentDemands(parentId) {
    return request(`/api/parents/${parentId}/demands`);
  },
  parentOrders(parentId) {
    return request(`/api/parents/${parentId}/orders`);
  },
  publishDemand(parentId, payload) {
    return request(`/api/parents/${parentId}/demands`, {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  },
  resubmitDemand(parentId, demandId, payload) {
    return request(`/api/parents/${parentId}/demands/${demandId}`, {
      method: 'PUT',
      body: JSON.stringify(payload)
    });
  },
  tutorProfile(tutorId) {
    return request(`/api/tutors/${tutorId}/profile`);
  },
  submitTutorProfile(tutorId, payload) {
    return request(`/api/tutors/${tutorId}/profile`, {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  },
  resubmitTutorProfile(tutorId, payload) {
    return request(`/api/tutors/${tutorId}/profile`, {
      method: 'PUT',
      body: JSON.stringify(payload)
    });
  },
  async uploadTutorResumeFile(tutorId, file) {
    const formData = new FormData();
    formData.append('file', file);
    const response = await fetch(`/api/tutors/${tutorId}/profile/resume-file`, {
      method: 'POST',
      body: formData
    });
    if (!response.ok) {
      const payload = await response.json().catch(() => null);
      throw new Error(buildErrorMessage(payload));
    }
    return response.json();
  },
  applyForDemand(tutorId, payload) {
    return request(`/api/tutors/${tutorId}/applications`, {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  },
  tutorApplications(tutorId) {
    return request(`/api/tutors/${tutorId}/applications`);
  },
  tutorOrders(tutorId) {
    return request(`/api/tutors/${tutorId}/orders`);
  },
  adminProfiles() {
    return request('/api/admin/profiles');
  },
  auditProfile(adminId, profileId, payload) {
    return request(`/api/admin/${adminId}/profiles/${profileId}/audit`, {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  },
  adminDemands() {
    return request('/api/admin/demands');
  },
  auditDemand(adminId, demandId, payload) {
    return request(`/api/admin/${adminId}/demands/${demandId}/audit`, {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  },
  adminApplications() {
    return request('/api/admin/applications');
  },
  reviewApplication(adminId, applicationId, payload) {
    return request(`/api/admin/${adminId}/applications/${applicationId}/review`, {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  },
  adminOrders() {
    return request('/api/admin/orders');
  },
  adminAudits() {
    return request('/api/admin/audits');
  }
};
