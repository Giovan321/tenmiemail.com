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
body{
    font-family:Arial;
    text-align:center;
    background:#000080;
    color:white;
}
input{
    padding:10px;
}
button{
    padding:10px;
}
table{
    margin:auto;
    border-collapse:collapse;
}
td,th{
    border:1px solid black;
    padding:10px;
}
.game-banner {
    margin: 30px auto;
    padding: 20px;
    background: linear-gradient(135deg, #ff6b00, #ffd700);
    border-radius: 16px;
    width: fit-content;
    box-shadow: 0 0 20px rgba(255, 165, 0, 0.6);
    animation: pulse 2s infinite;
}
.game-banner h2 {
    margin: 0 0 10px 0;
    color: #000;
    font-size: 1.4rem;
}
.game-btn {
    display: inline-block;
    padding: 14px 32px;
    background: #000;
    color: #ffd700;
    font-size: 1.1rem;
    font-weight: bold;
    border-radius: 8px;
    text-decoration: none;
    letter-spacing: 1px;
    transition: transform 0.2s;
}
.game-btn:hover {
    transform: scale(1.07);
    background: #111;
}
@keyframes pulse {
    0%, 100% { box-shadow: 0 0 20px rgba(255,165,0,0.6); }
    50%       { box-shadow: 0 0 35px rgba(255,165,0,1); }
}
</style>
</head>

<body>

<h1>Registrarse</h1>

<form method="POST">
<input type="email" name="email" placeholder="Tu correo" required>
<button type="submit">Registrar</button>
</form>

<!-- GAME BANNER -->
<div class="game-banner">
    <h2>🎮 ¡Nuevo! Batalla Pokémon</h2>
    <a class="game-btn" href="/game">🕹️ Free Game Here</a>
</div>

<h2>Correos registrados</h2>

<table>
<tr>
<th>Email</th>
</tr>

{% for email in emails %}
<tr>
<td>{{ email }}</td>
</tr>
{% endfor %}

</table>

<p>{{mensaje}}</p>

</body>
</html>
"""

game_html = """
<!DOCTYPE html>
<html>
<head>
<title>Pokemon Battle</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    font-family: Arial, sans-serif;
    background: #1a1a2e;
    color: white;
    text-align: center;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}
h1 {
    font-size: 2.5rem;
    color: #ffd700;
    text-shadow: 0 0 20px rgba(255, 215, 0, 0.5);
    margin-bottom: 10px;
}
.subtitle {
    color: #aaa;
    margin-bottom: 40px;
    font-size: 1rem;
}
.cards {
    display: flex;
    gap: 24px;
    justify-content: center;
    flex-wrap: wrap;
    margin-bottom: 40px;
}
.card {
    background: #16213e;
    border: 2px solid #ffd700;
    border-radius: 16px;
    padding: 30px 24px;
    width: 200px;
    cursor: pointer;
    transition: transform 0.2s, box-shadow 0.2s;
}
.card:hover {
    transform: translateY(-6px);
    box-shadow: 0 8px 30px rgba(255, 215, 0, 0.3);
}
.card .emoji { font-size: 3rem; margin-bottom: 12px; }
.card h3 { color: #ffd700; margin-bottom: 8px; }
.card p { color: #aaa; font-size: 0.85rem; }
.coming-soon {
    background: #0f3460;
    border-radius: 12px;
    padding: 16px 32px;
    color: #aaa;
    font-size: 0.95rem;
    margin-bottom: 30px;
}
.coming-soon span { color: #ffd700; font-weight: bold; }
.back-btn {
    color: #ffd700;
    text-decoration: none;
    font-size: 0.9rem;
    opacity: 0.7;
    transition: opacity 0.2s;
}
.back-btn:hover { opacity: 1; }
</style>
</head>
<body>

<h1>⚡ Pokémon Battle ⚡</h1>
<p class="subtitle">Choose your game mode</p>

<div class="cards">
    <div class="card">
        <div class="emoji">🤖</div>
        <h3>vs Bot</h3>
        <p>Fight against the computer. Coming soon online!</p>
    </div>
    <div class="card">
        <div class="emoji">👥</div>
        <h3>vs Player</h3>
        <p>Challenge a friend in the same room. Multiplayer online coming soon!</p>
    </div>
</div>

<div class="coming-soon">
    🚧 <span>Online multiplayer</span> is coming soon — stay tuned!
</div>

<a class="back-btn" href="/">← Back to home</a>

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
