# Execute an approved PayPal payment
# Use this call to execute (complete) a PayPal payment that has been approved by the payer.
# You can optionally update transaction information by passing in one or more transactions.
# API used: /v1/payments/payment
from paypalrestsdk import Payment
import logging
import paypalrestsdk
paypalrestsdk.configure({
  "mode": "sandbox", # sandbox or live
  "client_id": "AQDGYqEnyUHOPUoN-XQB3KdhOVzbyiZygxADi43WrhddXhukThRuWZbnROnLli7FU2EbjwnXGjjwXIpA",
  "client_secret": "EPdMfqLZkZn6J-OJO2aaGxsHzb1BMNEuax-MJYavtwZbcWdPwbQcpxzN1RjleDrHXN23ZN_kGx63HccK" })

logging.basicConfig(level=logging.INFO)

# ID of the payment. This ID is provided when creating payment.
payment = Payment.find("PAY-62970685CY5925627K73NBCQ")

# PayerID is required to approve the payment.
if payment.execute({"payer_id": "BLT5BMJCXZLAW"}):  # return True or False
    print("Payment[%s] execute successfully" % (payment.id))
else:
    print(payment.error)