from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from .models import CarModel
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
from .restapis import get_dealers_from_cf, get_dealer_reviews_from_cf, post_request, get_request
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
def about(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/about.html', context)
# ...


# Create a `contact` view to return a static contact page
def contact(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/contact.html', context)

def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    elif request.method == 'POST':
        # Check if user exists
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.error("New user")
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect("djangoapp:index")
        else:
            context['message'] = "User already exists."
            return render(request, 'djangoapp/registration.html', context)


def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('djangoapp:index')
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'djangoapp/login.html', context)
    else:
        return render(request, 'djangoapp/login.html', context)


def logout_request(request):
    logout(request)
    return redirect('djangoapp:index')

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request, state_params=''):
    context = {}
    if request.method == "GET" and request.method == "GET":
        url = "https://7373a815.eu-gb.apigw.appdomain.cloud/api/dealership"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url, state_params=state_params)
        # Concat all dealer's short name
        # dealer_names = ', '.join([dealer.short_name for dealer in dealerships])
        # return HttpResponse(dealer_names)
        context['dealerships'] = dealerships
        return render(request, 'djangoapp/index.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
# def get_dealer_details(request, dealer_id):
# ...
def get_dealer_details(request, dealer_id):
    context = {}
    if request.method == "GET" and request.method == "GET":
        dealer_url = url = "https://7373a815.eu-gb.apigw.appdomain.cloud/api/dealership"
        dealer = get_request(dealer_url, dealer_id=dealer_id)
        url = "https://7373a815.eu-gb.apigw.appdomain.cloud/api/review"
        # Get reviews from the URL
        reviews = get_dealer_reviews_from_cf(url, dealer_id=dealer_id)
        # return HttpResponse(reviews)
        context['dealer'] = dealer['dealer']
        context['reviews'] = reviews
        return render(request, 'djangoapp/dealer_details.html', context)

# Create a `add_review` view to submit a review
def add_review(request, dealer_id):
    context = {}
    user = request.user
    if request.method == 'GET':
        dealer_url = url = "https://7373a815.eu-gb.apigw.appdomain.cloud/api/dealership"
        dealer = get_request(dealer_url, dealer_id=dealer_id)
        cars = CarModel.objects.all()
        context['cars'] = cars
        context['dealer'] = dealer['dealer']
        return render(request, 'djangoapp/add_review.html', context)
    if user.is_authenticated:
        if request.method == "POST":
            review = dict()
            car = get_object_or_404(CarModel, pk=request.POST['car'])
            is_purchased = False
            if request.POST['purchase']:
                is_purchased = True
            else:
                is_purchased = False

            dealer_url = url = "https://7373a815.eu-gb.apigw.appdomain.cloud/api/dealership"
            dealer = get_request(dealer_url, dealer_id=dealer_id)
            print(dealer['dealer'])
            review["time"] = datetime.utcnow().isoformat()
            review["dealership"] = dealer_id
            review["review"] = request.POST['review']
            review["car_make"] = car.make.name
            review["car_model"] = car.name
            review["car_year"] = car.year.strftime("%Y")
            review["name"] = dealer['dealer']['full_name']
            review["purchase"] = is_purchased
            review["purchase_date"] = request.POST['purchasedate']
            payload = {}
            payload['review'] = review
            url = "https://7373a815.eu-gb.apigw.appdomain.cloud/api/review"
            post_request(url=url, json_payload=payload, kwargs={})
            return redirect("djangoapp:dealer_details", dealer_id=dealer_id)
        else:
            context['error'] = 'Invalid request'
            return render(request, 'djangoapp/add_review.html', context)
    else:
        context['error'] = 'Unauthorized'
        return render(request, 'djangoapp/add_review.html', context)


