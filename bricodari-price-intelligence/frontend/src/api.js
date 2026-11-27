async function request(path, options = {}) {
  const res = await fetch(path, options);
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || res.statusText);
  }
  const type = res.headers.get("content-type") || "";
  if (type.includes("application/json")) return res.json();
  return res.text();
}

export const api = {
  health: () => request("/api/health"),
  stats: () => request("/api/stats"),
  dashboard: () => request("/api/dashboard"),
  jobs: () => request("/api/jobs"),
  erpPrices: () => request("/api/erp-prices?limit=100"),
  products: (params = {}) => {
    const sp = new URLSearchParams();
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== null && v !== "") sp.set(k, String(v));
    });
    const q = sp.toString();
    return request(`/api/products${q ? `?${q}` : ""}`);
  },
  comparisons: (params = {}) => {
    const sp = new URLSearchParams();
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== null && v !== "") sp.set(k, String(v));
    });
    const q = sp.toString();
    return request(`/api/comparisons${q ? `?${q}` : ""}`);
  },
  rebuildComparisons: () =>
    request("/api/comparisons/rebuild", { method: "POST" }),
  competitors: () => request("/api/competitors"),
  createCompetitor: (body) =>
    request("/api/competitors", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }),
  deleteCompetitor: (id) =>
    request(`/api/competitors/${id}`, { method: "DELETE" }),
  uploadErp: (file) => {
    const form = new FormData();
    form.append("file", file);
    return request("/api/imports/erp/upload", { method: "POST", body: form });
  },
  uploadCompetitors: (file) => {
    const form = new FormData();
    form.append("file", file);
    return request("/api/imports/competitors/upload", {
      method: "POST",
      body: form,
    });
  },
  exportUrl: "/api/comparisons/export.csv",
  syncWoo: (maxProducts) => {
    const q =
      maxProducts != null ? `?max_products=${maxProducts}` : "";
    return request(`/api/woocommerce/sync${q}`, { method: "POST" });
  },
  syncStatus: () => request("/api/woocommerce/sync/status"),
  updateSyncSchedule: (body) =>
    request("/api/woocommerce/sync/schedule", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }),
  testWoo: () => request("/api/woocommerce/test"),
};
