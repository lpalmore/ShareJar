# Create Payment Using PayPal Sample
# This sample code demonstrates how you can process a
# PayPal Account based Payment.
# API used: /v1/payments/payment
from paypalrestsdk import Payment
from django.core.exceptions import ObjectDoesNotExist
from models import Balances, Member, Charity
from decimal import Decimal
import logging
import paypalrestsdk
paypalrestsdk.configure({
  "mode": "sandbox", # sandbox or live
  "client_id": "AQDGYqEnyUHOPUoN-XQB3KdhOVzbyiZygxADi43WrhddXhukThRuWZbnROnLli7FU2EbjwnXGjjwXIpA",
  "client_secret": "EPdMfqLZkZn6J-OJO2aaGxsHzb1BMNEuax-MJYavtwZbcWdPwbQcpxzN1RjleDrHXN23ZN_kGx63HccK" })

logging.basicConfig(level=logging.INFO)

def initPayment(userEmail, amount, charityName, charityEmail):
    # Payment
    # A Payment Resource; create one using
    # the above types and intent as 'sale'
    payment = Payment({
        "intent": "sale",
        # Payer
        # A resource representing a Payer that funds a payment
        # Payment Method as 'paypal'
        "payer": {
            "payment_method": "paypal",
            "payer_info": {
                "email": userEmail#"sharejardev-facilitator@gmail.com"
        }   },

        # Redirect URLs: TODO: These can't stay localhost forever
        "redirect_urls": {
            "return_url": 'https://sharejardev.herokuapp.com/confirmPayment',#"http://localhost:3000/payment/execute",
            "cancel_url": 'https://sharejardev.herokuapp.com/makePayment/%s'%(charityName)},#"http://localhost:3000/"},

        # Transaction
        # A transaction defines the contract of a
        # payment - what is the payment for and who
        # is fulfilling it.
        "transactions": [{
            "payee": {
                "email": charityEmail
            },
            # ItemList
            "item_list": {
                "items": [{
                    "name": "11/11 Item",
                    "sku": "item",
                    "price": amount,
                    "currency": "USD",
                    "quantity": 1}]},

            # Amount
            # Let's you specify a payment amount.
            "amount": {
                "total": amount,
                "currency": "USD"},
            "description": "This is the payment transaction description."}]})
    return payment


def createPayment(userEmail, amount, charityName, charityEmail):
    # Create Payment and return status
    payment = initPayment(userEmail, amount, charityName, charityEmail)
    if payment.create():
        print("Payment[%s] created successfully" % (payment.id))
        # Redirect the user to given approval url
        for link in payment.links:
            if link.method == "REDIRECT":
                # Convert to str to avoid google appengine unicode issue
                # https://github.com/paypal/rest-api-sdk-python/pull/58
                redirect_url = str(link.href)
                #print("Redirect for approval: %s" % (redirect_url))
                return redirect_url
    else:
        print("Error while creating payment:")
        print(payment.error)
        return None

def executePayment(payerID, paymentID, member):
    payment = Payment.find(paymentID);
    success = payment.execute({"payer_id": payerID})
    if success:
        print "Successfully executed payment"
    else:
        print (payment.error)
    try:
        charity = Charity.objects.all().filter(paypal_email=payment.transactions[0].payee.email)
    except ObjectDoesNotExist:
        pass
    try:
        balances = Balances.objects.all().filter(member=member, charity=charity)
    except ObjectDoesNotExist:
        pass
    b = balances.first()
    total = Decimal(payment.transactions[0].amount.total)
    b.balance -= total
    b.save()
    return success
