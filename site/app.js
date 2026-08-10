const OWNER = "BlockChain-BailBonds";
const REPO = "ViewerRank";
const API = `https://api.github.com/repos/${OWNER}/${REPO}`;
const REFRESH_MS = 10 * 60 * 1000;

const $ = (id) => document.getElementById(id);

function formatNumber(value) {
  return new Intl.NumberFormat().format(value ?? 0);
}

function relativeTime(dateString) {
  const then = new Date(dateString).getTime();
  const seconds = Math.max(1, Math.floor((Date.now() - then) / 1000));
  const ranges = [
    [31536000, "year"], [2592000, "month"], [604800, "week"],
    [86400, "day"], [3600, "hour"], [60, "minute"], [1, "second"],
  ];
  for (const [size, unit] of ranges) {
    if (seconds >= size) {
      const n = Math.floor(seconds / size);
      return `${n} ${unit}${n === 1 ? "" : "s"} ago`;
    }
  }
  return "just now";
}

async function getJson(url) {
  const response = await fetch(url, {
    headers: { Accept: "application/vnd.github+json" },
    cache: "no-store",
  });
  const remaining = response.headers.get("x-ratelimit-remaining");
  if (remaining !== null) $("rateLimit").textContent = remaining;
  if (!response.ok) throw new Error(`${response.status} ${response.statusText}`);
  return response.json();
}

function setCi(run) {
  const node = $("ciStatus");
  node.className = "status-text";
  if (!run) {
    node.textContent = "No runs";
    $("ciDetail").textContent = "latest workflow";
    return;
  }
  if (run.status !== "completed") {
    node.textContent = "Running";
    node.classList.add("progress");
  } else if (run.conclusion === "success") {
    node.textContent = "Passing";
    node.classList.add("success");
  } else {
    node.textContent = run.conclusion || "Failed";
    node.classList.add("failure");
  }
  $("ciDetail").textContent = `${run.name} · ${relativeTime(run.updated_at)}`;
}

function renderCommits(commits) {
  const root = $("commits");
  root.replaceChildren();
  if (!commits.length) {
    const empty = document.createElement("div");
    empty.className = "empty";
    empty.textContent = "No commits found.";
    root.appendChild(empty);
    return;
  }
  commits.slice(0, 5).forEach((item) => {
    const row = document.createElement("a");
    row.className = "feed-item";
    row.href = item.html_url;
    row.target = "_blank";
    row.rel = "noreferrer";

    const main = document.createElement("div");
    const title = document.createElement("div");
    title.className = "feed-title";
    title.textContent = item.commit.message.split("\n")[0];
    const meta = document.createElement("div");
    meta.className = "feed-meta";
    meta.textContent = `${item.commit.author?.name || "unknown"} · ${relativeTime(item.commit.author?.date)}`;
    main.append(title, meta);

    const badge = document.createElement("span");
    badge.className = "badge";
    badge.textContent = item.sha.slice(0, 7);
    row.append(main, badge);
    root.appendChild(row);
  });
}

function renderPulls(pulls) {
  const root = $("pulls");
  root.replaceChildren();
  if (!pulls.length) {
    const empty = document.createElement("div");
    empty.className = "empty";
    empty.textContent = "No open pull requests.";
    root.appendChild(empty);
    return;
  }
  pulls.slice(0, 5).forEach((item) => {
    const row = document.createElement("a");
    row.className = "feed-item";
    row.href = item.html_url;
    row.target = "_blank";
    row.rel = "noreferrer";

    const main = document.createElement("div");
    const title = document.createElement("div");
    title.className = "feed-title";
    title.textContent = item.title;
    const meta = document.createElement("div");
    meta.className = "feed-meta";
    meta.textContent = `#${item.number} · ${item.user?.login || "unknown"} · updated ${relativeTime(item.updated_at)}`;
    main.append(title, meta);

    const badge = document.createElement("span");
    badge.className = "badge";
    badge.textContent = item.draft ? "DRAFT" : "OPEN";
    row.append(main, badge);
    root.appendChild(row);
  });
}

async function refresh() {
  const button = $("refreshButton");
  button.disabled = true;
  button.textContent = "Refreshing…";
  try {
    const [repo, pulls, runs, commits] = await Promise.all([
      getJson(API),
      getJson(`${API}/pulls?state=open&sort=updated&direction=desc&per_page=6`),
      getJson(`${API}/actions/runs?branch=main&per_page=5`),
      getJson(`${API}/commits?sha=main&per_page=5`),
    ]);

    $("stars").textContent = formatNumber(repo.stargazers_count);
    $("forks").textContent = formatNumber(repo.forks_count);
    $("openPrs").textContent = formatNumber(pulls.length);
    setCi(runs.workflow_runs?.[0]);
    renderCommits(commits);
    renderPulls(pulls);
    $("lastUpdated").textContent = new Date().toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
  } catch (error) {
    console.error("ViewerRank live refresh failed", error);
    $("lastUpdated").textContent = "refresh failed";
  } finally {
    button.disabled = false;
    button.textContent = "Refresh live data";
  }
}

$("refreshButton").addEventListener("click", refresh);
document.addEventListener("visibilitychange", () => {
  if (document.visibilityState === "visible") refresh();
});

refresh();
setInterval(refresh, REFRESH_MS);
