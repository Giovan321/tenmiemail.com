from flask import Flask, request, render_template_string, session
from flask_socketio import SocketIO, emit, join_room, leave_room
import random, string
import psycopg2
import eventlet

app = Flask(__name__)

def get_conn():
    return psycopg2.connect(
        dbname="registros_dev",
        user="DatabaseGio",
        password="giovan12",
        host="18.218.222.117",
        port=5432
    )

html = """
<!DOCTYPE html>
<html>
<head>
<title>⚡ Pokémon Battle — Register</title>
<link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&family=Nunito:wght@400;700;900&display=swap" rel="stylesheet">
<style>
:root { --yellow:#FFD700; --orange:#FF6B00; --dark:#0d0d1a; --card:#16213e; }
* { box-sizing:border-box; margin:0; padding:0; }
body {
    font-family:'Nunito',sans-serif;
    background:var(--dark);
    color:white;
    min-height:100vh;
    text-align:center;
    padding:100px 20px 60px;
}
body::before {
    content:'';
    position:fixed; inset:0;
    background-image:
        radial-gradient(1px 1px at 15% 25%, rgba(255,255,255,0.3) 0%, transparent 100%),
        radial-gradient(1px 1px at 40% 70%, rgba(255,255,255,0.2) 0%, transparent 100%),
        radial-gradient(1px 1px at 70% 15%, rgba(255,255,255,0.3) 0%, transparent 100%),
        radial-gradient(1px 1px at 85% 60%, rgba(255,255,255,0.2) 0%, transparent 100%);
    pointer-events:none; z-index:0;
}
h1 {
    position:relative; z-index:1;
    font-family:'Press Start 2P',monospace;
    font-size:clamp(0.8rem,2.2vw,1.3rem);
    color:var(--yellow);
    text-shadow:0 0 24px rgba(255,215,0,0.5), 3px 3px 0 #b8860b;
    margin-bottom:10px;
    animation:flicker 4s infinite;
}
@keyframes flicker { 0%,94%,100%{opacity:1;} 97%{opacity:0.6;} }
.subtitle {
    position:relative; z-index:1;
    color:#666; font-size:0.9rem;
    margin-bottom:28px; letter-spacing:1px;
}
.register-form {
    position:relative; z-index:1;
    display:flex; gap:10px;
    justify-content:center; flex-wrap:wrap;
    margin-bottom:12px;
}
.register-form input {
    background:var(--card); border:2px solid #2a3050;
    color:white; padding:13px 18px; border-radius:10px;
    font-size:1rem; font-family:'Nunito',sans-serif;
    width:280px; outline:none; transition:border-color 0.2s;
}
.register-form input:focus { border-color:var(--yellow); }
.register-form button {
    background:linear-gradient(135deg,var(--orange),var(--yellow));
    color:#000; border:none; padding:13px 28px;
    border-radius:10px; font-family:'Press Start 2P',monospace;
    font-size:0.62rem; cursor:pointer;
    transition:transform 0.2s, box-shadow 0.2s;
    box-shadow:0 4px 16px rgba(255,165,0,0.4);
}
.register-form button:hover { transform:translateY(-2px); box-shadow:0 8px 24px rgba(255,165,0,0.6); }
.msg { position:relative; z-index:1; font-size:0.85rem; color:#69f0ae; margin-bottom:20px; min-height:1.2em; }
.game-banner {
    position:relative; z-index:1;
    margin:24px auto 34px;
    padding:22px 32px;
    background:linear-gradient(135deg,rgba(255,107,0,0.15),rgba(255,215,0,0.08));
    border:2px solid rgba(255,215,0,0.25);
    border-radius:18px; width:fit-content;
    animation:glow 2.5s infinite;
}
@keyframes glow {
    0%,100% { box-shadow:0 0 20px rgba(255,165,0,0.2); }
    50%      { box-shadow:0 0 40px rgba(255,165,0,0.5); }
}
.game-banner h2 {
    margin:0 0 14px 0; color:var(--yellow);
    font-size:0.72rem; font-family:'Press Start 2P',monospace;
}
.game-btn {
    display:inline-block; padding:13px 26px;
    background:linear-gradient(135deg,var(--orange),var(--yellow));
    color:#000; font-size:0.68rem; font-weight:bold;
    border-radius:10px; text-decoration:none;
    font-family:'Press Start 2P',monospace;
    transition:transform 0.2s, box-shadow 0.2s;
    box-shadow:0 4px 14px rgba(255,165,0,0.4);
}
.game-btn:hover { transform:scale(1.07) translateY(-2px); box-shadow:0 8px 24px rgba(255,165,0,0.6); }
.email-section { position:relative; z-index:1; max-width:560px; margin:0 auto; }
.section-title {
    font-family:'Press Start 2P',monospace; font-size:0.55rem;
    color:#555; letter-spacing:2px; text-transform:uppercase; margin-bottom:14px;
}
.search-box {
    background:var(--card); border:2px solid #2a3050;
    color:white; padding:11px 16px; border-radius:10px;
    font-size:0.9rem; font-family:'Nunito',sans-serif;
    width:100%; outline:none; transition:border-color 0.2s; margin-bottom:12px;
}
.search-box:focus { border-color:var(--yellow); }
.email-table {
    width:100%; border-collapse:collapse;
    background:var(--card); border-radius:14px; overflow:hidden;
}
.email-table th {
    background:rgba(255,215,0,0.08); color:var(--yellow);
    font-family:'Press Start 2P',monospace; font-size:0.52rem;
    padding:14px 18px; text-align:left; letter-spacing:1px;
    border-bottom:2px solid #2a3050;
}
.email-table td {
    padding:12px 18px; border-bottom:1px solid #1e2a4a;
    color:#aaa; font-size:0.9rem; text-align:left;
}
.email-table tr:last-child td { border-bottom:none; }
.email-table tr:hover td { background:rgba(255,215,0,0.04); color:white; }
.no-results { color:#555; font-size:0.85rem; padding:20px; }
.lb-top3 { position:relative; z-index:1; display:flex; gap:12px; justify-content:center; flex-wrap:wrap; margin:18px 0 0; }
.lb-card { background:rgba(255,215,0,0.07); border:1px solid rgba(255,215,0,0.2); border-radius:12px; padding:10px 18px; text-align:center; min-width:120px; }
.lb-rank { font-family:'Press Start 2P',monospace; font-size:1rem; margin-bottom:4px; }
.lb-name { font-size:0.82rem; font-weight:700; color:white; }
.lb-pts  { font-size:0.72rem; color:#aaa; }
</style>
</head>
<body>

<!-- COOKIE-STYLE POPUP -->
<div id="how-to-popup" style="
    position:fixed; top:50%; left:50%; transform:translate(-50%,-50%);
    z-index:99998; background:#1a1a2e;
    border:2px solid rgba(255,215,0,0.5);
    border-radius:20px; padding:40px 48px;
    max-width:680px; width:90%;
    box-shadow:0 16px 60px rgba(0,0,0,0.7);
    display:flex; flex-direction:column; align-items:center; gap:24px;
    font-family:'Nunito',sans-serif; text-align:center;
">
    <div style="width:100%;">
        <div style="font-size:1.4rem; color:#FFD700; font-weight:bold; margin-bottom:14px;">🚨 Panic Button</div>
        <div style="font-size:1.05rem; color:#ccc; line-height:1.7;">If the teacher comes, press the red button in the top-left corner — it'll switch to a boring study article instantly.</div>
    </div>
    <button onclick="document.getElementById('how-to-popup').style.display='none'" style="
        background:#ff1a1a; color:white; border:none;
        padding:14px 36px; border-radius:10px;
        font-size:1rem; font-weight:bold; cursor:pointer;
    ">Got it ✓</button>
</div>

<!-- PANIC BUTTON — TOP LEFT -->
<a href="/article" style="
    position:fixed; top:16px; left:16px; z-index:99999;
    background:#ff1a1a; color:white;
    font-family:Arial,sans-serif; font-weight:bold;
    font-size:0.95rem; padding:17px 22px;
    border-radius:10px; text-decoration:none;
    box-shadow:0 4px 20px rgba(255,26,26,0.6);
    line-height:1.5; text-align:center;
">🚨 TEACHER<br>COMING</a>

<h1>⚡ Want to play with other people?</h1>
<p class="subtitle">Enter your email so other players can challenge you!</p>

<form method="POST" class="register-form">
    <input type="email" name="email" placeholder="your@email.com" required>
    <button type="submit">REGISTER</button>
</form>
<p class="msg">{{mensaje}}</p>

<div class="game-banner">
    <h2>⚡ POKÉMON BATTLE</h2>
    <a class="game-btn" href="/game">🕹️ Local Game</a>
    &nbsp;&nbsp;
    <a class="game-btn" href="/online">🌍 Play Online</a>
    &nbsp;&nbsp;
    <a class="game-btn" href="/leaderboard" style="background:linear-gradient(135deg,#4a00e0,#8e2de2);color:white;">🏆 Leaderboard</a>
    {% if top3 %}
    <div class="lb-top3">
    {% for p in top3 %}
        <div class="lb-card">
            <div class="lb-rank">{% if loop.index == 1 %}🥇{% elif loop.index == 2 %}🥈{% else %}🥉{% endif %}</div>
            <div class="lb-name">{{ p.username }}</div>
            <div class="lb-pts">{{ p.points }} pts · {{ p.wins }}W {{ p.losses }}L</div>
        </div>
    {% endfor %}
    </div>
    {% endif %}
</div>

<div class="email-section">
    <p class="section-title">Registered Players</p>
    <input type="text" class="search-box" id="email-search" placeholder="🔍  Search emails..." oninput="filterEmails()">
    <table class="email-table" id="email-table">
        <thead><tr><th>EMAIL</th></tr></thead>
        <tbody id="email-body">
        {% for email in emails %}
        <tr><td>{{ email }}</td></tr>
        {% endfor %}
        </tbody>
    </table>
    <p class="no-results" id="no-results" style="display:none;">No emails match your search.</p>
</div>

<script>
function filterEmails() {
    const q = document.getElementById('email-search').value.toLowerCase();
    const rows = document.querySelectorAll('#email-body tr');
    let visible = 0;
    rows.forEach(row => {
        const match = row.textContent.toLowerCase().includes(q);
        row.style.display = match ? '' : 'none';
        if (match) visible++;
    });
    document.getElementById('no-results').style.display = visible === 0 ? 'block' : 'none';
}
</script>
</body>
</html>
"""

game_html = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>⚡ Pokémon Battle</title>
<link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&family=Nunito:wght@400;700;900&display=swap" rel="stylesheet">
<style>
:root {
    --yellow: #FFD700;
    --orange: #FF6B00;
    --dark:   #0d0d1a;
    --card:   #16213e;
    --pika:   #F7C948;
    --char:   #FF4500;
    --bulb:   #78C850;
}
* { box-sizing:border-box; margin:0; padding:0; }
body {
    font-family:'Nunito',sans-serif;
    background:var(--dark);
    color:white;
    min-height:100vh;
    overflow-x:hidden;
}
body::before {
    content:'';
    position:fixed; inset:0;
    background-image:
        radial-gradient(1px 1px at 10% 20%, rgba(255,255,255,0.35) 0%, transparent 100%),
        radial-gradient(1px 1px at 35% 75%, rgba(255,255,255,0.25) 0%, transparent 100%),
        radial-gradient(1px 1px at 62% 12%, rgba(255,255,255,0.35) 0%, transparent 100%),
        radial-gradient(1px 1px at 80% 55%, rgba(255,255,255,0.2)  0%, transparent 100%),
        radial-gradient(1px 1px at 90% 35%, rgba(255,255,255,0.3)  0%, transparent 100%),
        radial-gradient(1px 1px at 22% 68%, rgba(255,255,255,0.2)  0%, transparent 100%);
    pointer-events:none; z-index:0;
}

/* ── SCREENS ── */
.screen { display:none !important; position:relative; z-index:1; }
.screen.active { display:flex !important; flex-direction:column; align-items:center; justify-content:center; min-height:100vh; padding:40px 20px; }

/* ══ LOBBY ══ */
#lobby { }
.logo {
    font-family:'Press Start 2P',monospace;
    font-size:clamp(1.1rem,3.5vw,2rem);
    color:var(--yellow);
    text-shadow:0 0 30px rgba(255,215,0,0.6), 3px 3px 0 #b8860b;
    margin-bottom:8px;
    animation:flicker 4s infinite;
}
@keyframes flicker { 0%,94%,100%{opacity:1;} 97%{opacity:0.6;} }
.tagline { color:#666; font-size:0.85rem; margin-bottom:50px; letter-spacing:3px; text-transform:uppercase; }

.mode-cards { display:flex; gap:20px; flex-wrap:wrap; justify-content:center; margin-bottom:50px; }
.mode-card {
    background:var(--card); border:2px solid transparent;
    border-radius:20px; padding:32px 24px;
    width:210px; cursor:pointer;
    transition:all 0.25s; position:relative; overflow:hidden;
}
.mode-card:hover { border-color:var(--yellow); transform:translateY(-8px); box-shadow:0 16px 40px rgba(255,215,0,0.2); }
.mode-card .icon { font-size:3rem; margin-bottom:14px; display:block; }
.mode-card h3 { font-family:'Press Start 2P',monospace; font-size:0.65rem; color:var(--yellow); margin-bottom:10px; }
.mode-card p  { color:#777; font-size:0.8rem; line-height:1.55; }

.back-link { color:#444; font-size:0.78rem; text-decoration:none; transition:color 0.2s; }
.back-link:hover { color:var(--yellow); }

/* ══ SETUP ══ */
#setup { }
.setup-title { font-family:'Press Start 2P',monospace; font-size:0.85rem; color:var(--yellow); margin-bottom:6px; }
.setup-sub   { color:#555; font-size:0.8rem; margin-bottom:36px; }

.input-group { margin-bottom:18px; text-align:left; }
.input-group label { display:block; font-size:0.75rem; color:#888; margin-bottom:7px; letter-spacing:1px; text-transform:uppercase; }
.input-group input {
    background:var(--card); border:2px solid #2a3050;
    color:white; padding:13px 16px; border-radius:10px;
    font-size:1rem; font-family:'Nunito',sans-serif;
    width:280px; outline:none; transition:border-color 0.2s;
}
.input-group input:focus { border-color:var(--yellow); }

.pokemon-pick { display:flex; gap:14px; margin-bottom:24px; }
.poke-btn {
    flex:1; padding:18px 14px; border:2px solid #2a3050;
    border-radius:14px; background:var(--card);
    cursor:pointer; transition:all 0.2s; color:white;
    font-family:'Nunito',sans-serif;
}
.poke-btn img { width:76px; height:76px; object-fit:contain; display:block; margin:0 auto 10px; }
.poke-btn span { font-family:'Press Start 2P',monospace; font-size:0.55rem; }
.poke-btn.selected-pika { border-color:var(--pika); background:rgba(247,201,72,0.1); box-shadow:0 0 18px rgba(247,201,72,0.3); }
.poke-btn.selected-char { border-color:var(--char); background:rgba(255,69,0,0.1);  box-shadow:0 0 18px rgba(255,69,0,0.3);  }
.poke-btn.selected-bulb { border-color:var(--bulb); background:rgba(120,200,80,0.1); box-shadow:0 0 18px rgba(120,200,80,0.3); }
.poke-btn:hover { transform:scale(1.05); }

.btn-primary {
    background:linear-gradient(135deg,var(--orange),var(--yellow));
    color:#000; border:none; padding:15px 44px;
    border-radius:12px; font-family:'Press Start 2P',monospace;
    font-size:0.72rem; cursor:pointer;
    transition:transform 0.2s, box-shadow 0.2s;
    box-shadow:0 4px 18px rgba(255,165,0,0.4);
}
.btn-primary:hover { transform:translateY(-3px); box-shadow:0 8px 28px rgba(255,165,0,0.6); }
.btn-secondary {
    background:transparent; color:#555; border:1px solid #2a3050;
    padding:11px 22px; border-radius:10px; cursor:pointer;
    font-family:'Nunito',sans-serif; font-size:0.82rem;
    transition:all 0.2s; margin-top:10px;
}
.btn-secondary:hover { border-color:#666; color:white; }

/* ══ BATTLE ══ */
#battle { }
.battle-header { font-family:'Press Start 2P',monospace; font-size:0.55rem; color:#444; margin-bottom:18px; letter-spacing:2px; }

.arena {
    display:flex; align-items:center; justify-content:center;
    gap:24px; width:100%; max-width:680px;
    margin-bottom:20px; flex-wrap:wrap;
}
.fighter {
    flex:1; min-width:140px; max-width:210px;
    background:var(--card); border-radius:18px;
    padding:18px 14px; text-align:center;
    border:2px solid #1e2a4a; transition:border-color 0.3s;
}
.fighter.active-turn { border-color:var(--yellow); box-shadow:0 0 18px rgba(255,215,0,0.2); }
.fighter.shaking { animation:shake 0.4s; }
@keyframes shake { 0%,100%{transform:translateX(0);} 25%{transform:translateX(-7px);} 75%{transform:translateX(7px);} }

.fighter-name   { font-family:'Press Start 2P',monospace; font-size:0.5rem; color:#888; margin-bottom:5px; text-transform:uppercase; }
.fighter-pokemon{ font-family:'Press Start 2P',monospace; font-size:0.6rem; color:var(--yellow); margin-bottom:10px; }
.fighter img    { width:86px; height:86px; object-fit:contain; filter:drop-shadow(0 0 10px rgba(255,215,0,0.3)); transition:transform 0.3s, filter 0.15s; }
.fighter img.attacking { animation:atk-anim 0.5s; }
@keyframes atk-anim { 0%,100%{transform:scale(1);} 50%{transform:scale(1.22) rotate(-5deg);} }
.fighter img.hurt { filter:sepia(1) saturate(6) hue-rotate(310deg) brightness(0.6) drop-shadow(0 0 14px rgba(255,0,0,0.9)); transform:scale(0.92); }

.hp-bar-wrap { margin-top:10px; }
.hp-label    { font-size:0.72rem; color:#888; margin-bottom:4px; display:flex; justify-content:space-between; }
.hp-label span{ color:white; font-weight:700; }
.hp-bar  { height:9px; background:#0d0d1a; border-radius:99px; overflow:hidden; }
.hp-fill { height:100%; border-radius:99px; transition:width 0.5s ease, background 0.5s; }
.hp-fill.high{ background:linear-gradient(90deg,#00c853,#69f0ae); }
.hp-fill.mid { background:linear-gradient(90deg,#ffd600,#ffab00); }
.hp-fill.low { background:linear-gradient(90deg,#e53935,#ff1744); }

.vs-badge { font-family:'Press Start 2P',monospace; font-size:1.1rem; color:#2a3050; flex-shrink:0; }

.battle-log {
    width:100%; max-width:680px;
    background:var(--card); border-radius:14px;
    padding:14px 18px; min-height:54px;
    margin-bottom:18px; border-left:3px solid var(--yellow);
    font-size:0.88rem; color:#ccc; line-height:1.6;
}
.log-dmg   { color:#ff6b6b; font-weight:700; }
.log-dodge { color:#74b9ff; font-weight:700; }
.log-bot   { color:#fd79a8; }
.log-heal  { color:#69f0ae; font-weight:700; }

.attacks-grid {
    width:100%; max-width:680px;
    display:grid; grid-template-columns:repeat(auto-fit,minmax(138px,1fr));
    gap:10px; margin-bottom:10px;
}
.atk-btn {
    background:var(--card); border:2px solid #1e2a4a;
    color:white; padding:13px 10px; border-radius:12px;
    cursor:pointer; font-family:'Nunito',sans-serif;
    font-size:0.8rem; font-weight:700;
    transition:all 0.2s; display:flex; flex-direction:column; align-items:center; gap:4px;
}
.atk-btn .atk-dmg { font-size:0.68rem; color:#777; }
.atk-btn:hover:not(:disabled) { border-color:var(--yellow); background:rgba(255,215,0,0.08); transform:translateY(-2px); }
.atk-btn:disabled { opacity:0.3; cursor:not-allowed; }
.atk-btn.dodge-btn { border-color:#3a5a80; color:#74b9ff; }
.atk-btn.dodge-btn:hover:not(:disabled) { background:rgba(116,185,255,0.1); border-color:#74b9ff; }

.turn-label { font-family:'Press Start 2P',monospace; font-size:0.55rem; color:#555; margin-bottom:10px; }

/* result overlay */
.result-overlay {
    display:none; position:fixed; inset:0;
    background:rgba(0,0,0,0.88); z-index:100;
    align-items:center; justify-content:center; flex-direction:column;
}
.result-overlay.show { display:flex; }
.result-box {
    background:var(--card); border:2px solid var(--yellow);
    border-radius:24px; padding:44px 52px; text-align:center;
    animation:pop-in 0.4s cubic-bezier(0.175,0.885,0.32,1.275);
}
@keyframes pop-in { from{transform:scale(0.5);opacity:0;} to{transform:scale(1);opacity:1;} }
.result-box img { width:110px; height:110px; object-fit:contain; margin-bottom:14px; filter:drop-shadow(0 0 18px gold); }
.result-box h2  { font-family:'Press Start 2P',monospace; font-size:0.95rem; color:var(--yellow); margin-bottom:8px; }
.result-box p   { color:#888; font-size:0.85rem; margin-bottom:22px; }
.result-btns    { display:flex; gap:12px; justify-content:center; flex-wrap:wrap; }
</style>
</head>
<body>

<!-- ══════════ LOBBY ══════════ -->
<div id="lobby" class="screen active">
    <div class="logo">⚡ POKÉMON BATTLE</div>
    <p class="tagline">Choose your destiny</p>

    <div class="mode-cards">
        <div class="mode-card" onclick="startSetup('bot')">
            <span class="icon">🤖</span>
            <h3>VS BOT</h3>
            <p>Fight the computer. A random AI will battle you with the opposite Pokémon.</p>
        </div>
        <div class="mode-card" onclick="startSetup('pvp')">
            <span class="icon">👥</span>
            <h3>LOCAL PVP</h3>
            <p>Pass & play. Two players take turns on the same screen.</p>
        </div>
    </div>

    <a href="/" class="back-link">← Back to home</a>
    <a href="/online" class="back-link" style="margin-left:20px;">🌍 Play Online</a>
</div>

<!-- ══════════ SETUP ══════════ -->
<div id="setup" class="screen">
    <div class="setup-title" id="setup-title">PLAYER SETUP</div>
    <p class="setup-sub" id="setup-sub">Configure your battle</p>

    <div class="input-group">
        <label>Your Name (6 letters)</label>
        <input type="text" id="name1-input" maxlength="6" placeholder="GIOVAN" autocomplete="off">
    </div>

    <div id="name2-group" class="input-group" style="display:none">
        <label>Player 2 Name (6 letters)</label>
        <input type="text" id="name2-input" maxlength="6" placeholder="SATOSH" autocomplete="off">
    </div>

    <p style="color:#555;font-size:0.75rem;margin-bottom:14px;text-transform:uppercase;letter-spacing:1px;">Player 1 — Pick your Pokémon</p>
    <div class="pokemon-pick">
        <button class="poke-btn" id="pika-btn" onclick="selectPoke(1,'pikachu')">
            <img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/25.png" alt="Pikachu">
            <span>PIKACHU</span>
        </button>
        <button class="poke-btn" id="char-btn" onclick="selectPoke(1,'charizard')">
            <img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/6.png" alt="Charizard">
            <span>CHARIZARD</span>
        </button>
        <button class="poke-btn" id="bulb-btn" onclick="selectPoke(1,'bulbasaur')">
            <img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/1.png" alt="Bulbasaur">
            <span>BULBASAUR</span>
        </button>
    </div>

    <div id="poke2-group" style="display:none">
        <p style="color:#555;font-size:0.75rem;margin-bottom:14px;text-transform:uppercase;letter-spacing:1px;">Player 2 — Pick your Pokémon</p>
        <div class="pokemon-pick">
            <button class="poke-btn" id="pika2-btn" onclick="selectPoke(2,'pikachu')">
                <img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/25.png" alt="Pikachu">
                <span>PIKACHU</span>
            </button>
            <button class="poke-btn" id="char2-btn" onclick="selectPoke(2,'charizard')">
                <img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/6.png" alt="Charizard">
                <span>CHARIZARD</span>
            </button>
            <button class="poke-btn" id="bulb2-btn" onclick="selectPoke(2,'bulbasaur')">
                <img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/1.png" alt="Bulbasaur">
                <span>BULBASAUR</span>
            </button>
        </div>
    </div>

    <button class="btn-primary" onclick="beginBattle()">START BATTLE ⚡</button>
    <br>
    <button class="btn-secondary" onclick="showScreen('lobby')">← Back</button>
</div>

<!-- ══════════ BATTLE ══════════ -->
<div id="battle" class="screen">
    <div class="battle-header" id="turn-counter">TURN 1 / 10</div>
    <div class="arena">
        <div class="fighter" id="f1">
            <div class="fighter-name"  id="f1-name">PLAYER</div>
            <div class="fighter-pokemon" id="f1-poke">PIKACHU</div>
            <img id="f1-img" src="" alt="">
            <div class="hp-bar-wrap">
                <div class="hp-label">HP <span id="f1-hp">150</span>/150</div>
                <div class="hp-bar"><div class="hp-fill high" id="f1-bar" style="width:100%"></div></div>
            </div>
        </div>
        <div class="vs-badge">VS</div>
        <div class="fighter" id="f2">
            <div class="fighter-name"  id="f2-name">ENEMY</div>
            <div class="fighter-pokemon" id="f2-poke">CHARIZARD</div>
            <img id="f2-img" src="" alt="">
            <div class="hp-bar-wrap">
                <div class="hp-label">HP <span id="f2-hp">150</span>/150</div>
                <div class="hp-bar"><div class="hp-fill high" id="f2-bar" style="width:100%"></div></div>
            </div>
        </div>
    </div>

    <div class="turn-label" id="turn-label">YOUR TURN</div>
    <div class="battle-log" id="battle-log">Battle begins! Choose your attack.</div>
    <div class="attacks-grid" id="attacks-grid"></div>
</div>

<!-- ══════════ RESULT ══════════ -->
<div class="result-overlay" id="result-overlay">
    <div class="result-box">
        <img id="result-img" src="" alt="" style="display:none">
        <h2 id="result-title">WINNER!</h2>
        <p  id="result-sub">Battle over</p>
        <p  id="result-fav" style="color:#69f0ae;font-size:0.78rem;margin-bottom:8px;"></p>
        <div class="result-btns">
            <button class="btn-primary"   onclick="resetGame()">PLAY AGAIN</button>
            <button class="btn-secondary" onclick="window.location.href='/'">Main Menu</button>
        </div>
    </div>
</div>

<script>
const POKE_IMG = {
    pikachu:  'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/25.png',
    charizard:'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/6.png',
    bulbasaur:'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/1.png'
};
const ATTACKS = {
    pikachu: [
        {name:'Electro Rope', dmg:'1–100',  fn:()=>rnd(1,100)},
        {name:'Iron Tail',    dmg:'40–90',  fn:()=>rnd(40,90)},
        {name:'Elite Thunder',dmg:'50–80',  fn:()=>rnd(50,80)},
        {name:'Charge',       dmg:'50',     fn:()=>50},
    ],
    charizard:[
        {name:'Fire Ring',    dmg:'1–100',  fn:()=>rnd(1,100)},
        {name:'Ancient Power',dmg:'40–90',  fn:()=>rnd(40,90)},
        {name:'Fire Ball',    dmg:'50–80',  fn:()=>rnd(50,80)},
        {name:'Charge',       dmg:'50',     fn:()=>50},
    ],
    bulbasaur:[
        {name:'Vine Whip',    dmg:'1–100',  fn:()=>rnd(1,100)},
        {name:'Razor Leaf',   dmg:'40–90',  fn:()=>rnd(40,90)},
        {name:'Solar Beam',   dmg:'50–80',  fn:()=>rnd(50,80)},
        {name:'Charge',       dmg:'50',     fn:()=>50},
    ]
};
function rnd(a,b){return Math.floor(Math.random()*(b-a+1))+a;}

let gameMode='bot', name1='', name2='ENEMY', choice1=null, choice2=null;
let hp1=150, hp2=150, dodge1=false, dodge2=false, turn=0, maxTurns=10, pvpTurn=1, chargeBlock1=0, chargeBlock2=0;

// ── STARTUP CHECKS ──
console.log('✅ Pokemon Battle JS loaded OK');
window.addEventListener('load', ()=>{
    console.log('✅ Page fully loaded');
    const testUrls = {
        'Pikachu':   'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/25.png',
        'Charizard': 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/6.png',
        'Bulbasaur': 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/1.png'
    };
    Object.entries(testUrls).forEach(([name, url])=>{
        const img = new Image();
        img.onload  = ()=> console.log(`✅ ${name} image loaded OK`);
        img.onerror = ()=> console.error(`❌ ${name} image FAILED — no internet or PokeAPI is down`);
        img.src = url;
    });
    ['lobby','setup','battle'].forEach(id=>{
        const el = document.getElementById(id);
        console.log(el ? `✅ Screen #${id} found` : `❌ Screen #${id} MISSING from DOM`);
    });
});

function showScreen(id){
    console.log(`📺 Switching to screen: ${id}`);
    document.querySelectorAll('.screen').forEach(s=>s.classList.remove('active'));
    const target = document.getElementById(id);
    if(!target){ console.error(`❌ showScreen: #${id} not found!`); return; }
    target.classList.add('active');
    window.scrollTo(0,0);
}

function startSetup(mode){
    console.log(`🎮 startSetup called: ${mode}`);
    gameMode=mode;
    choice1=null; choice2=null;
    ['pika-btn','char-btn','bulb-btn','pika2-btn','char2-btn','bulb2-btn'].forEach(id=>{
        const el=document.getElementById(id);
        if(el) el.className='poke-btn';
    });
    document.getElementById('name1-input').value='';
    document.getElementById('name2-input').value='';
    document.getElementById('name2-group').style.display  = mode==='pvp'?'block':'none';
    document.getElementById('poke2-group').style.display  = mode==='pvp'?'block':'none';
    document.getElementById('setup-title').textContent    = mode==='pvp'?'PLAYERS SETUP':'YOUR SETUP';
    showScreen('setup');
}

function selectPoke(player, poke){
    if(player===1){
        choice1=poke;
        document.getElementById('pika-btn').className='poke-btn'+(poke==='pikachu'?' selected-pika':'');
        document.getElementById('char-btn').className='poke-btn'+(poke==='charizard'?' selected-char':'');
        document.getElementById('bulb-btn').className='poke-btn'+(poke==='bulbasaur'?' selected-bulb':'');
    } else {
        choice2=poke;
        document.getElementById('pika2-btn').className='poke-btn'+(poke==='pikachu'?' selected-pika':'');
        document.getElementById('char2-btn').className='poke-btn'+(poke==='charizard'?' selected-char':'');
        document.getElementById('bulb2-btn').className='poke-btn'+(poke==='bulbasaur'?' selected-bulb':'');
    }
}

function beginBattle(){
    const n1=document.getElementById('name1-input').value.trim();
    if(n1.length!==6){alert('Name must be exactly 6 letters!');return;}
    if(!choice1){alert('Player 1: choose a Pokémon!');return;}
    name1=n1.toUpperCase();

    if(gameMode==='pvp'){
        const n2=document.getElementById('name2-input').value.trim();
        if(n2.length!==6){alert('Player 2 name must be exactly 6 letters!');return;}
        if(!choice2){alert('Player 2: choose a Pokémon!');return;}
        name2=n2.toUpperCase();
    } else {
        name2='ENEMY';
        const allPokes=['pikachu','charizard','bulbasaur'];
        const others=allPokes.filter(p=>p!==choice1);
        choice2=others[Math.floor(Math.random()*others.length)];
    }
    // Track favorite pokemon picks
    const pickKey='picks_'+choice1;
    localStorage.setItem(pickKey,(parseInt(localStorage.getItem(pickKey)||'0')+1).toString());
    initBattle();
    showScreen('battle');
}

function initBattle(){
    hp1=150; hp2=150; dodge1=false; dodge2=false; turn=0; pvpTurn=1; chargeBlock1=0; chargeBlock2=0;
    document.getElementById('f1-name').textContent  = name1;
    document.getElementById('f2-name').textContent  = name2;
    document.getElementById('f1-poke').textContent  = choice1.toUpperCase();
    document.getElementById('f2-poke').textContent  = choice2.toUpperCase();
    document.getElementById('f1-img').src = POKE_IMG[choice1];
    document.getElementById('f2-img').src = POKE_IMG[choice2];
    document.getElementById('result-overlay').classList.remove('show');
    updateHP();
    setLog('Battle begins! Choose your attack.');
    renderAttacks(1);
}

function updateHP(){
    function setBar(barId, numId, hp){
        const pct=Math.max(0,(hp/150)*100);
        const bar=document.getElementById(barId);
        bar.style.width=pct+'%';
        bar.className='hp-fill '+(pct>50?'high':pct>20?'mid':'low');
        document.getElementById(numId).textContent=Math.max(0,hp);
    }
    setBar('f1-bar','f1-hp',hp1);
    setBar('f2-bar','f2-hp',hp2);
    document.getElementById('turn-counter').textContent='TURN '+(turn+1)+' / '+maxTurns;
}

function setLog(html){ document.getElementById('battle-log').innerHTML=html; }

function renderAttacks(playerNum){
    const poke = playerNum===1?choice1:choice2;
    const displayName = playerNum===1?name1:name2;
    document.getElementById('turn-label').textContent = displayName+"'S TURN";
    document.getElementById('f1').classList.toggle('active-turn', playerNum===1);
    document.getElementById('f2').classList.toggle('active-turn', playerNum===2);

    const grid=document.getElementById('attacks-grid');
    grid.innerHTML='';
    ATTACKS[poke].forEach(atk=>{
        const btn=document.createElement('button');
        btn.className='atk-btn';
        btn.innerHTML=`<span>${atk.name}</span><span class="atk-dmg">${atk.dmg} dmg</span>`;
        btn.onclick=()=>doAttack(atk, playerNum);
        grid.appendChild(btn);
    });
    const dodgeBtn=document.createElement('button');
    dodgeBtn.className='atk-btn dodge-btn';
    dodgeBtn.innerHTML='<span>🛡️ Dodge</span><span class="atk-dmg">10% next hit</span>';
    dodgeBtn.onclick=()=>doDodge(playerNum);
    grid.appendChild(dodgeBtn);
}

function disableAll(){ document.querySelectorAll('.atk-btn').forEach(b=>b.disabled=true); }

function hurtImg(imgId){
    const img=document.getElementById(imgId);
    img.classList.add('hurt');
    setTimeout(()=>img.classList.remove('hurt'),700);
}

function doAttack(atk, playerNum){
    disableAll();
    let dmg=atk.fn();
    const atkImg=document.getElementById(playerNum===1?'f1-img':'f2-img');
    const defImg=document.getElementById(playerNum===1?'f2-img':'f1-img');
    const defEl =document.getElementById(playerNum===1?'f2':'f1');

    atkImg.classList.add('attacking');
    setTimeout(()=>atkImg.classList.remove('attacking'),500);

    if(playerNum===1){
        if(dodge2){dmg=Math.floor(dmg/10);dodge2=false;}
        hp2-=dmg;
        setLog(`<span class="log-dmg">⚡ ${name1} used ${atk.name} — ${dmg} damage!</span>`);
    } else {
        if(dodge1){dmg=Math.floor(dmg/10);dodge1=false;}
        hp1-=dmg;
        setLog(`<span class="log-dmg">🔥 ${name2} used ${atk.name} — ${dmg} damage!</span>`);
    }

    setTimeout(()=>{ defEl.classList.add('shaking'); hurtImg(defImg.id); },80);
    setTimeout(()=>{defEl.classList.remove('shaking');},480);

    // Healing: attacker heals 30 HP unless they used Charge (blocks healing for 2 turns)
    if(playerNum===1){
        if(atk.name==='Charge'){ chargeBlock1=2; }
        if(chargeBlock1>0){ chargeBlock1--; }
        else { hp1=Math.min(150,hp1+30); setLog(document.getElementById('battle-log').innerHTML+`<br><span class="log-heal">💚 ${name1} recovered 30 HP!</span>`); }
    } else {
        if(atk.name==='Charge'){ chargeBlock2=2; }
        if(chargeBlock2>0){ chargeBlock2--; }
        else { hp2=Math.min(150,hp2+30); setLog(document.getElementById('battle-log').innerHTML+`<br><span class="log-heal">💚 ${name2} recovered 30 HP!</span>`); }
    }
    updateHP();

    setTimeout(()=>{
        if(checkEnd()) return;
        if(gameMode==='pvp'){ pvpTurn=pvpTurn===1?2:1; renderAttacks(pvpTurn); }
        else { turn++; if(turn>=maxTurns){checkEnd(true);return;} botTurn(); }
    },750);
}

function doDodge(playerNum){
    if(playerNum===1){
        dodge1=true;
        setLog(`<span class="log-dodge">🛡️ ${name1} braces! Next hit deals only 10% damage.</span>`);
        if(chargeBlock1>0){ chargeBlock1--; }
        else { hp1=Math.min(150,hp1+30); setLog(document.getElementById('battle-log').innerHTML+`<br><span class="log-heal">💚 ${name1} recovered 30 HP!</span>`); updateHP(); }
    } else {
        dodge2=true;
        setLog(`<span class="log-dodge">🛡️ ${name2} braces! Next hit deals only 10% damage.</span>`);
        if(chargeBlock2>0){ chargeBlock2--; }
        else { hp2=Math.min(150,hp2+30); setLog(document.getElementById('battle-log').innerHTML+`<br><span class="log-heal">💚 ${name2} recovered 30 HP!</span>`); updateHP(); }
    }
    if(gameMode==='pvp'){ pvpTurn=pvpTurn===1?2:1; renderAttacks(pvpTurn); }
    else { turn++; if(turn>=maxTurns){checkEnd(true);return;} setTimeout(botTurn,600); }
}

function botTurn(){
    document.getElementById('turn-label').textContent='ENEMY IS THINKING...';
    document.getElementById('f2').classList.add('active-turn');
    document.getElementById('f1').classList.remove('active-turn');
    disableAll();

    setTimeout(()=>{
        const opts=ATTACKS[choice2];
        const atk=opts[Math.floor(Math.random()*opts.length)];
        let dmg=atk.fn();

        document.getElementById('f2-img').classList.add('attacking');
        setTimeout(()=>document.getElementById('f2-img').classList.remove('attacking'),500);

        if(dodge1){dmg=Math.floor(dmg/10);dodge1=false;}
        hp1-=dmg;
        setLog(`<span class="log-bot">🤖 Enemy used ${atk.name} — <span class="log-dmg">${dmg} damage!</span></span>`);

        setTimeout(()=>{ document.getElementById('f1').classList.add('shaking'); hurtImg('f1-img'); },80);
        setTimeout(()=>{document.getElementById('f1').classList.remove('shaking');},480);

        // Bot healing
        if(atk.name==='Charge'){ chargeBlock2=2; }
        if(chargeBlock2>0){ chargeBlock2--; }
        else { hp2=Math.min(150,hp2+30); setLog(document.getElementById('battle-log').innerHTML+`<br><span class="log-heal">💚 ${name2} recovered 30 HP!</span>`); }
        updateHP();

        setTimeout(()=>{
            if(checkEnd()) return;
            renderAttacks(1);
        },750);
    },950);
}

function checkEnd(timeout=false){
    if(hp1<=0 && hp2<=0){ showResult(null,"IT'S A TIE!","Both fighters fainted!"); return true; }
    if(hp1<=0){ showResult(POKE_IMG[choice2], name2+" WINS!", name1+" has fainted!"); return true; }
    if(hp2<=0){ showResult(POKE_IMG[choice1], name1+" WINS!", name2+" has fainted!"); return true; }
    if(timeout){
        if(hp1>hp2)  { showResult(POKE_IMG[choice1], name1+" WINS!", "Time's up — more HP remaining!"); return true; }
        if(hp2>hp1)  { showResult(POKE_IMG[choice2], name2+" WINS!", "Time's up — more HP remaining!"); return true; }
        showResult(null,"IT'S A TIE!","Time's up — equal HP!"); return true;
    }
    return false;
}

function getFavPokemon(){
    const pokes=['pikachu','charizard','bulbasaur'];
    let maxCnt=0, fav=null;
    pokes.forEach(p=>{ const c=parseInt(localStorage.getItem('picks_'+p)||'0'); if(c>maxCnt){maxCnt=c;fav=p;} });
    return fav?{name:fav,count:maxCnt}:null;
}

function showResult(img, title, sub){
    const ri=document.getElementById('result-img');
    if(img){ri.src=img;ri.style.display='block';}else{ri.style.display='none';}
    document.getElementById('result-title').textContent=title;
    document.getElementById('result-sub').textContent=sub;
    const fav=getFavPokemon();
    document.getElementById('result-fav').textContent=fav?'Fav Pokemon: '+fav.name.toUpperCase()+' ('+fav.count+' picks)':'';
    document.getElementById('result-overlay').classList.add('show');
}

function resetGame(){
    document.getElementById('result-overlay').classList.remove('show');
    initBattle();
}

</script>

<!-- PANIC BUTTON -->
<a href="/article" id="panic-btn" style="
    position:fixed; top:16px; left:16px; z-index:99999;
    background:#ff1a1a; color:white;
    font-family:Arial,sans-serif; font-weight:bold;
    font-size:0.95rem; padding:17px 22px;
    border-radius:10px; text-decoration:none;
    box-shadow:0 4px 20px rgba(255,26,26,0.6);
    line-height:1.5; text-align:center;
">🚨 TEACHER<br>COMING</a>
</body>
</html>
"""

# ── SOCKETIO SETUP ──
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# In-memory room state
rooms = {}  # { room_code: { players: [], game: {} } }
waiting_pool = []  # list of sid waiting for random match
turn_timers  = {}  # { room_code: greenlet }
rematch_data = {}  # { room_code: {p:[{sid,username,pokemon}], requester_sid} }

def make_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def get_damage(att):
    if att in ["electro rope", "fire ring", "vine whip"]:      return random.randint(1, 100)
    elif att in ["iron tail", "ancient power", "razor leaf"]:  return random.randint(40, 90)
    elif att in ["elite thunder", "fire ball", "solar beam"]:  return random.randint(50, 80)
    elif att == "charge":                                       return 50
    return 0

# ── DB HELPERS ──
def get_or_create_user(username):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, wins, losses FROM usernames WHERE username=%s", (username,))
    row = cur.fetchone()
    if not row:
        cur.execute("INSERT INTO usernames (username) VALUES (%s) RETURNING id, wins, losses", (username,))
        row = cur.fetchone()
        conn.commit()
    cur.close(); conn.close()
    return {"id": row[0], "wins": row[1], "losses": row[2]}

def update_fav_pokemon(username, pokemon):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT fav_pokemon, fav_pokemon_picks FROM usernames WHERE username=%s", (username,))
    row = cur.fetchone()
    if row:
        fav, picks = row
        picks = picks or 0
        if fav is None or picks == 0:
            cur.execute("UPDATE usernames SET fav_pokemon=%s, fav_pokemon_picks=1 WHERE username=%s", (pokemon, username))
        elif fav == pokemon:
            cur.execute("UPDATE usernames SET fav_pokemon_picks=fav_pokemon_picks+1 WHERE username=%s", (username,))
        else:
            if picks <= 1:
                cur.execute("UPDATE usernames SET fav_pokemon=%s, fav_pokemon_picks=1 WHERE username=%s", (pokemon, username))
            else:
                cur.execute("UPDATE usernames SET fav_pokemon_picks=fav_pokemon_picks-1 WHERE username=%s", (username,))
    conn.commit(); cur.close(); conn.close()

def save_match(p1, p2, winner):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO matches (player1, player2, winner) VALUES (%s,%s,%s)", (p1, p2, winner))
    if winner == p1:
        cur.execute("UPDATE usernames SET wins=wins+1 WHERE username=%s", (p1,))
        cur.execute("UPDATE usernames SET losses=losses+1 WHERE username=%s", (p2,))
    elif winner == p2:
        cur.execute("UPDATE usernames SET wins=wins+1 WHERE username=%s", (p2,))
        cur.execute("UPDATE usernames SET losses=losses+1 WHERE username=%s", (p1,))
    conn.commit(); cur.close(); conn.close()

def get_stats(username):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT wins, losses, fav_pokemon FROM usernames WHERE username=%s", (username,))
    row = cur.fetchone()
    if not row:
        cur.close(); conn.close()
        return None
    wins, losses, fav_pokemon = row
    total = wins + losses
    rate = round((wins/total)*100) if total > 0 else 0
    points = wins * 10 - losses * 10
    cur.execute("SELECT COUNT(*)+1 FROM usernames WHERE wins*10 - losses*10 > %s", (points,))
    rank = cur.fetchone()[0]
    cur.close(); conn.close()
    return {"wins": wins, "losses": losses, "total": total, "rate": rate, "points": points, "rank": rank, "fav_pokemon": fav_pokemon}

def get_leaderboard(limit=10):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT username, wins, losses, wins*10 - losses*10 AS points
        FROM usernames
        ORDER BY points DESC, wins DESC
        LIMIT %s
    """, (limit,))
    rows = cur.fetchall()
    cur.close(); conn.close()
    return [{"username": r[0], "wins": r[1], "losses": r[2], "points": r[3]} for r in rows]

def cancel_turn_timer(code):
    if code in turn_timers:
        try: turn_timers[code].cancel()
        except: pass
        del turn_timers[code]

def do_timeout(code):
    if code not in rooms:
        return
    room = rooms[code]
    players = room['players']
    losing_idx  = room['turn']
    winning_idx = 1 - losing_idx
    if losing_idx >= len(players) or winning_idx >= len(players):
        return
    loser  = players[losing_idx]
    winner = players[winning_idx]
    save_match(players[0]['username'], players[1]['username'], winner['username'])
    log_msg = f"⏱️ {loser['username']} timed out — {winner['username']} wins!"
    rematch_data[code] = {'p': [{'sid': p['sid'], 'username': p['username'], 'pokemon': p['pokemon']} for p in players]}
    del rooms[code]
    if code in turn_timers:
        del turn_timers[code]
    socketio.emit('game_over', {'winner': winner['username'], 'log': log_msg, 'your_hp': winner['hp'], 'opp_hp': 0}, to=winner['sid'])
    socketio.emit('game_over', {'winner': winner['username'], 'log': log_msg, 'your_hp': 0, 'opp_hp': winner['hp']}, to=loser['sid'])

def start_turn_timer(code):
    cancel_turn_timer(code)
    turn_timers[code] = eventlet.spawn_after(30, do_timeout, code)

# ── FLASK ROUTES ──
@app.route("/", methods=["GET", "POST"])
def index():
    conn = get_conn()
    cur = conn.cursor()
    mensaje = ""

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        print(f"DEBUG: Received email = '{email}'")
        try:
            cur.execute("INSERT INTO users (email) VALUES (%s)", (email,))
            conn.commit()
            mensaje = "correo registrado"
            print("DEBUG: Insert successful")
        except Exception as e:
            conn.rollback()
            mensaje = f"Error: {e}"
            print(f"DEBUG: Insert failed: {e}")

    cur.execute("SELECT email FROM users")
    rows = cur.fetchall()
    emails = [r[0] for r in rows]
    print(f"DEBUG: emails in DB = {emails}")

    cur.close()
    conn.close()
    top3 = get_leaderboard(3)
    return render_template_string(html, emails=emails, mensaje=mensaje, top3=top3)

@app.route("/game")
def game():
    return render_template_string(game_html)

@app.route("/article")
def article():
    return render_template_string(article_html)

@app.route("/online")
def online():
    return render_template_string(online_html)

@app.route("/online/friend")
def online_friend():
    return render_template_string(online_friend_html)

@app.route("/online/random")
def online_random():
    return render_template_string(online_random_html)

@app.route("/api/stats/<username>")
def stats(username):
    data = get_stats(username)
    if not data:
        return {"error": "User not found"}, 404
    return data

@app.route("/api/leaderboard")
def leaderboard_api():
    return {"players": get_leaderboard(10)}

@app.route("/leaderboard")
def leaderboard_page():
    return render_template_string(leaderboard_html)

# ── SOCKET EVENTS ──
@socketio.on('join_friend_room')
def on_join_friend(data):
    username = data['username']
    code     = data.get('code', '').upper().strip()
    pokemon  = data['pokemon']
    sid      = request.sid

    get_or_create_user(username)
    update_fav_pokemon(username, pokemon)

    if not code:
        # Create new room
        code = make_code()
        rooms[code] = {
            'players': [{'sid': sid, 'username': username, 'pokemon': pokemon, 'hp': 150, 'dodge': False, 'heal_blocked': 0}],
            'turn': 0,
            'started': False
        }
        join_room(code)
        emit('room_created', {'code': code})
    else:
        # Join existing room
        if code not in rooms:
            emit('error', {'msg': 'Room not found'})
            return
        room = rooms[code]
        if len(room['players']) >= 2:
            emit('error', {'msg': 'Room is full'})
            return
        room['players'].append({'sid': sid, 'username': username, 'pokemon': pokemon, 'hp': 150, 'dodge': False, 'heal_blocked': 0})
        join_room(code)
        start_game(code)

@socketio.on('join_random')
def on_join_random(data):
    username = data['username']
    pokemon  = data['pokemon']
    sid      = request.sid

    get_or_create_user(username)
    update_fav_pokemon(username, pokemon)

    # Check if someone is waiting
    if waiting_pool:
        waiting = waiting_pool.pop(0)
        code = make_code()
        rooms[code] = {
            'players': [
                waiting,
                {'sid': sid, 'username': username, 'pokemon': pokemon, 'hp': 150, 'dodge': False, 'heal_blocked': 0}
            ],
            'turn': 0,
            'started': False
        }
        join_room(code)
        # Also put waiting player in room
        from flask_socketio import rooms as get_rooms
        socketio.server.enter_room(waiting['sid'], code)
        start_game(code)
    else:
        waiting_pool.append({'sid': sid, 'username': username, 'pokemon': pokemon, 'hp': 150, 'dodge': False, 'heal_blocked': 0})
        emit('waiting', {'msg': 'Waiting for opponent...'})

@socketio.on('cancel_random')
def on_cancel_random():
    global waiting_pool
    waiting_pool = [p for p in waiting_pool if p['sid'] != request.sid]
    emit('cancelled')

def start_game(code):
    room = rooms[code]
    room['started'] = True
    p1 = room['players'][0]
    p2 = room['players'][1]
    room['turn'] = 0  # 0 = p1's turn, 1 = p2's turn
    socketio.emit('game_start', {
        'you':      p1['username'], 'opponent': p2['username'],
        'your_pokemon': p1['pokemon'], 'opp_pokemon': p2['pokemon'],
        'your_hp':  150, 'opp_hp': 150,
        'your_turn': True, 'code': code
    }, to=p1['sid'])
    socketio.emit('game_start', {
        'you':      p2['username'], 'opponent': p1['username'],
        'your_pokemon': p2['pokemon'], 'opp_pokemon': p1['pokemon'],
        'your_hp':  150, 'opp_hp': 150,
        'your_turn': False, 'code': code
    }, to=p2['sid'])
    start_turn_timer(code)

@socketio.on('attack')
def on_attack(data):
    code   = data['code']
    move   = data['move']
    sid    = request.sid

    if code not in rooms: return
    cancel_turn_timer(code)
    room = rooms[code]
    players = room['players']

    # Figure out attacker/defender
    atk_idx = next((i for i,p in enumerate(players) if p['sid']==sid), None)
    if atk_idx is None: return
    def_idx = 1 - atk_idx

    # Verify it's their turn
    if room['turn'] != atk_idx:
        emit('error', {'msg': "Not your turn"})
        return

    attacker = players[atk_idx]
    defender = players[def_idx]

    if move == 'dodge':
        attacker['dodge'] = True
        room['turn'] = def_idx  # switch turn to defender
        msg = f"🛡️ {attacker['username']} is dodging!"
        socketio.emit('move_result', {
            'log': msg,
            'your_hp': attacker['hp'], 'opp_hp': defender['hp'],
            'your_turn': False
        }, to=attacker['sid'])
        socketio.emit('move_result', {
            'log': msg,
            'your_hp': defender['hp'], 'opp_hp': attacker['hp'],
            'your_turn': True
        }, to=defender['sid'])
        start_turn_timer(code)
    else:
        dmg = get_damage(move)
        if defender['dodge']:
            dmg = dmg // 10
            defender['dodge'] = False
        defender['hp'] -= dmg
        defender['hp'] = max(0, defender['hp'])

        # Healing: charge blocks attacker healing for 2 turns
        if move == 'charge':
            attacker['heal_blocked'] = 2
        if attacker.get('heal_blocked', 0) > 0:
            attacker['heal_blocked'] -= 1
            heal = 0
        else:
            heal = 30
        attacker['hp'] = min(150, attacker['hp'] + heal)

        msg = f"⚔️ {attacker['username']} used {move} — {dmg} damage!"
        if heal > 0:
            msg += f" (+{heal}❤️)"

        if defender['hp'] <= 0:
            winner = attacker['username']
            save_match(players[0]['username'], players[1]['username'], winner)
            rematch_data[code] = {'p': [{'sid': p['sid'], 'username': p['username'], 'pokemon': p['pokemon']} for p in players]}
            del rooms[code]
            socketio.emit('game_over', {
                'winner': winner, 'log': msg,
                'your_hp': attacker['hp'], 'opp_hp': defender['hp']
            }, to=attacker['sid'])
            socketio.emit('game_over', {
                'winner': winner, 'log': msg,
                'your_hp': defender['hp'], 'opp_hp': attacker['hp']
            }, to=defender['sid'])
            return

        # Next turn
        room['turn'] = def_idx
        socketio.emit('move_result', {
            'log': msg,
            'your_hp': attacker['hp'], 'opp_hp': defender['hp'],
            'your_turn': False
        }, to=attacker['sid'])
        socketio.emit('move_result', {
            'log': msg,
            'your_hp': defender['hp'], 'opp_hp': attacker['hp'],
            'your_turn': True
        }, to=defender['sid'])
        start_turn_timer(code)

@socketio.on('chat_message')
def on_chat(data):
    code = data.get('code', '')
    text = data.get('text', '').strip()[:200]
    if not text or not code:
        return
    sid = request.sid
    if code not in rooms:
        return
    room = rooms[code]
    sender = next((p['username'] for p in room['players'] if p['sid'] == sid), 'Unknown')
    socketio.emit('chat_incoming', {'username': sender, 'text': text}, room=code)

@socketio.on('rematch_request')
def on_rematch_request(data):
    code = data.get('code', '')
    sid  = request.sid
    if code not in rematch_data:
        emit('error', {'msg': 'Rematch data expired'}); return
    rd = rematch_data[code]
    players = rd['p']
    requester = next((p for p in players if p['sid'] == sid), None)
    opponent  = next((p for p in players if p['sid'] != sid), None)
    if not requester or not opponent:
        emit('error', {'msg': 'Player not found'}); return
    rd['requester_sid'] = sid
    socketio.emit('rematch_incoming', {'from': requester['username'], 'code': code}, to=opponent['sid'])

@socketio.on('rematch_accept')
def on_rematch_accept(data):
    code = data.get('code', '')
    if code not in rematch_data:
        emit('error', {'msg': 'Rematch expired'}); return
    rd = rematch_data[code]
    players = rd['p']
    new_code = make_code()
    rooms[new_code] = {
        'players': [{'sid': p['sid'], 'username': p['username'], 'pokemon': p['pokemon'], 'hp': 150, 'dodge': False, 'heal_blocked': 0} for p in players],
        'turn': 0, 'started': False
    }
    for p in players:
        socketio.server.enter_room(p['sid'], new_code)
    del rematch_data[code]
    start_game(new_code)

@socketio.on('rematch_deny')
def on_rematch_deny(data):
    code = data.get('code', '')
    if code not in rematch_data:
        return
    rd = rematch_data[code]
    req_sid = rd.get('requester_sid')
    if req_sid:
        socketio.emit('rematch_denied', {}, to=req_sid)
    del rematch_data[code]

@socketio.on('disconnect')
def on_disconnect():
    sid = request.sid
    global waiting_pool
    waiting_pool = [p for p in waiting_pool if p['sid'] != sid]
    for code, room in list(rooms.items()):
        for p in room['players']:
            if p['sid'] == sid:
                cancel_turn_timer(code)
                socketio.emit('opponent_left', {'msg': 'Opponent disconnected.'}, room=code)
                del rooms[code]
                break

# ── ONLINE HTML PAGES ──
online_html = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>⚡ Online Battle</title>
<link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&family=Nunito:wght@400;700;900&display=swap" rel="stylesheet">
<style>
:root{--yellow:#FFD700;--orange:#FF6B00;--dark:#0d0d1a;--card:#16213e;}
*{box-sizing:border-box;margin:0;padding:0;}
body{font-family:'Nunito',sans-serif;background:var(--dark);color:white;min-height:100vh;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:40px 20px;text-align:center;}
.logo{font-family:'Press Start 2P',monospace;font-size:clamp(1rem,3vw,1.8rem);color:var(--yellow);text-shadow:0 0 30px rgba(255,215,0,0.5),3px 3px 0 #b8860b;margin-bottom:8px;}
.sub{color:#666;font-size:0.8rem;letter-spacing:3px;text-transform:uppercase;margin-bottom:50px;}
.cards{display:flex;gap:20px;flex-wrap:wrap;justify-content:center;margin-bottom:40px;}
.card{background:var(--card);border:2px solid transparent;border-radius:20px;padding:32px 24px;width:210px;cursor:pointer;transition:all 0.25s;text-decoration:none;color:white;display:block;}
.card:hover{border-color:var(--yellow);transform:translateY(-8px);box-shadow:0 16px 40px rgba(255,215,0,0.2);}
.card .icon{font-size:3rem;margin-bottom:14px;display:block;}
.card h3{font-family:'Press Start 2P',monospace;font-size:0.65rem;color:var(--yellow);margin-bottom:10px;}
.card p{color:#777;font-size:0.8rem;line-height:1.55;}
.stats-box{background:var(--card);border:1px solid rgba(255,215,0,0.2);border-radius:16px;padding:24px 32px;max-width:400px;width:100%;margin-bottom:28px;}
.stats-box h3{font-family:'Press Start 2P',monospace;font-size:0.65rem;color:var(--yellow);margin-bottom:16px;}
.stats-row{display:flex;gap:10px;align-items:center;}
.stats-row input{flex:1;background:#0d0d1a;border:2px solid #2a3050;color:white;padding:12px 14px;border-radius:10px;font-family:'Nunito',sans-serif;font-size:0.95rem;outline:none;transition:border-color 0.2s;}
.stats-row input:focus{border-color:var(--yellow);}
.stats-row button{background:linear-gradient(135deg,var(--orange),var(--yellow));color:#000;border:none;padding:12px 18px;border-radius:10px;font-family:'Press Start 2P',monospace;font-size:0.6rem;cursor:pointer;}
#stats-result{margin-top:14px;font-size:0.88rem;color:#aaa;line-height:1.8;}
#stats-result .big{font-family:'Press Start 2P',monospace;font-size:1rem;color:var(--yellow);}
.back-link{color:#444;font-size:0.78rem;text-decoration:none;transition:color 0.2s;}
.back-link:hover{color:var(--yellow);}
</style>
</head>
<body>
<div class="logo">⚡ ONLINE BATTLE</div>
<p class="sub">Choose your mode</p>

<div class="cards">
    <a class="card" href="/online/friend">
        <span class="icon">🤝</span>
        <h3>PLAY WITH FRIEND</h3>
        <p>Create a room and share the code, or enter a friend's code to battle.</p>
    </a>
    <a class="card" href="/online/random">
        <span class="icon">🌍</span>
        <h3>PLAY RANDOM</h3>
        <p>Get matched with a random opponent from anywhere.</p>
    </a>
    <a class="card" href="/leaderboard">
        <span class="icon">🏆</span>
        <h3>LEADERBOARD</h3>
        <p>See the top players ranked by points. +10 per win, -10 per loss.</p>
    </a>
</div>

<div class="stats-box">
    <h3>📊 STATS &amp; RANK</h3>
    <div class="stats-row">
        <input type="text" id="stats-input" placeholder="Enter username" maxlength="20">
        <button onclick="checkStats()">GO</button>
    </div>
    <div id="stats-result"></div>
</div>

<a href="/" class="back-link">← Back to home</a>

<script>
async function checkStats(){
    const u = document.getElementById('stats-input').value.trim();
    if(!u) return;
    const res = await fetch('/api/stats/'+encodeURIComponent(u));
    const el  = document.getElementById('stats-result');
    if(res.status===404){ el.innerHTML='❌ Username not found.'; return; }
    const d = await res.json();
    const favLine = d.fav_pokemon ? `<br>⭐ Fav: <strong>${d.fav_pokemon.toUpperCase()}</strong>` : '';
    el.innerHTML = `<span class="big">${d.rate}%</span> win rate &nbsp;·&nbsp; <span class="big" style="color:#c084fc">#${d.rank}</span> rank<br>${d.wins} wins · ${d.losses} losses · ${d.total} games · <strong>${d.points} pts</strong>${favLine}`;
}
document.getElementById('stats-input').addEventListener('keydown', e=>{ if(e.key==='Enter') checkStats(); });
</script>

<!-- PANIC BUTTON -->
<a href="/article" id="panic-btn" style="
    position:fixed; top:16px; left:16px; z-index:99999;
    background:#ff1a1a; color:white;
    font-family:Arial,sans-serif; font-weight:bold;
    font-size:0.95rem; padding:17px 22px;
    border-radius:10px; text-decoration:none;
    box-shadow:0 4px 20px rgba(255,26,26,0.6);
    line-height:1.5; text-align:center;
">🚨 TEACHER<br>COMING</a>
</body>
</html>
"""

online_friend_html = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>⚡ Play with Friend</title>
<link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&family=Nunito:wght@400;700;900&display=swap" rel="stylesheet">
<script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>
<style>
:root{--yellow:#FFD700;--orange:#FF6B00;--dark:#0d0d1a;--card:#16213e;--pika:#F7C948;--char:#FF4500;--bulb:#78C850;}
*{box-sizing:border-box;margin:0;padding:0;}
body{font-family:'Nunito',sans-serif;background:var(--dark);color:white;min-height:100vh;overflow-x:hidden;}
.screen{display:none!important;position:relative;z-index:1;}
.screen.active{display:flex!important;flex-direction:column;align-items:center;justify-content:center;min-height:100vh;padding:40px 20px;}
.logo{font-family:'Press Start 2P',monospace;font-size:clamp(0.9rem,2.5vw,1.5rem);color:var(--yellow);text-shadow:3px 3px 0 #b8860b;margin-bottom:8px;text-align:center;}
.sub{color:#666;font-size:0.78rem;letter-spacing:2px;text-transform:uppercase;margin-bottom:36px;text-align:center;}
.input-group{margin-bottom:16px;text-align:left;}
.input-group label{display:block;font-size:0.72rem;color:#888;margin-bottom:7px;letter-spacing:1px;text-transform:uppercase;}
.input-group input{background:var(--card);border:2px solid #2a3050;color:white;padding:13px 16px;border-radius:10px;font-size:1rem;font-family:'Nunito',sans-serif;width:280px;outline:none;transition:border-color 0.2s;}
.input-group input:focus{border-color:var(--yellow);}
.pokemon-pick{display:flex;gap:14px;margin-bottom:24px;}
.poke-btn{flex:1;padding:18px 14px;border:2px solid #2a3050;border-radius:14px;background:var(--card);cursor:pointer;transition:all 0.2s;color:white;font-family:'Nunito',sans-serif;}
.poke-btn img{width:72px;height:72px;object-fit:contain;display:block;margin:0 auto 8px;}
.poke-btn span{font-family:'Press Start 2P',monospace;font-size:0.55rem;}
.poke-btn.sel-pika{border-color:var(--pika);background:rgba(247,201,72,0.1);box-shadow:0 0 16px rgba(247,201,72,0.3);}
.poke-btn.sel-char{border-color:var(--char);background:rgba(255,69,0,0.1);box-shadow:0 0 16px rgba(255,69,0,0.3);}
.poke-btn.sel-bulb{border-color:var(--bulb);background:rgba(120,200,80,0.1);box-shadow:0 0 16px rgba(120,200,80,0.3);}
.or-divider{color:#444;font-size:0.8rem;margin:10px 0;text-align:center;}
.btn-primary{background:linear-gradient(135deg,var(--orange),var(--yellow));color:#000;border:none;padding:15px 44px;border-radius:12px;font-family:'Press Start 2P',monospace;font-size:0.7rem;cursor:pointer;transition:transform 0.2s,box-shadow 0.2s;box-shadow:0 4px 18px rgba(255,165,0,0.4);margin-bottom:10px;}
.btn-primary:hover{transform:translateY(-3px);box-shadow:0 8px 28px rgba(255,165,0,0.6);}
.btn-secondary{background:transparent;color:#555;border:1px solid #2a3050;padding:11px 22px;border-radius:10px;cursor:pointer;font-family:'Nunito',sans-serif;font-size:0.82rem;transition:all 0.2s;margin-top:6px;}
.btn-secondary:hover{border-color:#666;color:white;}
.code-display{font-family:'Press Start 2P',monospace;font-size:2rem;color:var(--yellow);letter-spacing:8px;background:var(--card);padding:20px 32px;border-radius:14px;border:2px solid rgba(255,215,0,0.3);margin:20px 0;text-shadow:0 0 20px rgba(255,215,0,0.4);}
.waiting-msg{color:#888;font-size:0.85rem;margin-bottom:20px;animation:pulse 1.5s infinite;}
@keyframes pulse{0%,100%{opacity:1;}50%{opacity:0.4;}}
/* battle styles */
.arena{display:flex;align-items:center;justify-content:center;gap:20px;width:100%;max-width:660px;margin-bottom:18px;flex-wrap:wrap;}
.fighter{flex:1;min-width:130px;max-width:200px;background:var(--card);border-radius:16px;padding:16px 12px;text-align:center;border:2px solid #1e2a4a;transition:border-color 0.3s;}
.fighter.active-turn{border-color:var(--yellow);box-shadow:0 0 16px rgba(255,215,0,0.2);}
.fighter.shaking{animation:shake 0.4s;}
@keyframes shake{0%,100%{transform:translateX(0);}25%{transform:translateX(-7px);}75%{transform:translateX(7px);}}
.fighter-name{font-family:'Press Start 2P',monospace;font-size:0.48rem;color:#888;margin-bottom:4px;}
.fighter-poke{font-family:'Press Start 2P',monospace;font-size:0.58rem;color:var(--yellow);margin-bottom:8px;}
.fighter img{width:80px;height:80px;object-fit:contain;filter:drop-shadow(0 0 8px rgba(255,215,0,0.3));transition:filter 0.15s,transform 0.15s;}
.fighter img.atk{animation:atk-anim 0.5s;}
@keyframes atk-anim{0%,100%{transform:scale(1);}50%{transform:scale(1.2) rotate(-5deg);}}
.fighter img.hurt{filter:sepia(1) saturate(6) hue-rotate(310deg) brightness(0.6) drop-shadow(0 0 14px rgba(255,0,0,0.9));transform:scale(0.92);}
.hp-wrap{margin-top:8px;}
.hp-label{font-size:0.7rem;color:#888;margin-bottom:3px;display:flex;justify-content:space-between;}
.hp-label span{color:white;font-weight:700;}
.hp-bar{height:8px;background:#0d0d1a;border-radius:99px;overflow:hidden;}
.hp-fill{height:100%;border-radius:99px;transition:width 0.5s,background 0.5s;}
.hp-fill.high{background:linear-gradient(90deg,#00c853,#69f0ae);}
.hp-fill.mid{background:linear-gradient(90deg,#ffd600,#ffab00);}
.hp-fill.low{background:linear-gradient(90deg,#e53935,#ff1744);}
.vs-badge{font-family:'Press Start 2P',monospace;font-size:1rem;color:#2a3050;flex-shrink:0;}
.battle-log{width:100%;max-width:660px;background:var(--card);border-radius:12px;padding:12px 16px;min-height:50px;margin-bottom:16px;border-left:3px solid var(--yellow);font-size:0.85rem;color:#ccc;line-height:1.6;}
.attacks-grid{width:100%;max-width:660px;display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:8px;margin-bottom:8px;}
.atk-btn{background:var(--card);border:2px solid #1e2a4a;color:white;padding:12px 8px;border-radius:10px;cursor:pointer;font-family:'Nunito',sans-serif;font-size:0.78rem;font-weight:700;transition:all 0.2s;display:flex;flex-direction:column;align-items:center;gap:3px;}
.atk-btn .dmg{font-size:0.65rem;color:#777;}
.atk-btn:hover:not(:disabled){border-color:var(--yellow);background:rgba(255,215,0,0.08);transform:translateY(-2px);}
.atk-btn:disabled{opacity:0.3;cursor:not-allowed;}
.dodge-btn{border-color:#3a5a80;color:#74b9ff;}
.dodge-btn:hover:not(:disabled){background:rgba(116,185,255,0.1);border-color:#74b9ff;}
.turn-label{font-family:'Press Start 2P',monospace;font-size:0.52rem;color:#555;margin-bottom:8px;}
.result-overlay{display:none;position:fixed;inset:0;background:rgba(0,0,0,0.88);z-index:100;align-items:center;justify-content:center;flex-direction:column;}
.result-overlay.show{display:flex;}
.result-box{background:var(--card);border:2px solid var(--yellow);border-radius:22px;padding:40px 50px;text-align:center;animation:pop-in 0.4s cubic-bezier(0.175,0.885,0.32,1.275);}
@keyframes pop-in{from{transform:scale(0.5);opacity:0;}to{transform:scale(1);opacity:1;}}
.result-box img{width:100px;height:100px;object-fit:contain;margin-bottom:12px;filter:drop-shadow(0 0 16px gold);}
.result-box h2{font-family:'Press Start 2P',monospace;font-size:0.9rem;color:var(--yellow);margin-bottom:8px;}
.result-box p{color:#888;font-size:0.82rem;margin-bottom:20px;}
.result-btns{display:flex;gap:10px;justify-content:center;flex-wrap:wrap;}
/* timer */
.timer-bar{font-family:'Press Start 2P',monospace;font-size:0.48rem;color:#ff6b6b;margin-bottom:6px;text-align:center;display:none;}
.timer-bar.active{display:block;}
.timer-bar span{font-size:0.9rem;}
/* chat */
.chat-wrap{width:100%;max-width:660px;margin-top:10px;}
.chat-msgs{background:#0d0d1a;border:1px solid #2a3050;border-radius:10px 10px 0 0;height:90px;overflow-y:auto;padding:7px 12px;font-size:0.8rem;color:#aaa;line-height:1.7;}
.chat-row{display:flex;gap:0;}
.chat-row input{flex:1;background:#161e3a;border:1px solid #2a3050;border-top:none;border-radius:0 0 0 10px;color:white;padding:7px 12px;font-family:'Nunito',sans-serif;font-size:0.85rem;outline:none;}
.chat-row input:focus{border-color:var(--yellow);}
.chat-row button{background:var(--orange);color:#000;border:none;padding:7px 14px;border-radius:0 0 10px 0;font-weight:bold;cursor:pointer;font-size:0.8rem;}
/* rematch dialog */
.rm-dialog{display:none;position:fixed;inset:0;background:rgba(0,0,0,0.85);z-index:200;align-items:center;justify-content:center;}
.rm-dialog.show{display:flex;}
.rm-box{background:var(--card);border:2px solid var(--yellow);border-radius:20px;padding:30px 38px;text-align:center;}
.rm-box h3{font-family:'Press Start 2P',monospace;font-size:0.65rem;color:var(--yellow);margin-bottom:12px;}
.rm-box p{color:#aaa;font-size:0.88rem;margin-bottom:18px;}
</style>
</head>
<body>

<!-- SETUP SCREEN -->
<div id="setup" class="screen active">
    <div class="logo">🤝 PLAY WITH FRIEND</div>
    <p class="sub">Create or join a room</p>

    <div class="input-group">
        <label>Your Username</label>
        <input type="text" id="username" maxlength="20" placeholder="Ash" autocomplete="off">
    </div>

    <p style="color:#555;font-size:0.72rem;margin-bottom:12px;text-transform:uppercase;letter-spacing:1px;">Choose your Pokémon</p>
    <div class="pokemon-pick">
        <button class="poke-btn" id="pika-btn" onclick="selPoke('pikachu')">
            <img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/25.png">
            <span>PIKACHU</span>
        </button>
        <button class="poke-btn" id="char-btn" onclick="selPoke('charizard')">
            <img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/6.png">
            <span>CHARIZARD</span>
        </button>
        <button class="poke-btn" id="bulb-btn" onclick="selPoke('bulbasaur')">
            <img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/1.png">
            <span>BULBASAUR</span>
        </button>
    </div>

    <button class="btn-primary" onclick="createRoom()">CREATE ROOM</button>
    <div class="or-divider">— or enter a code —</div>
    <div class="input-group" style="margin-bottom:10px;">
        <input type="text" id="room-code-input" maxlength="6" placeholder="ABC123" autocomplete="off" style="text-transform:uppercase;letter-spacing:4px;text-align:center;">
    </div>
    <button class="btn-primary" onclick="joinRoom()">JOIN ROOM</button>
    <br>
    <button class="btn-secondary" onclick="window.location.href='/online'">← Back</button>
</div>

<!-- WAITING SCREEN -->
<div id="waiting" class="screen">
    <div class="logo">⏳ WAITING...</div>
    <p class="sub">Share this code with your friend</p>
    <div class="code-display" id="room-code-display">------</div>
    <p class="waiting-msg">Waiting for opponent to join...</p>
    <button class="btn-secondary" onclick="window.location.href='/online/friend'">Cancel</button>
</div>

<!-- BATTLE SCREEN -->
<div id="battle" class="screen">
    <div class="arena">
        <div class="fighter" id="f-you">
            <div class="fighter-name" id="f-you-name">YOU</div>
            <div class="fighter-poke"  id="f-you-poke">PIKACHU</div>
            <img id="f-you-img" src="">
            <div class="hp-wrap">
                <div class="hp-label">HP <span id="f-you-hp">150</span>/150</div>
                <div class="hp-bar"><div class="hp-fill high" id="f-you-bar" style="width:100%"></div></div>
            </div>
        </div>
        <div class="vs-badge">VS</div>
        <div class="fighter" id="f-opp">
            <div class="fighter-name" id="f-opp-name">OPP</div>
            <div class="fighter-poke"  id="f-opp-poke">CHARIZARD</div>
            <img id="f-opp-img" src="">
            <div class="hp-wrap">
                <div class="hp-label">HP <span id="f-opp-hp">150</span>/150</div>
                <div class="hp-bar"><div class="hp-fill high" id="f-opp-bar" style="width:100%"></div></div>
            </div>
        </div>
    </div>
    <div class="turn-label" id="turn-label">YOUR TURN</div>
    <div class="timer-bar" id="timer-bar">⏱️ <span id="timer-secs">30</span>s left</div>
    <div class="battle-log" id="battle-log">Battle begins!</div>
    <div class="attacks-grid" id="attacks-grid"></div>
    <div class="chat-wrap">
        <div class="chat-msgs" id="chat-msgs"></div>
        <div class="chat-row">
            <input type="text" id="chat-input" placeholder="Say something..." maxlength="200" onkeydown="if(event.key==='Enter')sendChat()">
            <button onclick="sendChat()">Send</button>
        </div>
    </div>
</div>

<!-- REMATCH DIALOG -->
<div class="rm-dialog" id="rm-dialog">
    <div class="rm-box">
        <h3>⚔️ REMATCH REQUEST</h3>
        <p id="rm-msg">Opponent wants a rematch!</p>
        <div style="display:flex;gap:10px;justify-content:center;">
            <button class="btn-primary" onclick="acceptRematch()">Accept</button>
            <button class="btn-secondary" onclick="denyRematch()">Deny</button>
        </div>
    </div>
</div>

<!-- RESULT OVERLAY -->
<div class="result-overlay" id="result-overlay">
    <div class="result-box">
        <img id="res-img" src="">
        <h2 id="res-title">WINNER!</h2>
        <p  id="res-sub"></p>
        <div class="result-btns">
            <button class="btn-primary" id="rematch-btn" onclick="requestRematch()">⚔️ Rematch</button>
            <button class="btn-primary"   onclick="window.location.href='/online/friend'">Play Again</button>
            <button class="btn-secondary" onclick="window.location.href='/online'">Main Menu</button>
        </div>
    </div>
</div>

<script>
const POKE_IMG = {
    pikachu:  'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/25.png',
    charizard:'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/6.png',
    bulbasaur:'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/1.png'
};
const ATTACKS = {
    pikachu:  [{name:'Electro Rope',dmg:'1–100'},{name:'Iron Tail',dmg:'40–90'},{name:'Elite Thunder',dmg:'50–80'},{name:'Charge',dmg:'50'}],
    charizard:[{name:'Fire Ring',dmg:'1–100'},{name:'Ancient Power',dmg:'40–90'},{name:'Fire Ball',dmg:'50–80'},{name:'Charge',dmg:'50'}],
    bulbasaur:[{name:'Vine Whip',dmg:'1–100'},{name:'Razor Leaf',dmg:'40–90'},{name:'Solar Beam',dmg:'50–80'},{name:'Charge',dmg:'50'}]
};

const socket = io();
let myPokemon='', myUsername='', oppPokemon='', roomCode='', myTurn=false, myIdx=0;
let timerInterval=null, pendingRematchCode='';

function showScreen(id){
    document.querySelectorAll('.screen').forEach(s=>s.classList.remove('active'));
    document.getElementById(id).classList.add('active');
}

function selPoke(p){
    myPokemon=p;
    document.getElementById('pika-btn').className='poke-btn'+(p==='pikachu'?' sel-pika':'');
    document.getElementById('char-btn').className='poke-btn'+(p==='charizard'?' sel-char':'');
    document.getElementById('bulb-btn').className='poke-btn'+(p==='bulbasaur'?' sel-bulb':'');
}

function validate(){
    const u=document.getElementById('username').value.trim();
    if(!u){alert('Enter a username!');return null;}
    if(!myPokemon){alert('Choose a Pokémon!');return null;}
    myUsername=u;
    return u;
}

function createRoom(){
    if(!validate()) return;
    socket.emit('join_friend_room',{username:myUsername, pokemon:myPokemon, code:''});
}

function joinRoom(){
    if(!validate()) return;
    const code=document.getElementById('room-code-input').value.trim().toUpperCase();
    if(!code){alert('Enter a room code!');return;}
    socket.emit('join_friend_room',{username:myUsername, pokemon:myPokemon, code:code});
}

socket.on('room_created', d=>{
    roomCode=d.code;
    document.getElementById('room-code-display').textContent=d.code;
    showScreen('waiting');
});

socket.on('error', d=>alert(d.msg));

socket.on('game_start', d=>{
    roomCode=d.code; myTurn=d.your_turn;
    document.getElementById('f-you-name').textContent=d.you;
    document.getElementById('f-opp-name').textContent=d.opponent;
    document.getElementById('f-you-poke').textContent=d.your_pokemon.toUpperCase();
    document.getElementById('f-opp-poke').textContent=d.opp_pokemon.toUpperCase();
    document.getElementById('f-you-img').src=POKE_IMG[d.your_pokemon];
    document.getElementById('f-opp-img').src=POKE_IMG[d.opp_pokemon];
    myPokemon=d.your_pokemon; oppPokemon=d.opp_pokemon;
    setBar('f-you-bar','f-you-hp',d.your_hp);
    setBar('f-opp-bar','f-opp-hp',d.opp_hp);
    renderAttacks(myTurn);
    showScreen('battle');
    setLog('Battle begins! ' + (myTurn?'Your turn!':'Waiting for opponent...'));
    document.getElementById('chat-msgs').innerHTML='';
    document.getElementById('result-overlay').classList.remove('show');
    document.getElementById('rm-dialog').classList.remove('show');
});

socket.on('move_result', d=>{
    setBar('f-you-bar','f-you-hp', d.your_hp);
    setBar('f-opp-bar','f-opp-hp', d.opp_hp);
    myTurn=d.your_turn;
    setLog(d.log);
    renderAttacks(myTurn);
    // d.your_turn=true means opponent just attacked → my Pokemon was hit
    const defEl=document.getElementById(myTurn?'f-opp':'f-you');
    defEl.classList.add('shaking');
    setTimeout(()=>defEl.classList.remove('shaking'),400);
    hurtImg(myTurn?'f-opp-img':'f-you-img');
});

socket.on('game_over', d=>{
    stopTimer();
    setBar('f-you-bar','f-you-hp', d.your_hp);
    setBar('f-opp-bar','f-opp-hp', d.opp_hp);
    setLog(d.log);
    const won = d.winner===myUsername;
    document.getElementById('res-img').src=POKE_IMG[won?myPokemon:oppPokemon];
    document.getElementById('res-title').textContent=won?'YOU WIN! 🏆':'YOU LOST 💀';
    document.getElementById('res-sub').textContent=won?'GG! Victory recorded.':'Better luck next time!';
    document.getElementById('rematch-btn').disabled=false;
    document.getElementById('rematch-btn').textContent='⚔️ Rematch';
    document.getElementById('result-overlay').classList.add('show');
});

socket.on('opponent_left', d=>{
    stopTimer();
    alert(d.msg);
    window.location.href='/online/friend';
});

socket.on('chat_incoming', d=>{
    const box=document.getElementById('chat-msgs');
    const isMe=d.username===myUsername;
    box.innerHTML+=`<span style="color:${isMe?'#FFD700':'#74b9ff'}">${d.username}:</span> ${escHtml(d.text)}<br>`;
    box.scrollTop=box.scrollHeight;
});

socket.on('rematch_incoming', d=>{
    pendingRematchCode=d.code;
    document.getElementById('rm-msg').textContent=d.from+' wants a rematch!';
    document.getElementById('rm-dialog').classList.add('show');
});

socket.on('rematch_denied', ()=>{
    alert('Opponent declined the rematch.');
});

function startTimer(){
    stopTimer();
    let secs=30;
    const bar=document.getElementById('timer-bar');
    const num=document.getElementById('timer-secs');
    bar.classList.add('active');
    num.textContent=secs;
    timerInterval=setInterval(()=>{
        secs--;
        num.textContent=secs;
        if(secs<=0) stopTimer();
    },1000);
}

function stopTimer(){
    clearInterval(timerInterval);
    timerInterval=null;
    document.getElementById('timer-bar').classList.remove('active');
}

function sendChat(){
    const inp=document.getElementById('chat-input');
    const text=inp.value.trim();
    if(!text||!roomCode) return;
    socket.emit('chat_message',{code:roomCode,text});
    inp.value='';
}

function requestRematch(){
    if(!roomCode) return;
    document.getElementById('rematch-btn').disabled=true;
    document.getElementById('rematch-btn').textContent='Waiting...';
    socket.emit('rematch_request',{code:roomCode});
}

function acceptRematch(){
    document.getElementById('rm-dialog').classList.remove('show');
    socket.emit('rematch_accept',{code:pendingRematchCode});
}

function denyRematch(){
    document.getElementById('rm-dialog').classList.remove('show');
    socket.emit('rematch_deny',{code:pendingRematchCode});
    pendingRematchCode='';
}

function escHtml(t){return t.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}


function hurtImg(imgId){
    const img=document.getElementById(imgId);
    if(!img) return;
    img.classList.add('hurt');
    setTimeout(()=>img.classList.remove('hurt'),700);
}

function setBar(barId,numId,hp){
    const pct=Math.max(0,(hp/150)*100);
    const bar=document.getElementById(barId);
    if(!bar) return;
    bar.style.width=pct+'%';
    bar.className='hp-fill '+(pct>50?'high':pct>20?'mid':'low');
    document.getElementById(numId).textContent=Math.max(0,hp);
}

function setLog(msg){ document.getElementById('battle-log').innerHTML=msg; }

function renderAttacks(myTurn){
    const grid=document.getElementById('attacks-grid');
    grid.innerHTML='';
    document.getElementById('turn-label').textContent=myTurn?"YOUR TURN":"OPPONENT'S TURN...";
    document.getElementById('f-you').classList.toggle('active-turn',myTurn);
    document.getElementById('f-opp').classList.toggle('active-turn',!myTurn);
    if(myTurn) startTimer(); else stopTimer();
    ATTACKS[myPokemon].forEach(atk=>{
        const btn=document.createElement('button');
        btn.className='atk-btn';
        btn.disabled=!myTurn;
        btn.innerHTML=`<span>${atk.name}</span><span class="dmg">${atk.dmg} dmg</span>`;
        btn.onclick=()=>sendAttack(atk.name.toLowerCase());
        grid.appendChild(btn);
    });
    const d=document.createElement('button');
    d.className='atk-btn dodge-btn';
    d.disabled=!myTurn;
    d.innerHTML='<span>🛡️ Dodge</span><span class="dmg">10% next hit</span>';
    d.onclick=()=>sendAttack('dodge');
    grid.appendChild(d);
}

function sendAttack(move){
    stopTimer();
    document.querySelectorAll('.atk-btn').forEach(b=>b.disabled=true);
    socket.emit('attack',{code:roomCode, move:move});
}
</script>

<!-- PANIC BUTTON -->
<a href="/article" id="panic-btn" style="
    position:fixed; top:16px; left:16px; z-index:99999;
    background:#ff1a1a; color:white;
    font-family:Arial,sans-serif; font-weight:bold;
    font-size:0.95rem; padding:17px 22px;
    border-radius:10px; text-decoration:none;
    box-shadow:0 4px 20px rgba(255,26,26,0.6);
    line-height:1.5; text-align:center;
">🚨 TEACHER<br>COMING</a>
</body>
</html>
"""

online_random_html = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>⚡ Random Battle</title>
<link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&family=Nunito:wght@400;700;900&display=swap" rel="stylesheet">
<script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>
<style>
:root{--yellow:#FFD700;--orange:#FF6B00;--dark:#0d0d1a;--card:#16213e;--pika:#F7C948;--char:#FF4500;--bulb:#78C850;}
*{box-sizing:border-box;margin:0;padding:0;}
body{font-family:'Nunito',sans-serif;background:var(--dark);color:white;min-height:100vh;overflow-x:hidden;}
.screen{display:none!important;position:relative;z-index:1;}
.screen.active{display:flex!important;flex-direction:column;align-items:center;justify-content:center;min-height:100vh;padding:40px 20px;}
.logo{font-family:'Press Start 2P',monospace;font-size:clamp(0.9rem,2.5vw,1.5rem);color:var(--yellow);text-shadow:3px 3px 0 #b8860b;margin-bottom:8px;text-align:center;}
.sub{color:#666;font-size:0.78rem;letter-spacing:2px;text-transform:uppercase;margin-bottom:36px;text-align:center;}
.input-group{margin-bottom:16px;text-align:left;}
.input-group label{display:block;font-size:0.72rem;color:#888;margin-bottom:7px;letter-spacing:1px;text-transform:uppercase;}
.input-group input{background:var(--card);border:2px solid #2a3050;color:white;padding:13px 16px;border-radius:10px;font-size:1rem;font-family:'Nunito',sans-serif;width:280px;outline:none;transition:border-color 0.2s;}
.input-group input:focus{border-color:var(--yellow);}
.pokemon-pick{display:flex;gap:14px;margin-bottom:24px;}
.poke-btn{flex:1;padding:18px 14px;border:2px solid #2a3050;border-radius:14px;background:var(--card);cursor:pointer;transition:all 0.2s;color:white;font-family:'Nunito',sans-serif;}
.poke-btn img{width:72px;height:72px;object-fit:contain;display:block;margin:0 auto 8px;}
.poke-btn span{font-family:'Press Start 2P',monospace;font-size:0.55rem;}
.poke-btn.sel-pika{border-color:var(--pika);background:rgba(247,201,72,0.1);box-shadow:0 0 16px rgba(247,201,72,0.3);}
.poke-btn.sel-char{border-color:var(--char);background:rgba(255,69,0,0.1);box-shadow:0 0 16px rgba(255,69,0,0.3);}
.poke-btn.sel-bulb{border-color:var(--bulb);background:rgba(120,200,80,0.1);box-shadow:0 0 16px rgba(120,200,80,0.3);}
.btn-primary{background:linear-gradient(135deg,var(--orange),var(--yellow));color:#000;border:none;padding:15px 44px;border-radius:12px;font-family:'Press Start 2P',monospace;font-size:0.7rem;cursor:pointer;transition:transform 0.2s,box-shadow 0.2s;box-shadow:0 4px 18px rgba(255,165,0,0.4);margin-bottom:10px;}
.btn-primary:hover{transform:translateY(-3px);box-shadow:0 8px 28px rgba(255,165,0,0.6);}
.btn-secondary{background:transparent;color:#555;border:1px solid #2a3050;padding:11px 22px;border-radius:10px;cursor:pointer;font-family:'Nunito',sans-serif;font-size:0.82rem;transition:all 0.2s;margin-top:6px;}
.btn-secondary:hover{border-color:#666;color:white;}
.waiting-msg{color:#888;font-size:0.88rem;margin-bottom:20px;animation:pulse 1.5s infinite;}
@keyframes pulse{0%,100%{opacity:1;}50%{opacity:0.4;}}
.arena{display:flex;align-items:center;justify-content:center;gap:20px;width:100%;max-width:660px;margin-bottom:18px;flex-wrap:wrap;}
.fighter{flex:1;min-width:130px;max-width:200px;background:var(--card);border-radius:16px;padding:16px 12px;text-align:center;border:2px solid #1e2a4a;transition:border-color 0.3s;}
.fighter.active-turn{border-color:var(--yellow);box-shadow:0 0 16px rgba(255,215,0,0.2);}
.fighter.shaking{animation:shake 0.4s;}
@keyframes shake{0%,100%{transform:translateX(0);}25%{transform:translateX(-7px);}75%{transform:translateX(7px);}}
.fighter-name{font-family:'Press Start 2P',monospace;font-size:0.48rem;color:#888;margin-bottom:4px;}
.fighter-poke{font-family:'Press Start 2P',monospace;font-size:0.58rem;color:var(--yellow);margin-bottom:8px;}
.fighter img{width:80px;height:80px;object-fit:contain;filter:drop-shadow(0 0 8px rgba(255,215,0,0.3));transition:filter 0.15s,transform 0.15s;}
.fighter img.hurt{filter:sepia(1) saturate(6) hue-rotate(310deg) brightness(0.6) drop-shadow(0 0 14px rgba(255,0,0,0.9));transform:scale(0.92);}
.hp-wrap{margin-top:8px;}
.hp-label{font-size:0.7rem;color:#888;margin-bottom:3px;display:flex;justify-content:space-between;}
.hp-label span{color:white;font-weight:700;}
.hp-bar{height:8px;background:#0d0d1a;border-radius:99px;overflow:hidden;}
.hp-fill{height:100%;border-radius:99px;transition:width 0.5s,background 0.5s;}
.hp-fill.high{background:linear-gradient(90deg,#00c853,#69f0ae);}
.hp-fill.mid{background:linear-gradient(90deg,#ffd600,#ffab00);}
.hp-fill.low{background:linear-gradient(90deg,#e53935,#ff1744);}
.vs-badge{font-family:'Press Start 2P',monospace;font-size:1rem;color:#2a3050;flex-shrink:0;}
.battle-log{width:100%;max-width:660px;background:var(--card);border-radius:12px;padding:12px 16px;min-height:50px;margin-bottom:16px;border-left:3px solid var(--yellow);font-size:0.85rem;color:#ccc;line-height:1.6;}
.attacks-grid{width:100%;max-width:660px;display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:8px;}
.atk-btn{background:var(--card);border:2px solid #1e2a4a;color:white;padding:12px 8px;border-radius:10px;cursor:pointer;font-family:'Nunito',sans-serif;font-size:0.78rem;font-weight:700;transition:all 0.2s;display:flex;flex-direction:column;align-items:center;gap:3px;}
.atk-btn .dmg{font-size:0.65rem;color:#777;}
.atk-btn:hover:not(:disabled){border-color:var(--yellow);background:rgba(255,215,0,0.08);transform:translateY(-2px);}
.atk-btn:disabled{opacity:0.3;cursor:not-allowed;}
.dodge-btn{border-color:#3a5a80;color:#74b9ff;}
.dodge-btn:hover:not(:disabled){background:rgba(116,185,255,0.1);border-color:#74b9ff;}
.turn-label{font-family:'Press Start 2P',monospace;font-size:0.52rem;color:#555;margin-bottom:8px;}
.result-overlay{display:none;position:fixed;inset:0;background:rgba(0,0,0,0.88);z-index:100;align-items:center;justify-content:center;flex-direction:column;}
.result-overlay.show{display:flex;}
.result-box{background:var(--card);border:2px solid var(--yellow);border-radius:22px;padding:40px 50px;text-align:center;animation:pop-in 0.4s cubic-bezier(0.175,0.885,0.32,1.275);}
@keyframes pop-in{from{transform:scale(0.5);opacity:0;}to{transform:scale(1);opacity:1;}}
.result-box img{width:100px;height:100px;object-fit:contain;margin-bottom:12px;filter:drop-shadow(0 0 16px gold);}
.result-box h2{font-family:'Press Start 2P',monospace;font-size:0.9rem;color:var(--yellow);margin-bottom:8px;}
.result-box p{color:#888;font-size:0.82rem;margin-bottom:20px;}
.result-btns{display:flex;gap:10px;justify-content:center;flex-wrap:wrap;}
.timer-bar{font-family:'Press Start 2P',monospace;font-size:0.48rem;color:#ff6b6b;margin-bottom:6px;text-align:center;display:none;}
.timer-bar.active{display:block;}
.timer-bar span{font-size:0.9rem;}
.chat-wrap{width:100%;max-width:660px;margin-top:10px;}
.chat-msgs{background:#0d0d1a;border:1px solid #2a3050;border-radius:10px 10px 0 0;height:90px;overflow-y:auto;padding:7px 12px;font-size:0.8rem;color:#aaa;line-height:1.7;}
.chat-row{display:flex;gap:0;}
.chat-row input{flex:1;background:#161e3a;border:1px solid #2a3050;border-top:none;border-radius:0 0 0 10px;color:white;padding:7px 12px;font-family:'Nunito',sans-serif;font-size:0.85rem;outline:none;}
.chat-row input:focus{border-color:var(--yellow);}
.chat-row button{background:var(--orange);color:#000;border:none;padding:7px 14px;border-radius:0 0 10px 0;font-weight:bold;cursor:pointer;font-size:0.8rem;}
.rm-dialog{display:none;position:fixed;inset:0;background:rgba(0,0,0,0.85);z-index:200;align-items:center;justify-content:center;}
.rm-dialog.show{display:flex;}
.rm-box{background:var(--card);border:2px solid var(--yellow);border-radius:20px;padding:30px 38px;text-align:center;}
.rm-box h3{font-family:'Press Start 2P',monospace;font-size:0.65rem;color:var(--yellow);margin-bottom:12px;}
.rm-box p{color:#aaa;font-size:0.88rem;margin-bottom:18px;}
</style>
</head>
<body>

<!-- SETUP -->
<div id="setup" class="screen active">
    <div class="logo">🌍 RANDOM BATTLE</div>
    <p class="sub">Get matched with a stranger</p>
    <div class="input-group">
        <label>Your Username</label>
        <input type="text" id="username" maxlength="20" placeholder="Ash" autocomplete="off">
    </div>
    <p style="color:#555;font-size:0.72rem;margin-bottom:12px;text-transform:uppercase;letter-spacing:1px;">Choose your Pokémon</p>
    <div class="pokemon-pick">
        <button class="poke-btn" id="pika-btn" onclick="selPoke('pikachu')">
            <img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/25.png">
            <span>PIKACHU</span>
        </button>
        <button class="poke-btn" id="char-btn" onclick="selPoke('charizard')">
            <img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/6.png">
            <span>CHARIZARD</span>
        </button>
        <button class="poke-btn" id="bulb-btn" onclick="selPoke('bulbasaur')">
            <img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/1.png">
            <span>BULBASAUR</span>
        </button>
    </div>
    <button class="btn-primary" onclick="findMatch()">FIND MATCH 🔍</button>
    <br>
    <button class="btn-secondary" onclick="window.location.href='/online'">← Back</button>
</div>

<!-- WAITING -->
<div id="waiting" class="screen">
    <div class="logo">🔍 SEARCHING...</div>
    <p class="waiting-msg">Looking for an opponent...</p>
    <button class="btn-secondary" onclick="cancelSearch()">Cancel</button>
</div>

<!-- BATTLE -->
<div id="battle" class="screen">
    <div class="arena">
        <div class="fighter" id="f-you">
            <div class="fighter-name" id="f-you-name">YOU</div>
            <div class="fighter-poke"  id="f-you-poke">PIKACHU</div>
            <img id="f-you-img" src="">
            <div class="hp-wrap">
                <div class="hp-label">HP <span id="f-you-hp">150</span>/150</div>
                <div class="hp-bar"><div class="hp-fill high" id="f-you-bar" style="width:100%"></div></div>
            </div>
        </div>
        <div class="vs-badge">VS</div>
        <div class="fighter" id="f-opp">
            <div class="fighter-name" id="f-opp-name">OPP</div>
            <div class="fighter-poke"  id="f-opp-poke">CHARIZARD</div>
            <img id="f-opp-img" src="">
            <div class="hp-wrap">
                <div class="hp-label">HP <span id="f-opp-hp">150</span>/150</div>
                <div class="hp-bar"><div class="hp-fill high" id="f-opp-bar" style="width:100%"></div></div>
            </div>
        </div>
    </div>
    <div class="turn-label" id="turn-label">YOUR TURN</div>
    <div class="timer-bar" id="timer-bar">⏱️ <span id="timer-secs">30</span>s left</div>
    <div class="battle-log" id="battle-log">Battle begins!</div>
    <div class="attacks-grid" id="attacks-grid"></div>
    <div class="chat-wrap">
        <div class="chat-msgs" id="chat-msgs"></div>
        <div class="chat-row">
            <input type="text" id="chat-input" placeholder="Say something..." maxlength="200" onkeydown="if(event.key==='Enter')sendChat()">
            <button onclick="sendChat()">Send</button>
        </div>
    </div>
</div>

<!-- REMATCH DIALOG -->
<div class="rm-dialog" id="rm-dialog">
    <div class="rm-box">
        <h3>⚔️ REMATCH REQUEST</h3>
        <p id="rm-msg">Opponent wants a rematch!</p>
        <div style="display:flex;gap:10px;justify-content:center;">
            <button class="btn-primary" onclick="acceptRematch()">Accept</button>
            <button class="btn-secondary" onclick="denyRematch()">Deny</button>
        </div>
    </div>
</div>

<!-- RESULT -->
<div class="result-overlay" id="result-overlay">
    <div class="result-box">
        <img id="res-img" src="">
        <h2 id="res-title">WINNER!</h2>
        <p  id="res-sub"></p>
        <div class="result-btns">
            <button class="btn-primary" id="rematch-btn" onclick="requestRematch()">⚔️ Rematch</button>
            <button class="btn-primary"   onclick="window.location.href='/online/random'">Play Again</button>
            <button class="btn-secondary" onclick="window.location.href='/online'">Main Menu</button>
        </div>
    </div>
</div>

<script>
const POKE_IMG={pikachu:'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/25.png',charizard:'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/6.png',bulbasaur:'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/1.png'};
const ATTACKS={pikachu:[{name:'Electro Rope',dmg:'1–100'},{name:'Iron Tail',dmg:'40–90'},{name:'Elite Thunder',dmg:'50–80'},{name:'Charge',dmg:'50'}],charizard:[{name:'Fire Ring',dmg:'1–100'},{name:'Ancient Power',dmg:'40–90'},{name:'Fire Ball',dmg:'50–80'},{name:'Charge',dmg:'50'}],bulbasaur:[{name:'Vine Whip',dmg:'1–100'},{name:'Razor Leaf',dmg:'40–90'},{name:'Solar Beam',dmg:'50–80'},{name:'Charge',dmg:'50'}]};
const socket=io();
let myPokemon='',myUsername='',oppPokemon='',roomCode='',myTurn=false,timerInterval=null,pendingRematchCode='';

function showScreen(id){document.querySelectorAll('.screen').forEach(s=>s.classList.remove('active'));document.getElementById(id).classList.add('active');}
function selPoke(p){myPokemon=p;document.getElementById('pika-btn').className='poke-btn'+(p==='pikachu'?' sel-pika':'');document.getElementById('char-btn').className='poke-btn'+(p==='charizard'?' sel-char':'');document.getElementById('bulb-btn').className='poke-btn'+(p==='bulbasaur'?' sel-bulb':'');}

function findMatch(){
    const u=document.getElementById('username').value.trim();
    if(!u){alert('Enter a username!');return;}
    if(!myPokemon){alert('Choose a Pokémon!');return;}
    myUsername=u;
    socket.emit('join_random',{username:myUsername,pokemon:myPokemon});
    showScreen('waiting');
}

function cancelSearch(){
    socket.emit('cancel_random');
    window.location.href='/online';
}

socket.on('waiting',()=>showScreen('waiting'));
socket.on('error',d=>alert(d.msg));
socket.on('cancelled',()=>window.location.href='/online');

socket.on('game_start',d=>{
    roomCode=d.code; myTurn=d.your_turn; myPokemon=d.your_pokemon; oppPokemon=d.opp_pokemon;
    myUsername=document.getElementById('username').value.trim()||d.you;
    document.getElementById('f-you-name').textContent=d.you;
    document.getElementById('f-opp-name').textContent=d.opponent;
    document.getElementById('f-you-poke').textContent=d.your_pokemon.toUpperCase();
    document.getElementById('f-opp-poke').textContent=d.opp_pokemon.toUpperCase();
    document.getElementById('f-you-img').src=POKE_IMG[d.your_pokemon];
    document.getElementById('f-opp-img').src=POKE_IMG[d.opp_pokemon];
    setBar('f-you-bar','f-you-hp',150);
    setBar('f-opp-bar','f-opp-hp',150);
    renderAttacks(myTurn);
    showScreen('battle');
    setLog('Battle begins! '+(myTurn?'Your turn!':'Waiting for opponent...'));
    document.getElementById('chat-msgs').innerHTML='';
    document.getElementById('result-overlay').classList.remove('show');
    document.getElementById('rm-dialog').classList.remove('show');
});

socket.on('move_result',d=>{
    setBar('f-you-bar','f-you-hp', d.your_hp);
    setBar('f-opp-bar','f-opp-hp', d.opp_hp);
    myTurn=d.your_turn;
    setLog(d.log);
    renderAttacks(myTurn);
    const defEl=document.getElementById(myTurn?'f-opp':'f-you');
    defEl.classList.add('shaking');
    setTimeout(()=>defEl.classList.remove('shaking'),400);
    hurtImg(myTurn?'f-opp-img':'f-you-img');
});

socket.on('game_over',d=>{
    stopTimer();
    setBar('f-you-bar','f-you-hp', d.your_hp);
    setBar('f-opp-bar','f-opp-hp', d.opp_hp);
    setLog(d.log);
    const won=d.winner===myUsername;
    document.getElementById('res-img').src=POKE_IMG[won?myPokemon:oppPokemon];
    document.getElementById('res-title').textContent=won?'YOU WIN! 🏆':'YOU LOST 💀';
    document.getElementById('res-sub').textContent=won?'GG! Victory recorded.':'Better luck next time!';
    document.getElementById('rematch-btn').disabled=false;
    document.getElementById('rematch-btn').textContent='⚔️ Rematch';
    document.getElementById('result-overlay').classList.add('show');
});

socket.on('opponent_left',d=>{stopTimer();alert(d.msg);window.location.href='/online/random';});

socket.on('chat_incoming',d=>{
    const box=document.getElementById('chat-msgs');
    const isMe=d.username===myUsername;
    box.innerHTML+=`<span style="color:${isMe?'#FFD700':'#74b9ff'}">${d.username}:</span> ${escHtml(d.text)}<br>`;
    box.scrollTop=box.scrollHeight;
});

socket.on('rematch_incoming',d=>{
    pendingRematchCode=d.code;
    document.getElementById('rm-msg').textContent=d.from+' wants a rematch!';
    document.getElementById('rm-dialog').classList.add('show');
});

socket.on('rematch_denied',()=>{ alert('Opponent declined the rematch.'); });

function startTimer(){
    stopTimer();
    let secs=30;
    const bar=document.getElementById('timer-bar');
    const num=document.getElementById('timer-secs');
    bar.classList.add('active'); num.textContent=secs;
    timerInterval=setInterval(()=>{ secs--; num.textContent=secs; if(secs<=0) stopTimer(); },1000);
}
function stopTimer(){
    clearInterval(timerInterval); timerInterval=null;
    document.getElementById('timer-bar').classList.remove('active');
}
function sendChat(){
    const inp=document.getElementById('chat-input');
    const text=inp.value.trim();
    if(!text||!roomCode) return;
    socket.emit('chat_message',{code:roomCode,text}); inp.value='';
}
function requestRematch(){
    if(!roomCode) return;
    document.getElementById('rematch-btn').disabled=true;
    document.getElementById('rematch-btn').textContent='Waiting...';
    socket.emit('rematch_request',{code:roomCode});
}
function acceptRematch(){
    document.getElementById('rm-dialog').classList.remove('show');
    socket.emit('rematch_accept',{code:pendingRematchCode});
}
function denyRematch(){
    document.getElementById('rm-dialog').classList.remove('show');
    socket.emit('rematch_deny',{code:pendingRematchCode});
    pendingRematchCode='';
}
function escHtml(t){return t.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}

function hurtImg(imgId){const img=document.getElementById(imgId);if(!img)return;img.classList.add('hurt');setTimeout(()=>img.classList.remove('hurt'),700);}
function setBar(barId,numId,hp){const pct=Math.max(0,(hp/150)*100);const bar=document.getElementById(barId);if(!bar)return;bar.style.width=pct+'%';bar.className='hp-fill '+(pct>50?'high':pct>20?'mid':'low');document.getElementById(numId).textContent=Math.max(0,Math.round(hp));}
function setLog(msg){document.getElementById('battle-log').innerHTML=msg;}

function renderAttacks(myTurn){
    const grid=document.getElementById('attacks-grid');
    grid.innerHTML='';
    document.getElementById('turn-label').textContent=myTurn?"YOUR TURN":"OPPONENT'S TURN...";
    document.getElementById('f-you').classList.toggle('active-turn',myTurn);
    document.getElementById('f-opp').classList.toggle('active-turn',!myTurn);
    if(myTurn) startTimer(); else stopTimer();
    ATTACKS[myPokemon].forEach(atk=>{
        const btn=document.createElement('button');
        btn.className='atk-btn'; btn.disabled=!myTurn;
        btn.innerHTML=`<span>${atk.name}</span><span class="dmg">${atk.dmg} dmg</span>`;
        btn.onclick=()=>sendAttack(atk.name.toLowerCase());
        grid.appendChild(btn);
    });
    const d=document.createElement('button');
    d.className='atk-btn dodge-btn'; d.disabled=!myTurn;
    d.innerHTML='<span>🛡️ Dodge</span><span class="dmg">10% next hit</span>';
    d.onclick=()=>sendAttack('dodge');
    grid.appendChild(d);
}

function sendAttack(move){stopTimer();document.querySelectorAll('.atk-btn').forEach(b=>b.disabled=true);socket.emit('attack',{code:roomCode,move:move});}
</script>

<!-- PANIC BUTTON -->
<a href="/article" id="panic-btn" style="
    position:fixed; top:16px; left:16px; z-index:99999;
    background:#ff1a1a; color:white;
    font-family:Arial,sans-serif; font-weight:bold;
    font-size:0.95rem; padding:17px 22px;
    border-radius:10px; text-decoration:none;
    box-shadow:0 4px 20px rgba(255,26,26,0.6);
    line-height:1.5; text-align:center;
">🚨 TEACHER<br>COMING</a>
</body>
</html>
"""

leaderboard_html = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>🏆 Leaderboard — Pokémon Battle</title>
<link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&family=Nunito:wght@400;700;900&display=swap" rel="stylesheet">
<style>
:root{--yellow:#FFD700;--orange:#FF6B00;--dark:#0d0d1a;--card:#16213e;}
*{box-sizing:border-box;margin:0;padding:0;}
body{font-family:'Nunito',sans-serif;background:var(--dark);color:white;min-height:100vh;display:flex;flex-direction:column;align-items:center;padding:60px 20px 80px;text-align:center;}
.logo{font-family:'Press Start 2P',monospace;font-size:clamp(1rem,3vw,1.8rem);color:var(--yellow);text-shadow:0 0 30px rgba(255,215,0,0.5),3px 3px 0 #b8860b;margin-bottom:8px;}
.sub{color:#666;font-size:0.78rem;letter-spacing:3px;text-transform:uppercase;margin-bottom:40px;}
.lb-wrap{width:100%;max-width:560px;}
.lb-row{display:flex;align-items:center;gap:14px;background:var(--card);border-radius:14px;padding:16px 20px;margin-bottom:10px;border:1px solid #1e2a4a;transition:border-color 0.2s;}
.lb-row:hover{border-color:rgba(255,215,0,0.3);}
.lb-row.top1{border-color:gold;background:rgba(255,215,0,0.05);}
.lb-row.top2{border-color:silver;background:rgba(192,192,192,0.04);}
.lb-row.top3{border-color:#cd7f32;background:rgba(205,127,50,0.04);}
.lb-medal{font-size:1.5rem;flex-shrink:0;width:36px;}
.lb-rank-num{font-family:'Press Start 2P',monospace;font-size:0.55rem;color:#555;width:24px;text-align:right;}
.lb-name{font-family:'Press Start 2P',monospace;font-size:0.6rem;color:white;flex:1;text-align:left;}
.lb-pts{font-family:'Press Start 2P',monospace;font-size:0.55rem;color:var(--yellow);}
.lb-record{font-size:0.75rem;color:#555;margin-left:4px;}
.no-data{color:#444;font-size:0.9rem;margin-top:40px;}
.back-link{color:#444;font-size:0.78rem;text-decoration:none;transition:color 0.2s;margin-top:30px;display:inline-block;}
.back-link:hover{color:var(--yellow);}
/* panic */
</style>
</head>
<body>
<div class="logo">🏆 LEADERBOARD</div>
<p class="sub">+10 pts per win &nbsp;·&nbsp; -10 pts per loss</p>
<div class="lb-wrap" id="lb-wrap">
    <p class="no-data">Loading...</p>
</div>
<a href="/online" class="back-link">← Back to Online</a>

<!-- PANIC BUTTON -->
<a href="/article" style="position:fixed;top:16px;left:16px;z-index:99999;background:#ff1a1a;color:white;font-family:Arial,sans-serif;font-weight:bold;font-size:0.95rem;padding:17px 22px;border-radius:10px;text-decoration:none;box-shadow:0 4px 20px rgba(255,26,26,0.6);line-height:1.5;text-align:center;">🚨 TEACHER<br>COMING</a>

<script>
const MEDALS=['🥇','🥈','🥉'];
async function loadLB(){
    const res=await fetch('/api/leaderboard');
    const data=await res.json();
    const wrap=document.getElementById('lb-wrap');
    if(!data.players||data.players.length===0){
        wrap.innerHTML='<p class="no-data">No players yet. Play some games!</p>';
        return;
    }
    wrap.innerHTML=data.players.map((p,i)=>{
        const cls=i===0?'top1':i===1?'top2':i===2?'top3':'';
        const medal=i<3?`<span class="lb-medal">${MEDALS[i]}</span>`:`<span class="lb-rank-num">#${i+1}</span>`;
        return `<div class="lb-row ${cls}">
            ${medal}
            <span class="lb-name">${p.username}</span>
            <span class="lb-pts">${p.points} pts</span>
            <span class="lb-record">${p.wins}W/${p.losses}L</span>
        </div>`;
    }).join('');
}
loadLB();
</script>
</body>
</html>
"""

article_html = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Cognitive Load and Reading Comprehension — Educational Psychology Review</title>
<link href="https://fonts.googleapis.com/css2?family=Merriweather:ital,wght@0,400;0,700;1,400&family=Source+Sans+3:wght@400;600&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box;margin:0;padding:0;}
body{font-family:'Source Sans 3',sans-serif;background:#f9f7f2;color:#1a1a1a;line-height:1.8;}
.journal-header{background:#2c3e50;color:white;padding:10px 0;text-align:center;font-size:0.72rem;letter-spacing:3px;text-transform:uppercase;}
.article-wrap{max-width:740px;margin:0 auto;padding:40px 24px 80px;}
.article-label{font-size:0.72rem;color:#888;text-transform:uppercase;letter-spacing:2px;margin-bottom:12px;}
h1{font-family:'Merriweather',serif;font-size:clamp(1.3rem,2.5vw,1.9rem);line-height:1.3;margin-bottom:16px;color:#111;}
.byline{font-size:0.85rem;color:#888;margin-bottom:6px;}
.date{font-size:0.8rem;color:#aaa;margin-bottom:24px;padding-bottom:24px;border-bottom:1px solid #ddd;}
.abstract{background:#f0ede6;border-left:4px solid #2c3e50;padding:20px 24px;margin-bottom:32px;border-radius:0 8px 8px 0;}
.abstract strong{display:block;font-size:0.75rem;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;color:#555;}
.abstract p{font-size:0.92rem;color:#333;font-style:italic;}
h2{font-family:'Merriweather',serif;font-size:1.1rem;margin:32px 0 12px;color:#111;}
p{margin-bottom:18px;font-size:0.97rem;color:#222;}
blockquote{border-left:3px solid #ccc;padding-left:20px;margin:24px 0;color:#555;font-style:italic;}
table{width:100%;border-collapse:collapse;margin:24px 0;font-size:0.88rem;}
th{background:#2c3e50;color:white;padding:10px 14px;text-align:left;}
td{padding:9px 14px;border-bottom:1px solid #ddd;}
tr:nth-child(even) td{background:#f5f3ee;}
.figure-caption{font-size:0.78rem;color:#888;font-style:italic;margin-top:6px;}
.references p{margin-bottom:6px;font-size:0.82rem;color:#555;line-height:1.9;}
</style>
</head>
<body>

<div class="journal-header">Educational Psychology Review &nbsp;·&nbsp; Vol. 38, Issue 2 &nbsp;·&nbsp; 2026</div>

<div class="article-wrap">

    <p class="article-label">Research Article &nbsp;·&nbsp; Peer Reviewed</p>
    <h1>Cognitive Load Theory and Its Implications for Reading Comprehension in Secondary Education Environments</h1>
    <p class="byline">Dr. Sandra Hoffmann, Ph.D¹ &nbsp;·&nbsp; Prof. James L. Whitmore, Ed.D² &nbsp;·&nbsp; Dr. Lucía Fernández, Ph.D³</p>
    <p class="date">¹ University of Michigan &nbsp;·&nbsp; ² Harvard Graduate School of Education &nbsp;·&nbsp; ³ Universidad Complutense de Madrid &nbsp;·&nbsp; Accepted: February 28, 2026</p>

    <div class="abstract">
        <strong>Abstract</strong>
        <p>This article examines the relationship between cognitive load and reading comprehension outcomes in secondary school students aged 13–18. Drawing on Sweller's (1988) cognitive load theory and subsequent developments in working memory research, we analyze how intrinsic, extraneous, and germane load interact during sustained reading tasks. Our review of 47 longitudinal studies (N = 12,840) suggests that environmental factors significantly elevate extraneous cognitive load, reducing available working memory capacity for deep reading comprehension by an estimated 31–44%. Implications for instructional design and classroom policy are discussed.</p>
    </div>

    <h2>1. Introduction</h2>
    <p>Reading comprehension remains one of the most extensively studied competencies in educational psychology. Cognitive load theory, originally formulated by Sweller (1988) and later expanded by Paas, Renkl, and Sweller (2003), proposes that human working memory is limited in both capacity and duration, and that learning tasks vary in the degree to which they impose demands on this finite resource.</p>
    <p>Within secondary educational settings, students encounter reading tasks of varying complexity across multiple subject domains. Each of these genres imposes distinct cognitive demands, and the degree to which students can allocate working memory resources to meaning-making has direct implications for comprehension outcomes.</p>

    <h2>2. Theoretical Framework</h2>
    <p>Cognitive load theory distinguishes among three types of load: intrinsic load, determined by the inherent complexity of the material; extraneous load, imposed by the manner in which information is presented; and germane load, associated with schema formation. In reading contexts, extraneous load is elevated by environmental distractors that compete for attentional resources.</p>
    <blockquote>"Working memory is not a warehouse — it is a workbench, and its surface area is severely limited." — Baddeley &amp; Hitch, 1974</blockquote>

    <h2>3. Environmental Moderators</h2>
    <p>A consistent finding across the reviewed literature is the significant negative impact of task-switching on sustained reading comprehension. Studies by Ophir, Nass, and Wagner (2009) demonstrated that chronic multitasking is associated with reduced capacity to filter irrelevant stimuli and poorer performance on sustained attention measures.</p>

    <table>
        <tr><th>Environmental Factor</th><th>Effect on Extraneous Load</th><th>Impact on Comprehension</th></tr>
        <tr><td>Classroom noise (&gt;65dB)</td><td>+18% increase</td><td>−22% accuracy</td></tr>
        <tr><td>Device presence (passive)</td><td>+11% increase</td><td>−14% accuracy</td></tr>
        <tr><td>Device use (active, off-task)</td><td>+39% increase</td><td>−41% accuracy</td></tr>
        <tr><td>Task switching (&gt;3 per session)</td><td>+27% increase</td><td>−31% accuracy</td></tr>
        <tr><td>Optimal quiet environment</td><td>Baseline</td><td>Baseline</td></tr>
    </table>
    <p class="figure-caption">Table 1. Summary of environmental moderators. Adapted from Plass, Moreno &amp; Brünken (2010).</p>

    <h2>4. Implications for Instructional Design</h2>
    <p>The evidence reviewed here has several practical implications for educators. Text selection should account for the prior knowledge profiles of students. Instructional materials should minimize extraneous load through clear organizational structures. Classroom environments should establish clear expectations around device use, manage ambient noise levels, and design task sequences that minimize unnecessary context-switching.</p>

    <h2>5. Conclusion</h2>
    <p>Cognitive load theory provides a robust framework for understanding the conditions under which reading comprehension succeeds or fails. Extraneous cognitive load — particularly that arising from environmental distractors and task-switching — represents one of the most modifiable determinants of reading comprehension outcomes in secondary education. Future research should examine the dose-response relationship between specific distractor types and comprehension decrements.</p>

    <h2>References</h2>
    <div class="references">
        <p>Baddeley, A. D., &amp; Hitch, G. J. (1974). Working memory. <em>Psychology of Learning and Motivation, 8</em>, 47–89.</p>
        <p>Ophir, E., Nass, C., &amp; Wagner, A. D. (2009). Cognitive control in media multitaskers. <em>PNAS, 106</em>(37), 15583–15587.</p>
        <p>Paas, F., Renkl, A., &amp; Sweller, J. (2003). Cognitive load theory and instructional design. <em>Educational Psychologist, 38</em>(1), 1–4.</p>
        <p>Plass, J. L., Moreno, R., &amp; Brünken, R. (2010). <em>Cognitive Load Theory.</em> Cambridge University Press.</p>
        <p>Sweller, J. (1988). Cognitive load during problem solving. <em>Cognitive Science, 12</em>(2), 257–285.</p>
    </div>

</div>
</body>
</html>
"""


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
