import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render

from superadmin.models import Customer,Vehicle,Driver,RideDetails
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView,ListView
from django.db.models import F

# Create your views here.
# @login_required(login_url='login')

def driverindex(request):
    cust_count = Customer.objects.count()
    driver_count = Driver.objects.count()
    booking_count = RideDetails.objects.count()
    vehicle_count = Vehicle.objects.count()

    context = {
        'cust_count': cust_count,
        'driver_count': driver_count,
        'booking_count': booking_count,
        'vehicle_count': vehicle_count,
    }
    return render(request,'driver/index.html',context)

# class DriverrideView(TemplateView):
#     template_name = 'driver/driver_ridelist.html'

# def driver_dashboard(request):
#     driver_id = request.user.driver.id  # Assuming driver ID is accessible via user object
#     assigned_bookings = RideDetails.objects.filter(driver_id=driver_id, ride_status='assignbookings')

#     context = {
#         'assigned_bookings': assigned_bookings
#     }
#     return render(request, 'driverapp/dashboard.html', context)


# def driver_ride_list_view(request, driver_id):
#     # Get the driver using company_format
#     driver = Driver.objects.get(company_format=driver_id)
#     # Filter rides assigned to this driver
#     rides = RideDetails.objects.filter(driver=driver, ride_status='assignbookings')
#     context = {
#         'object_list': rides
#     }
#     return render(request, 'driver/ride_list.html', context)

# def start_ride(request):
#     if request.method == 'POST':
#         data = json.loads(request.body)
#         ride_id = data.get('ride_id')

#         try:
#             ride = RideDetails.objects.get(ride_id=ride_id)
#             ride.ride_status = 'ongoingbookings'
#             ride.save()
#             return JsonResponse({'status': 'success'})
#         except RideDetails.DoesNotExist:
#             return JsonResponse({'status': 'error', 'message': 'Ride not found.'}, status=404)
#         except Exception as e:
#             return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

#     return JsonResponse({'status': 'failed'}, status=400)

# def stop_ride(request):
#     if request.method == 'POST':
#         data = json.loads(request.body)
#         ride_id = data.get('ride_id')

#         try:
#             ride = RideDetails.objects.get(ride_id=ride_id)
#             ride.ride_status = 'completedbookings'
#             ride.save()
#             return JsonResponse({'status': 'success'})
#         except RideDetails.DoesNotExist:
#             return JsonResponse({'status': 'error', 'message': 'Ride not found.'}, status=404)
#         except Exception as e:
#             return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

#     return JsonResponse({'status': 'failed'}, status=400)  

def assigned_rides_view(request):
    statuses = ['assignbookings', 'ongoingbookings','completedbookings']
    assigned_rides = RideDetails.objects.filter(ride_status__in=statuses)
    context = {
        'assigned_rides': assigned_rides
    }
    return render(request, 'driver/driverassigned_rides.html', context)


# class assigned_rides_view(ListView):
#     model = RideDetails
#     template_name = "driver/driverassigned_rides.html"

#     def get_queryset(self):
#         # Get only rides that are assigned
#         return RideDetails.objects.filter(ride_status='assignbookings').select_related('driver') 

def start_ride(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        ride_id = data.get('ride_id')

        try:
            ride = RideDetails.objects.get(ride_id=ride_id)
            driver = ride.driver
            driver.driver_status = 'occupied'
            driver.save()
            ride.ride_status = 'ongoingbookings'
            ride.save()
            return JsonResponse({'status': 'success'})
        except RideDetails.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Ride not found.'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

def stop_ride(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        ride_id = data.get('ride_id')

        try:
            ride = RideDetails.objects.get(ride_id=ride_id)
            driver = ride.driver
            driver.number_of_rides += 1
            driver.driver_status = 'free'
            driver.save()
            # driver.save(update_fields=['number_of_rides', 'driver_status'])
            ride.ride_status = 'completedbookings'
            ride.save()
            return JsonResponse({'status': 'success'})
        except RideDetails.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Ride not found.'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)