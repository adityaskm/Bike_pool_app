from django.shortcuts import render
from bike_app.models import rideData, user
from bike_app.serializers import rideDataSerializer
from rest_framework import viewsets
from rest_framework.response import Response
from bike_app.forms import findRideform, userLogin, userSignup
from django.http import HttpRequest,HttpResponse
from rest_framework.views import APIView
from bike_app.processing_data import get_location, cal_haversine_distance
from datetime import datetime
from bike_app.response_classes import findRideResponse
from django.core import serializers
from django.contrib.auth.models import User




def home(request):
    return render(request, 'bike_app/index.html')


# def login(request):
#     return render(request, 'bike_app/login.html')


class userLogin(viewsets.ModelViewSet):
    queryset = user.objects.all()
    template_name = 'bike_app/login.html'
    login_form = userLogin()

    def list(self, request, *args, **kwargs):
        login_form = self.login_form
        args = {'form' : login_form}
        return render(request, self.template_name, args)


class userSignup(viewsets.ModelViewSet):
    queryset = user.objects.all()
    template_name = 'bike_app/signup.html'
    signup_form = userSignup()

    def list(self, request, *args, **kwargs):
        signup_form = self.signup_form
        args = {'form': signup_form}
        return render(request, self.template_name, args)


    def create(self, request, *args, **kwargs):
        # try:
        django_auth_user = User()
        data = request.POST
        user_email = data['email']
        user_firstname = data['firstname']
        user_lastname = data['lastname']
        user_password = django_auth_user.set_password(data['password'])
        if self.queryset.filter(email = user_email).exists():
            pass
        else:
            new_user = user(first_name = user_firstname, last_name = user_lastname, email = user_email, password = user_password)
            new_user.save()
        # except:
        #     return Response('Form data not valid')



class offerRide(viewsets.ModelViewSet):
    queryset = rideData.objects.all()
    template_name = 'bike_app/offer_ride.html'


    def create(self, request, *args, **kwargs):
        # try:
        data = request.POST
        pickup = data['pickup']
        dropoff = data['dropoff']

        # Should add a validation check here
        pickup_lat_long = get_location(pickup)
        dropoff_lat_long = get_location(dropoff)
        date_time = data['datetimepicker']
        date_time_field = datetime.strftime(datetime.strptime(date_time, '%m/%d/%Y %H:%M %p'),'%Y-%m-%d %H:%M:%S')
        stopover_list = []
        for i in range(0, len(data) - 4):
            stopover_list.append(data['stopover_' + str(i)])
        stopover_lat_long_list = [str(get_location(k)) for k in stopover_list]
        rideData_obj = rideData(user_id = 101, pickup = str(pickup_lat_long), dropoff = str(dropoff_lat_long), stopovers = ''.join(stopover_lat_long_list), depart_time = date_time_field)
        if self.queryset.filter(user_id = 101, pickup = str(pickup), depart_time = date_time_field).exists():
            pass
        else:
            rideData_obj.save()
            return HttpResponse('Success')
        # except:
        #     return HttpResponse('Please check your input data')

    def list(self, request):
        return render(request, self.template_name)





# def findRide(request):
#     form = findRideform()
#     args = {'form' : form}
#     if request.method == 'GET':
#         return render(request, 'bike_app/find_ride.html',args)
#
#     elif request.method == 'POST':
#         pickup = request.POST['pickup']
#         geolocation = get_location(pickup)
#         return HttpResponse('Success')


class findRide(viewsets.ModelViewSet):
    queryset = rideData.objects.all()
    template_name = 'bike_app/find_ride.html'

    def list(self, request, *args, **kwargs):
        form = findRideform
        args = {'form' : form}
        return render(request, self.template_name, args)

    def create(self, request, *args, **kwargs):
        data = request.POST
        pickup_loc = data['pickup']
        dropoff_loc = data['dropoff']
        travel_date = data['date']
        travel_time = data['time']
        travel_date_time = datetime.strftime(datetime.strptime(travel_date + ' ' + travel_time, '%Y-%m-%d %H:%M'),'%Y-%m-%d %H:%M:%S')

        # Should include a validation check here
        pickup_lat_long = get_location(pickup_loc)
        dropoff_lat_long = get_location(dropoff_loc)
        rides = self.queryset.filter(depart_time__date = travel_date)
        results = []
        for each_ride in rides:
            dist = cal_haversine_distance(str(pickup_lat_long), each_ride.pickup)
            # results[each_ride.user_id] = {}
            # results[each_ride.user_id]['distance'] = dist
            # results[each_ride.user_id]['depart_time'] = datetime.strftime(each_ride.depart_time.date(), '%Y-%m-%d')
            # results[each_ride.user_id]['fare'] = round(50 + 12 * dist)
            respone_obj = findRideResponse(user_id = each_ride.user_id, distance = dist, depart_time = datetime.strftime(each_ride.depart_time.date(), '%Y-%m-%d'), fare = round(50 + 12 * dist))
            results.append(respone_obj)
        results = sorted(results, key = lambda x : x.distance, reverse = True)
        results = serializers.serialize('json', results)
        return HttpResponse(results)













