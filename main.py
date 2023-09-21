from flask import Flask, render_template, request, redirect
from datetime import datetime
import pymongo

app = Flask(__name__)

# Realizar a conexão com o banco de dados
url = "mongodb+srv://josejunior1007:LBylhl9LMi22I3x4@shopee.cmy5b2f.mongodb.net/?retryWrites=true&w=majority"
try:
    client = pymongo.MongoClient(url)
    db = client["Shopee"]
    col_expedicao = db["Expedicao"]
    print("DB connected ...")
except Exception as ex:
    print(ex)

# Rotas Prontas
@app.route("/")
def initial():
    pipeline = [
        {"$match": {
            "Status": {"$in": ["Assigned"]},
            "Motorista": {"$ne": None}
        }},
        {"$group": {
            "_id": "$Task ID",
            "count": {"$sum": 1},
            "City": {"$first": "$City"},
            "Total Distance": {"$first": "$Total Distance"},
            "Corridor/Cage": {"$first": "$Corridor/Cage"},
            "3pl": {"$first": "$3pl"},
            "Motorista": {"$first": "$Motorista"},
            "Placa": {"$first": "$Placa"},
            "Data": {"$first": "$Data"},
            "Status": {"$first": "$Status"}
        }}
    ]

    result = list(col_expedicao.aggregate(pipeline))
    return render_template("index.html", result=result)

# Seleção dos Dispatchers
@app.route("/selecao")
def selecao():
    pipeline = [
        {"$match": {
            "Status": {"$nin": ["Processing", "Complete", "Dispatched"]},
            "Motorista": {"$type": "double", "$exists": True}
        }},
        {"$group": {
            "_id": "$Task ID",
            "count": {"$sum": 1},
            "City": {"$first": "$City"},
            "Total Distance": {"$first": "$Total Distance"},
            "Corridor/Cage": {"$first": "$Corridor/Cage"},
            "3pl": {"$first": "$3pl"},
            "Motorista": {"$first": "$Motorista"},
            "Placa": {"$first": "$Placa"},
            "Data": {"$first": "$Data"},
            "Status": {"$first": "$Status"}
        }}
    ]

    result = list(col_expedicao.aggregate(pipeline))
    count = len(result)
    return render_template("selecao.html", result=result, count=count)

# Atualiza os dados dos Motoristas
@app.route("/atualizar-dados/<id>", methods=["POST", "GET"])
def atualizardados(id):
    if request.method == "POST":
        empresa = request.form.get("3pl")
        motorista = request.form.get("motorista")
        placa = request.form.get("placa")

        col_expedicao.update_many({"Task ID": id}, {"$set": {"Status": "Assigned", "3pl": empresa, "Motorista": motorista, "Placa": placa}})
        return redirect("/")
    return render_template("atualizardados.html")

# Atualiza os status de NoShow e Dispatched
@app.route("/atualizar-status/<id>", methods=["POST", "GET"])
def atualizarstatus(id):
    if request.method == "POST":
        status = request.form.get("status", False)
        if status == 'noshow':
            col_expedicao.update_many({"Task ID": id}, {"$set": {"Status": "NoShow"}})
    return redirect("/")

# Atualiza os dados da AT despachada
@app.route("/dispatched/<id>", methods=["POST", "GET"])
def dispatched(id):
    if request.method == "POST":
        horaInicio = request.form.get("horaInicio")
        horaFim = request.form.get("horaFim")
        doubleCheck = request.form.get("doubleCheck")

        col_expedicao.update_many({"Task ID": id}, {"$set": {"Status": "Dispatched", "horaInicio": horaInicio, "horaFim": horaFim, "doubleCheck": doubleCheck}})
        return redirect("/")
    return render_template("info_add.html")

# Rotas Expedidas
@app.route("/expedidas")
def expedidas():
    pipeline = [
        {"$match": {"Status": {"$in": ["Complete", "Dispatched"]}} },
        {"$group": {
            "_id": "$Task ID",
            "count": {"$sum": 1},
            "City": {"$first": "$City"},
            "Total Distance": {"$first": "$Total Distance"},
            "Corridor/Cage": {"$first": "$Corridor/Cage"},
            "3pl": {"$first": "$3pl"},
            "Motorista": {"$first": "$Motorista"},
            "Placa": {"$first": "$Placa"},
            "Data": {"$first": "$Data"},
            "Status": {"$first": "$Status"},
            "HoraInicio": {"$first": "$horaInicio"},
            "HoraFim": {"$first": "$horaFim"},
            "DoubleCheck": {"$first": "$doubleCheck"}
        }}
    ]

    result = list(col_expedicao.aggregate(pipeline))
    count = len(result)
    return render_template("expedidas.html", result=result, count=count)

# Rotas no Aguardo da Confirmação
@app.route("/aguardando")
def aguardando():
    pipeline = [
        {"$match": {"Status": "Processing"} },
        {"$group": {
            "_id": "$Task ID",
            "count": {"$sum": 1},
            "City": {"$first": "$City"},
            "Total Distance": {"$first": "$Total Distance"},
            "Corridor/Cage": {"$first": "$Corridor/Cage"}
        }}
    ]

    result = list(col_expedicao.aggregate(pipeline))
    count = len(result)
    return render_template("aguardando.html", result=result, count=count)

# Atualiza a AT que estava no aguardo
@app.route("/atualizar-data/<id>", methods=["POST", "GET"])
def atualizardata(id):
    if request.method == "POST":
        data = request.form.get("data")
        data_formatada = datetime.strptime(data, "%Y-%m-%d")  # Converta a string para um objeto de data
        data_formatada_str = data_formatada.strftime("%d/%m/%Y")
        col_expedicao.update_many({"Task ID": id}, {"$set": {"Status": "Processed", "Data": data_formatada_str}})

        return redirect("/")
    return render_template("atualizardata.html")

if __name__ == "__main__":
    app.run(debug=True)
