from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
import razorpay
import hashlib
import hmac
from django.conf import settings
from .models import Payment, PaymentStatus
from django.views.decorators.csrf import csrf_exempt
import json

def home(request):
    return render(request, 'index.html') # template to take input from the user.

# Order_payment schema
def order_payment(request):
    if request.method == "POST":
        name = request.POST.get("name")
        amount = request.POST.get('amount')

        # Create a client for razorpay
        client = razorpay.Client(auth=(settings.RZP_API_KEY, settings.RZP_API_SECRET))

        # setting up 'app details' before making any request to Razorpay
        # client.set_app_details({"title" : "<YOUR_APP_TITLE>", "version" : "<YOUR_APP_VERSION>"})
        client.set_app_details({"title" : "Django", "version" : "4.2.1"})

        # Amount in Razorpay works in subunits of currency i.e Rs 700 would become 70000 paise. That’s why we multiplied the amount by 100.
        data = {
            "amount": int(amount) * 100,
            "currency": "INR",
            "payment_capture": "1"
        }

        # creating razorpay orders to capture payments automatically.
        razorpay_order = client.order.create(data=data)

        # Create Payment Model object
        payment_obj = Payment.objects.create(
            name=name, amount=amount, razor_pay_order_id=razorpay_order["id"]
        )
        payment_obj.save()

        # Handling the successful and failed payment is done with the help of the "webhook"
        context = {
            "razorpay_order": razorpay_order,
            "razorpay_key": settings.RZP_API_KEY,
            "payment_obj": payment_obj
        }
        return render(request, 'payment.html', context)
    return render(request, "payment.html")

# webhook view to handle successful and failed payments.
# As POST request will be made by Razorpay and it won’t have the csrf token, so we need to csrf_exempt this url.
@csrf_exempt
def handle_payment_webhook(request):
    try:
        if request.method == "POST":
            request_data = json.loads(request.body.decode('utf-8'))

            # Retrieve the webhook secret key from your Razorpay dashboard
            webhook_secret = "secret_webhook_1234"

            """
            Verify the webhook signature

            retrieve the value of the 'X-Razorpay-Signature' header from the incoming request
            generates a new signature using the HMAC (Hash-based Message Authentication Code) algorithm with SHA-256 hashing
            If the two signatures match, it indicates that the webhook request was not tampered with and can be considered valid
            """

            signature = request.headers.get('X-Razorpay-Signature')
            generated_signature = hmac.new(webhook_secret.encode(), request.body, hashlib.sha256).hexdigest()
        
            # compare both the signatures and check the 'event'
            if signature == generated_signature and request_data['event'] == "payment.captured":

                payment = request_data['payload']['payment']
                # payment_status = payment['entity']['status']
                payment_id = payment['entity']['id']
                order_id = payment['entity']['order_id']      

                # saving razorpay ids to the database
                payment_obj = Payment.objects.get(razor_pay_order_id=order_id)
                payment_obj.razor_pay_payment_id = payment_id
                payment_obj.razor_pay_payment_signature = signature # from 'X-Razorpay-Signature' header
                payment_obj.status = PaymentStatus.SUCCESS.value
                payment_obj.save()
                context={"payment_obj": payment_obj}
                # Redirect to the success view
                redirect_url = reverse('success')
                # redirect_url = reverse('success') + f'?order_id={order_id}'
                return redirect(redirect_url)
                # return HttpResponse(status=200)  # Return a success response to Razorpay webhook
            
            else:
                payment_obj = Payment.objects.get(razor_pay_order_id=order_id)
                payment_obj.status = PaymentStatus.FAILURE.value
                payment_obj.save()
                return HttpResponse(status=400)  # Return a failure response to Razorpay webhook

        else: # if webhook request is not POST
            try:
                # error = request_data['payload']['payment']['entity']
                payment_obj = Payment.objects.get(razor_pay_order_id=order_id)
                payment_obj.payment_id = payment_id
                payment_obj.status = PaymentStatus.FAILURE.value
                payment_obj.save()
                return HttpResponse(status=400)  # Return a failure response to Razorpay webhook
                
            except Exception as e:
                print("➡ e :", e)


        # If some other error occurs then below reponse will be shown
        # Ex: In case of wrong OTP
    except Exception as e:
        print("➡ e :", e)
        return HttpResponse(status=400)  # Return a failure response to Razorpay webhook


def success(request):
    # order_id = request.GET.get('order_id')
    # payment_obj = Payment.objects.get(razor_pay_order_id=order_id)
    # context = {"payment_obj": payment_obj}
    # return render(request, 'success.html', context)

    return render(request, 'success.html')