/* Shared bookmark API client. Auth cookies are sent only to this application. */
(() => {
  "use strict";
  function create(kind) {
    if (!["job", "course"].includes(kind)) throw new Error("Unsupported bookmark kind");
    const entries = new Map(), pending = new Set();
    let ready = false;
    async function request(url, options = {}) {
      const response = await fetch(url, {credentials: "same-origin", cache: "no-store", ...options});
      let data = null;
      if (response.status !== 204) {
        try { data = await response.json(); } catch {}
      }
      if (!response.ok) {
        const detail = data?.detail;
        const message = typeof detail === "string" ? detail : detail?.message;
        const error = new Error(response.status === 401 ? "로그인 후 관심목록을 저장해 주세요." : message || "관심목록을 처리하지 못했습니다. 다시 시도해 주세요.");
        error.status = response.status;
        error.code = detail?.code;
        error.loginRequired = response.status === 401;
        throw error;
      }
      return data;
    }
    async function load() {
      ready = false;
      const next = new Map();
      try {
        for (let page = 1; ; page++) {
          const data = await request("/api/bookmarks?item_type=" + kind + "&size=100&page=" + page);
          if (!data || !Array.isArray(data.items)) throw new Error("관심목록 응답을 확인하지 못했습니다.");
          for (const item of data.items) {
            if (item.item_type === kind) next.set(String(item.source_id), String(item.id));
          }
          if (page * data.size >= data.total || data.items.length === 0) break;
        }
      } catch (error) {
        if (!error.loginRequired) throw error;
        // Public catalogue visitors may browse, but saving still requires login.
      }
      entries.clear();
      for (const [id, bookmark] of next) entries.set(id, bookmark);
      ready = true;
      return [...entries.keys()];
    }
    async function toggle(sourceId) {
      sourceId = String(sourceId);
      if (!ready || pending.has(sourceId)) throw new Error("관심목록을 처리 중입니다. 잠시 후 다시 시도해 주세요.");
      pending.add(sourceId);
      try {
        if (entries.has(sourceId)) {
          try { await request("/api/bookmarks/" + encodeURIComponent(entries.get(sourceId)), {method: "DELETE"}); }
          catch (error) { if (error.status !== 404) throw error; }
          entries.delete(sourceId);
          return false;
        }
        let item;
        try {
          item = await request("/api/bookmarks", {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify({item_type: kind, source_id: sourceId})});
        } catch (error) {
          if (error.status !== 409 || error.code !== "BOOKMARK_ALREADY_EXISTS") throw error;
          item = await request("/api/bookmarks/" + encodeURIComponent(kind + ":" + sourceId));
        }
        entries.set(sourceId, String(item.id));
        return true;
      } finally { pending.delete(sourceId); }
    }
    return {load, toggle, ids: () => [...entries.keys()], isPending: id => pending.has(String(id)), get ready() { return ready; }};
  }
  window.CompassBookmarks = {create};
})();
