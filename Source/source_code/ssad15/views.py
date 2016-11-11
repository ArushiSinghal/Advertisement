from django.shortcuts import render
from django.http import HttpResponse
from global_values import *
from django.template import loader
from .models import *
from django.shortcuts import get_list_or_404,get_object_or_404,redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
import datetime
from forms import *
def index(request):
    return HttpResponse("Location Based Advertising")


# Get zone correponding to the location pinged by the device
def getzone(longitude,latitude):
    print longitude,latitude
    x = longitude
    y = latitude
    rows_done = math.floor((y- bottom_extreme)/dely)
    in_a_row = math.floor((x - left_extreme)/delx)
    zone_no = rows_done*zonesAlongX + in_a_row
    return int(zone_no)

def getOverLappingArea(left,right,bottom,top,zone_no):
    print "required zone no is ",zone_no
    Zone = zone.objects.filter(id=zone_no)
    # error handling
    if len(Zone) == 0 :
        # => that an invalid location has been picked
        # raise error
        print "Invalid location has been entered by the user"
        return False
    else :
        # select the required zone
        Zone = Zone[0]

    lowerx = Zone.bottom_left_coordinate_x
    lowery = Zone.bottom_left_coordinate_y
    topx = float(lowerx) + float(delx)
    topy = float(lowery) + float(dely)
    l = float(max(lowerx,left))
    r = float(min(topx,right))
    b = float(max(lowery,bottom))
    t = float(min(topy,top))
    area = float((r-l)*(t-b))
    #converting degree to Km
    area = area * kmTodegree * kmTodegree
    return area

def getWeekNumber(cur_date) :
    return datetime.date(cur_date.year,cur_date.month,cur_date.day).isocalendar()[1]

def check_for_slot(zone_no,required_bundles,required_slots,cont_slots,sets,week_no) :
    Slots = slots.objects.filter(zone_id = zone_no,week = week_no).order_by('slot_no')
    total_bundles = DEFAULT_BUNDLES

    # pre condition : zone_info should have been populated atleast once : initilize_zone.py
    info = zone_info.objects.filter(zone_id = zone_no).order_by('-week')
    if len(info)!=0 :

        # find if the total no of bundles have been modified by the Admin
        # if yes find the most recent modification and use that
        for inf in info :
            if inf.week <= week_no :
                total_bundles = inf.no_of_bundles
                break

    else :

        #error raised
        # probable cause database has not been populated
        #displaying appropriate warnings
        print "Warning : Admin : Database has not been populated"
        print "Run initilize_zone.py to rectify the error"
        redirect(invalid_empty_database)

    i=0

    # algorithm to check avaialable availability of slots
    while i < len(Slots) :
        slot = Slots[i]
        valid = True
        for j in range(cont_slots) :
            if i+j+1 > len(Slots) and i+j+1 <= MAX_SLOTS :
                pass
            elif i+j+1 <= len(Slots) and total_bundles - Slots[i+j].no_of_bundles_used >= required_bundles :
                pass
            else :
                valid = False
                break
        if valid :
            sets -= 1
            i += cont_slots
            if sets == 0 :
                # if the demand has been met return true
                return True
        else :
            i += 1
    if len(Slots) + sets*cont_slots <= MAX_SLOTS :
        # if the demand can be met
        return True

    # slots are not avaialable in the given zone
    return False

def check_availability(request) :

    # intializing the variables need for the calculations
    Xcenter = float(request.bussinessPoint_longitude)
    Ycenter = float(request.bussinessPoint_latitude)
    left = Xcenter - DELX/2
    right = Xcenter + DELX/2
    bottom = Ycenter - DELY/2
    top = Ycenter + DELY/2

    # starting the loop to map the request into zones and check the availability
    y = bottom
    wn = getWeekNumber(request.start_week)
    wn = int(wn)

    # the number of slots that must be given in continuous
    # eg a 45 second add must be given 2 slots at min in continuous to be displayed
    cont_slots = math.ceil(request.time_of_advertisement/30.0)
    cont_slots = int(cont_slots)

    # sets is the times an advertisement have to be displayed
    sets = request.no_of_slots / cont_slots
    sets = int(sets)

    for week_no in range(int(request.no_of_weeks)) :
        week_no += wn
        while y < top :
            x = left
            while x < right :

                # find the zone no based the coordinates
                zone_no = getzone(x,y)

                # get the overlap area between the bussiness area wrt to the current point and the zone
                OArea = getOverLappingArea(left,right,bottom,top,zone_no)
                if OArea == False :
                    # error has been raised
                    # the user has inputed an invalid location
                    redirect(invalid_location)

                # the number of bundles that needs to be given to the current advertisement in the current zone
                required_bundles = (OArea/BAREA)*request.select_bundles

                # calls the check_for_slot() to check for availability of slots in the current zone
                if not check_for_slot(zone_no,required_bundles,request.no_of_slots,cont_slots,sets,week_no) :
                    # no slots are avaialable in the current zone
                    # rasie error
                    return False

                x += delx
            y += dely
    return True


def update_slot(zone_no,required_bundles,cont_slots,sets,week_no,ad):
    pass

def update_scheduler(request) :
    # making sure that the slot is still avaialable
    if not check_availability(request) :
        # slots are no longer available
        return False

    else :
        # availability still holds good
        # intializing the variables need for the calculations
        Xcenter = float(request.bussinessPoint_longitude)
        Ycenter = float(request.bussinessPoint_latitude)
        left = Xcenter - DELX/2
        right = Xcenter + DELX/2
        bottom = Ycenter - DELY/2
        top = Ycenter + DELY/2

        # starting the loop to map the request into zones and check the availability
        y = bottom
        wn = getWeekNumber(request.start_week)
        wn = int(wn)

        # the number of slots that must be given in continuous
        # eg a 45 second add must be given 2 slots at min in continuous to be displayed
        cont_slots = math.ceil(request.time_of_advertisement/30.0)
        cont_slots = int(cont_slots)

        # sets is the times an advertisement have to be displayed
        sets = request.no_of_slots / cont_slots
        sets = int(sets)

        # add the advertisement to advertisement table
        ad = advertisement(upload=request.upload_Advertisement,time_len=request.time_of_advertisement)
        ad.save()

        for week_no in range(int(request.no_of_weeks)) :
            week_no += wn
            while y < top :
                x = left
                while x < right :

                    # find the zone no based the coordinates
                    zone_no = getzone(x,y)

                    # get the overlap area between the bussiness area wrt to the current point and the zone
                    OArea = getOverLappingArea(left,right,bottom,top,zone_no)
                    if OArea == False :
                        # error has been raised
                        # the user has inputed an invalid location
                        redirect(invalid_location)

                    # the number of bundles that needs to be given to the current advertisement in the current zone
                    required_bundles = (OArea/BAREA)*request.select_bundles

                    #update the current slot
                    update_slot(zone_no,required_bundles,cont_slots,sets,week_no,ad)

                    x += delx
                y += dely
        return True


# get advertisment corresponding to the zone device is in and also the server time

def find_slot_no(Zone_id) :
    cur = datetime.datetime.now()
    cur_slot = running_slots.objects.all.filter(zone_id=Zone_id)[0]
    diff = (cur.minute - cur_slot.start_time.minute)*60 + (cur.second - cur_slot.start_time.second)
    change = math.floor(diff/30.0)
    cur_slot.slot += change
    max_avail_slots = len(slot.objects.filter(zone_id=Zone_id))
    if cur_slot.slot > max_avail_slots :
        cur_slot.slot = 1
        running.objects.filter(zone_id=Zone_id).delete()
        running_ads.objects.filter(zone_id=Zone_id).delete()
    if change > 0 :
        cur_slot.start_time = cur
    cur_slot.save()
    return cur_slot.slot

def get_advertisement(Zone_id):
    slot_no = find_slot_no(Zone_id)
    all_adv = slot.objects.filter(zone_id_id=Zone_id,slot_no=slot_no,is_starting = True)
    X = running.objects.filter(zone=Zone_id,slot_no=slot_no)
    if len(X) == 0 :
        X = running(zone_id=Zone_id,slot_no=slot_no,alloted=0)
        X.save()
    else :
        X = X[0]
    X.alloted += 1
    X.save()
    X = X.alloted
    Ad = 0
    priority = 0
    for ad in all_adv :
        given = running_ads.objects.filter(zone_id=Zone_id,ad=ad.advertisement_id,slot_no=slot_no)
        if len(given) == 0 :
            given = running_ads(zone_id=Zone_id,slot_no=slot_no,ad=ad.advertisement_id,given=0)
            given.save()
        else :
            given = given[0]
        if ad.bundles_tobegiven*X - given.given > priority :
            priority = ad.bundles_tobegiven*X - given.given
            Ad = ad.advertisement_id

    cur_ad = running_ads.objects.filter(ad=Ad)[0]
    cur_ad.given += 1
    cur_ad.save()

    cont_slots = math.ceil(cur_ad.time_len /30.0)
    for sl in range(slot_no+1,slot_no+cont_slots) :
        rs = running_slots.objects.filter(zone_id=Zone_id,slot=sl)
        if len(rs) == 0 :
            rs = running_slots(zone_id=Zone_id,slot=sl,alloted=0)
        else :
            rs = rs[0]
        rs.alloted += 1
        rs.save()
        ra = running_ads(zone_id=Zone_id,ad=cur_ad.id,slot_no=sl)
        if len(ra) == 0 :
            ra = running_ads(zone_id=Zone_id,slot_no=sl,given=0)
        else :
            ra = ra[0]
        ra.given += 1
        ra.save()
    my_ad=get_object_or_404(advertisement,id=Ad)
    path = my_ad.upload.url
    return str(path),my_ad.time_len
    # my_ad = advertisement.objects.filter()
    # Slot=running.objects.filter(zone_id=Zone_id)[0]
    # tot = slot.objects.filter(zone_id=Zone_id)
    # tot_slots = len(tot)
    # if tot_slots == 0 :
    #     pass # to handeled later
    # Slot.slot_no = Slot.slot_no + 1
    # if Slot.slot_no > tot_slots :
    #     Slot.slot_no=1
    # slot_no=Slot.slot_no
    # print "the current slot is ",slot_no
    # Slot.save()
    # SSlot=get_object_or_404(slot,zone_id_id=Zone_id,slot_no=slot_no)
    # ad_id=SSlot.advertisement_id_id
    # print "Ad is ",ad
    # path=ad.upload.url
    # path=str(path)
    # return path

#get the pinged location from the device
#get corresponding zone no and display advertisement according to time and zone
#this function to be changed for scheduling in R2
import json
def display_advertisement(request):
    #checking if location is posted or not
    #error set to 1 represents an error in getting location of the device
    error = 0
    if request.method == 'POST':
        if 'longitude' in request.POST:
            longitude = float(request.POST['longitude'])
        else :
            error=1
        if 'latitude' in request.POST :
            latitude= float(request.POST['latitude'])
        else :
            error=1
    else :
        error = 1
    print float(longitude),float(latitude)
    if error:
        return HttpResponse("Error in getting location !")
    else :
        zone_no=getzone(longitude,latitude)
        print "zone no is ",zone_no
        path,time_len=get_advertisement(zone_no)
        # path = "media/" + path
        print "path fron db is",path
        # path = "chaitanya"
        context={'path':path,'time_len':time_len}
        return HttpResponse(
            json.dumps(context),
            content_type="application/json"
        )
        # return render(request, 'ssad15/display_advertisement.html', context)
# function to calculate total cost to be paid by the customer
def total_cost(request):
    print "total cost has been called"
    Xcenter = float(request.bussinessPoint_longitude)
    Ycenter = float(request.bussinessPoint_latitude)
    left = Xcenter - DELX/2
    right = Xcenter + DELX/2
    bottom = Ycenter - DELY/2
    top = Ycenter + DELY/2
    #variable to store total_cost
    total_cost=0
    # starting the loop to map the request into zones and calculate total cost
    y = bottom
    wn = getWeekNumber(request.start_week)
    no_of_slots=request.no_of_slots
    for week_no in xrange(wn+int(request.no_of_weeks)) :
        while y < top :
            x = left
            while x < right :
                zone_no = getzone(x,y)
                OArea = getOverLappingArea(left,right,bottom,top,zone_no)
                required_bundles = (OArea/BAREA)*request.select_bundles
                z=zone_info.objects.filter(zone_id=zone_no).order_by('-week')
                i = 0
                while i< len(z):
                    if z[i].week <= week_no:
                        w=z[i].week
                        break
                    else :
                        i += 1
                if i!= len(z) :
                    zone=get_object_or_404(zone_info,zone_id=zone_no,week=w)
                    cost=zone.cost
                else :
                    cost
                total_cost=total_cost+required_bundles * cost * no_of_slots
                x += delx
            y += dely
    return int(total_cost)
def select_zone(request) :
    error = 0
    if request.method == 'POST':
        if 'longitude' in request.POST:
            longitude = float(request.POST['longitude'])
        else :
            error=1
        if 'latitude' in request.POST :
            latitude= float(request.POST['latitude'])
        else :
            error=1
        print float(longitude),float(latitude)
        if error:
            return HttpResponse("Error in getting location !")
        else :
            return redirect(edit_zone,longitude=longitude,latitude=latitude)
    else :
        pass
    return render(request,'ssad15/select_zone.html')

def edit_zone(request,longitude,latitude) :
    print longitude
    print latitude
    editing_done=False
    if request.method == 'POST' :
        form =zone_info_form(request.POST)
        if form.is_valid() :
            print "changes done by the admin are valid"
            form = form.cleaned_data
            Xcenter = float(longitude)
            Ycenter = float(latitude)
            left = Xcenter - DELX/2
            right = Xcenter + DELX/2
            bottom = Ycenter - DELY/2
            top = Ycenter + DELY/2
            #variable to store total_cost
            # starting the loop to map the request into zones and calculate total cost
            y = bottom
            wn = getWeekNumber(form['week'])
            while y < top :
                x = left
                while x < right :
                    zone_no = getzone(x,y)
                    zone_info(zone_id=zone_no,week=wn,cost=form['cost'],no_of_bundles=form['no_of_bundles']).save()
                    x += delx
                y += dely
            print "calling render"
            return render(request,'ssad15/changesdone.html')
        else :
            print form.errors
    else :
        form = zone_info_form()
    return render(request,'ssad15/edit_zone.html',{'form':form,'editing_done':editing_done,'longitude':longitude,'latitude':latitude})

#after device is logged in,it will be redirected to this controller
def start_advertisement(request):
    return render(request,'ssad15/start_advertisement.html')
def render_advertisement(request):
    return render(request,'ssad15/render_advertisement.html')

def invalid_location(request) :
    pass

def invalid_empty_database(request) :
    pass
