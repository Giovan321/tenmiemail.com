from flask import Flask, request, render_template_string
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
<h1>Registrarse</h1>
<form method="POST">
<input type="email" name="email" placeholder="Tu correo" required>
<button type="submit">Registrar</button>
</form>

<div class="game-banner">
    <h2>⚡ Pokémon Battle</h2>
    <a class="game-btn" href="/game">🕹️ Free Game Here</a>
</div>

<h2>Correos registrados</h2>
<table>
<tr><th>Email</th></tr>
{% for email in emails %}
<tr><td>{{ email }}</td></tr>
{% endfor %}
</table>
<p>{{mensaje}}</p>
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
.screen { display:none; position:relative; z-index:1; }
.screen.active { display:block; }

/* ══ LOBBY ══ */
#lobby {
    min-height:100vh;
    display:flex; flex-direction:column;
    align-items:center; justify-content:center;
    padding:40px 20px;
}
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
#setup {
    min-height:100vh; display:flex; flex-direction:column;
    align-items:center; justify-content:center; padding:40px 20px;
}
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
#battle { min-height:100vh; padding:24px 16px; display:flex; flex-direction:column; align-items:center; }
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
            <button class="btn-secondary" onclick="showScreen('lobby')">Main Menu</button>
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

function showScreen(id){
    document.querySelectorAll('.screen').forEach(s=>s.classList.remove('active'));
    document.getElementById(id).classList.add('active');
    window.scrollTo(0,0);
}

function startSetup(mode){
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
</body>
</html>
"""

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
