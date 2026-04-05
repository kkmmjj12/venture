const API = "";  // 같은 서버에서 서빙

// 상태
let state = {
  category: "전체",
  sort: "latest",
  source: null,
  search: "",
  items: [],
  total: 0,
  loading: false,
};

const GRADIENTS = [
  "thumb-gradient-1","thumb-gradient-2","thumb-gradient-3","thumb-gradient-4",
  "thumb-gradient-5","thumb-gradient-6","thumb-gradient-7","thumb-gradient-8",
];
const CAT_ICONS = {
  "AI/머신러닝": "🤖", "빅데이터": "📊", "데이터": "🗃️",
  "앱개발": "📱", "웹개발": "🌐", "IoT/임베디드": "🔌",
  "게임/VR": "🎮", "보안/해킹": "🔒", "블록체인": "⛓️",
  "UI/UX": "🎨", "기타IT": "💻", "전체": "🏆",
};
const SOURCE_LABEL = {
  linkareer: "링커리어", wevity: "위비티",
  thinkgood: "씽굿", gonmofair: "공모전박람회",
};

// ── 초기화 ──
document.addEventListener("DOMContentLoaded", async () => {
  await loadCategories();
  await loadSources();
  await fetchCompetitions();
  loadStats();
  bindEvents();
});

function bindEvents() {
  document.getElementById("searchInput").addEventListener("keydown", e => {
    if (e.key === "Enter") doSearch();
  });
  document.getElementById("searchBtn").addEventListener("click", doSearch);
}

// ── 검색 ──
function doSearch() {
  state.search = document.getElementById("searchInput").value.trim();
  fetchCompetitions();
}

// ── 카테고리 로드 ──
async function loadCategories() {
  try {
    const res = await fetch(`${API}/api/categories`);
    const cats = await res.json();
    const container = document.getElementById("categoryTabs");
    container.innerHTML = cats.map(c => `
      <button class="cat-tab ${c.name === state.category ? "active" : ""}"
        onclick="selectCategory('${c.name}')">
        ${CAT_ICONS[c.name] || "📌"} ${c.name}
        <span class="count">${c.count}</span>
      </button>
    `).join("");
  } catch (e) {
    console.error("카테고리 로드 실패:", e);
  }
}

// ── 출처 필터 로드 ──
async function loadSources() {
  try {
    const res = await fetch(`${API}/api/sources`);
    const sources = await res.json();
    const container = document.getElementById("sourceFilters");
    container.innerHTML = sources.map(s => `
      <button class="source-chip" data-src="${s.id}"
        onclick="selectSource('${s.id}')">
        ${s.name} <small>(${s.count})</small>
      </button>
    `).join("");
  } catch (e) {}
}

// ── 통계 ──
async function loadStats() {
  try {
    const res = await fetch(`${API}/api/stats`);
    const data = await res.json();
    document.getElementById("statTotal").textContent = data.total;
    document.getElementById("statClosing").textContent = data.closing_soon;
  } catch (e) {}
}

// ── 공모전 목록 로드 ──
async function fetchCompetitions() {
  if (state.loading) return;
  state.loading = true;
  showLoading();

  const params = new URLSearchParams({
    sort: state.sort,
    limit: 60,
    offset: 0,
  });
  if (state.category && state.category !== "전체") params.set("category", state.category);
  if (state.source) params.set("source", state.source);
  if (state.search) params.set("search", state.search);

  try {
    const res = await fetch(`${API}/api/competitions?${params}`);
    const data = await res.json();
    state.items = data.items;
    state.total = data.total;
    renderGrid();
    updateResultCount();
  } catch (e) {
    showEmpty("데이터를 불러오지 못했습니다. 서버를 확인해주세요.");
  } finally {
    state.loading = false;
  }
}

// ── 카테고리 선택 ──
function selectCategory(cat) {
  state.category = cat;
  document.querySelectorAll(".cat-tab").forEach(el => {
    el.classList.toggle("active", el.textContent.includes(cat));
  });
  fetchCompetitions();
}

// ── 출처 선택 ──
function selectSource(srcId) {
  if (state.source === srcId) {
    state.source = null;
  } else {
    state.source = srcId;
  }
  document.querySelectorAll(".source-chip").forEach(el => {
    el.classList.toggle("active", el.dataset.src === state.source);
  });
  fetchCompetitions();
}

// ── 정렬 ──
function setSort(sort) {
  state.sort = sort;
  document.querySelectorAll(".sort-btn").forEach(el => {
    el.classList.toggle("active", el.dataset.sort === sort);
  });
  fetchCompetitions();
}

// ── 카드 렌더링 ──
function renderGrid() {
  const grid = document.getElementById("grid");
  if (!state.items.length) {
    showEmpty("해당 조건의 공모전이 없습니다.");
    return;
  }

  grid.innerHTML = state.items.map((item, idx) => {
    const grad = GRADIENTS[idx % GRADIENTS.length];
    const dday = getDdayBadge(item.days_left);
    const srcBadge = getSourceBadge(item.source_site);
    const catIcon = CAT_ICONS[item.category] || "💻";
    const thumbHtml = item.thumbnail
      ? `<img src="${escHtml(item.thumbnail)}" alt="" onerror="this.style.display='none'; this.parentElement.classList.add('${grad}'); this.parentElement.querySelector('.card-thumb-placeholder').style.display='flex';">`
      : "";
    const orgText = item.organization ? `🏢 ${escHtml(item.organization)}` : "";
    const deadlineText = item.deadline
      ? `마감 <strong>${item.deadline}</strong>`
      : "마감일 미정";

    return `
    <a class="card" href="${escHtml(item.source_url)}" target="_blank" rel="noopener">
      <div class="card-thumb ${item.thumbnail ? "" : grad}">
        ${thumbHtml}
        <span class="card-thumb-placeholder" style="display:${item.thumbnail ? "none" : "flex"}">${catIcon}</span>
        ${dday}
        ${srcBadge}
      </div>
      <div class="card-body">
        <div class="card-category">${catIcon} ${escHtml(item.category || "기타IT")}</div>
        <div class="card-title">${escHtml(item.title)}</div>
        <div class="card-org">${orgText}</div>
        <div class="card-footer">
          <div class="deadline-info">${deadlineText}</div>
          <span class="btn-detail">자세히 보기 →</span>
        </div>
      </div>
    </a>`;
  }).join("");
}

function getDdayBadge(daysLeft) {
  if (daysLeft === null || daysLeft === undefined) return `<span class="dday-badge dday-gray">마감일미정</span>`;
  if (daysLeft < 0) return `<span class="dday-badge dday-gray">종료</span>`;
  if (daysLeft === 0) return `<span class="dday-badge dday-red">오늘마감!</span>`;
  if (daysLeft <= 3) return `<span class="dday-badge dday-red">D-${daysLeft}</span>`;
  if (daysLeft <= 7) return `<span class="dday-badge dday-orange">D-${daysLeft}</span>`;
  if (daysLeft <= 14) return `<span class="dday-badge dday-yellow">D-${daysLeft}</span>`;
  return `<span class="dday-badge dday-green">D-${daysLeft}</span>`;
}

function getSourceBadge(source) {
  const label = SOURCE_LABEL[source] || source;
  return `<span class="source-badge badge-${source || "linkareer"}">${label}</span>`;
}

function updateResultCount() {
  const el = document.getElementById("resultCount");
  if (el) el.innerHTML = `총 <strong>${state.total}</strong>개의 공모전`;
}

// ── 수동 새로고침 ──
async function refreshData() {
  try {
    const res = await fetch(`${API}/api/refresh`, { method: "POST" });
    const data = await res.json();
    showToast(data.message || "크롤링을 시작했습니다.");
    setTimeout(() => {
      fetchCompetitions();
      loadCategories();
      loadSources();
      loadStats();
    }, 4000);
  } catch (e) {
    showToast("새로고침에 실패했습니다.");
  }
}

// ── Discord 테스트 ──
async function discordTest() {
  try {
    const res = await fetch(`${API}/api/discord/test`, { method: "POST" });
    const data = await res.json();
    showToast(data.message || data.error || "Discord 테스트 완료");
  } catch (e) {
    showToast("Discord 연결 테스트 실패");
  }
}

// ── Discord 수동 알림 ──
async function discordNotify() {
  try {
    const res = await fetch(`${API}/api/discord/notify`, { method: "POST" });
    const data = await res.json();
    showToast(data.message || data.error || "Discord 알림 전송 완료");
  } catch (e) {
    showToast("Discord 알림 전송 실패");
  }
}

// ── 유틸 ──
function showLoading() {
  document.getElementById("grid").innerHTML = `
    <div class="loading" style="grid-column:1/-1">
      <div class="spinner"></div>
      공모전 정보를 불러오는 중...
    </div>`;
}

function showEmpty(msg) {
  document.getElementById("grid").innerHTML = `
    <div class="empty" style="grid-column:1/-1">
      <div class="empty-icon">🔍</div>
      <div>${msg}</div>
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
