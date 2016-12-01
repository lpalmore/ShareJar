# Create Payment Using PayPal Sample
# This sample code demonstrates how you can process a
# PayPal Account based Payment.
# API used: /v1/payments/payment
from paypalrestsdk import Payment
from django.core.exceptions import ObjectDoesNotExist
from models import Balances, Member, Charity, Team
from decimal import Decimal
import logging
import paypalrestsdk
paypalrestsdk.configure({
  "mode": "sandbox", # sandbox or live
  "client_id": "AQDGYqEnyUHOPUoN-XQB3KdhOVzbyiZygxADi43WrhddXhukThRuWZbnROnLli7FU2EbjwnXGjjwXIpA",
  "client_secret": "EPdMfqLZkZn6J-OJO2aaGxsHzb1BMNEuax-MJYavtwZbcWdPwbQcpxzN1RjleDrHXN23ZN_kGx63HccK" })

logging.basicConfig(level=logging.INFO)

def initPayment(userEmail, amount, charityName, charityEmail, teamName=None):
    # Payment
    # A Payment Resource; create one using
    # the above types and intent as 'sale'
    print "initPayment ------------------"
    print charityName
    print teamName
    urlCharityName = charityName.replace(" ", "%20")
    returnURL = ""
    if teamName:
        urlTeamName = teamName.replace(" ", "%20")
        returnURL = 'http://localhost:8000/confirmPayment/%s'%urlTeamName
    else:
        returnURL = 'http://localhost:8000/confirmPayment'
    print returnURL
    print charityName
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
            "return_url": returnURL,#"http://localhost:3000/payment/execute",
            "cancel_url": 'http://localhost:8000/makePayment/%s'%urlCharityName},#"http://localhost:3000/"},

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
                    "name": "This is a test of login_required",
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


def createPayment(userEmail, amount, charityName, charityEmail, teamName=None):
    # Create Payment and return status
    payment = initPayment(userEmail, amount, charityName, charityEmail, teamName)
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

def executePayment(payerID, paymentID, member, teamName):
    payment = Payment.find(paymentID)
    paymentEmail = payment.payer.payer_info.email
    paymentMember = Member.objects.get(paypal_email=paymentEmail)
    if not member == paymentMember:
        print 'Error: logged in user is not user who created payment. Payment will not be executed.'
        return False
    success = payment.execute({"payer_id": payerID})
    if success:
        print "Successfully executed payment"
    else:
        print (payment.error)
    try:
        charity = Charity.objects.all().filter(paypal_email=payment.transactions[0].payee.email)
    except ObjectDoesNotExist:
        pass
    if not teamName == "":
        team = Team.objects.all().filter(name=teamName)
        try:
            b = Balances.objects.get(member=member, charity=charity, team=team)
        except ObjectDoesNotExist:
            pass
    else:
        try:
            b = Balances.objects.get(member=member, charity=charity, team=None)
        except ObjectDoesNotExist:
            pass
    total = Decimal(payment.transactions[0].amount.total)
    b.balance -= total
    if b.balance <= 0:
        b.delete()
    else:
        b.save()
    return success
