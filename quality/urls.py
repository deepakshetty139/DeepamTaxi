from django.urls import path
from quality.views import *
from taxipro.views import global_fetch_customer_details

urlpatterns = [

    path('qindex',qindex,name='qindex'),
    path('qridelist', RideList.as_view(), name='qridelist'),
    path('qaddride', AddRide.as_view(), name='qaddride'),
    path('qEditRide/<int:id>/', EditRide.as_view(), name='qEditRide'),
    path('qUpdateRide', UpdateRide.as_view(), name='qUpdateRide'),
    path('qRideHistory/<int:ride_id>/', RideDetailsHistoryView.as_view(),name='qRideHistory'),
    path('global_fetch_customer_details/',global_fetch_customer_details, name='global_fetch_customer_details'),
    
    #profile
    path('profile', profile.as_view(), name='q_profile'),
    path('update-user/', UpdateUserView.as_view(), name='q_update_user'),
    path('qinvoice/<int:ride_id>/', InvoiceView.as_view(), name='qinvoice_view'),

    # bookings
    path('qcompleted_rides', CompletedRideList.as_view(), name='qcompleted_rides'),
    path('qassign_driver', assign_driver, name='qassign_driver'),
    path('qview_assigned_rides', AssignedRideList.as_view(), name='qview_assigned_rides'),
    path('qadvance_bookings', AdvanceBookingsList.as_view(), name='qadvance_bookings'),
    path('qpending_bookings', PendingBookingsList.as_view(), name='qpending_bookings'),
    path('qongoing_rides', OngoingRideList.as_view(), name='qongoing_rides'),
    path('qcancelledbookings',CancelledListView.as_view(),name='qcancelledbookings'),
    path('qcancel_ride', cancel_ride, name='qcancel_ride'),

]