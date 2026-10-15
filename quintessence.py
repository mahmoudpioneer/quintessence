#!/usr/bin/env python3
"""Quintessence installer: build, install, update, test and uninstall on macOS, Linux and Windows.

    python3 quintessence.py update      # fetch the five toolkits, build, install, smoke-test
    python3 quintessence.py install     # build + install from toolkits already in vendor/
    python3 quintessence.py build       # assemble dist/ only
    python3 quintessence.py test        # verify an install
    python3 quintessence.py uninstall   # remove the skill and the agents it installed

Environment: INSTALL_DIR (default ~/.claude/skills/quintessence), AGENTS_DIR (default ~/.claude/agents),
QUINTESSENCE_SKIP_CAPTURE=1 to skip the browser test. Standard library only; needs git and Python 3.9+.
"""
import datetime
import json
import os
import shutil
import stat
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent
VENDOR = ROOT / "vendor"
DIST = ROOT / "dist"
WINDOWS = os.name == "nt"
HOME = Path.home()
INSTALL_DIR = Path(os.environ.get("INSTALL_DIR") or HOME / ".claude" / "skills" / "quintessence")
AGENTS_DIR = Path(os.environ.get("AGENTS_DIR") or HOME / ".claude" / "agents")

REPOS = {
    "uupm": "nextlevelbuilder/ui-ux-pro-max-skill",
    "impeccable": "pbakaus/impeccable",
    "emil": "emilkowalski/skills",
    "forever": "isas1/forever-ai-components",
    "taste": "leonxlnx/taste-skill",
}
EMIL_SKILLS = ["emil-design-eng", "animate", "review-animations", "improve-animations", "find-animation-opportunities",
               "animation-vocabulary", "apple-design", "mobile-native", "pick-ui-library", "prototype", "ask-sonner"]
TASTE_SKILLS = ["taste-skill", "minimalist-skill", "soft-skill", "brutalist-skill", "redesign-skill", "stitch-skill", "output-skill"]
UUPM_EXTRAS = ["design-system", "ui-styling", "brand", "banner-design", "slides", "design"]
AGENT_NAMES = ["impeccable-finish-reviewer", "impeccable-documenter", "impeccable-asset-producer", "impeccable-manual-edit-applier"]
IGNORE = shutil.ignore_patterns(".git", "tests", "__pycache__", ".DS_Store")
AGENT_MARK = "<!-- installed by Quintessence; uninstall with quintessence.py uninstall -->"

SH_PATCH = """# --- Quintessence patch: privacy defaults ---
export IMPECCABLE_NO_TELEMETRY="${IMPECCABLE_NO_TELEMETRY:-1}" DO_NOT_TRACK="${DO_NOT_TRACK:-1}" IMPECCABLE_NO_UPDATE_CHECK="${IMPECCABLE_NO_UPDATE_CHECK:-1}"
if [ "${QUINTESSENCE_OFFLINE:-0}" = 1 ]; then export IMPECCABLE_API_URL="http://127.0.0.1:9/api"; fi
# --- end patch ---
"""
CMD_PATCH = """rem --- Quintessence patch: privacy defaults ---
if not defined IMPECCABLE_NO_TELEMETRY set "IMPECCABLE_NO_TELEMETRY=1"
if not defined DO_NOT_TRACK set "DO_NOT_TRACK=1"
if not defined IMPECCABLE_NO_UPDATE_CHECK set "IMPECCABLE_NO_UPDATE_CHECK=1"
if "%QUINTESSENCE_OFFLINE%"=="1" set "IMPECCABLE_API_URL=http://127.0.0.1:9/api"
rem --- end patch ---
"""


def repo_dir(key):
    return VENDOR / REPOS[key].replace("/", "_")


def posix(p):
    """Forward-slash path: works in docs, Git Bash and Python on every OS."""
    return Path(p).as_posix()


def run(cmd, **kw):
    kw.setdefault("check", True)
    return subprocess.run(cmd, **kw)


def rmtree(path):
    def on_error(func, p, _exc):
        os.chmod(p, stat.S_IWRITE)  # Windows marks git objects read-only
        func(p)
    if Path(path).exists():
        if sys.version_info >= (3, 12):
            shutil.rmtree(path, onexc=on_error)
        else:
            shutil.rmtree(path, onerror=on_error)


def copy(src, dst):
    shutil.copytree(src, dst, ignore=IGNORE, dirs_exist_ok=True)


def edit(path, fn):
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    p.write_text(fn(text), encoding="utf-8", newline="")


def launcher():
    scripts = INSTALL_DIR / "modules" / "impeccable" / "scripts"
    return [ "cmd", "/c", str(scripts / "impeccable.cmd")] if WINDOWS else [str(scripts / "impeccable")]


# ---------------------------------------------------------------- build

def build():
    for key in REPOS:
        if not (repo_dir(key) / ".git").exists():
            sys.exit(f"missing {repo_dir(key)} — run: python3 quintessence.py update")
    out, agents_out = DIST / "quintessence", DIST / "agents"
    rmtree(out)
    rmtree(agents_out)
    (out / "modules").mkdir(parents=True)
    (out / "LICENSES").mkdir()
    agents_out.mkdir(parents=True)

    shutil.copy2(ROOT / "src" / "SKILL.md", out / "SKILL.md")
    copy(ROOT / "src" / "scripts", out / "scripts")

    # ui-ux-pro-max + extras; point plugin-root paths at the install dir, fix the python command per OS.
    uupm = repo_dir("uupm") / ".claude" / "skills"
    copy(uupm / "ui-ux-pro-max", out / "modules" / "ui-ux-pro-max")
    for s in UUPM_EXTRAS:
        copy(uupm / s, out / "modules" / f"uupm-{s}")
    py = "python" if WINDOWS else "python3"
    for skill_md in [out / "modules" / "ui-ux-pro-max" / "SKILL.md", *(out / "modules").glob("uupm-*/SKILL.md")]:
        def fix(t):
            t = t.replace("${CLAUDE_PLUGIN_ROOT}/.claude/skills/ui-ux-pro-max", posix(INSTALL_DIR / "modules" / "ui-ux-pro-max"))
            lines = []
            for line in t.split("\n"):
                if line.startswith('python "') or line.startswith("python scripts/") or line.startswith("python3 "):
                    line = py + line[line.index(" "):]
                lines.append(line)
            return "\n".join(lines)
        edit(skill_md, fix)

    # impeccable + privacy patch on both launchers
    copy(repo_dir("impeccable") / ".claude" / "skills" / "impeccable", out / "modules" / "impeccable")
    scripts = out / "modules" / "impeccable" / "scripts"

    def patch_sh(t):
        t = t.replace("\r\n", "\n")
        if "\nset -eu\n" not in t:
            sys.exit("impeccable's launcher changed upstream; update SH_PATCH placement in quintessence.py")
        return t.replace("\nset -eu\n", "\nset -eu\n" + SH_PATCH, 1)

    def patch_cmd(t):
        t = t.replace("\r\n", "\n")
        if "\nsetlocal\n" not in t:
            sys.exit("impeccable's Windows launcher changed upstream; update CMD_PATCH placement in quintessence.py")
        return t.replace("\nsetlocal\n", "\nsetlocal\n" + CMD_PATCH, 1).replace("\n", "\r\n")

    edit(scripts / "impeccable", patch_sh)
    edit(scripts / "impeccable.cmd", patch_cmd)
    os.chmod(scripts / "impeccable", 0o755)

    # impeccable's subagents, pointed at the installed launcher
    for a in (repo_dir("impeccable") / ".claude" / "agents").glob("impeccable-*.md"):
        text = a.read_text(encoding="utf-8").replace(".claude/skills/impeccable/", posix(INSTALL_DIR / "modules" / "impeccable") + "/")
        (agents_out / a.name).write_text(text.rstrip("\n") + "\n\n" + AGENT_MARK + "\n", encoding="utf-8", newline="")

    # emil + taste
    for s in EMIL_SKILLS:
        copy(repo_dir("emil") / "skills" / s, out / "modules" / "emil" / s)
    shutil.copy2(repo_dir("emil") / "performance-cheatsheet.md", out / "modules" / "emil")
    for s in TASTE_SKILLS:
        copy(repo_dir("taste") / "skills" / s, out / "modules" / "taste" / s)

    # forever: wrapper + component library
    copy(ROOT / "src" / "modules" / "forever", out / "modules" / "forever")
    copy(repo_dir("forever") / "infinite", out / "modules" / "forever" / "infinite")

    for p in [*(out / "scripts").iterdir(), out / "modules" / "forever" / "scripts" / "forever_search.py"]:
        os.chmod(p, 0o755)

    lic = out / "LICENSES"
    for src, name in [(repo_dir("uupm") / "LICENSE", "ui-ux-pro-max.MIT.txt"),
                      (repo_dir("impeccable") / "LICENSE", "impeccable.Apache-2.0.txt"),
                      (repo_dir("impeccable") / "NOTICE.md", "impeccable.NOTICE.md"),
                      (repo_dir("emil") / "LICENSE", "emilkowalski-skills.MIT.txt"),
                      (repo_dir("forever") / "LICENSE", "forever-ai-components.MIT.txt"),
                      (repo_dir("forever") / "NOTICE.md", "forever-ai-components.NOTICE.md"),
                      (repo_dir("taste") / "LICENSE", "taste-skill.MIT.txt")]:
        shutil.copy2(src, lic / name)

    def git(key, *args):
        return run(["git", "-C", str(repo_dir(key)), *args], capture_output=True, text=True).stdout.strip()
    rows = "\n".join(f"| {k} | {git(k, 'remote', 'get-url', 'origin')} | {git(k, 'rev-parse', '--short', 'HEAD')} |" for k in REPOS)
    (out / "SOURCES.md").write_text(
        f"# Upstream sources\n\nBuilt {datetime.datetime.now(datetime.timezone.utc):%Y-%m-%dT%H:%MZ} on {sys.platform}. "
        "Modules are copied unmodified except:\n"
        "- ui-ux-pro-max SKILL.md paths rewritten to the install dir; the python command matches this OS.\n"
        "- impeccable's launchers (`scripts/impeccable`, `scripts/impeccable.cmd`) get a privacy patch: telemetry and update "
        "check off, `QUINTESSENCE_OFFLINE=1` for an offline concept roll.\n"
        "- impeccable's agents (installed to the agents dir) point at this install's launcher.\n\n"
        f"| Module | Repo | Commit |\n|---|---|---|\n{rows}\n", encoding="utf-8")

    size = sum(f.stat().st_size for f in out.rglob("*") if f.is_file()) / 1e6
    print(f"built {out} ({size:.0f} MB) + {len(list(agents_out.iterdir()))} agents")


# ---------------------------------------------------------------- install / uninstall

def install():
    build()
    manifest = INSTALL_DIR / ".installed-agents"
    prior_agents = set(manifest.read_text(encoding="utf-8").split()) if manifest.exists() else set()
    rmtree(INSTALL_DIR)
    INSTALL_DIR.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(DIST / "quintessence", INSTALL_DIR)
    AGENTS_DIR.mkdir(parents=True, exist_ok=True)
    installed = []
    for a in sorted((DIST / "agents").iterdir()):
        dest = AGENTS_DIR / a.name
        built = a.read_text(encoding="utf-8")
        unmarked = built.replace("\n\n" + AGENT_MARK + "\n", "\n")  # what pre-marker installs wrote
        current = dest.read_text(encoding="utf-8") if dest.exists() else None
        ours = current is None or AGENT_MARK in current or current == unmarked or a.name in prior_agents
        if not ours:
            print(f"skipping {a.name}: {dest} exists and wasn't installed by Quintessence", file=sys.stderr)
            continue
        shutil.copy2(a, dest)
        installed.append(a.name)
    (INSTALL_DIR / ".installed-agents").write_text("\n".join(installed) + "\n", encoding="utf-8")
    print(f"installed → {INSTALL_DIR} (+ {len(installed)} agents in {AGENTS_DIR})")

    old = INSTALL_DIR.parent / "design-max"
    if old.exists():
        rmtree(old)
        print("removed old design-max install")

    probe = run(launcher() + ["engine-probe"], check=False, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if probe.returncode == 0 and "impeccable-engine" in probe.stdout:
        print(f"impeccable engine ready ({probe.stdout.strip()})")
    else:
        print("warning: impeccable engine unavailable — Quintessence still works, minus the deterministic detector\n"
              + (probe.stderr or probe.stdout).strip()[-400:], file=sys.stderr)

    for cmd, label in [([str(INSTALL_DIR / "modules" / "ui-ux-pro-max" / "scripts" / "search.py"), "saas dashboard", "--domain", "style", "-n", "1"], "ui-ux-pro-max search"),
                       ([str(INSTALL_DIR / "modules" / "forever" / "scripts" / "forever_search.py"), "loader", "--perf", "cheap", "-n", "1"], "forever search")]:
        ok = run([sys.executable, *cmd], check=False, capture_output=True).returncode == 0
        print(f"{label} {'OK' if ok else 'FAILED'}")
    print("Done. Start a new Claude Code session and run /quintessence")


def uninstall():
    manifest = INSTALL_DIR / ".installed-agents"
    if manifest.exists():
        for name in manifest.read_text(encoding="utf-8").split():
            f = AGENTS_DIR / name
            if f.exists() and AGENT_MARK in f.read_text(encoding="utf-8"):
                f.unlink()
                print(f"removed agent {name}")
    rmtree(INSTALL_DIR)
    print(f"removed {INSTALL_DIR}")
    print("The impeccable engine cache in ~/.impeccable was left in place; delete it yourself if you no longer need it.")


def update():
    VENDOR.mkdir(exist_ok=True)
    for key, slug in REPOS.items():
        d = repo_dir(key)
        if (d / ".git").exists():
            run(["git", "-C", str(d), "pull", "-q", "--ff-only"])
        else:
            # Keep upstream line endings: a CRLF shell launcher breaks under Git Bash on Windows.
            run(["git", "clone", "-q", "--depth", "1", "-c", "core.autocrlf=false", f"https://github.com/{slug}.git", str(d)])
        sha = run(["git", "-C", str(d), "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
        print(f"{slug} @ {sha}")
    install()


# ---------------------------------------------------------------- test

def png_size(path):
    with open(path, "rb") as f:
        head = f.read(24)
    if head[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"{path} is not a PNG")
    return struct.unpack(">II", head[16:24])


def test():
    passed, failed, skipped = 0, 0, 0
    tmp = Path(tempfile.mkdtemp(prefix="qtest-"))
    env = dict(os.environ, PYTHONUTF8="1")

    def check(name, fn):
        nonlocal passed, failed
        try:
            ok = fn()
        except Exception as e:  # noqa: BLE001 — a test harness reports every failure the same way
            ok, err = False, e
        else:
            err = None
        if ok:
            print(f"PASS  {name}")
            passed += 1
        else:
            print(f"FAIL  {name}" + (f"\n      {type(err).__name__}: {err}" if err else ""))
            failed += 1

    def skip(name, why):
        nonlocal skipped
        print(f"SKIP  {name} ({why})")
        skipped += 1

    def out(cmd, cwd=None, extra_env=None):
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=cwd,
                           env=dict(env, **(extra_env or {})))
        return r.stdout + r.stderr

    q = INSTALL_DIR
    py = sys.executable

    print(f"== Install structure ({q})")
    check("router SKILL.md has name: quintessence", lambda: "\nname: quintessence\n" in (q / "SKILL.md").read_text(encoding="utf-8"))
    check("old design-max install removed", lambda: not (q.parent / "design-max").exists())
    for a in AGENT_NAMES:
        check(f"agent {a} installed", lambda a=a: f"name: {a}" in (AGENTS_DIR / f"{a}.md").read_text(encoding="utf-8"))
    check("agents carry the Quintessence marker", lambda: all(AGENT_MARK in (AGENTS_DIR / f"{a}.md").read_text(encoding="utf-8") for a in AGENT_NAMES))
    check("agents point at this install's launcher",
          lambda: all(".claude/skills/impeccable/" not in (AGENTS_DIR / f"{a}.md").read_text(encoding="utf-8") for a in AGENT_NAMES))
    modules = (["ui-ux-pro-max", "impeccable", "forever"] + [f"uupm-{s}" for s in UUPM_EXTRAS]
               + [f"emil/{s}" for s in EMIL_SKILLS] + [f"taste/{s}" for s in TASTE_SKILLS])
    for m in modules:
        check(f"module {m} has SKILL.md", lambda m=m: (q / "modules" / m / "SKILL.md").stat().st_size > 0)
    check("no unresolved ${CLAUDE_PLUGIN_ROOT} in module docs",
          lambda: not any("CLAUDE_PLUGIN_ROOT" in f.read_text(encoding="utf-8") for f in (q / "modules").rglob("SKILL.md")))
    check("forever library has 600+ components", lambda: len(list((q / "modules" / "forever" / "infinite").rglob("*.html"))) >= 600)
    check("licenses bundled (7 files)", lambda: len(list((q / "LICENSES").iterdir())) >= 7)

    print("== ui-ux-pro-max")
    uu = [py, str(q / "modules" / "ui-ux-pro-max" / "scripts" / "search.py")]
    check("design-system generator", lambda: "TYPOGRAPHY" in out(uu + ["fintech dashboard dark", "--design-system", "-p", "Test"]))
    check("style domain search", lambda: "glass" in out(uu + ["glassmorphism", "--domain", "style", "-n", "2"]).lower())
    check("ux domain search", lambda: "focus" in out(uu + ["keyboard focus modal", "--domain", "ux", "-n", "2"]).lower())
    check("stack search (nextjs)", lambda: "suspense" in out(uu + ["suspense streaming", "--stack", "nextjs", "-n", "2"]).lower())
    check("json output parses", lambda: json.loads(out(uu + ["saas", "--domain", "color", "--json"])) is not None)

    print("== forever")
    fs = [py, str(q / "modules" / "forever" / "scripts" / "forever_search.py")]
    check("keyword + filter search", lambda: "•" in out(fs + ["loader", "--perf", "cheap", "--label", "mobile-ready", "-n", "3"]))
    check("role/technique filter", lambda: (lambda d: d and all(c["role"] == "button" for c in d))(
        json.loads(out(fs + ["--role", "button", "--technique", "css-only", "--json"]))))
    check("--show returns agent meta", lambda: "useWhen" in out(fs + ["--show", "navigation/10-command-palette.html"]))
    check("--facets lists filters", lambda: "perfTier" in out(fs + ["--facets"]))
    check("nonsense query → no matches", lambda: "No matches" in out(fs + ["zzqqxx"]))

    print("== quintessence scripts")
    brief = [py, str(q / "scripts" / "design_brief.py")]
    swipe = "saas marketing tool ad research performance marketers landing"
    check("design brief runs", lambda: "## KEEP" in out(brief + ["saas marketing tool landing", "-p", "T"]))
    check("brief rejects Inter (detector-flagged)", lambda: "Body font Inter: impeccable" in out(brief + [swipe, "-p", "T"]))
    check("brief resolves 'no transitions' clash", lambda: "Emil" in out(brief + [swipe, "-p", "T"]))
    check("brief --json parses", lambda: {"keep", "review", "reject"} <= json.loads(out(brief + ["fintech dashboard", "--json"])).keys())

    node = shutil.which("node")
    if os.environ.get("QUINTESSENCE_SKIP_CAPTURE") == "1":
        skip("capture writes desktop + mobile", "QUINTESSENCE_SKIP_CAPTURE=1")
    elif not node:
        skip("capture writes desktop + mobile", "node not installed")
    else:
        site = tmp / "site"
        site.mkdir()
        (site / "index.html").write_text('<!doctype html><meta name=viewport content="width=device-width">'
                                         '<body style="margin:0"><div style="height:1500px;background:#234">capture test</div>',
                                         encoding="utf-8")
        cap_out = out([node, str(q / "scripts" / "capture.mjs"), (site / "index.html").as_uri(), "--out", str(tmp / "cap")])
        if "No Chrome" in cap_out:
            skip("capture writes desktop + mobile", "no Chromium-based browser installed")
        else:
            check("capture writes desktop + mobile",
                  lambda: png_size(tmp / "cap" / "mobile.png")[0] == 390 and png_size(tmp / "cap" / "desktop.png") == (1440, 1500)
                  or print(cap_out.strip()[-500:]))

    print("== impeccable")
    imp = launcher()
    check("engine handshake", lambda: "impeccable-engine" in out(imp + ["engine-probe"]))
    scripts = q / "modules" / "impeccable" / "scripts"
    check("launcher privacy patch present (sh)", lambda: 'IMPECCABLE_NO_TELEMETRY="${IMPECCABLE_NO_TELEMETRY:-1}"' in (scripts / "impeccable").read_text(encoding="utf-8"))
    check("launcher privacy patch present (cmd)", lambda: 'set "IMPECCABLE_NO_TELEMETRY=1"' in (scripts / "impeccable.cmd").read_text(encoding="utf-8"))
    check("sh launcher keeps LF line endings", lambda: b"\r\n" not in (scripts / "impeccable").read_bytes())
    (tmp / "PRODUCT.md").write_text("# Product\n\n## Platform\n\nweb\n\n## Users\n\nTest users.\n", encoding="utf-8")
    check("offline mode gives an offline roll", lambda: "source: degraded" in out(
        imp + ["concept-seed", "--scope", "direction", "--mode", "persuade"], cwd=tmp, extra_env={"QUINTESSENCE_OFFLINE": "1"}))
    (tmp / "slop.html").write_text("""<!doctype html><html><head><style>
body{font-family:Inter,sans-serif}
.hero{background:linear-gradient(135deg,#6366f1,#a855f7);padding:80px}
.hero p{color:#9ca3af}
.card{border-radius:16px;padding:24px;box-shadow:0 4px 6px rgba(0,0,0,.1);border:1px solid #e5e7eb}
</style></head><body>
<section class="hero"><h1>Supercharge Your Workflow</h1><p>Unlock AI-driven productivity</p></section>
<div class="card"><div class="card"><h3>Feature</h3><p>Sync every account automatically.</p></div></div>
</body></html>""", encoding="utf-8")
    (tmp / "clean.html").write_text("""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Ledger</title><style>
body{font-family:"Source Serif 4",Georgia,serif;background:#ffffff;color:#14212b;font-size:18px;line-height:1.6}
h1{font-size:3rem;line-height:1.1} h2{font-size:1.75rem}
</style></head><body><main><h1>Monthly ledger</h1><h2>March totals</h2><p>Income and expenses for March, grouped by account.</p></main></body></html>""",
                                    encoding="utf-8")
    slop = out(imp + ["detect", str(tmp / "slop.html")])
    check("detector flags generic page", lambda: "anti-patterns found" in slop)
    for rule in ["ai-color-palette", "overused-font", "gray-on-color", "nested-cards", "marketing-buzzword"]:
        check(f"  catches {rule}", lambda rule=rule: f"[{rule}]" in slop)
    check("detector passes clean page", lambda: "[" not in out(imp + ["detect", str(tmp / "clean.html")]))
    check("context loader runs", lambda: "RESOLVED_CONTEXT" in out(imp + ["context", "--target", "slop.html"], cwd=tmp))

    rmtree(tmp)
    print(f"\n== {passed} passed, {failed} failed" + (f", {skipped} skipped" if skipped else ""))
    return failed == 0


def main():
    cmds = {"build": build, "install": install, "update": update, "uninstall": uninstall, "test": test}
    if len(sys.argv) != 2 or sys.argv[1] not in cmds:
        sys.exit(__doc__)
    if sys.version_info < (3, 9):
        sys.exit("Quintessence needs Python 3.9 or newer.")
    if shutil.which("git") is None and sys.argv[1] in ("update", "build", "install"):
        sys.exit("git is required: https://git-scm.com/downloads")
    result = cmds[sys.argv[1]]()
    sys.exit(0 if result is not False else 1)


if __name__ == "__main__":
    main()
