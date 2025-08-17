from flask import Flask, request, jsonify
from flask_cors import CORS
import gerar_pix

app = Flask(__name__)
CORS(app)

@app.route("/gerar-pix", methods=["POST"])
def gerar_pix_endpoint():
    data = request.get_json()
    if not data or "valor" not in data:
        return jsonify({"erro": "Informe o valor no JSON. Ex.: {\"valor\": \"25.90\"}"}), 400
    try:
        resultado = gerar_pix.main(data["valor"])
        return jsonify(resultado)
    except Exception as e:
        import traceback
        print("=== ERRO NO ENDPOINT ===")
        traceback.print_exc()  # mostra erro completo nos logs do Render
        return jsonify({"erro": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)