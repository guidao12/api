import os
import base64
from io import BytesIO
from decimal import Decimal, InvalidOperation
from dotenv import load_dotenv
from pushinpay import PushinPay
import qrcode

def reais_para_centavos(txt_valor: str) -> int:
    limpo = (
        txt_valor.strip()
        .replace("R$", "")
        .replace(" ", "")
        .replace(",", ".")
    )
    try:
        valor = Decimal(limpo)
    except InvalidOperation:
        raise ValueError("Valor inválido. Ex.: 25.90 ou 25,90")
    if valor <= 0:
        raise ValueError("O valor deve ser maior que zero.")
    return int((valor.quantize(Decimal("0.01")) * 100))

def gerar_qrcode_base64(payload: str) -> str:
    """Gera QRCode em base64 ao invés de salvar em arquivo"""
    img = qrcode.make(payload)
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")

def main(entrada):
    api_key = os.getenv("PUSHINPAY_API_KEY")

    if not api_key:
        raise Exception("❌ Configure o arquivo .env com PUSHINPAY_API_KEY=SEU_TOKEN")

    valor_centavos = int(float(entrada) * 100)
    print(f"🔎 Enviando valor: {valor_centavos} centavos para PushinPay")

    push = PushinPay(api_key)    

    # cria a cobrança PIX
    qr = push.pix.create_qrcode(value=valor_centavos)
    print(f"✅ Resposta PushinPay: {qr}")
    copia_e_cola = getattr(qr, "qr_code", str(qr)).strip()

    # gera o QR Code em base64
    qr_base64 = gerar_qrcode_base64(copia_e_cola)

    # retorna como dicionário (ideal para a API Flask converter em JSON)
    return {
        "valor": entrada,
        "pixCopyPaste": copia_e_cola,
        "qrCodeBase64": qr_base64
    }

if __name__ == "__main__":
    print(main("29.90"))

