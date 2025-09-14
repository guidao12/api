
import os
import stripe
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Configura a chave secreta do Stripe a partir das variáveis de ambiente
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

def criar_sessao_checkout(data: dict):
    """
    Cria uma sessão de checkout do Stripe.
    Espera um dicionário com 'cartItems', 'deliveryFee', 'success_url', 'cancel_url'.
    """
    if not stripe.api_key:
        raise Exception("❌ Configure o arquivo .env com STRIPE_SECRET_KEY=sk_...")

    cart_items = data.get('cartItems')
    delivery_fee = data.get('deliveryFee', 0)
    success_url = data.get('success_url')
    cancel_url = data.get('cancel_url')

    if not all([cart_items, success_url, cancel_url]):
        raise ValueError("Dados incompletos. 'cartItems', 'success_url', e 'cancel_url' são obrigatórios.")

    # Formata os itens para o padrão do Stripe
    line_items = []
    for item in cart_items:
        line_items.append({
            'price_data': {
                'currency': 'brl',
                'product_data': {
                    'name': item.get('name'),
                    'description': item.get('details') or f"Quantidade: {item.get('quantity', 1)}",
                    'images': [item.get('image')] if item.get('image') else [],
                },
                'unit_amount': int(float(item.get('price', 0)) * 100), # Valor em centavos
            },
            'quantity': item.get('quantity', 1),
        })
    
    # Adiciona a taxa de entrega se for maior que zero
    if delivery_fee > 0:
        line_items.append({
            'price_data': {
                'currency': 'brl',
                'product_data': {
                    'name': 'Taxa de Entrega',
                },
                'unit_amount': int(float(delivery_fee) * 100),
            },
            'quantity': 1,
        })

    # Cria a sessão de checkout no Stripe
    print("🔎 Criando sessão de checkout no Stripe...")
    checkout_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=line_items,
        mode='payment',
        success_url=success_url,
        cancel_url=cancel_url,
    )
    print("✅ Sessão do Stripe criada com sucesso!")
    
    return checkout_session
