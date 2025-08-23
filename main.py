from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import gerar_pix
import traceback
import os

app = Flask(__name__)

url = os.getenv("DOMAIN")
#CORS(app, origins=[url])
CORS(app)


# Rate limiting (100 requisições/hora por IP)
limiter = Limiter(get_remote_address, app=app, default_limits=["100 per hour"])


@app.route("/gerar-pix", methods=["POST"])
@limiter.limit("20 per minute")  # máximo 20 requisições por minuto
def gerar_pix_endpoint():
    data = request.get_json()
    if not data or "valor" not in data:
        return jsonify({"erro": "Informe o valor no JSON. Ex.: {\"valor\": \"25.90\"}"}), 400
    
    try:
        # usa a função de validação do gerar_pix para consistência
        _ = gerar_pix.reais_para_centavos(data["valor"])
        resultado = gerar_pix.main(data["valor"])
        return jsonify(resultado)
    except Exception as e:
        traceback.print_exc()  # loga internamente
        return jsonify({"erro": "Erro interno ao gerar PIX"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
