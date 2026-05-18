from flask import Flask, render_template, request, redirect, jsonify, session
from datetime import datetime, timedelta, date
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "senha_secreta_da_barbearia"

USUARIO_ADMIN = "admin"
SENHA_ADMIN = "1234"

PRECOS = {
    "Corte": 40,
    "Corte + Barba": 60,
    "Corte + Sobrancelha": 50,
    "Corte + Sobrancelha + Barba": 70,
    "Corte + Cavanhaque": 55,
    "Corte + Sobrancelha + Cavanhaque": 60,
    "Barba": 20,
    "Sobrancelha": 20,
    "Corte + Luzes": 100,
    "Corte + Relaxamento": 70
}

def preco_servico(servico):
    return PRECOS.get(servico, 0)

def minutos_servico(servico):

    if servico in [
        "Corte + Barba",
        "Corte + Sobrancelha + Barba",
        "Corte + Cavanhaque",
        "Corte + Sobrancelha + Cavanhaque",
        "Corte + Relaxamento"
    ]:
        return 45

    if servico == "Corte + Luzes":
        return 90

    return 30

def horario_para_datetime(data, horario):
    return datetime.strptime(
        f"{data} {horario}",
        "%Y-%m-%d %H:%M"
    )

def tem_conflito(data, horario_novo, servico_novo):

    inicio_novo = horario_para_datetime(data, horario_novo)

    fim_novo = inicio_novo + timedelta(
        minutes=minutos_servico(servico_novo)
    )

    conexao = sqlite3.connect("database.db")
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT horario, servico
        FROM agendamentos
        WHERE data = ?
    """, (data,))

    agendamentos = cursor.fetchall()

    conexao.close()

    for horario_existente, servico_existente in agendamentos:

        inicio_existente = horario_para_datetime(
            data,
            horario_existente
        )

        fim_existente = inicio_existente + timedelta(
            minutes=minutos_servico(servico_existente)
        )

        if (
            inicio_novo < fim_existente and
            fim_novo > inicio_existente
        ):
            return True

    return False

def criar_banco():

    conexao = sqlite3.connect("database.db")
    cursor = conexao.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agendamentos (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            nome TEXT NOT NULL,
            telefone TEXT NOT NULL,
            servico TEXT NOT NULL,
            data TEXT NOT NULL,
            horario TEXT NOT NULL,
            observacao TEXT
        )
    """)

    conexao.commit()
    conexao.close()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        usuario = request.form["usuario"]
        senha = request.form["senha"]

        if (
            usuario == USUARIO_ADMIN and
            senha == SENHA_ADMIN
        ):

            session["admin"] = True

            return redirect("/agendamentos")

        else:
            return "Usuário ou senha incorretos."

    return render_template("login.html")

@app.route("/logout")
def logout():

    session.pop("admin", None)

    return redirect("/login")

@app.route("/horarios_ocupados")
def horarios_ocupados():

    data = request.args.get("data")

    horarios_base = [

        "09:00",
        "09:30",
        "10:00",
        "10:30",

        "11:00",
        "11:30",
        "12:00",

        "14:00",
        "14:30",
        "15:00",
        "15:30",

        "16:00",
        "16:30",
        "17:00",
        "17:30",

        "18:00",
        "18:30"
    ]

    ocupados = []

    for horario in horarios_base:

        if tem_conflito(
            data,
            horario,
            "Corte"
        ):
            ocupados.append(horario)

    return jsonify(ocupados)

@app.route("/agendar", methods=["POST"])
def agendar():

    nome = request.form["nome"]
    telefone = request.form["telefone"]
    servico = request.form["servico"]
    data = request.form["data"]
    horario = request.form["horario"]
    observacao = request.form["observacao"]

    if tem_conflito(data, horario, servico):

        return """
        Esse horário entra em conflito com outro agendamento.
        Volte e escolha outro horário.
        """

    conexao = sqlite3.connect("database.db")
    cursor = conexao.cursor()

    cursor.execute("""

        INSERT INTO agendamentos
        (
            nome,
            telefone,
            servico,
            data,
            horario,
            observacao
        )

        VALUES (?, ?, ?, ?, ?, ?)

    """, (
        nome,
        telefone,
        servico,
        data,
        horario,
        observacao
    ))

    conexao.commit()
    conexao.close()

    return redirect("/")

@app.route("/agendamentos")
def agendamentos():

    if not session.get("admin"):
        return redirect("/login")

    hoje = date.today().strftime("%Y-%m-%d")
    mes_atual = date.today().strftime("%Y-%m")

    conexao = sqlite3.connect("database.db")
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT *
        FROM agendamentos
        ORDER BY data, horario
    """)

    dados = cursor.fetchall()

    conexao.close()

    faturamento_total = 0
    faturamento_hoje = 0
    faturamento_mes = 0

    for item in dados:

        servico = item[3]
        data_agendada = item[4]

        valor = preco_servico(servico)

        faturamento_total += valor

        if data_agendada == hoje:
            faturamento_hoje += valor

        if data_agendada.startswith(mes_atual):
            faturamento_mes += valor

    return render_template(
        "agendamentos.html",

        agendamentos=dados,

        faturamento_total=faturamento_total,
        faturamento_hoje=faturamento_hoje,
        faturamento_mes=faturamento_mes
    )

@app.route("/excluir/<int:id>", methods=["POST"])
def excluir(id):

    if not session.get("admin"):
        return redirect("/login")

    conexao = sqlite3.connect("database.db")
    cursor = conexao.cursor()

    cursor.execute("""
        DELETE FROM agendamentos
        WHERE id = ?
    """, (id,))

    conexao.commit()
    conexao.close()

    return redirect("/agendamentos")

if __name__ == "__main__":

    criar_banco()

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port
    )