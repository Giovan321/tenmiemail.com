from flask import Flask, request, render_template_string
import psycopg2

app = Flask(__name__)

def get_conn():
    return psycopg2.connect(
        dbname="registros",
        user="DatabaseGio",
        password="giovan12",
        host="127.0.0.1",  # TU SERVIDOR NUEVO
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
</style>
</head>

<body>

<h1>Registrarse</h1>

<form method="POST">
<input type="email" name="email" placeholder="Tu correo" required>
<button type="submit">Registrar</button>
</form>

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

@app.route("/", methods=["GET","POST"])
def index():

    conn = get_conn()
    cur = conn.cursor()
    mensaje = ""

    if request.method == "POST":
        email = request.form["email"]

        try:
            cur.execute(
                "INSERT INTO users (email) VALUES (%s)",
                (email,)
            )
            conn.commit()
            mensaje = "correo registrado"
        except Exception as e:
            conn.rollback()
            mensaje = "correo ya registrado"

    cur.execute("SELECT email FROM users")
    rows = cur.fetchall()
    emails = [r[0] for r in rows]

    cur.close()
    conn.close()

    return render_template_string(html, emails=emails, mensaje=mensaje)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
