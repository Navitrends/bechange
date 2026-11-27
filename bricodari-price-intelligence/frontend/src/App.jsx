import { useEffect, useMemo, useState } from "react";
import { api } from "./api";

const NAV = [
  { id: "home", label: "Tableau de bord", group: "Vue" },
  { id: "catalog", label: "1. Catalogue site", group: "Sources" },
  { id: "purchases", label: "2. Prix d'achat", group: "Sources" },
  { id: "competitors", label: "3. Concurrents", group: "Sources" },
  { id: "compare", label: "4. Comparateur", group: "Analyse" },
  { id: "alerts", label: "Alertes", group: "Analyse" },
  { id: "history", label: "Historique", group: "Système" },
];

function AlertBadge({ level }) {
  const map = {
    cher: { text: "Trop cher", className: "badge badge-danger" },
    moins_cher: { text: "Moins cher", className: "badge badge-ok" },
    ok: { text: "Aligné", className: "badge badge-neutral" },
  };
  const item = map[level] || { text: level || "—", className: "badge" };
  return <span className={item.className}>{item.text}</span>;
}

function formatPrice(v) {
  if (v == null || Number.isNaN(Number(v))) return "—";
  return `${Number(v).toFixed(3)} DT`;
}

function formatPct(v) {
  if (v == null || Number.isNaN(Number(v))) return "—";
  const n = Number(v);
  return `${n > 0 ? "+" : ""}${n.toFixed(1)}%`;
}

function StatusDot({ status }) {
  const ok = String(status || "").includes("completed");
  return <span className={`dot ${ok ? "dot-ok" : "dot-warn"}`} />;
}

export default function App() {
  const [page, setPage] = useState("home");
  const [dash, setDash] = useState(null);
  const [rows, setRows] = useState([]);
  const [products, setProducts] = useState([]);
  const [erp, setErp] = useState([]);
  const [competitors, setCompetitors] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [health, setHealth] = useState(null);
  const [filter, setFilter] = useState("");
  const [alert, setAlert] = useState("");
  const [selected, setSelected] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [newComp, setNewComp] = useState({ name: "", website_url: "" });
  const [catalogQ, setCatalogQ] = useState("");
  const [syncStatus, setSyncStatus] = useState(null);
  const [intervalHours, setIntervalHours] = useState(6);

  async function refreshAll() {
    setError("");
    try {
      const [d, c, p, e, comps, j, h, s] = await Promise.all([
        api.dashboard(),
        api.comparisons(),
        api.products({ limit: 50, ...(catalogQ ? { q: catalogQ } : {}) }),
        api.erpPrices(),
        api.competitors(),
        api.jobs(),
        api.health(),
        api.syncStatus(),
      ]);
      setDash(d);
      setRows(c);
      setProducts(p);
      setErp(e);
      setCompetitors(comps);
      setJobs(j);
      setHealth(h);
      setSyncStatus(s);
      if (s?.interval_hours) setIntervalHours(s.interval_hours);
    } catch (err) {
      setError(err.message);
    }
  }

  useEffect(() => {
    refreshAll();
  }, []);

  useEffect(() => {
    if (!syncStatus?.running) return undefined;
    const timer = setInterval(async () => {
      try {
        const s = await api.syncStatus();
        setSyncStatus(s);
        if (!s.running) {
          setMessage(
            `Sync terminée : ${s.last_rows_ok ?? 0}/${s.last_rows_total ?? 0} (${s.last_status})`
          );
          setLoading(false);
          await refreshAll();
        }
      } catch (err) {
        setError(err.message);
      }
    }, 3000);
    return () => clearInterval(timer);
  }, [syncStatus?.running]);

  useEffect(() => {
    const t = setTimeout(async () => {
      try {
        setProducts(
          await api.products({ limit: 50, ...(catalogQ ? { q: catalogQ } : {}) })
        );
      } catch (err) {
        setError(err.message);
      }
    }, 300);
    return () => clearTimeout(t);
  }, [catalogQ]);

  const filteredCompare = useMemo(() => {
    return rows.filter((r) => {
      if (alert && r.alert_level !== alert) return false;
      if (!filter) return true;
      const q = filter.toLowerCase();
      return (
        (r.name || "").toLowerCase().includes(q) ||
        (r.sku || "").toLowerCase().includes(q) ||
        (r.category || "").toLowerCase().includes(q)
      );
    });
  }, [rows, filter, alert]);

  const alertRows = useMemo(
    () => rows.filter((r) => r.alert_level === "cher" || r.alert_level === "moins_cher"),
    [rows]
  );

  const workflow = [
    {
      step: 1,
      title: "Catalogue site",
      desc: "Sync auto depuis bricodari.tn",
      value: dash?.products ?? 0,
      unit: "produits",
      page: "catalog",
      ready: (dash?.products ?? 0) > 0,
    },
    {
      step: 2,
      title: "Prix d'achat",
      desc: "Upload Excel dans la plateforme",
      value: dash?.erp_price_records ?? 0,
      unit: "lignes",
      page: "purchases",
      ready: (dash?.erp_price_records ?? 0) > 0,
    },
    {
      step: 3,
      title: "Concurrents",
      desc: "Upload Excel prix marché",
      value: dash?.competitors ?? 0,
      unit: "sites",
      page: "competitors",
      ready: (dash?.competitors ?? 0) > 0,
    },
    {
      step: 4,
      title: "Comparaison",
      desc: "Écarts, marges, alertes",
      value: dash?.products_compared ?? 0,
      unit: "comparés",
      page: "compare",
      ready: (dash?.products_compared ?? 0) > 0,
    },
  ];

  async function runRebuild() {
    setLoading(true);
    setMessage("");
    try {
      const res = await api.rebuildComparisons();
      setMessage(`Étape 4 OK — ${res.products_compared} produits comparés`);
      await refreshAll();
      setPage("compare");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function runSyncWoo() {
    setLoading(true);
    setMessage("Synchronisation lancée en arrière-plan...");
    setError("");
    try {
      const res = await api.syncWoo();
      setMessage(res.message || "Sync démarrée");
      const s = await api.syncStatus();
      setSyncStatus(s);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  }

  async function saveSchedule(enabled) {
    setLoading(true);
    setError("");
    try {
      const s = await api.updateSyncSchedule({
        enabled,
        interval_hours: Number(intervalHours) || 6,
      });
      setSyncStatus(s);
      setMessage(
        enabled
          ? `Sync auto activée toutes les ${s.interval_hours} h`
          : "Sync auto désactivée"
      );
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  function formatDate(iso) {
    if (!iso) return "—";
    try {
      return new Date(iso).toLocaleString("fr-FR");
    } catch {
      return iso;
    }
  }

  async function onUpload(kind, file) {
    if (!file) return;
    setLoading(true);
    setMessage("");
    setError("");
    try {
      const res =
        kind === "erp"
          ? await api.uploadErp(file)
          : await api.uploadCompetitors(file);
      setMessage(
        `Import ${kind === "erp" ? "achat" : "concurrents"} : ${res.rows_ok}/${res.rows_total}`
      );
      await api.rebuildComparisons();
      await refreshAll();
      setPage("compare");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function addCompetitor(e) {
    e.preventDefault();
    setLoading(true);
    try {
      await api.createCompetitor({
        name: newComp.name,
        website_url: newComp.website_url,
        currency: "TND",
        country: "TN",
      });
      setNewComp({ name: "", website_url: "" });
      setMessage("Concurrent ajouté");
      await refreshAll();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function removeCompetitor(id) {
    setLoading(true);
    try {
      await api.deleteCompetitor(id);
      await refreshAll();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  const groups = [...new Set(NAV.map((n) => n.group))];

  return (
    <div className="layout">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-mark">B</span>
          <div>
            <strong>Bricodari</strong>
            <small>Price Intelligence</small>
          </div>
        </div>

        <nav>
          {groups.map((group) => (
            <div key={group} className="nav-group">
              <p className="nav-group-title">{group}</p>
              {NAV.filter((n) => n.group === group).map((item) => (
                <button
                  key={item.id}
                  className={page === item.id ? "nav-item active" : "nav-item"}
                  onClick={() => setPage(item.id)}
                >
                  {item.label}
                  {item.id === "alerts" && (dash?.alerts_cher ?? 0) > 0 && (
                    <em className="nav-count">{dash.alerts_cher}</em>
                  )}
                </button>
              ))}
            </div>
          ))}
        </nav>

        <div className="sidebar-foot">
          <button className="btn btn-primary" onClick={runRebuild} disabled={loading}>
            {loading ? "Traitement..." : "Lancer comparaison"}
          </button>
          <a className="btn btn-ghost" href={api.exportUrl}>
            Export CSV
          </a>
        </div>
      </aside>

      <main className="main">
        <header className="topbar">
          <div>
            <p className="eyebrow">Bricodari · Veille concurrentielle</p>
            <h1>{NAV.find((n) => n.id === page)?.label}</h1>
          </div>
          <div className="top-actions">
            <span className={`pill ${health?.woocommerce_configured ? "pill-ok" : ""}`}>
              {health?.woocommerce_configured ? "Site connecté" : "Site non configuré"}
            </span>
          </div>
        </header>

        {message && <div className="flash ok">{message}</div>}
        {error && <div className="flash err">{error}</div>}

        {page === "home" && (
          <>
            <section className="workflow">
              <div className="panel-head">
                <h2>Workflow</h2>
                <p className="muted">
                  Site = sync auto · Achats & concurrents = upload dans la plateforme
                </p>
              </div>
              <div className="workflow-steps">
                {workflow.map((w, idx) => (
                  <button
                    key={w.step}
                    className={`workflow-card ${w.ready ? "ready" : ""}`}
                    onClick={() => setPage(w.page)}
                  >
                    <div className="workflow-num">{w.step}</div>
                    <div>
                      <strong>{w.title}</strong>
                      <small>{w.desc}</small>
                      <em>
                        {w.value} {w.unit}
                      </em>
                    </div>
                    {idx < workflow.length - 1 && <span className="workflow-arrow">→</span>}
                  </button>
                ))}
              </div>
            </section>

            <section className="grid cards">
              <article className="card">
                <span>Produits site</span>
                <strong>{dash?.products ?? "—"}</strong>
                <small>{dash?.products_with_sku ?? 0} avec SKU</small>
              </article>
              <article className="card">
                <span>Prix d'achat importés</span>
                <strong>{dash?.erp_price_records ?? "—"}</strong>
              </article>
              <article className="card alert-card">
                <span>Alertes trop cher</span>
                <strong>{dash?.alerts_cher ?? 0}</strong>
              </article>
              <article className="card">
                <span>Écart moyen</span>
                <strong>{formatPct(dash?.avg_gap_pct)}</strong>
              </article>
              <article className="card">
                <span>Marge moyenne</span>
                <strong>
                  {dash?.avg_margin_pct == null ? "—" : `${dash.avg_margin_pct}%`}
                </strong>
              </article>
              <article className="card">
                <span>Concurrents suivis</span>
                <strong>{dash?.competitors ?? "—"}</strong>
              </article>
            </section>

            <section className="split">
              <div className="panel">
                <div className="panel-head">
                  <h2>Alertes à traiter</h2>
                  <button className="link" onClick={() => setPage("alerts")}>
                    Voir
                  </button>
                </div>
                <div className="list">
                  {alertRows.slice(0, 5).map((r) => (
                    <button
                      key={r.product_id}
                      className="list-item"
                      onClick={() => {
                        setSelected(r);
                        setPage("compare");
                      }}
                    >
                      <div>
                        <strong>{r.name}</strong>
                        <small>{r.sku} · {formatPct(r.gap_vs_min_pct)}</small>
                      </div>
                      <AlertBadge level={r.alert_level} />
                    </button>
                  ))}
                  {alertRows.length === 0 && (
                    <p className="empty-inline">Aucune alerte.</p>
                  )}
                </div>
              </div>
              <div className="panel">
                <div className="panel-head">
                  <h2>Comment ça marche</h2>
                </div>
                <ol className="howto">
                  <li>
                    <strong>Catalogue site</strong> synchronisé depuis WooCommerce
                    (ajouts / modifs repris au sync).
                  </li>
                  <li>
                    <strong>Prix d'achat</strong> : déposer le Excel ici (plus de
                    OneDrive).
                  </li>
                  <li>
                    <strong>Prix concurrents</strong> : déposer le Excel ici.
                  </li>
                  <li>
                    <strong>Comparateur</strong> calcule écarts, marges et alertes.
                  </li>
                </ol>
                <button className="btn btn-primary" onClick={runRebuild} disabled={loading}>
                  Relancer la comparaison
                </button>
              </div>
            </section>
          </>
        )}

        {page === "catalog" && (
          <section>
            <div className="source-banner">
              <div>
                <h2>Source : bricodari.tn</h2>
                <p>
                  Catalogue synchronisé automatiquement depuis WooCommerce.
                  Ajouts et modifications du site sont repris à chaque sync.
                </p>
              </div>
              <button
                className="btn btn-primary"
                onClick={runSyncWoo}
                disabled={loading || syncStatus?.running}
              >
                {syncStatus?.running ? "Sync en cours..." : "Synchroniser maintenant"}
              </button>
            </div>

            <div className="split" style={{ marginTop: 12 }}>
              <div className="panel">
                <div className="panel-head">
                  <h2>Sync automatique</h2>
                  <span className={`pill ${syncStatus?.enabled ? "pill-ok" : ""}`}>
                    {syncStatus?.enabled ? "Activée" : "Désactivée"}
                  </span>
                </div>
                <div className="toolbar">
                  <label style={{ margin: 0, minWidth: 160 }}>
                    Intervalle (heures)
                    <input
                      type="number"
                      min={1}
                      max={168}
                      value={intervalHours}
                      onChange={(e) => setIntervalHours(e.target.value)}
                    />
                  </label>
                  <button
                    className="btn btn-primary"
                    onClick={() => saveSchedule(true)}
                    disabled={loading}
                  >
                    Activer / Enregistrer
                  </button>
                  <button
                    className="btn btn-ghost"
                    onClick={() => saveSchedule(false)}
                    disabled={loading}
                  >
                    Désactiver
                  </button>
                </div>
                <p className="muted">
                  Prochaine sync : {formatDate(syncStatus?.next_run_at)}
                </p>
              </div>
              <div className="panel">
                <div className="panel-head">
                  <h2>Dernière synchronisation</h2>
                </div>
                <div className="detail-grid">
                  <div>
                    <span>Statut</span>
                    <strong>{syncStatus?.running ? "En cours" : syncStatus?.last_status || "—"}</strong>
                  </div>
                  <div>
                    <span>Produits</span>
                    <strong>
                      {syncStatus?.last_rows_ok ?? "—"}/{syncStatus?.last_rows_total ?? "—"}
                    </strong>
                  </div>
                  <div>
                    <span>Début</span>
                    <strong style={{ fontSize: "0.9rem" }}>
                      {formatDate(syncStatus?.last_started_at)}
                    </strong>
                  </div>
                  <div>
                    <span>Fin</span>
                    <strong style={{ fontSize: "0.9rem" }}>
                      {formatDate(syncStatus?.last_finished_at)}
                    </strong>
                  </div>
                </div>
                <p className="muted">{syncStatus?.last_message || "Aucune sync récente"}</p>
              </div>
            </div>

            <div className="toolbar">
              <input
                placeholder="Rechercher dans le catalogue..."
                value={catalogQ}
                onChange={(e) => setCatalogQ(e.target.value)}
              />
            </div>
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>SKU</th>
                    <th>Produit</th>
                    <th>Catégorie</th>
                    <th>Prix site</th>
                    <th>Statut</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {products.map((p) => (
                    <tr key={p.id}>
                      <td>
                        <code>{p.sku || "vide"}</code>
                      </td>
                      <td>{p.name}</td>
                      <td>
                        <small>{p.category}</small>
                      </td>
                      <td>{formatPrice(p.display_price)}</td>
                      <td>{p.status}</td>
                      <td>
                        {p.permalink && (
                          <a href={p.permalink} target="_blank" rel="noreferrer">
                            Lien
                          </a>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        )}

        {page === "purchases" && (
          <section>
            <div className="source-banner">
              <div>
                <h2>Source : fichier Excel / CSV</h2>
                <p>
                  Déposez ici la liste des prix d’achat. Plus besoin de OneDrive :
                  l’historique reste dans la plateforme.
                </p>
              </div>
              <label className="btn btn-primary file-btn">
                Importer prix d'achat
                <input
                  hidden
                  type="file"
                  accept=".xlsx,.xls,.csv"
                  onChange={(e) => onUpload("erp", e.target.files?.[0])}
                />
              </label>
            </div>
            <p className="muted">Colonnes attendues : SKU, Désignation, Prix achat, Fournisseur</p>
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>SKU</th>
                    <th>Désignation</th>
                    <th>Fournisseur</th>
                    <th>Prix achat</th>
                    <th>Fichier source</th>
                  </tr>
                </thead>
                <tbody>
                  {erp.map((r) => (
                    <tr key={r.id}>
                      <td>
                        <code>{r.sku || "—"}</code>
                      </td>
                      <td>{r.designation}</td>
                      <td>{r.supplier_name}</td>
                      <td>{formatPrice(r.purchase_price)}</td>
                      <td>
                        <small>{r.source_file}</small>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        )}

        {page === "competitors" && (
          <section className="split">
            <div>
              <div className="source-banner">
                <div>
                  <h2>Source : fichier Excel concurrents</h2>
                  <p>
                    Uploadez les prix concurrents dans la plateforme. Colonnes : SKU,
                    Concurrent, Prix.
                  </p>
                </div>
                <label className="btn btn-primary file-btn">
                  Importer prix concurrents
                  <input
                    hidden
                    type="file"
                    accept=".xlsx,.xls,.csv"
                    onChange={(e) => onUpload("competitors", e.target.files?.[0])}
                  />
                </label>
              </div>
              <div className="panel" style={{ marginTop: 16 }}>
                <div className="panel-head">
                  <h2>Concurrents suivis</h2>
                </div>
                <div className="list">
                  {competitors.map((c) => (
                    <div key={c.id} className="list-item static">
                      <div>
                        <strong>{c.name}</strong>
                        <small>{c.website_url}</small>
                      </div>
                      <button className="link danger" onClick={() => removeCompetitor(c.id)}>
                        Supprimer
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            </div>
            <form className="panel" onSubmit={addCompetitor}>
              <h2>Ajouter un concurrent</h2>
              <label>
                Nom
                <input
                  required
                  value={newComp.name}
                  onChange={(e) => setNewComp({ ...newComp, name: e.target.value })}
                />
              </label>
              <label>
                URL
                <input
                  required
                  value={newComp.website_url}
                  onChange={(e) =>
                    setNewComp({ ...newComp, website_url: e.target.value })
                  }
                  placeholder="https://..."
                />
              </label>
              <button className="btn btn-primary" type="submit" disabled={loading}>
                Enregistrer
              </button>
            </form>
          </section>
        )}

        {(page === "compare" || page === "alerts") && (
          <section className={selected ? "compare-layout" : ""}>
            <div>
              <div className="toolbar">
                <input
                  placeholder="Rechercher SKU, nom, catégorie..."
                  value={filter}
                  onChange={(e) => setFilter(e.target.value)}
                />
                <select
                  value={page === "alerts" ? "cher" : alert}
                  onChange={(e) => setAlert(e.target.value)}
                  disabled={page === "alerts"}
                >
                  <option value="">Toutes alertes</option>
                  <option value="cher">Trop cher</option>
                  <option value="moins_cher">Moins cher</option>
                  <option value="ok">Aligné</option>
                </select>
                <a className="btn btn-ghost" href={api.exportUrl}>
                  Export
                </a>
              </div>
              <div className="table-wrap">
                <table>
                  <thead>
                    <tr>
                      <th>SKU</th>
                      <th>Produit</th>
                      <th>Achat</th>
                      <th>Vente site</th>
                      <th>Min marché</th>
                      <th>Écart</th>
                      <th>Marge</th>
                      <th>Alerte</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(page === "alerts" ? alertRows : filteredCompare).map((r) => (
                      <tr
                        key={r.product_id}
                        className={selected?.product_id === r.product_id ? "selected" : ""}
                        onClick={() => setSelected(r)}
                      >
                        <td>
                          <code>{r.sku || "—"}</code>
                        </td>
                        <td>
                          <div className="product-cell">
                            <strong>{r.name}</strong>
                            <small>{r.category}</small>
                          </div>
                        </td>
                        <td>{formatPrice(r.purchase_price)}</td>
                        <td>{formatPrice(r.sell_price)}</td>
                        <td>
                          {formatPrice(r.competitor_min_price)}
                          <small className="block">{r.competitor_min_name}</small>
                        </td>
                        <td className={r.gap_vs_min_pct > 10 ? "text-danger" : ""}>
                          {formatPct(r.gap_vs_min_pct)}
                        </td>
                        <td>
                          {r.estimated_margin_pct == null
                            ? "—"
                            : `${r.estimated_margin_pct}%`}
                        </td>
                        <td>
                          <AlertBadge level={r.alert_level} />
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {selected && (
              <aside className="detail panel">
                <div className="panel-head">
                  <h2>Fiche comparative</h2>
                  <button className="link" onClick={() => setSelected(null)}>
                    Fermer
                  </button>
                </div>
                <p className="detail-title">{selected.name}</p>
                <p className="muted">
                  <code>{selected.sku}</code>
                </p>
                <AlertBadge level={selected.alert_level} />
                <div className="detail-grid">
                  <div>
                    <span>Prix d'achat</span>
                    <strong>{formatPrice(selected.purchase_price)}</strong>
                  </div>
                  <div>
                    <span>Prix vente site</span>
                    <strong>{formatPrice(selected.sell_price)}</strong>
                  </div>
                  <div>
                    <span>Concurrent min</span>
                    <strong>{formatPrice(selected.competitor_min_price)}</strong>
                    <small>{selected.competitor_min_name}</small>
                  </div>
                  <div>
                    <span>Concurrent max</span>
                    <strong>{formatPrice(selected.competitor_max_price)}</strong>
                    <small>{selected.competitor_max_name}</small>
                  </div>
                  <div>
                    <span>Écart</span>
                    <strong>{formatPct(selected.gap_vs_min_pct)}</strong>
                  </div>
                  <div>
                    <span>Marge</span>
                    <strong>
                      {selected.estimated_margin_pct == null
                        ? "—"
                        : `${selected.estimated_margin_pct}%`}
                    </strong>
                  </div>
                </div>
                <p className="reco">{selected.recommendation}</p>
                {selected.permalink && (
                  <a
                    className="btn btn-ghost"
                    href={selected.permalink}
                    target="_blank"
                    rel="noreferrer"
                  >
                    Voir sur le site
                  </a>
                )}
              </aside>
            )}
          </section>
        )}

        {page === "history" && (
          <section className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Type</th>
                  <th>Source</th>
                  <th>Résultat</th>
                  <th>Statut</th>
                </tr>
              </thead>
              <tbody>
                {jobs.map((j) => (
                  <tr key={j.id}>
                    <td>{j.id}</td>
                    <td>{j.job_type}</td>
                    <td>{j.source_name}</td>
                    <td>
                      {j.rows_ok}/{j.rows_total}
                    </td>
                    <td>
                      <StatusDot status={j.status} />
                      {j.status}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>
        )}
      </main>
    </div>
  );
}
