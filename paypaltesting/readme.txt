How to execute:
1. Run paypal.py from the command line, it'll print out "Redirect for approval: [url]", copy and paste the url into a browser
2. It'll ask you to log in as sharejardev-facilitator@gmail.com (I think, either that or sharejardev-buyer@gmail.com), the password is sweb4gEhU+=c for both
3. Once you click through all the approval stuff, it'll redirect you to a blank localhost:3000 page & in the url there should be a paymentID and a payerID, copy & paste those into execute.py
4. Run execute.py, should say "Payment[PaymentID] execute successfully"
5. If you log in to either account on sandbox.paypal.com after a bit, it should show the transaction for both buyer and seller