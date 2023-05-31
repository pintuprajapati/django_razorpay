# Project
RazorPay Payment Gateway integration in Django with Callback functionality

# How to run this project and test it on your system
By following below steps, you'll be able to directly run this project and check/test the razorpay payment gateway.

I have also provided some TEST CARD details and official links for testing

## Installation (venv and dependencies)
- Create an virtual environment (venv) and activate it
    ```
    python3 -m venv env_razorpay
    source env_razorpay/bin/activate
    ```
- Clone the project

- Install the dependencies using requirements.txt file
    ```
    pip3 install -r requirements.txt
    ```
## Run the django server
- First do the makemigration operation
    ```
    python3 manage.py makemigrations
    ```
- Do the migrate operation
    ```
    python3 manage.py migrate
    ```
- Create superuser
    ```
    python3 manage.py createsuperuser
    ```

# Razorpay Login and API KEY
- You will have to create an account on razorpay site (https://razorpay.com/)
- Now Generate 2 API Keys from here (https://dashboard.razorpay.com/#/app/keys)
    1. API KEY ID
    2. API SECRET ID

- Keep it saved somewhere (for the later use)
- Now add both of these keys into your `settings.py` file at the bottom (replace the key in the project)
    ```
    # RazorPay API Key and API secret key
    # You can define these keys into ".env" directory too
    
    RZP_API_KEY="razorpay_api_key"
    RZP_API_SECRET="razorpay_api_secret_key"
    ```
- If you don't add the 2 API Keys then you might get error something like this
    ```BadRequestError at /payment/
    Authentication failed
    Request Method:	POST
    Request URL:	http://127.0.0.1:8000/payment/
    Django Version:	4.2.1
    Exception Type:	BadRequestError
    Exception Value:Authentication failed
    ```

- Run the django server and go to this url: http://127.0.0.1:8000/
    ```
    python3 manage.py runserver
    ```

Hurrah!!! You have successfully installed and setup everything.

Now you can test the integetration whether it's according to your business logic or not? You can modify according to your needs.

# Some offical razorpay documentations

- For code integration: https://razorpay.com/docs/payments/server-integration/python/payment-gateway/build-integration/
- Test Cards and Test UPI ID: https://razorpay.com/docs/payments/payments/test-card-upi-details/
    - If it asks for OTP then enter `1234` it will work
- Check the payment status here: https://dashboard.razorpay.com/app/payments
- Error Structure/Response from razorpay side: https://razorpay.com/docs/api/errors/


# Razorpay Python Client (Just for information)
Python bindings for interacting with the Razorpay API

This is primarily meant for merchants who wish to perform interactions with the Razorpay API programatically.

## Installation

```
pip install razorpay
```

## Usage

You need to setup your key and secret using the following:
You can find your API keys at <https://dashboard.razorpay.com/#/app/keys>.

```py
import razorpay
client = razorpay.Client(auth=("<YOUR_API_KEY>", "<YOUR_API_SECRET>"))
```

## App Details

After setting up client, you can set your app details before making any request
to Razorpay using the following:

```py
client.set_app_details({"title" : "<YOUR_APP_TITLE>", "version" : "<YOUR_APP_VERSION>"})
```

For example, you can set the title to `Django` and version to `4.2.1`. Please ensure
that both app title and version are strings.
