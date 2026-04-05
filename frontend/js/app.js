const API = "";   // 같은 FastAPI 서버에서 서빙

const CAT_ICONS = {
  "AI/머신러닝": "🤖", "빅데이터": "📊", "데이터": "🗃️",
  "앱개발": "📱",       "웹개발": "🌐",   "IoT/임베디드": "🔌",
  "게임/VR": "🎮",      "보안/해킹": "🔒", "블록체인": "⛓️",
  "UI/UX": "🎨",        "기타IT": "💻",    "전체": "🔍",
};

const SOURCE_LABEL = {
  linkareer: "링커리어",
  wevity:    "위비티",
  thinkgood: "씽굿",
  gonmofair: "공모전박람회",
  campuspick:"캠퍼스픽",
};

let state = {
  category: "전체",
  sort:     "latest",
  source:   null,
  search:   "",
  total:    0,
  loading:  false,
};

// ── 초기화 ──────────────────────────────────────
document.addEventListener("DOMContentLoaded", async () => {
  await Promise.all([loadCategories(), loadSources(), loadStats()]);
  await fetchCompetitions();

  // 검색 입력 이벤트
  document.getElementById("searchInput").addEventListener("input", e => {
    state.search = e.target.value.trim();
    fetchCompetitions();
  });
});

// ── 통계 ─────────────────────────────────────────
async function loadStats() {
  try {
    const res  = await fetch(`${API}/api/stats`);
    const data = await res.json();
    document.getElementById("statTotal").textContent   = data.total    ?? "—";
    document.getElementById("statClosing").textContent = data.closing_soon ?? "—";
  } catch (e) { /* 실패 시 무시 */ }
}

// ── 카테고리 탭 ──────────────────────────────────
async function loadCategories() {
  try {
    const res  = await fetch(`${API}/api/categories`);
    const cats = await res.json();
    const bar  = document.getElementById("catBar");

    bar.innerHTML = cats.map(c => {
      const icon   = CAT_ICONS[c.name] || "📌";
      const active = c.name === state.category ? "active" : "";
      return `<button class="cat-btn ${active}" data-cat="${escHtml(c.name)}" onclick="selectCat(this)">
        ${icon} ${escHtml(c.name)}
        <span class="cnt">${c.count}</span>
      </button>`;
    }).join("");
  } catch (e) {
    console.error("카테고리 로드 실패:", e);
  }
}

// ── 출처 필터 ─────────────────────────────────────
async function loadSources() {
  try {
    const res     = await fetch(`${API}/api/sources`);
    const sources = await res.json();
    const row     = document.getElementById("sourceRow");

    row.innerHTML = sources.map(s => `
      <button class="src-chip" data-src="${escHtml(s.id)}" onclick="selectSource(this)">
        ${escHtml(s.name)} <small>(${s.count})</small>
      </button>
    `).join("");
  } catch (e) { /* 무시 */ }
}

// ── 공모전 목록 ───────────────────────────────────
async function fetchCompetitions() {
  if (state.loading) return;
  state.loading = true;
  showLoading();

  const params = new URLSearchParams({ sort: state.sort, limit: 80, offset: 0 });
  if (state.category && state.category !== "전체") params.set("category", state.category);
  if (state.source)  params.set("source", state.source);
  if (state.search)  params.set("search", state.search);

  try {
    const res  = await fetch(`${API}/api/competitions?${params}`);
    const data = await res.json();
    state.total = data.total;
    renderList(data.items);
    document.getElementById("resultCount").textContent = data.total;
  } catch (e) {
    showEmpty("데이터를 불러오지 못했습니다. 서버가 실행 중인지 확인하세요.");
  } finally {
    state.loading = false;
  }
}

// ── 리스트 렌더링 ─────────────────────────────────
function renderList(items) {
  const wrap = document.getElementById("listWrap");

  if (!items || !items.length) {
    showEmpty("조건에 맞는 공모전이 없습니다.");
    return;
  }

  wrap.innerHTML = items.map(item => {
    const icon      = CAT_ICONS[item.category] || "💻";
    const dday      = getDday(item.days_left);
    const srcKey    = item.source_site || "linkareer";
    const srcLabel  = SOURCE_LABEL[srcKey] || srcKey;
    const expired   = item.days_left !== null && item.days_left < 0;
    const thumbHtml = item.thumbnail
      ? `<img src="${escHtml(item.thumbnail)}" alt="" onerror="this.style.display='none'; this.nextSibling.style.display='flex';">
         <span style="display:none">${icon}</span>`
      : icon;
    const deadlineText = item.deadline
      ? `${item.deadline.slice(5).replace("-", "/")} 마감`
      : "마감일 미정";
    const orgText = item.organization ? `🏢 ${escHtml(item.organization)}` : "";
    const isNew   = item.days_left !== null && item.days_left >= 0 && isRecentItem(item);

    return `
    <a class="row-card${expired ? " expired" : ""}"
       href="${escHtml(item.source_url || item.original_url || "#")}"
       target="_blank" rel="noopener noreferrer">
      <div class="row-icon">${thumbHtml}</div>
      <div class="row-main">
        <div class="row-top">
          ${isNew ? '<span class="new-dot" title="최근 등록"></span>' : ""}
          <span class="row-title">${escHtml(item.title)}</span>
          <span class="row-cat">${escHtml(item.category || "기타IT")}</span>
        </div>
        <div class="row-org">${orgText}</div>
      </div>
      <div class="row-meta">
        <span class="src-badge badge-${escHtml(srcKey)}">${escHtml(srcLabel)}</span>
        <div class="deadline-wrap">
          <div class="deadline-date">${deadlineText}</div>
          <div class="dday ${dday.cls}">${dday.text}</div>
        </div>
      </div>
    </a>`;
  }).join("");
}

// ── D-day 계산 ────────────────────────────────────
function getDday(daysLeft) {
  if (daysLeft === null || daysLeft === undefined)
    return { text: "미정",        cls: "dday-gray" };
  if (daysLeft < 0)
    return { text: "마감",        cls: "dday-gray" };
  if (daysLeft === 0)
    return { text: "오늘 마감!",  cls: "dday-red"  };
  if (daysLeft <= 3)
    return { text: `D-${daysLeft}`, cls: "dday-red"    };
  if (daysLeft <= 7)
    return { text: `D-${daysLeft}`, cls: "dday-yellow" };
  return   { text: `D-${daysLeft}`, cls: "dday-green"  };
}

// 최근 등록 여부 (crawled_at 기반으로 3일 이내인 항목 — 실제론 서버가 판단)
function isRecentItem(item) {
  if (!item.crawled_at) return false;
  const diff = (Date.now() - new Date(item.crawled_at).getTime()) / 86400000;
  return diff <= 3;
}

// ── 카테고리 선택 ─────────────────────────────────
function selectCat(btn) {
  state.category = btn.dataset.cat;
  document.querySelectorAll(".cat-btn").forEach(b => b.classList.remove("active"));
  btn.classList.add("active");
  fetchCompetitions();
}

// ── 출처 선택 ─────────────────────────────────────
function selectSource(btn) {
  const id = btn.dataset.src;
  if (state.source === id) {
    state.source = null;
    btn.classList.remove("active");
  } else {
    state.source = id;
    document.querySelectorAll(".src-chip").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
  }
  fetchCompetitions();
}

// ── 정렬 ─────────────────────────────────────────
function setSort(sort, btn) {
  state.sort = sort;
  document.querySelectorAll(".sort-btn").forEach(b => b.classList.remove("active"));
  btn.classList.add("active");
  fetchCompetitions();
}

// ── 수동 갱신 (크롤링 트리거) ─────────────────────
async function refreshData() {
  try {
    const res  = await fetch(`${API}/api/refresh`, { method: "POST" });
    const data = await res.json();
    showToast(data.message || "크롤링을 시작했습니다. 잠시 후 새로고침 해주세요.");
    setTimeout(async () => {
      await Promise.all([loadCategories(), loadSources(), loadStats()]);
      fetchCompetitions();
    }, 5000);
  } catch (e) {
    showToast("서버 연결에 실패했습니다.");
  }
}

// ── UI 유틸 ──────────────────────────────────────
function showLoading() {
  document.getElementById("listWrap").innerHTML = `
    <div class="loading">
      <div class="spinner"></div>
      <p>공모전 정보를 불러오는 중...</p>
    </div>`;
}

function showEmpty(msg) {
  document.getElementById("listWrap").innerHTML = `
    <div class="empty">
      <div class="empty-icon">🔍</div>
      <p>${msg}</p>
    </div>`;
}

function showToast(msg) {
  const t = document.getElementById("toast");
  t.textContent = msg;
  t.classList.add("show");
  setTimeout(() => t.classList.remove("show"), 3000);
}

function escHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}
