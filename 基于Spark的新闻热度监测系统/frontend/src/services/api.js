import axios from "axios";

const request = axios.create({
  baseURL: "/api",
  timeout: 15000,
});

const pipelineRequest = axios.create({
  baseURL: "/api",
  timeout: 300000,
});

export const api = {
  getOverview() {
    return request.get("/dashboard/overview");
  },
  getSourceCatalog() {
    return request.get("/sources/catalog");
  },
  getNews(params) {
    return request.get("/news/search", { params });
  },
  getEvents(params) {
    return request.get("/events/clusters", { params });
  },
  getEventDetail(params) {
    return request.get("/events/detail", { params });
  },
  getSentimentSummary() {
    return request.get("/sentiment/summary");
  },
  getAlertBriefs() {
    return request.get("/alerts/briefs");
  },
  getServiceBriefs() {
    return request.get("/services/briefs");
  },
  getInfluenceOverview() {
    return request.get("/influence/overview");
  },
  runPipeline(payload) {
    return pipelineRequest.post("/pipeline/run", payload);
  },
  runLivePipeline() {
    return pipelineRequest.post("/pipeline/run", {
      mode: "full",
      sample_limit: 0,
      rss_limit: 12,
      web_limit: 0,
      api_limit: 15,
      hot_score_scenario: "general",
      include_sample: false,
      include_batch: false,
      include_rss: true,
      include_web: false,
      include_api: true,
      include_history: true,
      fast_live: false,
    });
  },
};

export default request;
