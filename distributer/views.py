from datetime import date
import json
from django.shortcuts import render
import re
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from rest_framework.views import APIView
from django.views.generic import TemplateView,ListView,View,DetailView
from rest_framework.response import Response
from rest_framework import status
from superadmin.models import Brand,Category,Model, RideDetails, RideDetailsHistory,User,Customer,Driver,Ridetype,Vehicle
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt


# Create your views here.
@login_required(login_url='login')
def index(request):
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
    return render(request,'distributer/index.html',context)


# driver ################################
@method_decorator(login_required(login_url='login'), name='dispatch')
class AddDriverView(TemplateView):
    template_name = "distributer/add_driver.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        last_driver = Driver.objects.all().order_by('-driver_id').first()
        if last_driver:
            last_company_format = int(last_driver.company_format.replace('DRIV', ''))
            next_company_format = f'DRIV{last_company_format + 1:02}'
        else:
            next_company_format = 'DRIV01'
        context['next_company_format'] = next_company_format
        return context

    def post(self, request):
        name = request.POST['name']
        phone_number = request.POST['phone_number']
        email = request.POST['email']
        address = request.POST['address']
        status = request.POST['status']
        company_format = request.POST.get('company_format', '')
        document_verification_type = request.POST['document_verification_type']
        document_link = request.POST['document_link']

        dr = Driver()
        dr.name=name
        dr.phone_number=phone_number
        dr.email=email
        dr.address=address
        dr.status=status
        dr.company_format=company_format
        dr.document_verification_type=document_verification_type
        dr.document_link=document_link
        
        dr.save()
        return JsonResponse({'status': "Success"})

@method_decorator(login_required(login_url='login'), name='dispatch')
class DriverListView(ListView):
    model = Driver
    template_name = "distributer/view_driver.html"

@method_decorator(login_required(login_url='login'), name='dispatch')
class DeleteDriverView(View):
    def get(self, request):
        driver_id = request.GET.get('driver_id', None)
        Driver.objects.get(driver_id=driver_id).delete()
        data = {
            'deleted': True
        }
        return JsonResponse(data)

@method_decorator(login_required(login_url='login'), name='dispatch')
class EditDriverView(TemplateView):
    template_name = 'distributer/edit_driver.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['driver_id'] = self.kwargs['id']
            driverlist = Driver.objects.filter(driver_id=context['driver_id'])
        except:
            driverlist = Driver.objects.filter(driver_id=context['driver_id'])
            
        context['driverlist'] = list(driverlist)
        return context

@method_decorator(login_required(login_url='login'), name='dispatch')
class UpdateDriverView(APIView):  
    def post(self, request):
        driver_id = request.POST['driver_id']
        name = request.POST['name']
        phone_number = request.POST['phone_number']
        email = request.POST['email']
        address = request.POST['address']
        status = request.POST['status']
        company_format = request.POST['company_format']
        document_verification_type = request.POST['document_verification_type']
        document_link = request.POST['document_link']

        driver = Driver.objects.get(driver_id=driver_id)
        driver.name = name
        driver.phone_number = phone_number
        driver.email = email
        driver.address = address
        driver.status = status
        driver.company_format = company_format
        driver.document_verification_type = document_verification_type
        driver.document_link = document_link
        driver.save()

        return JsonResponse({'success': True}, status=200)
    

# ride details ##########################################
def fetch_customer_details(request):
    phone_number = request.GET.get('phone_number', None)
    if phone_number:
        try:
            customer = Customer.objects.get(phone_number=phone_number)
            customer_details = {
                'id': customer.customer_id,  # Ensure the customer ID is included
                'name': customer.customer_name,
                'email': customer.email,
                'address': customer.address
            }
            return JsonResponse({'success': True, 'customer': customer_details})
        except Customer.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Customer not found'})
    return JsonResponse({'success': False, 'message': 'Invalid request'})

class AddRide(TemplateView):
    template_name = "distributer/add_ride.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['customerlist'] = Customer.objects.all()
        context['ridetypelist'] = Ridetype.objects.all()
        context['catlist'] = Category.objects.all()
        context['blist'] = Brand.objects.all()
        context['modellist'] = Model.objects.all()
        
        last_ride = RideDetails.objects.all().order_by('-ride_id').first()
        if last_ride:
            last_company_format = int(last_ride.company_format.replace('RID', ''))
            next_company_format = f'RID{last_company_format + 1:02}'
        else:
            next_company_format = 'RID01'
        context['next_company_format'] = next_company_format
        
        return context
    
    def post(self, request):
        try:
            company_format = request.POST['company_format']
            ride_type_id = request.POST['ridetype']
            source = request.POST['source']
            destination = request.POST['destination']
            pickup_date = request.POST['pickup_date']
            pickup_time = request.POST['pickup_time']
            model_id = request.POST['model']
            total_fare = request.POST['total_fare']
            customer_id = request.POST['customer']
            customer_notes = request.POST['customer_notes']
            ride_status = request.POST['ride_status']
            
            print(f"Received Data: {company_format}, {ride_type_id}, {source}, {destination}, {pickup_date}, {pickup_time}, {model_id}, {total_fare}, {customer_id}, {customer_notes}, {ride_status}")

            # Ensure objects exist in database before saving
            customer = Customer.objects.get(customer_id=customer_id)
            ridetype = Ridetype.objects.get(ridetype_id=ride_type_id)
            model = Model.objects.get(model_id=model_id)

            # Determine ride status based on pickup date
            today = date.today().isoformat()
            ride_status = 'advancebookings' if pickup_date > today else 'currentbookings'
            
            ride_details = RideDetails(
                company_format=company_format,
                customer=customer,
                ridetype=ridetype,
                model=model,
                source=source,
                destination=destination,
                pickup_date=pickup_date,
                pickup_time=pickup_time,
                total_fare=total_fare,
                customer_notes=customer_notes,
                ride_status=ride_status,
                assigned_by=request.user,
                cancelled_by=request.user,
                created_by=request.user,
                updated_by=request.user
            )
            ride_details.save()
            
            return JsonResponse({'status': "Success", 'message': 'Ride details added successfully'})
        except Customer.DoesNotExist:
            print(f"Customer with ID {customer_id} does not exist.")
            return JsonResponse({'status': 'Error', 'message': f'Customer with ID {customer_id} does not exist.'})
        except Exception as e:
            print(f"Error saving ride details: {e}")
            return JsonResponse({'status': 'Error', 'message': str(e)})
                
        
@method_decorator(login_required(login_url='login'), name='dispatch')
class RideList(ListView):
    model = RideDetails
    template_name = "distributer/view_ride.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['drivers'] = Driver.objects.all()
        context['ride_id'] = self.kwargs.get('ride_id', 1)  # Adjust this based on your URL setup
        return context

    def get_queryset(self):
        today = date.today()
        # Update ride status for rides with a past pickup date
        past_rides = RideDetails.objects.filter(pickup_date__lt=today, ride_status='currentbookings')
        past_rides.update(ride_status='pendingbookings')
        
        # Fetch rides with a pickup date of today and status as current bookings
        current_rides = RideDetails.objects.filter(ride_status='currentbookings', pickup_date=today)
        
        return current_rides

#################################### advance bookings ###########################################

@method_decorator(login_required(login_url='login'), name='dispatch')
class AdvanceBookingsList(ListView):
    model = RideDetails
    template_name = "distributer/advance_bookings.html"  # Ensure you create this template

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['drivers'] = Driver.objects.all()
        context['ride_id'] = self.kwargs.get('ride_id', 1)  # Adjust this based on your URL setup
        return context

    def get_queryset(self):
        today = date.today()
        
        # Update ride status for rides where the pickup date is today
        today_rides = RideDetails.objects.filter(pickup_date=today, ride_status='advancebookings')
        today_rides.update(ride_status='currentbookings')
        
        # Fetch rides with a pickup date greater than today and status as advance bookings
        advance_rides = RideDetails.objects.filter(ride_status='advancebookings', pickup_date__gt=today)
        
        return advance_rides
##############################################################################################################   
@method_decorator(login_required(login_url='login'), name='dispatch')
class PendingBookingsList(ListView):
    model = RideDetails
    template_name = "distributer/pending_bookings.html"  # Ensure you create this template

    def get_queryset(self):
        today = date.today()
        return RideDetails.objects.filter(ride_status='pendingbookings', pickup_date__lt=today)
    
# ongoing rides########################################################################################################
class OngoingRideList(ListView):
    model = RideDetails
    template_name = "distributer/ongoing_rides.html"

    def get_queryset(self):
        return RideDetails.objects.filter(Q(ride_status='ongoingbookings') & Q(assigned_by=self.request.user)).select_related('driver') 

    
# completed rides########################################################################################################
class CompletedRideList(ListView):
    model = RideDetails
    template_name = "distributer/completed_rides.html"

    def get_queryset(self):
        return RideDetails.objects.filter(Q(ride_status='completedbookings') & Q(assigned_by=self.request.user)).select_related('driver')
    

# invoice rides########################################################################################################

class InvoiceView(DetailView):
    model = RideDetails
    template_name = 'distributer/invoice.html'
    context_object_name = 'ride'
    
    def get_object(self):
        ride_id = self.kwargs.get("ride_id")
        return get_object_or_404(RideDetails, ride_id=ride_id)    

class AssignDriverView(ListView):
    model = Driver
    template_name = 'distributer/view_ride.html'
    context_object_name = 'drivers'

    def get_queryset(self):
        return Driver.objects.filter(status='active')


@method_decorator(login_required(login_url='login'), name='dispatch')
class DeleteRide(View):
    def get(self, request):
        ride_id = request.GET.get('ride_id', None)
        RideDetails.objects.get(ride_id=ride_id).delete()
        data = {
            'deleted': True
        }
        return JsonResponse(data)

@method_decorator(login_required(login_url='login'), name='dispatch')
class EditRide(TemplateView):
    template_name = 'distributer/edit_ride.html'
  
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customerlist = Customer.objects.all()
        ridetypelist = Ridetype.objects.all()
        modellist = Model.objects.all()
        catlist = Category.objects.all()
        blist = Brand.objects.all()

        try:
            context['ride_id'] = self.kwargs['id']
            ride = RideDetails.objects.filter(ride_id=context['ride_id'])
        except:
            ride = RideDetails.objects.filter(ride_id=context['ride_id'])
            
        context = {
            'customerlist': list(customerlist),
            'ridetypelist': list(ridetypelist),
            'modellist': list(modellist),
            'catlist': list(catlist),
            'blist': list(blist),
            'ride': list(ride)

        }
        return context

@method_decorator(login_required(login_url='login'), name='dispatch')
class UpdateRide(APIView):
    @csrf_exempt
    def post(self, request):
        
            # Retrieve and validate ride_id from request
            ride_id = request.POST.get('ride_id')
            if not ride_id:
                return JsonResponse({'success': False, 'error': 'Missing ride_id'}, status=400)

            try:
                ride_id = int(ride_id)
            except ValueError:
                return JsonResponse({'success': False, 'error': 'Invalid ride_id'}, status=400)
            
            # Retrieve the ride object
            try:
                ride = RideDetails.objects.get(ride_id=ride_id)
            except RideDetails.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Ride not found'}, status=404)
            
            # Update customer if provided
            customer_id = request.POST.get('customer', None)
            if customer_id:
                try:
                    customer_id = int(customer_id)
                    customer = Customer.objects.get(customer_id=customer_id)
                    ride.customer = customer
                except (ValueError, Customer.DoesNotExist):
                    return JsonResponse({'success': False, 'error': 'Invalid customer_id'}, status=400)
            
            # Update the ride with new data
            ride.source = request.POST.get('source', ride.source)
            ride.destination = request.POST.get('destination', ride.destination)
            ride.pickup_date = request.POST.get('pickup_date', ride.pickup_date)
            ride.pickup_time = request.POST.get('pickup_time', ride.pickup_time)
            ride.total_fare = request.POST.get('total_fare', ride.total_fare)
            ride.customer_notes = request.POST.get('customer_notes', ride.customer_notes)
            ride.updated_by = request.user
            ride.save()

            # Create a RideDetailsHistory entry after updating the ride
            RideDetailsHistory.objects.create(
                ride_id=ride.ride_id,
                company_format=ride.company_format,
                ridetype=ride.ridetype,
                source=ride.source,
                destination=ride.destination,
                pickup_date=ride.pickup_date,
                pickup_time=ride.pickup_time,
                model=ride.model,
                driver=ride.driver,
                assigned_by=ride.assigned_by.username if ride.assigned_by else None,
                cancelled_by=ride.cancelled_by.username if ride.cancelled_by else None,
                total_fare=ride.total_fare,
                customer=ride.customer,
                customer_notes=ride.customer_notes,
                ride_status=ride.ride_status,
                booking_datetime=ride.booking_datetime,
                created_on=ride.created_on,
                updated_on=ride.updated_on,
                created_by=ride.created_by.username if ride.created_by else None,
                updated_by=request.user.username,
                comments=ride.comments
            )

            return JsonResponse({'success': True}, status=200)
    
class RideDetailsHistoryView(TemplateView):
    template_name = 'distributer/history_ride.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ride_id = self.kwargs['ride_id']
        ride = get_object_or_404(RideDetails, ride_id=ride_id)
        history = RideDetailsHistory.objects.filter(ride_id=ride_id).order_by('updated_on')
        context['ride'] = ride
        context['history'] = history
        return context

# @method_decorator(login_required(login_url='login'), name='dispatch')
# class UpdateRide(APIView):
#     def post(self, request):
#         ride_id = request.POST['ride_id']
#         company_format = request.POST['company_format']
#         customer_id = request.POST['customer']
#         vehicle_id = request.POST['vehicle']
#         ride_type_id = request.POST['ridetype']
#         source = request.POST['source']
#         destination = request.POST['destination']
#         booking_datetime = request.POST['Booking_datetime']
#         drop_datetime = request.POST['drop_datetime']
#         driver_id = request.POST['driver']
#         totalfare_before_gst = request.POST['totalfare_before_gst']
#         gst = request.POST['gst']
#         total_after_gst = request.POST['total_after_gst']
#         drivers_charge = request.POST['drivers_charge']
#         petrol_charge = request.POST['petrol_charge']
#         company_share = request.POST['company_share']
#         no_of_days = request.POST['no_of_days']
#         ride_status = request.POST['ride_status']
#         customer_feedback = request.POST['customer_feedback']
#         driver_feedback = request.POST['driver_feedback']

#         ride_details = RideDetails.objects.get(ride_id=ride_id)
#         ride_details.company_format = company_format
#         ride_details.customer = Customer.objects.get(customer_id=customer_id)
#         ride_details.vehicle = Vehicle.objects.get(vehicle_id=vehicle_id)
#         ride_details.ridetype = Ridetype.objects.get(ridetype_id=ride_type_id)
#         ride_details.source = source
#         ride_details.destination = destination
#         ride_details.Booking_datetime = booking_datetime
#         ride_details.drop_datetime = drop_datetime
#         ride_details.driver = Driver.objects.get(driver_id=driver_id)
#         ride_details.totalfare_before_gst = totalfare_before_gst
#         ride_details.gst = gst
#         ride_details.total_after_gst = total_after_gst
#         ride_details.drivers_charge = drivers_charge
#         ride_details.petrol_charge = petrol_charge
#         ride_details.company_share = company_share
#         ride_details.no_of_days = no_of_days
#         ride_details.ride_status = ride_status
#         ride_details.customer_feedback = customer_feedback
#         ride_details.driver_feedback = driver_feedback
#         ride_details.updated_by = request.user  # Set updated_by to the current user

#         ride_details.save()
#         return JsonResponse({'success': True}, status=200)
    
@method_decorator(login_required(login_url='login'), name='dispatch')
class profile(TemplateView):
    template_name = 'distributer/app-profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            user_id = self.request.session.get('user_id')
            print("---------------------------",user_id)
            userlist = User.objects.filter(id=user_id)
        except:
            userlist = User.objects.filter(id=user_id)
            
        context['userlist']= list(userlist)
        return context
    
@method_decorator(login_required(login_url='login'), name='dispatch')
class UpdateUserView(View):
    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        password = request.POST.get('password')

        if request.user:
            user = request.user
            # Simple validation
            if username and password:
                user.username = username
                user.set_password(password)
                user.save()
                #user = authenticate(username=user.username, password=password)
                if user is not None:
                    return JsonResponse({'status': 'success'}, status=200)
                return JsonResponse({'status': 'error', 'message': 'Authentication failed'}, status=400)
            return JsonResponse({'status': 'error', 'message': 'Invalid data'}, status=400)
        return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)
    

# current booking ##################################################################################################
@method_decorator(login_required(login_url='login'), name='dispatch')
class RideList(ListView):
    model = RideDetails
    template_name = "distributer/view_ride.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['drivers'] = Driver.objects.all()
        # Pass a sample ride_id or adjust based on your logic
        context['ride_id'] = self.kwargs.get('ride_id', 1)  # Adjust this based on your URL setup
        return context
    
    def get_queryset(self):
        return RideDetails.objects.filter(ride_status='currentbookings')
    
# assign driver###########################################################################################################
def assign_driver(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        driver_id = data.get('driver_id')  # This will be company_format
        ride_id = data.get('ride_id')

        try:
            ride = RideDetails.objects.get(ride_id=ride_id)  # Use ride_id instead of id
            driver = Driver.objects.get(company_format=driver_id)  # Lookup driver using company_format
            ride.driver = driver  # Assign the driver object
            ride.ride_status = 'assignbookings'
            ride.assigned_by = request.user
            ride.save()

            return JsonResponse({'status': 'success'})
        except RideDetails.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Ride not found.'}, status=404)
        except Driver.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Driver not found.'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'failed'}, status=400)

# assigned ride list##################################################################################################
@method_decorator(login_required(login_url='login'), name='dispatch')
class AssignedRideList(ListView):
    model = RideDetails
    template_name = "distributer/assigned_rides.html"

    def get_queryset(self):
        # Get only rides that are assigned
        return RideDetails.objects.filter(Q(ride_status='assignbookings') & Q(assigned_by=self.request.user)).select_related('driver')
    
##################    cancel booking    #################################################################### 
@method_decorator(login_required(login_url='login'), name='dispatch')
class CancelledListView(ListView):
    model = RideDetails
    template_name = "distributer/view_cancelbookings.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['drivers'] = Driver.objects.all()
        # Pass a sample ride_id or adjust based on your logic
        context['ride_id'] = self.kwargs.get('ride_id', 1)  # Adjust this based on your URL setup
        return context

    def get_queryset(self):
        return RideDetails.objects.filter(Q(ride_status='cancelledbookings') & Q(cancelled_by=self.request.user)).select_related('driver')


def cancel_ride(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        comments = data.get('comments')
        ride_id = data.get('ride_id')

        try:
            ride = RideDetails.objects.get(ride_id=ride_id)
            ride.comments = comments
            ride.ride_status = 'cancelledbookings'
            ride.cancelled_by =request.user
            ride.save()

            return JsonResponse({'status': 'success'})
        except RideDetails.DoesNotExist:
            return JsonResponse({'status': 'error', 'essage': 'Ride not found.'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'essage': str(e)}, status=500)

    return JsonResponse({'status': 'failed'}, status=400)