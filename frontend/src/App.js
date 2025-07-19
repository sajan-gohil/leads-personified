import React, { useState, useEffect } from 'react';
import './App.css';
import {
  BrowserRouter as Router,
  Routes,
  Route,
  useNavigate,
  useParams,
} from 'react-router-dom';
import { useMemo } from 'react';

const BACKEND_URL = 'http://localhost:8000';
const STATUS_OPTIONS = ['unchecked', 'converted', 'failed', 'in-progress'];

function WorkorderList({ onUpload, workorders, error, onWorkorderClick, uploading, showUpload, setShowUpload, selectedFile, setSelectedFile, handleUpload }) {
  return (
    <div style={{ background: '#fff', minHeight: '100vh', fontFamily: 'Inter, Arial, sans-serif' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '2rem 2rem 1rem 2rem', borderBottom: '1px solid #eee' }}>
        <h2 style={{ margin: 0, fontWeight: 600, fontSize: '2rem', color: '#222' }}>Workorders</h2>
        <button
          onClick={() => setShowUpload(true)}
          style={{ padding: '0.6rem 1.2rem', background: '#2563eb', color: '#fff', border: 'none', borderRadius: '5px', fontWeight: 500, fontSize: '1rem', cursor: 'pointer', boxShadow: '0 1px 4px rgba(0,0,0,0.04)' }}
        >
          + Create Workorder
        </button>
      </div>
      <div style={{ maxWidth: 900, margin: '2rem auto', background: '#fff', borderRadius: 8, boxShadow: '0 2px 8px rgba(0,0,0,0.03)', padding: '2rem' }}>
        {error && <div style={{ color: 'red', marginBottom: '1rem' }}>{error}</div>}
        <table style={{ width: '100%', borderCollapse: 'collapse', background: '#fff' }}>
          <thead>
            <tr style={{ background: '#f7f7f7', borderBottom: '2px solid #eee' }}>
              <th style={{ textAlign: 'left', padding: '0.75rem', color: '#444', fontWeight: 600 }}>ID</th>
              <th style={{ textAlign: 'left', padding: '0.75rem', color: '#444', fontWeight: 600 }}>File Name</th>
              <th style={{ textAlign: 'left', padding: '0.75rem', color: '#444', fontWeight: 600 }}>Upload Date</th>
              <th style={{ textAlign: 'left', padding: '0.75rem', color: '#444', fontWeight: 600 }}>Status</th>
            </tr>
          </thead>
          <tbody>
            {workorders.length === 0 && (
              <tr>
                <td colSpan={4} style={{ textAlign: 'center', color: '#aaa', padding: '2rem' }}>No workorders yet.</td>
              </tr>
            )}
            {workorders.map((wo) => (
              <tr
                key={wo.id}
                style={{ cursor: 'pointer', borderBottom: '1px solid #f0f0f0', transition: 'background 0.2s' }}
                onClick={() => onWorkorderClick(wo.id)}
                onMouseOver={e => e.currentTarget.style.background = '#f5f8ff'}
                onMouseOut={e => e.currentTarget.style.background = '#fff'}
              >
                <td style={{ padding: '0.75rem', color: '#222', fontWeight: 500 }}>{wo.id}</td>
                <td style={{ padding: '0.75rem', color: '#2563eb', textDecoration: 'underline' }}>{wo.filename}</td>
                <td style={{ padding: '0.75rem', color: '#555' }}>{wo.upload_date ? new Date(wo.upload_date).toLocaleString() : '-'}</td>
                <td style={{ padding: '0.75rem', color: wo.status === 'uploaded' ? '#059669' : '#b91c1c', fontWeight: 500 }}>{wo.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {/* Upload Modal */}
      {showUpload && (
        <div style={{ position: 'fixed', top: 0, left: 0, width: '100vw', height: '100vh', background: 'rgba(0,0,0,0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100 }}>
          <div style={{ background: '#fff', padding: '2rem 2.5rem', borderRadius: 8, boxShadow: '0 4px 24px rgba(0,0,0,0.10)', minWidth: 320 }}>
            <h3 style={{ marginTop: 0, marginBottom: '1.5rem', color: '#222', fontWeight: 600 }}>Upload Workorder</h3>
            <input type="file" accept=".csv, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, application/vnd.ms-excel" onChange={e => setSelectedFile(e.target.files[0])} />
            <div style={{ marginTop: '1.5rem', display: 'flex', justifyContent: 'flex-end', gap: '0.5rem' }}>
              <button
                onClick={() => setShowUpload(false)}
                style={{ padding: '0.5rem 1.1rem', background: '#f3f4f6', color: '#222', border: 'none', borderRadius: '4px', fontWeight: 500, cursor: 'pointer' }}
                disabled={uploading}
              >
                Cancel
              </button>
              <button
                onClick={handleUpload}
                disabled={!selectedFile || uploading}
                style={{ padding: '0.5rem 1.1rem', background: '#2563eb', color: '#fff', border: 'none', borderRadius: '4px', fontWeight: 500, cursor: 'pointer' }}
              >
                {uploading ? 'Uploading...' : 'Upload'}
              </button>
            </div>
            {error && <div style={{ color: 'red', marginTop: '1rem' }}>{error}</div>}
          </div>
        </div>
      )}
    </div>
  );
}

function cosineSimilarity(a, b) {
  let dot = 0, normA = 0, normB = 0;
  for (let i = 0; i < a.length; i++) {
    dot += a[i] * b[i];
    normA += a[i] * a[i];
    normB += b[i] * b[i];
  }
  return dot / (Math.sqrt(normA) * Math.sqrt(normB));
}

function WorkorderDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [leads, setLeads] = useState([]);
  const [leadStatuses, setLeadStatuses] = useState({});
  const [personaModal, setPersonaModal] = useState({ open: false, persona: '' });
  const [dataModal, setDataModal] = useState({ open: false, data: '' });
  const [workorder, setWorkorder] = useState(null);
  const [rerankedLeads, setRerankedLeads] = useState(null);

  useEffect(() => {
    fetch(`${BACKEND_URL}/workorders/${id}`)
      .then((res) => res.json())
      .then((data) => {
        setWorkorder(data);
        setLeads(data.leads || []);
        const statuses = {};
        (data.leads || []).forEach((lead, idx) => {
          statuses[idx] = lead.status || 'unchecked';
        });
        setLeadStatuses(statuses);
      })
      .catch(() => setLeads([]));
  }, [id]);

  const handleStatusChange = async (idx, value) => {
    setLeadStatuses((prev) => ({ ...prev, [idx]: value }));
    // Save status to backend for the specific lead
    const lead = leads[idx];
    if (!lead || !lead.id) return;
    try {
      await fetch(`${BACKEND_URL}/workorders/${id}/leads/${lead.id}/status`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: value }),
      });
    } catch (error) {
      console.error('Failed to save lead status:', error);
      // Optionally show an error message to the user
    }
  };

  const getLeadName = (lead) => {
    if (!lead || typeof lead !== 'object') return '';
    if (lead.company_name) return lead.company_name;
    const nameKey = Object.keys(lead.data || lead).find((k) => k.toLowerCase().includes('name'));
    return nameKey ? (lead.data || lead)[nameKey] : '';
  };
  const getClusterId = (lead) => {
    if (!lead) return '-';
    return lead.cluster_id !== undefined ? lead.cluster_id : (lead.data && lead.data.cluster_id !== undefined ? lead.data.cluster_id : '-');
  };
  const getPersona = (lead) => {
    if (!lead) return '';
    return lead.buyer_persona || (lead.data && lead.data.buyer_persona) || '';
  };
  const getLeadData = (lead) => {
    if (!lead) return {};
    return lead.data || lead;
  };

  // Helper to decode base64 or array string to float array (if needed)
  function parseEmbedding(lead) {
    if (!lead || !lead.buyer_persona_embedding) return null;
    // If backend returns as base64 or array string, parse accordingly
    if (Array.isArray(lead.buyer_persona_embedding)) return lead.buyer_persona_embedding;
    if (typeof lead.buyer_persona_embedding === 'string') {
      try {
        // Try JSON parse (if stored as JSON string)
        const arr = JSON.parse(lead.buyer_persona_embedding);
        if (Array.isArray(arr)) return arr;
      } catch {}
    }
    return null;
  }

  // Helper to reload workorder data
  const fetchWorkorder = async () => {
    const res = await fetch(`${BACKEND_URL}/workorders/${id}`);
    const data = await res.json();
    setWorkorder(data);
    setLeads(data.leads || []);
    setRerankedLeads(null); // Always use backend order after fetch
    const statuses = {};
    (data.leads || []).forEach((lead, idx) => {
      statuses[idx] = lead.status || 'unchecked';
    });
    setLeadStatuses(statuses);
  };

  const handleRerank = async () => {
    // Use the currently displayed leads (leadsToShow) for reranking
    const validLeads = leadsToShow.filter(lead => lead != null);
    if (validLeads.length === 0) return;

    // Find indices of converted and failed leads in leadsToShow
    const convertedIdx = validLeads.map((_, i) => leadStatuses[i] === 'converted' ? i : -1).filter(i => i !== -1);
    const failedIdx = validLeads.map((_, i) => leadStatuses[i] === 'failed' ? i : -1).filter(i => i !== -1);
    if (convertedIdx.length === 0 && failedIdx.length === 0) return;

    // Get embeddings
    const embeddings = validLeads.map(parseEmbedding);
    // Compute similarity to closest converted and failed
    const scores = validLeads.map((lead, i) => {
      const emb = embeddings[i];
      if (!emb) return { idx: i, score: 0 };
      let maxConverted = -Infinity;
      let maxFailed = -Infinity;
      for (const idx of convertedIdx) {
        if (embeddings[idx]) {
          maxConverted = Math.max(maxConverted, cosineSimilarity(emb, embeddings[idx]));
        }
      }
      for (const idx of failedIdx) {
        if (embeddings[idx]) {
          maxFailed = Math.max(maxFailed, cosineSimilarity(emb, embeddings[idx]));
        }
      }
      // Score: prioritize converted similarity, penalize failed similarity
      return { idx: i, score: (maxConverted === -Infinity ? 0 : maxConverted) - (maxFailed === -Infinity ? 0 : maxFailed) };
    });
    // Sort by score descending
    const sorted = [...scores].sort((a, b) => b.score - a.score).map(s => validLeads[s.idx]).filter(lead => lead != null);
    setRerankedLeads(sorted);
    // Persist order to backend using the correct lead IDs
    const leadIds = sorted.filter(l => l && l.id).map(l => l.id);
    const resp = await fetch(`${BACKEND_URL}/workorders/${id}/rerank`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(leadIds),
    });
    if (resp.ok) {
      // Only reload if the database update succeeded
      await fetchWorkorder();
    } else {
      // Optionally handle error (show message, etc)
      console.error('Rerank failed:', await resp.text());
    }
  };

  // On load, sort by display_order if present
  const leadsToShow = useMemo(() => {
    const validLeads = leads.filter(lead => lead != null);
    if (rerankedLeads) return rerankedLeads.filter(lead => lead != null);
    if (validLeads.some(l => l.display_order !== undefined && l.display_order !== null)) {
      return [...validLeads].sort((a, b) => (a.display_order ?? 9999) - (b.display_order ?? 9999));
    }
    return validLeads;
  }, [leads, rerankedLeads]);

  return (
    <div style={{ background: '#fff', minHeight: '100vh', fontFamily: 'Inter, Arial, sans-serif' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '2rem 2rem 1rem 2rem', borderBottom: '1px solid #eee' }}>
        <h2 style={{ margin: 0, fontWeight: 600, fontSize: '2rem', color: '#222' }}>Workorder #{id}</h2>
        <div>
          <button
            onClick={handleRerank}
            style={{ marginRight: 16, padding: '0.5rem 1.1rem', background: '#2563eb', color: '#fff', border: 'none', borderRadius: '4px', fontWeight: 500, cursor: 'pointer' }}
          >
            Rerank Leads
          </button>
          <button
            onClick={() => navigate('/')}
            style={{ padding: '0.5rem 1.1rem', background: '#f3f4f6', color: '#222', border: 'none', borderRadius: '4px', fontWeight: 500, cursor: 'pointer' }}
          >
            Back to Workorders
          </button>
        </div>
      </div>
      <div style={{ maxWidth: 1200, margin: '2rem auto', background: '#fff', borderRadius: 8, boxShadow: '0 2px 8px rgba(0,0,0,0.03)', padding: '2rem' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', background: '#fff' }}>
          <thead>
            <tr style={{ background: '#f7f7f7', borderBottom: '2px solid #eee' }}>
              <th style={{ padding: '0.75rem', color: '#444', fontWeight: 600 }}>#</th>
              <th style={{ padding: '0.75rem', color: '#444', fontWeight: 600 }}>Lead Name</th>
              <th style={{ padding: '0.75rem', color: '#444', fontWeight: 600 }}>Status</th>
              <th style={{ padding: '0.75rem', color: '#444', fontWeight: 600 }}>Cluster ID</th>
              <th style={{ padding: '0.75rem', color: '#444', fontWeight: 600 }}>Persona</th>
              <th style={{ padding: '0.75rem', color: '#444', fontWeight: 600 }}>Data</th>
            </tr>
          </thead>
          <tbody>
            {leadsToShow.length === 0 && (
              <tr>
                <td colSpan={6} style={{ textAlign: 'center', color: '#aaa', padding: '2rem' }}>No leads found.</td>
              </tr>
            )}
            {leadsToShow.filter(lead => lead != null).map((lead, idx) => (
              <tr key={lead?.id || idx} style={{ borderBottom: '1px solid #f0f0f0' }}>
                <td style={{ padding: '0.75rem', color: '#222' }}>{idx + 1}</td>
                <td style={{ padding: '0.75rem', color: '#2563eb' }}>{getLeadName(lead)}</td>
                <td style={{ padding: '0.75rem' }}>
                  <select
                    value={leadStatuses[idx] || 'unchecked'}
                    onChange={e => handleStatusChange(idx, e.target.value)}
                    style={{ padding: '0.3rem 0.7rem', borderRadius: 4, border: '1px solid #ddd', background: '#f7f7f7', fontWeight: 500 }}
                  >
                    {STATUS_OPTIONS.map(opt => (
                      <option key={opt} value={opt}>{opt}</option>
                    ))}
                  </select>
                </td>
                <td style={{ padding: '0.75rem', color: '#222' }}>{getClusterId(lead)}</td>
                <td style={{ padding: '0.75rem' }}>
                  <button
                    onClick={() => setPersonaModal({ open: true, persona: getPersona(lead) })}
                    style={{ padding: '0.3rem 0.7rem', background: '#2563eb', color: '#fff', border: 'none', borderRadius: 4, fontWeight: 500, cursor: 'pointer' }}
                  >
                    View
                  </button>
                </td>
                <td style={{ padding: '0.75rem' }}>
                  <button
                    onClick={() => setDataModal({ open: true, data: JSON.stringify(getLeadData(lead), null, 2) })}
                    style={{ padding: '0.3rem 0.7rem', background: '#059669', color: '#fff', border: 'none', borderRadius: 4, fontWeight: 500, cursor: 'pointer' }}
                  >
                    View
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {/* Persona Modal */}
      {personaModal.open && (
        <div style={{ position: 'fixed', top: 0, left: 0, width: '100vw', height: '100vh', background: 'rgba(0,0,0,0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 200 }}>
          <div style={{ background: '#fff', padding: '2rem 2.5rem', borderRadius: 8, boxShadow: '0 4px 24px rgba(0,0,0,0.10)', minWidth: 400, maxWidth: 700, maxHeight: '70vh', overflowY: 'auto', position: 'relative' }}>
            <button
              onClick={() => setPersonaModal({ open: false, persona: '' })}
              style={{ position: 'absolute', top: 10, right: 10, background: '#eee', border: 'none', borderRadius: 4, padding: '0.3rem 0.7rem', cursor: 'pointer', fontWeight: 600 }}
            >
              Close
            </button>
            <h3 style={{ marginTop: 0, color: '#222', fontWeight: 600 }}>Buyer Persona</h3>
            <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word', fontSize: 15, color: '#333', background: '#f7f7f7', padding: 16, borderRadius: 6, maxHeight: 400, overflowY: 'auto' }}>{personaModal.persona}</pre>
          </div>
        </div>
      )}
      {/* Data Modal */}
      {dataModal.open && (
        <div style={{ position: 'fixed', top: 0, left: 0, width: '100vw', height: '100vh', background: 'rgba(0,0,0,0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 200 }}>
          <div style={{ background: '#fff', padding: '2rem 2.5rem', borderRadius: 8, boxShadow: '0 4px 24px rgba(0,0,0,0.10)', minWidth: 400, maxWidth: 700, maxHeight: '70vh', overflowY: 'auto', position: 'relative' }}>
            <button
              onClick={() => setDataModal({ open: false, data: '' })}
              style={{ position: 'absolute', top: 10, right: 10, background: '#eee', border: 'none', borderRadius: 4, padding: '0.3rem 0.7rem', cursor: 'pointer', fontWeight: 600 }}
            >
              Close
            </button>
            <h3 style={{ marginTop: 0, color: '#222', fontWeight: 600 }}>Lead Data</h3>
            <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word', fontSize: 15, color: '#333', background: '#f7f7f7', padding: 16, borderRadius: 6, maxHeight: 400, overflowY: 'auto' }}>{dataModal.data}</pre>
          </div>
        </div>
      )}
    </div>
  );
}

function App() {
  const [workorders, setWorkorders] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const [showUpload, setShowUpload] = useState(false);

  useEffect(() => {
    fetch(`${BACKEND_URL}/workorders`)
      .then((res) => res.json())
      .then((data) => {
        setWorkorders(
          data.sort((a, b) => new Date(b.upload_date) - new Date(a.upload_date))
        );
      })
      .catch(() => setWorkorders([]));
  }, []);

  const navigate = useNavigate();

  const handleWorkorderClick = (id) => {
    navigate(`/workorder/${id}`);
  };

  const handleUpload = async () => {
    if (!selectedFile) return;
    setUploading(true);
    setError(null);
    const formData = new FormData();
    formData.append('file', selectedFile);
    try {
      const response = await fetch(`${BACKEND_URL}/workorders/upload`, {
        method: 'POST',
        body: formData,
      });
      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Upload failed');
      }
      setSelectedFile(null);
      setShowUpload(false);
      // Refresh workorders list
      const res = await fetch(`${BACKEND_URL}/workorders`);
      const data = await res.json();
      setWorkorders(
        data.sort((a, b) => new Date(b.upload_date) - new Date(a.upload_date))
      );
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  };

  return (
    <Routes>
      <Route
        path="/"
        element={
          <WorkorderList
            onUpload={handleUpload}
            workorders={workorders}
            error={error}
            onWorkorderClick={handleWorkorderClick}
            uploading={uploading}
            showUpload={showUpload}
            setShowUpload={setShowUpload}
            selectedFile={selectedFile}
            setSelectedFile={setSelectedFile}
            handleUpload={handleUpload}
          />
        }
      />
      <Route path="/workorder/:id" element={<WorkorderDetail />} />
    </Routes>
  );
}

export default function WrappedApp() {
  return (
    <Router>
      <App />
    </Router>
  );
}
