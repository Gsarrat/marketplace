# SDK do Mercado Pago
import mercadopago

# Adicione as credenciais
sdk = mercadopago.SDK("PROD_ACCESS_TOKEN")

def create_preference():
    # Cria um item na preferência
    preference_data = {
        "items": [
            {
                "title": "My Item",  # Substitua pelo título do produto real
                "quantity": 1,  # Substitua pela quantidade real
                "unit_price": 75.76  # Substitua pelo preço real
            }
        ],
        # URLs para redirecionamento após pagamento
        "back_urls": {
            "success": "https://seu-dominio.com/success",
            "failure": "https://seu-dominio.com/failure",
            "pending": "https://seu-dominio.com/pending"
        },
        "auto_return": "approved"  # Retorna automaticamente em caso de pagamento aprovado
    }

    # Cria a preferência no Mercado Pago
    preference_response = sdk.preference().create(preference_data)
    preference = preference_response["response"]
    
    return preference
