from flask import Flask, request, render_template_string
from datetime import datetime
import json
import random
import os

app = Flask(__name__)

ARQUIVO = "agendamentos.json"
SENHA_ADMIN = "12345"

HORARIOS = [
    "09:00","09:30","10:00","10:30",
    "11:00","11:30","12:00","12:30",
    "13:00","13:30","14:00","14:30",
    "15:00","15:30","16:00","16:30",
    "17:00","17:30","18:00"
]

# =========================
# CRIAR JSON
# =========================

if not os.path.exists(ARQUIVO):
    with open(ARQUIVO, "w", encoding="utf-8") as f:
        json.dump([], f)

# =========================
# CARREGAR
# =========================

def carregar():
    try:
        with open(ARQUIVO, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

# =========================
# SALVAR
# =========================

def salvar(dados):
    with open(ARQUIVO, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

# =========================
# HTML CLIENTE
# =========================

HTML = """

<!DOCTYPE html>
<html lang="pt-br">
<head>
<meta charset="UTF-8">
<title>Barbearia</title>

<style>

body{
    background:#000;
    font-family:Arial;
    display:flex;
    justify-content:center;
    align-items:center;
    min-height:100vh;
    margin:0;
    color:white;
    padding:20px;
}

.box{
    width:380px;
    background:#050505;
    border:2px solid red;
    border-radius:25px;
    padding:35px;
    box-shadow:0 0 25px red;
}

h1{
    color:red;
    text-align:center;
    font-size:50px;
}

.sub{
    text-align:center;
    color:#aaa;
    margin-bottom:30px;
}

input,select{
    width:100%;
    padding:16px;
    margin-bottom:15px;
    border:none;
    border-radius:12px;
    background:#111;
    color:white;
    font-size:17px;
    box-sizing:border-box;
}

button{
    width:100%;
    padding:16px;
    border:none;
    border-radius:12px;
    background:red;
    color:white;
    font-size:20px;
    font-weight:bold;
    cursor:pointer;
}

button:hover{
    background:#ff2a2a;
}

.confirmado{
    text-align:center;
}

.codigo{
    background:red;
    padding:18px;
    border-radius:15px;
    font-size:35px;
    margin:20px 0;
    font-weight:bold;
}

.info{
    background:#111;
    padding:18px;
    border-radius:15px;
    line-height:30px;
}

.erro{
    background:red;
    padding:14px;
    border-radius:10px;
    text-align:center;
    margin-top:15px;
}

</style>
</head>

<body>

<div class="box">

{% if confirmado %}

<div class="confirmado">

<h1>✓</h1>

<h2>AGENDAMENTO CONFIRMADO</h2>

<div class="codigo">
#{{codigo}}
</div>

<div class="info">

<b>Nome:</b> {{nome}} <br>
<b>Serviço:</b> {{servico}} <br>
<b>Valor:</b> {{valor}} <br>
<b>Data:</b> {{data}} <br>
<b>Horário:</b> {{horario}}

</div>

</div>

{% else %}

<h1>BARBEARIA</h1>

<div class="sub">
Sistema de Agendamento
</div>

<form method="POST">

<input type="text"
name="nome"
placeholder="Seu nome"
required>

<select name="servico" required>

<option value="">
Escolha um serviço
</option>

<option value="Corte|R$40">
Corte - R$40
</option>

<option value="Barba|R$25">
Barba - R$25
</option>

<option value="Corte + Barba|R$60">
Corte + Barba - R$60
</option>

</select>

<input type="date"
name="data"
required>

<select name="horario" required>

<option value="">
Escolha um horário
</option>

{% for h in horarios %}

{% if h in ocupados %}

<option disabled>
{{h}} - INDISPONÍVEL
</option>

{% else %}

<option value="{{h}}">
{{h}}
</option>

{% endif %}

{% endfor %}

</select>

<button type="submit">
Agendar Agora
</button>

</form>

{% if erro %}
<div class="erro">
{{erro}}
</div>
{% endif %}

{% endif %}

</div>

</body>
</html>

"""

# =========================
# HTML ADMIN
# =========================

ADMIN = """

<!DOCTYPE html>
<html lang="pt-br">
<head>
<meta charset="UTF-8">
<title>Painel Barbeiro</title>

<style>

body{
    background:black;
    font-family:Arial;
    color:white;
    margin:0;
    padding:20px;
}

.box{
    max-width:800px;
    margin:auto;
}

h1{
    color:red;
    text-align:center;
}

.login{
    background:#111;
    padding:25px;
    border-radius:20px;
}

input{
    width:100%;
    padding:15px;
    margin-top:10px;
    border:none;
    border-radius:10px;
    background:#222;
    color:white;
    font-size:17px;
    box-sizing:border-box;
}

button{
    width:100%;
    padding:15px;
    margin-top:10px;
    border:none;
    border-radius:10px;
    background:red;
    color:white;
    font-size:18px;
    font-weight:bold;
    cursor:pointer;
}

.card{
    background:#111;
    padding:20px;
    border-radius:20px;
    margin-top:20px;
    line-height:30px;
}

.remover{
    background:red;
}

.atendido{
    background:green;
}

.total{
    background:#111;
    padding:20px;
    border-radius:20px;
    margin-top:20px;
    text-align:center;
    font-size:25px;
}

.erro{
    background:red;
    padding:15px;
    border-radius:10px;
    margin-top:15px;
    text-align:center;
}

.status{
    color:lime;
    font-weight:bold;
}

</style>
</head>

<body>

<div class="box">

<h1>PAINEL BARBEIRO</h1>

{% if not logado %}

<div class="login">

<form method="POST">

<input type="password"
name="senha"
placeholder="Digite a senha">

<button type="submit">
Entrar
</button>

</form>

{% if erro %}
<div class="erro">
{{erro}}
</div>
{% endif %}

</div>

{% else %}

<form method="GET">

<input type="text"
name="buscar"
placeholder="Buscar código">

<button type="submit">
Buscar Código
</button>

</form>

<div class="total">
TOTAL GANHO: {{total}}
</div>

{% for ag in dados %}

<div class="card">

<b>Cliente:</b> {{ag.nome}} <br>

<b>Serviço:</b> {{ag.servico}} <br>

<b>Valor:</b> {{ag.valor}} <br>

<b>Data:</b> {{ag.data}} <br>

<b>Horário:</b> {{ag.horario}} <br>

<b>Código:</b> #{{ag.codigo}} <br>

<b>Status:</b>
<span class="status">
{{ag.status}}
</span>

<form action="/atendido" method="POST">

<input type="hidden"
name="codigo"
value="{{ag.codigo}}">

<button class="atendido">
Cliente Atendido
</button>

</form>

<form action="/remover" method="POST">

<input type="hidden"
name="codigo"
value="{{ag.codigo}}">

<button class="remover">
Remover Agendamento
</button>

</form>

</div>

{% endfor %}

{% endif %}

</div>

</body>
</html>

"""

# =========================
# CLIENTE
# =========================

@app.route("/", methods=["GET", "POST"])
def inicio():

    erro = None

    dados = carregar()

    hoje = datetime.now().strftime("%Y-%m-%d")

    ocupados = []

    for ag in dados:
        if ag["data"] == hoje:
            ocupados.append(ag["horario"])

    if request.method == "POST":

        nome = request.form["nome"]

        servico_completo = request.form["servico"]

        servico, valor = servico_completo.split("|")

        data = request.form["data"]

        horario = request.form["horario"]

        for ag in dados:

            if ag["data"] == data and ag["horario"] == horario:

                return render_template_string(
                    HTML,
                    horarios=HORARIOS,
                    ocupados=ocupados,
                    erro="⚠ Horário já ocupado!"
                )

        codigo = random.randint(1000, 9999)

        novo = {
            "nome": nome,
            "servico": servico,
            "valor": valor,
            "data": data,
            "horario": horario,
            "codigo": codigo,
            "status": "Agendado"
        }

        dados.append(novo)

        salvar(dados)

        return render_template_string(
            HTML,
            confirmado=True,
            codigo=codigo,
            nome=nome,
            servico=servico,
            valor=valor,
            data=data,
            horario=horario
        )

    return render_template_string(
        HTML,
        horarios=HORARIOS,
        ocupados=ocupados,
        erro=erro
    )

# =========================
# ADMIN
# =========================

@app.route("/admin", methods=["GET", "POST"])
def admin():

    erro = None
    logado = False

    if request.method == "POST":

        senha = request.form["senha"]

        if senha == SENHA_ADMIN:
            logado = True

        else:
            return render_template_string(
                ADMIN,
                erro="Senha incorreta!",
                logado=False
            )

    elif request.args.get("painel") == "1":
        logado = True

    dados = carregar()

    buscar = request.args.get("buscar")

    if buscar:

        filtrados = []

        for ag in dados:

            if buscar in str(ag["codigo"]):
                filtrados.append(ag)

        dados = filtrados

    total = 0

    for ag in dados:

        valor = ag.get("valor", "R$0")

        valor = (
            valor
            .replace("R$", "")
            .replace(",", ".")
        )

        total += float(valor)

    total = f"R${total:.2f}"

    return render_template_string(
        ADMIN,
        dados=dados,
        total=total,
        logado=logado,
        erro=erro
    )

# =========================
# REMOVER
# =========================

@app.route("/remover", methods=["POST"])
def remover():

    codigo = request.form["codigo"]

    dados = carregar()

    novos = []

    for ag in dados:

        if str(ag["codigo"]) != str(codigo):
            novos.append(ag)

    salvar(novos)

    return """
    <script>
    alert('Agendamento removido!')
    window.location.href='/admin?painel=1'
    </script>
    """

# =========================
# CLIENTE ATENDIDO
# =========================

@app.route("/atendido", methods=["POST"])
def atendido():

    codigo = request.form["codigo"]

    dados = carregar()

    for ag in dados:

        if str(ag["codigo"]) == str(codigo):
            ag["status"] = "Atendido"

    salvar(dados)

    return """
    <script>
    alert('Cliente marcado como atendido!')
    window.location.href='/admin?painel=1'
    </script>
    """

# =========================
# INICIAR
# =========================

if __name__ == "__main__":
    app.run(debug=True)