from flask import Flask, request, render_template_string, session
from flask_socketio import SocketIO, emit, join_room, leave_room
import random, string
import psycopg2

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
<title>Registro</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');
body{
    font-family:Arial;
    text-align:center;
    background:#000080;
    color:white;
}
input{ padding:10px; }
button{ padding:10px; }
table{ margin:auto; border-collapse:collapse; }
td,th{ border:1px solid black; padding:10px; }
.game-banner {
    margin: 30px auto;
    padding: 20px 30px;
    background: linear-gradient(135deg, #ff6b00, #ffd700);
    border-radius: 16px;
    width: fit-content;
    box-shadow: 0 0 20px rgba(255,165,0,0.6);
    animation: pulse 2s infinite;
}
.game-banner h2 { margin:0 0 10px 0; color:#000; font-size:1.1rem; font-family:'Press Start 2P', monospace; }
.game-btn {
    display:inline-block; padding:14px 32px;
    background:#000; color:#ffd700;
    font-size:0.85rem; font-weight:bold;
    border-radius:8px; text-decoration:none;
    letter-spacing:1px; transition:transform 0.2s;
    font-family:'Press Start 2P', monospace;
}
.game-btn:hover { transform:scale(1.07); }
@keyframes pulse {
    0%,100% { box-shadow:0 0 20px rgba(255,165,0,0.6); }
    50%      { box-shadow:0 0 40px rgba(255,165,0,1); }
}
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
    font-family:Arial,sans-serif; text-align:center;
">
    <div style="width:100%;">
        <div style="font-size:1.4rem; color:#FFD700; font-weight:bold; margin-bottom:14px;">🚨 Panic Button</div>
        <div style="font-size:1.05rem; color:#ccc; line-height:1.7;">If the teacher comes, press the red button in the top-left corner — it'll switch to a boring study article instantly.</div>
    </div>
    <button onclick="document.getElementById('how-to-popup').style.display='none'" style="
        background:#ff1a1a; color:white; border:none;
        padding:14px 36px; border-radius:10px;
        font-size:1rem; font-weight:bold;
        cursor:pointer;
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

<style>
@keyframes bounce { 0%,100%{transform:translateY(0);} 50%{transform:translateY(-8px);} }
</style>

<div style="margin-top:60px;">
<h1>⚡ Want to play with other people?</h1>
<p style="font-size:1rem;margin-bottom:16px;">Enter your email so other players can challenge you!</p>
<form method="POST">
<input type="email" name="email" placeholder="Tu correo" required>
<button type="submit">Registrar</button>
</form>

<div class="game-banner">
    <h2>⚡ Pokémon Battle</h2>
    <a class="game-btn" href="/game">🕹️ Local Game</a>
    &nbsp;&nbsp;
    <a class="game-btn" href="/online">🌍 Play Online</a>
</div>

<h2>Correos registrados</h2>
<table>
<tr><th>Email</th></tr>
{% for email in emails %}
<tr><td>{{ email }}</td></tr>
{% endfor %}
</table>
<p>{{mensaje}}</p>
</div>

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
.fighter img    { width:86px; height:86px; object-fit:contain; filter:drop-shadow(0 0 10px rgba(255,215,0,0.3)); transition:transform 0.3s; }
.fighter img.attacking { animation:atk-anim 0.5s; }
@keyframes atk-anim { 0%,100%{transform:scale(1);} 50%{transform:scale(1.22) rotate(-5deg);} }

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
        <div class="result-btns">
            <button class="btn-primary"   onclick="resetGame()">PLAY AGAIN</button>
            <button class="btn-secondary" onclick="window.location.href='/'">Main Menu</button>
        </div>
    </div>
</div>

<script>
const POKE_IMG = {
    pikachu:  'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/25.png',
    charizard:'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/6.png'
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
    ]
};
function rnd(a,b){return Math.floor(Math.random()*(b-a+1))+a;}

let gameMode='bot', name1='', name2='ENEMY', choice1=null, choice2=null;
let hp1=150, hp2=150, dodge1=false, dodge2=false, turn=0, maxTurns=10, pvpTurn=1;

// ── STARTUP CHECKS ──
console.log('✅ Pokemon Battle JS loaded OK');
window.addEventListener('load', ()=>{
    console.log('✅ Page fully loaded');
    const testUrls = {
        'Pikachu':   'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/25.png',
        'Charizard': 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/6.png'
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
    ['pika-btn','char-btn','pika2-btn','char2-btn'].forEach(id=>{
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
    } else {
        choice2=poke;
        document.getElementById('pika2-btn').className='poke-btn'+(poke==='pikachu'?' selected-pika':'');
        document.getElementById('char2-btn').className='poke-btn'+(poke==='charizard'?' selected-char':'');
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
        choice2=choice1==='pikachu'?'charizard':'pikachu';
    }
    initBattle();
    showScreen('battle');
}

function initBattle(){
    hp1=150; hp2=150; dodge1=false; dodge2=false; turn=0; pvpTurn=1;
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

function doAttack(atk, playerNum){
    disableAll();
    let dmg=atk.fn();
    const atkImg=document.getElementById(playerNum===1?'f1-img':'f2-img');
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

    setTimeout(()=>{defEl.classList.add('shaking');},80);
    setTimeout(()=>{defEl.classList.remove('shaking');},480);
    updateHP();

    setTimeout(()=>{
        if(checkEnd()) return;
        if(gameMode==='pvp'){ pvpTurn=pvpTurn===1?2:1; renderAttacks(pvpTurn); }
        else { turn++; if(turn>=maxTurns){checkEnd(true);return;} botTurn(); }
    },750);
}

function doDodge(playerNum){
    if(playerNum===1){ dodge1=true; setLog(`<span class="log-dodge">🛡️ ${name1} braces! Next hit deals only 10% damage.</span>`); }
    else              { dodge2=true; setLog(`<span class="log-dodge">🛡️ ${name2} braces! Next hit deals only 10% damage.</span>`); }
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

        setTimeout(()=>{document.getElementById('f1').classList.add('shaking');},80);
        setTimeout(()=>{document.getElementById('f1').classList.remove('shaking');},480);
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

function showResult(img, title, sub){
    const ri=document.getElementById('result-img');
    if(img){ri.src=img;ri.style.display='block';}else{ri.style.display='none';}
    document.getElementById('result-title').textContent=title;
    document.getElementById('result-sub').textContent=sub;
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

def make_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def get_damage(att):
    if att in ["electro rope", "fire ring"]:   return random.randint(1, 100)
    elif att in ["iron tail", "ancient power"]: return random.randint(40, 90)
    elif att in ["elite thunder", "fire ball"]: return random.randint(50, 80)
    elif att == "charge":                       return 50
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
    cur.execute("SELECT wins, losses FROM usernames WHERE username=%s", (username,))
    row = cur.fetchone()
    cur.close(); conn.close()
    if not row: return None
    wins, losses = row
    total = wins + losses
    rate = round((wins/total)*100) if total > 0 else 0
    return {"wins": wins, "losses": losses, "total": total, "rate": rate}

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
    return render_template_string(html, emails=emails, mensaje=mensaje)

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

# ── SOCKET EVENTS ──
@socketio.on('join_friend_room')
def on_join_friend(data):
    username = data['username']
    code     = data.get('code', '').upper().strip()
    pokemon  = data['pokemon']
    sid      = request.sid

    get_or_create_user(username)

    if not code:
        # Create new room
        code = make_code()
        rooms[code] = {
            'players': [{'sid': sid, 'username': username, 'pokemon': pokemon, 'hp': 150, 'dodge': False}],
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
        room['players'].append({'sid': sid, 'username': username, 'pokemon': pokemon, 'hp': 150, 'dodge': False})
        join_room(code)
        start_game(code)

@socketio.on('join_random')
def on_join_random(data):
    username = data['username']
    pokemon  = data['pokemon']
    sid      = request.sid

    get_or_create_user(username)

    # Check if someone is waiting
    if waiting_pool:
        waiting = waiting_pool.pop(0)
        code = make_code()
        rooms[code] = {
            'players': [
                waiting,
                {'sid': sid, 'username': username, 'pokemon': pokemon, 'hp': 150, 'dodge': False}
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
        waiting_pool.append({'sid': sid, 'username': username, 'pokemon': pokemon, 'hp': 150, 'dodge': False})
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

@socketio.on('attack')
def on_attack(data):
    code   = data['code']
    move   = data['move']
    sid    = request.sid

    if code not in rooms: return
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
    else:
        dmg = get_damage(move)
        if defender['dodge']:
            dmg = dmg // 10
            defender['dodge'] = False
        defender['hp'] -= dmg
        defender['hp'] = max(0, defender['hp'])

        msg = f"⚔️ {attacker['username']} used {move} — {dmg} damage!"

        if defender['hp'] <= 0:
            winner = attacker['username']
            save_match(players[0]['username'], players[1]['username'], winner)
            socketio.emit('game_over', {
                'winner': winner, 'log': msg,
                'your_hp': attacker['hp'], 'opp_hp': defender['hp']
            }, to=attacker['sid'])
            socketio.emit('game_over', {
                'winner': winner, 'log': msg,
                'your_hp': defender['hp'], 'opp_hp': attacker['hp']
            }, to=defender['sid'])
            del rooms[code]
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

@socketio.on('disconnect')
def on_disconnect():
    sid = request.sid
    global waiting_pool
    waiting_pool = [p for p in waiting_pool if p['sid'] != sid]
    for code, room in list(rooms.items()):
        for p in room['players']:
            if p['sid'] == sid:
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
</div>

<div class="stats-box">
    <h3>📊 CHECK WIN RATE</h3>
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
    el.innerHTML = `<span class="big">${d.rate}%</span> win rate<br>${d.wins} wins · ${d.losses} losses · ${d.total} games`;
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
:root{--yellow:#FFD700;--orange:#FF6B00;--dark:#0d0d1a;--card:#16213e;--pika:#F7C948;--char:#FF4500;}
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
.fighter img{width:80px;height:80px;object-fit:contain;filter:drop-shadow(0 0 8px rgba(255,215,0,0.3));}
.fighter img.atk{animation:atk-anim 0.5s;}
@keyframes atk-anim{0%,100%{transform:scale(1);}50%{transform:scale(1.2) rotate(-5deg);}}
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
    <div class="battle-log" id="battle-log">Battle begins!</div>
    <div class="attacks-grid" id="attacks-grid"></div>
</div>

<!-- RESULT OVERLAY -->
<div class="result-overlay" id="result-overlay">
    <div class="result-box">
        <img id="res-img" src="">
        <h2 id="res-title">WINNER!</h2>
        <p  id="res-sub"></p>
        <div class="result-btns">
            <button class="btn-primary"   onclick="window.location.href='/online/friend'">Play Again</button>
            <button class="btn-secondary" onclick="window.location.href='/online'">Main Menu</button>
        </div>
    </div>
</div>

<script>
const POKE_IMG = {
    pikachu:  'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/25.png',
    charizard:'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/6.png'
};
const ATTACKS = {
    pikachu:  [{name:'Electro Rope',dmg:'1–100'},{name:'Iron Tail',dmg:'40–90'},{name:'Elite Thunder',dmg:'50–80'},{name:'Charge',dmg:'50'}],
    charizard:[{name:'Fire Ring',dmg:'1–100'},{name:'Ancient Power',dmg:'40–90'},{name:'Fire Ball',dmg:'50–80'},{name:'Charge',dmg:'50'}]
};

const socket = io();
let myPokemon='', myUsername='', roomCode='', myTurn=false, myIdx=0;

function showScreen(id){
    document.querySelectorAll('.screen').forEach(s=>s.classList.remove('active'));
    document.getElementById(id).classList.add('active');
}

function selPoke(p){
    myPokemon=p;
    document.getElementById('pika-btn').className='poke-btn'+(p==='pikachu'?' sel-pika':'');
    document.getElementById('char-btn').className='poke-btn'+(p==='charizard'?' sel-char':'');
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
    myPokemon=d.your_pokemon;
    updateHP(d.your_hp, d.opp_hp);
    renderAttacks(myTurn);
    showScreen('battle');
    setLog('Battle begins! ' + (myTurn?'Your turn!':'Waiting for opponent...'));
});

socket.on('move_result', d=>{
    setBar('f-you-bar','f-you-hp', d.your_hp);
    setBar('f-opp-bar','f-opp-hp', d.opp_hp);
    myTurn=d.your_turn;
    setLog(d.log);
    renderAttacks(myTurn);
    const defEl=document.getElementById(myTurn?'f-opp':'f-you');
    defEl.classList.add('shaking');
    setTimeout(()=>defEl.classList.remove('shaking'),400);
});

socket.on('game_over', d=>{
    setBar('f-you-bar','f-you-hp', d.your_hp);
    setBar('f-opp-bar','f-opp-hp', d.opp_hp);
    setLog(d.log);
    const won = d.winner===myUsername;
    document.getElementById('res-img').src=won?POKE_IMG[myPokemon]:POKE_IMG[myPokemon==='pikachu'?'charizard':'pikachu'];
    document.getElementById('res-title').textContent=won?'YOU WIN! 🏆':'YOU LOST 💀';
    document.getElementById('res-sub').textContent=won?'GG! Victory recorded.':'Better luck next time!';
    document.getElementById('result-overlay').classList.add('show');
});

socket.on('opponent_left', d=>{
    alert(d.msg);
    window.location.href='/online/friend';
});

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
:root{--yellow:#FFD700;--orange:#FF6B00;--dark:#0d0d1a;--card:#16213e;--pika:#F7C948;--char:#FF4500;}
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
.fighter img{width:80px;height:80px;object-fit:contain;filter:drop-shadow(0 0 8px rgba(255,215,0,0.3));}
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
    <div class="battle-log" id="battle-log">Battle begins!</div>
    <div class="attacks-grid" id="attacks-grid"></div>
</div>

<!-- RESULT -->
<div class="result-overlay" id="result-overlay">
    <div class="result-box">
        <img id="res-img" src="">
        <h2 id="res-title">WINNER!</h2>
        <p  id="res-sub"></p>
        <div class="result-btns">
            <button class="btn-primary"   onclick="window.location.href='/online/random'">Play Again</button>
            <button class="btn-secondary" onclick="window.location.href='/online'">Main Menu</button>
        </div>
    </div>
</div>

<script>
const POKE_IMG={pikachu:'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/25.png',charizard:'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/6.png'};
const ATTACKS={pikachu:[{name:'Electro Rope',dmg:'1–100'},{name:'Iron Tail',dmg:'40–90'},{name:'Elite Thunder',dmg:'50–80'},{name:'Charge',dmg:'50'}],charizard:[{name:'Fire Ring',dmg:'1–100'},{name:'Ancient Power',dmg:'40–90'},{name:'Fire Ball',dmg:'50–80'},{name:'Charge',dmg:'50'}]};
const socket=io();
let myPokemon='',myUsername='',roomCode='',myTurn=false;

function showScreen(id){document.querySelectorAll('.screen').forEach(s=>s.classList.remove('active'));document.getElementById(id).classList.add('active');}
function selPoke(p){myPokemon=p;document.getElementById('pika-btn').className='poke-btn'+(p==='pikachu'?' sel-pika':'');document.getElementById('char-btn').className='poke-btn'+(p==='charizard'?' sel-char':'');}

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
    roomCode=d.code; myTurn=d.your_turn; myPokemon=d.your_pokemon;
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
});

socket.on('game_over',d=>{
    setBar('f-you-bar','f-you-hp', d.your_hp);
    setBar('f-opp-bar','f-opp-hp', d.opp_hp);
    setLog(d.log);
    const won=d.winner===myUsername;
    document.getElementById('res-img').src=won?POKE_IMG[myPokemon]:POKE_IMG[myPokemon==='pikachu'?'charizard':'pikachu'];
    document.getElementById('res-title').textContent=won?'YOU WIN! 🏆':'YOU LOST 💀';
    document.getElementById('res-sub').textContent=won?'GG! Victory recorded.':'Better luck next time!';
    document.getElementById('result-overlay').classList.add('show');
});

socket.on('opponent_left',d=>{alert(d.msg);window.location.href='/online/random';});

function setBar(barId,numId,hp){const pct=Math.max(0,(hp/150)*100);const bar=document.getElementById(barId);if(!bar)return;bar.style.width=pct+'%';bar.className='hp-fill '+(pct>50?'high':pct>20?'mid':'low');document.getElementById(numId).textContent=Math.max(0,Math.round(hp));}
function setLog(msg){document.getElementById('battle-log').innerHTML=msg;}

function renderAttacks(myTurn){
    const grid=document.getElementById('attacks-grid');
    grid.innerHTML='';
    document.getElementById('turn-label').textContent=myTurn?"YOUR TURN":"OPPONENT'S TURN...";
    document.getElementById('f-you').classList.toggle('active-turn',myTurn);
    document.getElementById('f-opp').classList.toggle('active-turn',!myTurn);
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

function sendAttack(move){document.querySelectorAll('.atk-btn').forEach(b=>b.disabled=true);socket.emit('attack',{code:roomCode,move:move});}
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
