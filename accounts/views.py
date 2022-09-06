from django.shortcuts import redirect, render
import requests
from django.contrib.auth import login,get_user_model
from django.core.exceptions import FieldDoesNotExist
from string import digits
from django.contrib import messages
import random
import pickle
from django.core.exceptions import ObjectDoesNotExist
from django.conf.global_settings import SESSION_COOKIE_AGE
from datetime import  datetime,timedelta
from django.conf import settings
from .sms_ir import SMSApi
import json
from functools import wraps


User = get_user_model()


AUTH_TIME = getattr(settings,'AUTH_TIME',timedelta(minutes=2))
AUTH_TIME_AGAIN = getattr(settings,'AUTH_TIME_AGAIN',timedelta(minutes=1))
AUTH_TIME_AGAIN_MILISECOND = getattr(settings,'AUTH_TIME_AGAIN_MILISECOND',timedelta(milliseconds=60000))
AUTH_STEP_ONE_TEMPLATE = getattr(settings,'AUTH_STEP_ONE_TEMPLATE','accounts/auth.html')
LOGIN_REDIRECT_OTP = getattr(settings,'LOGIN_REDIRECT_OTP','/')
AUTH_STEP_TWO_TEMPLATE = getattr(settings,'AUTH_STEP_TWO_TEMPLATE','accounts/second-auth.html')




def auth(request):
    
    if request.user.is_authenticated:
        return redirect('/')

    auth_token = {}

    try:

        auth_token = pickle.loads(bytes.fromhex(request.session.get('auth_key')))
        time_auth = auth_token.get('countdown')
        time_now = timedelta(hours=datetime.now().time().hour,seconds=datetime.now().time().second,minutes=datetime.now().time().minute)
        prev_time = timedelta(hours=time_auth.hour,minutes=time_auth.minute,seconds=time_auth.second)
        final_time = time_now - prev_time
        
        if final_time > AUTH_TIME:
            auth_token['use'] = True
            hex_auth = pickle.dumps(auth_token).hex()
            request.session['auth_key'] = hex_auth
    except:
        pass
    if request.method == 'POST':

        # OTP Start
        # get user number by post request
        number = request.POST.get('number')
        # validate number
        if len(number) > 13 or len(number) < 10:
            messages.error(request,'شماره تلفن معتبر وارد کنید')
            return redirect('accounts:auth')
        # remove 0 in first number
        if number[0] == '0':
            number = number[1:]
        
        # validate User can submit number
        if auth_token.get('use') == True or not request.session.get('auth_key'):
            # generate otp
            key = ''.join(random.choices(digits,k=6))
            

            # Send by sms.ir API
            api = SMSApi()
            token = api.get_token()
            api.send_ultra_fast_send(number,key,token=token)

            if number:
                # Encode Data
                auth_key = {"auth_number":number,'auth_key':key,'use':True,'countdown':datetime.now().time().replace(microsecond=0)}
                hex_auth = pickle.dumps(auth_key).hex()
                request.session['auth_key'] = hex_auth
         
            else:
                return redirect('accounts:auth')
            
            return redirect('accounts:second-auth')
        else:
            messages.error(request,'لطفا 1 الی دو دقیقه دیگر امتحان کنید')
    
    return render(request,AUTH_STEP_ONE_TEMPLATE,{})

def send_auth_token_again(request):
    session_auth_token = request.session.get('auth_key')
    if session_auth_token:
        
        auth_token = pickle.loads(bytes.fromhex(session_auth_token))
        time_auth = auth_token.get('countdown')
        time_now = timedelta(hours=datetime.now().time().hour,seconds=datetime.now().time().second,minutes=datetime.now().time().minute)
        prev_time = timedelta(hours=time_auth.hour,minutes=time_auth.minute,seconds=time_auth.second)
        final_time = time_now - prev_time
        
        if final_time > AUTH_TIME_AGAIN:
            key = ''.join(random.choices(digits,k=6))

            # API Instace
            api = SMSApi()
            token = api.get_token()
            # Send Code Again
            api.send_ultra_fast_send(auth_token.get('auth_number'),key,token=token)
            
            auth_key = {"auth_number":auth_token.get('auth_number'),'auth_key':key,'use':True,'countdown':datetime.now().time().replace(microsecond=0)}
            hex_auth = pickle.dumps(auth_key).hex()
            request.session['auth_key'] = hex_auth
            messages.success(request,'با موفقیت کد دوباره ارسال شد')


            return redirect('accounts:second-auth')
        
    else:
        return redirect('/')
    
    
def auth_second_step(request):
    if request.session.get('auth_timeout') and not request.method == 'POST' :
        return redirect('accounts:auth')
    if request.user.is_authenticated:
        return redirect('/')
    if not request.session.get('auth_key'):
        return redirect('accounts:auth')
    # Turn Use to True for timedelta
    auth_token = pickle.loads(bytes.fromhex(request.session.get('auth_key')))
    time_auth = auth_token.get('countdown')
    time_now = timedelta(hours=datetime.now().time().hour,seconds=datetime.now().time().second,minutes=datetime.now().time().minute)
    prev_time = timedelta(hours=time_auth.hour,minutes=time_auth.minute,seconds=time_auth.second)
    final_time = time_now - prev_time
    
    if final_time > AUTH_TIME:
        return redirect('accounts:auth')
   
    auth_key = pickle.loads(bytes.fromhex(request.session.get('auth_key')))

    auth_key['use'] = False
    hex_auth = pickle.dumps(auth_key).hex()
    request.session['auth_key'] = hex_auth
  
    next_path = request.GET.get('next')
    auth_key = pickle.loads(bytes.fromhex(request.session.get('auth_key')))
    
    if request.method == 'POST':
        key = request.POST.get('key')
        try:
            user_auth = User.objects.get(number=auth_key.get('auth_number'))
            if key == auth_key.get('auth_key'):
                login(request,user_auth)
                request.session.set_expiry(SESSION_COOKIE_AGE)
                # Redirect To Profile Next
            else:
                messages.error(request,'کد وارد شده اشتباه است')
                return redirect('accounts:second-auth')
        except ObjectDoesNotExist:
            # Check If request user does not exists
            if key == auth_key.get('auth_key'):
                user = User.objects.create(number=auth_key.get('auth_number'))
                login(request,user)
                request.session.set_expiry(SESSION_COOKIE_AGE)
                
            else:
                messages.error(request,'کد وارد شده اشتباه است')
                return redirect('accounts:second-auth')

            # Redirect To Profile Next
        
        return redirect(f'{LOGIN_REDIRECT_OTP}') if not next_path else redirect(f'/{next_path}')

    return render(request,AUTH_STEP_TWO_TEMPLATE,{'millisecond':AUTH_TIME_AGAIN_MILISECOND,'phone_number':auth_key.get('auth_number')})
        
