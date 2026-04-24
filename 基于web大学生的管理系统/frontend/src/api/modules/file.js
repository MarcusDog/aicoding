import http from '../http';

export const uploadFile = async (url, file) => {
  const formData = new FormData();
  formData.append('file', file);
  return http.post(url, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });
};
