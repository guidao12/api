
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import gerar_pix
import gerar_cartao  # Importa o novo módulo de cartão
import traceback
import os

app = Flask(__name__)

# Configuração de CORS e Domínio
url = os.getenv("DOMAIN")
CORS(app, origins=[url])

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

@app.route("/gerar-pagamento-cartao", methods=["POST"])
@limiter.limit("20 per minute")
def gerar_pagamento_cartao_endpoint():
    data = request.get_json()
    if not data:
        return jsonify({"erro": "Corpo da requisição não pode ser vazio"}), 400

    try:
        # Chama a função do módulo gerar_cartao para criar a sessão
        checkout_session = gerar_cartao.criar_sessao_checkout(data)
        
        # Retorna a URL de checkout para o frontend
        return jsonify({'stripeCheckoutUrl': checkout_session.url})

    except ValueError as ve: # Captura erros de validação
        return jsonify({"erro": str(ve)}), 400
    except Exception as e:
        traceback.print_exc()
        return jsonify({"erro": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
