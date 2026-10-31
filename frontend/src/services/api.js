import axios from "axios";

const http = axios.create({ baseURL: "/api" });

export const api = {
  health: () => http.get("/health").then((r) => r.data),
  upload: (file, onProgress) => {
    const fd = new FormData();
    fd.append("file", file);
    return http.post("/upload", fd, {
      onUploadProgress: (e) => e.total && onProgress?.(Math.round((e.loaded / e.total) * 100)),
    }).then((r) => r.data);
  },
  analyze: (id) => http.post(`/analyze/${id}`).then((r) => r.data),
  results: (id) => http.get(`/results/${id}`).then((r) => r.data),
  signal: (id, epoch, count = 1) => http.get(`/recordings/${id}/signal`, { params: { epoch, count } }).then((r) => r.data),
  history: () => http.get("/history").then((r) => r.data.recordings),
  remove: (id) => http.delete(`/recordings/${id}`).then((r) => r.data),
};

export const errMsg = (e) => e?.response?.data?.detail || e?.message || "Something went wrong";
