from django.http import HttpResponse
from django.shortcuts import render
import razorpay
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
            "receipt": "order_rcptid_11",
            "payment_capture": "1"
        }

        # creating razorpay orders to capture payments automatically.
        razorpay_order = client.order.create(data=data)

        # Create Payment Model object
        payment_obj = Payment.objects.create(
            name=name, amount=amount, razor_pay_order_id=razorpay_order["id"]
        )
        payment_obj.save()

        # Handling the successful and failed payment is done with the help of the "callback URL"
        # After payment, users will be redirected to this "callback URL" on successful payment and failed payment.
        context = {
            "razorpay_order": razorpay_order,
            "callback_url": "http://" + "127.0.0.1:8000" + "/callback/",
            "razorpay_key": settings.RZP_API_KEY,
            "payment_obj": payment_obj
        }
        return render(request, 'payment.html', context)
    return render(request, "payment.html")

# callback view to handle successful and failed payments.
# As POST request will be made by Razorpay and it won’t have the csrf token, so we need to csrf_exempt this url.
@csrf_exempt
def callback(request):
    def verify_signature(response_data):                
        client = razorpay.Client(auth=(settings.RZP_API_KEY, settings.RZP_API_SECRET))        
        return client.utility.verify_payment_signature(response_data)
    
    if "razorpay_signature" in request.POST:
        try:      
            payment_id = request.POST.get("razorpay_payment_id", "")
            provider_order_id = request.POST.get("razorpay_order_id", "")
            signature_id = request.POST.get("razorpay_signature", "")

            # saving razorpay ids to the database
            payment_obj = Payment.objects.get(razor_pay_order_id=provider_order_id)
            payment_obj.razor_pay_payment_id = payment_id
            payment_obj.razor_pay_payment_signature = signature_id
            payment_obj.save()

            if verify_signature(request.POST):
                payment_obj.status = PaymentStatus.SUCCESS.value
                payment_obj.save()
                return render(request, "callback.html", context={"payment_obj": payment_obj})
            else:
                payment_obj.status = PaymentStatus.FAILURE.value
                payment_obj.save()
                return render(request, "callback.html", context={"payment_obj": payment_obj})
        except Exception as e:
            print("➡ e :", e)

    else: # if razorpay_signature not in the POST
        try:
            # error_metadata = json.loads(request.POST.get("error[metadata]"))
            # payment_id = error_metadata.get("payment_id")
            # provider_order_id = error_metadata.get("order_id")
            # error_description = error_metadata.get("description")
            
            payment_id = json.loads(request.POST.get("error[metadata]")).get("payment_id")
            provider_order_id = json.loads(request.POST.get("error[metadata]")).get("order_id")

            payment_obj = Payment.objects.get(razor_pay_order_id=provider_order_id)
            payment_obj.payment_id = payment_id
            payment_obj.status = PaymentStatus.FAILURE.value

            payment_obj.save()
            return render(request, "callback.html", context={"payment_obj": payment_obj})
        except Exception as e:
            print("➡ e :", e)

    # If some other error occurs then below reponse will be shown
    # Ex: In case of wrong OTP
    return HttpResponse("Invalid request")

    