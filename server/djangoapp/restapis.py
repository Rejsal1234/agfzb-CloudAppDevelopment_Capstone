import requests
import json
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, SentimentOptions

def get_request(url, **kwargs):
    print(kwargs)
    print("GET from {} ".format(url))
    try:
        # Call get method of requests library with URL and parameters
        if "api_key" in kwargs:
            # Basic authentication GET
            params = dict()
            params["text"] = kwargs["text"]
            params["version"] = kwargs["version"]
            params["features"] = kwargs["features"]
            params["return_analyzed_text"] = kwargs["return_analyzed_text"]
            response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=params, auth=HTTPBasicAuth('apikey', kwargs["api_key"]))
        else:
            # no authentication GET
            response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs)
        status_code = response.status_code
        print("With status {} ".format(status_code))
        json_data = json.loads(response.text)
        return json_data
    except:
        # If any error occurs
        print("Network exception occurred")



def post_request(url, json_payload, **kwargs):
    print(kwargs)
    print("POST from {} ".format(url))
    try:
        response = requests.post(url, params=kwargs, json=json_payload)
        status_code = response.status_code
        print("With status {} ".format(status_code))
        json_data = json.loads(response.text)
        return json_data
    except:
        # If any error occurs
        print("Network exception occurred")





# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)


def get_dealers_from_cf(url, state_params, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url, state=state_params)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result["dealerships"]
        # For each dealer object
        for dealer_doc in dealers:
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   st=dealer_doc["st"], state=dealer_doc["state"], zip=dealer_doc["zip"])
            results.append(dealer_obj)

    return results


# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
# def get_dealer_by_id_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list
def get_dealer_reviews_from_cf(url, dealer_id, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url, dealer_id=dealer_id)
    if json_result:
        # Get the row list in JSON as dealers
        reviews = json_result["reviews"]
        # For each dealer object
        for dealer_doc in reviews:
            # Create a CarDealer object with values in `doc` object
            dealer_obj = DealerReview(dealership=dealer_doc["dealership"], name=dealer_doc["name"], purchase=dealer_doc["purchase"],
                                   id=dealer_doc["id"], review=dealer_doc["review"], purchase_date=dealer_doc["purchase_date"],
                                   car_make=dealer_doc["car_make"],
                                   car_model=dealer_doc["car_model"], car_year=dealer_doc["car_year"], sentiment=analyze_review_sentiments(dealer_doc["review"]))
            results.append(dealer_obj)

    return results


# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
def analyze_review_sentiments(text):
    url = "https://api.eu-gb.natural-language-understanding.watson.cloud.ibm.com/instances/d327b4ae-971c-4980-8a2f-6401f8b0efbb"
    api_key = "WMh5JH--VX2-6-AwXmKEKu18EU1yGCbXXW9j9IIK2vik"
    authenticator = IAMAuthenticator(api_key) 
    natural_language_understanding = NaturalLanguageUnderstandingV1(version='2021-08-01',authenticator=authenticator) 
    natural_language_understanding.set_service_url(url) 
    response = natural_language_understanding.analyze(text=text+"hello hello hello", features=Features(sentiment=SentimentOptions(targets=[text+"hello hello hello"]))).get_result() 
    label=json.dumps(response, indent=2) 
    label = response['sentiment']['document']['label'] 
    return label



