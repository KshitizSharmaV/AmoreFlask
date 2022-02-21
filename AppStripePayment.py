import flask
from flask import Blueprint, current_app,  Flask, jsonify, request
from firebase_admin import auth, exceptions
import traceback
import datetime
import stripe

from ProjectConf.AuthenticationDecorators import validateCookie

@current_app.route('/paymentsheet', methods=['POST'])
@validateCookie
def payment_sheet():
    # Set your secret key. Remember to switch to your live secret key in production.
    # See your keys here: https://dashboard.stripe.com/apikeys
    stripe.api_key = 'sk_test_s5jKY8Oahi9QE8RUVYfn7dUR'
    # Use an existing Customer ID if this is a returning customer
    customer = stripe.Customer.create()
    ephemeralKey = stripe.EphemeralKey.create(
        customer=customer['id'],
        stripe_version='2016-02-03',
    )
    paymentIntent = stripe.PaymentIntent.create(
        amount=1099,
        currency='eur',
        customer=customer['id'],
        automatic_payment_methods={
        'enabled': True,
        },
    )
    return jsonify(paymentIntent=paymentIntent.client_secret,
                    ephemeralKey=ephemeralKey.secret,
                    customer=customer.id,
                    publishableKey='pk_test_VZaIhkYtVBuG5JfPybmKmyiQ')



@current_app.route('/fetchpricing', methods=['POST'])
def fetch_pricing():
    pricingData = {
        "superLikesPricing" : [
            {
                "id":"SL1",
                "itemQuantity": 5,
                "description":"Super Likes",
                "pricePerQty":1.5,
                "currency":"USD"
            },
            {
                "id":"SL2",
                "itemQuantity": 15,
                "description":"Super Likes",
                "pricePerQty":1,
                "currency":"USD"
            },
            {
                "id":"SL3",
                "itemQuantity":30,
                "description":"Super Likes",
                "pricePerQty":0.70,
                "currency":"USD"
            }
        ],
        "boostPricing": [
            {
                "id":"BP1",
                "itemQuantity": 5,
                "description":"Boost",
                "pricePerQty": 3,
                "currency":"USD"
            },
            {
                "id":"BP2",
                "itemQuantity": 10,
                "description":"Boost",
                "pricePerQty":2.5,
                "currency":"USD"
            },
            {
                "id":"BP3",
                "itemQuantity":15,
                "description":"Boost",
                "pricePerQty":2,
                "currency":"USD"
            }
        ],
        "messagesPricing": [
            {
                "id":"MP1",
                "itemQuantity": 5,
                "description":"Messages",
                "pricePerQty": 3,
                "currency":"USD"
            },
            {
                "id":"MP2",
                "itemQuantity": 10,
                "description":"Messages",
                "pricePerQty":2.5,
                "currency":"USD"
            },
            {
                "id":"MP3",
                "itemQuantity":15,
                "description":"Messages",
                "pricePerQty":2,
                "currency":"USD"
            }
        ],
        "amoreGoldPricing": [
            {
                "id":"AG1",
                "itemQuantity": 1,
                "description":"Month",
                "pricePerQty": 12,
                "currency":"USD"
            },
            {
                "id":"AG2",
                "itemQuantity": 3,
                "description":"Months",
                "pricePerQty":10,
                "currency":"USD"
            },
            {
                "id":"AG3",
                "itemQuantity":6,
                "description":"Months",
                "pricePerQty":8,
                "currency":"USD"
            }
        ],
        "amorePlatinumPricing": [
            {
                "id":"AP1",
                "itemQuantity": 1,
                "description":"Month",
                "pricePerQty": 20,
                "currency":"USD"
            },
            {
                "id":"AP2",
                "itemQuantity": 3,
                "description":"Months",
                "pricePerQty":15,
                "currency":"USD"
            },
            {
                "id":"AP3",
                "itemQuantity":6,
                "description":"Months",
                "pricePerQty":12,
                "currency":"USD"
            }
        ]
    }
    current_app.logger.info("Fetching pricing data for subscription and items")
    return jsonify(pricingData)
