from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import docker

from os import path

app = Flask(__name__)
CORS(app)  # Permite requisições do frontend
client = docker.from_env()

USER_PATH = path.expanduser("~")
LOCAL_STORAGE_PATH = path.join(USER_PATH, )

# 📌 1️⃣ Listar todos os containers SQL Server
@app.route('/containers', methods=['GET'])
def list_containers():
    containers = client.containers.list(all=True)
    port = containers[0].ports['1433/tcp'][0]['HostPort']
    sql_containers = [
        {
            "id": c.id[:12],
            "name": c.name,
            "status": c.status,
            "ports": c.ports['1433/tcp'][0]['HostPort'] if c.ports.get('1433/tcp') else 'not running'
        }
        for c in containers if "mssql" in c.image.tags[0]
    ]
    return jsonify(sql_containers)

# 📌 2️⃣ Criar um novo banco de dados (container)
@app.route('/create', methods=['POST'])
def create_container():
    data = request.json
    name = f"sqlserver-{data.get('name')}"
    port = data.get('port')
    volumes = {}
    if data.get('persists'):
        volumes = {
            path.join(USER_PATH, "docker","sqlservers",name,"data"): {
                "bind": "/var/opt/mssql/data",
                "mode": "rw"
            },
            path.join(USER_PATH, "docker","sqlservers",name,"log"): {
                "bind": "/var/opt/mssql/log",
                "mode": "rw"
            },
            path.join(USER_PATH, "docker","sqlservers",name,"secrets"): {
                "bind": "/var/opt/mssql/secrets",
                "mode": "rw"
            }
        }
    if not name or not port:
        return jsonify({"error": "Nome e porta são obrigatórios!"}), 400

    try:
        container = client.containers.run(
            "mcr.microsoft.com/mssql/server:2022-latest",
            name=name,
            environment={
                "ACCEPT_EULA": "Y",
                "SA_PASSWORD": "free_123",
                "MSSQL_PID": "Evaluation",
                "MSSQL_TLS_ENABLED": "FALSE"
            },
            ports={"1433/tcp": port},
            detach=True,
            volumes=volumes
        )
        return jsonify({"message": f"Container {container.name} criado com sucesso!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 📌 3️⃣ Remover um container existente
@app.route('/delete/<container_id>', methods=['DELETE'])
def delete_container(container_id):
    try:
        container = client.containers.get(container_id)
        container.stop()
        container.remove()
        return jsonify({"message": f"Container {container.name} removido com sucesso!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 📌 4️⃣ Rota para renderizar o HTML
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
