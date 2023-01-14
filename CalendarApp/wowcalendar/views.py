import json
import os
from tkinter import messagebox
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, UserModel, User, AuthenticationForm
from collections import defaultdict
import random
import ast
import datetime
import pytz


from wowcalendar.models import Profile
from wowcalendar.models import Character
from wowcalendar.models import Class
from wowcalendar.models import Spec
from wowcalendar.models import Event
from wowcalendar.models import Participant

def index(request):
  
  if request.user.is_authenticated:
    return redirect(homePage)
   
  if request.method == 'POST': 
    
    if 'login_form' in request.POST:
      
      username = request.POST['username_login']
      password = request.POST['password_login']
      
      user = authenticate(request, username=username, password=password)
      
      if user is not None:
        login(request, user)
        messages.success(request, 'Succesfully logged in')
        return redirect(homePage)
      else:
        messages.warning(request, 'Invalid login information')
        form_login = AuthenticationForm(request.POST)
        return render(request, 'index.html', {'form': form_login})
    
    else:
      messages.warning(request, 'Invalid request')
      return redirect(index)
    
  return render(request, 'index.html')
  
def homePage(request):
  if request.user.is_authenticated:
    
    profile = Profile.objects.get(user_id=request.user)
    user = request.user
    
    if profile.role != "Restricted":
      
      if profile.role == "Admin" or profile.role == "Officer":
        has_permission = 1
      else:
        has_permission = 0
    
      characters = Character.objects.filter(profile_id=Profile.objects.get(user_id=request.user)).order_by('name')
      
      context_dict = {
        "profile" : profile,
        "user" : user,
        "characters" : characters,
        "has_permission" : has_permission,
      }
      
      return render(request, 'home.html', context=context_dict)
    
    else:
      logout(request)
      messages.warning(request, 'Account restricted')
      return redirect(index)
  
  return redirect(index)
  
def createAccount(request):
  
  if request.user.is_authenticated:
    return redirect('/home')
  
  if request.method == 'POST':
  
    if 'register_form' in request.POST:
      email = request.POST['email']
      username = request.POST['username']
      password1 = request.POST['password1']
      password2 = request.POST['password2']
      
      
      #user = authenticate(request, username=username, password=password1)
      
      form_register = UserCreationForm(request.POST)
      
      #Validate registration form
      try:
        user_exists = User.objects.get(username=request.POST['username'])
        
        messages.warning(request, 'Username already taken')
        return redirect(createAccount)
      
      except User.DoesNotExist:
           
        if form_register.is_valid():
          form_register.save()   
                 
          user = authenticate(username=username, password=password1)
          login(request, user)
          
          all_profiles = Profile.objects.filter().order_by('role')
          
          if all_profiles.count() == 0:
            temp_role = 'Admin'
          else:
            temp_role = 'User'
          
          #Save the new account
          profile = Profile(
            user_id=request.user,
            email=email,
            profile_username=str(request.user),
            role=temp_role,
            description='No description')
          profile.save()
          
          messages.success(request, 'Succesfully logged in')
          return redirect(homePage)
          
        else:
          messages.success(request, 'Invalid details')
          
    else:
      messages.warning(request, 'Invalid request')
      return redirect(createAccount)      
           
  return render(request, 'register.html')

def characterPage(request):
  
  if request.user.is_authenticated:
    
    profile = Profile.objects.get(user_id=request.user)
    user = request.user
    
    if profile.role != "Restricted":
    
      characters = list(Character.objects.filter(profile_id=Profile.objects.get(user_id=request.user)).order_by('name'))
      
      classes = []
      
      unknown_class = Class(
        name="Unknown",
        color="#808080")
      
      for character in characters:
        try:
          current_class = Class.objects.get(id=character.class_id)
        except Class.DoesNotExist:
          current_class = unknown_class
        
        classes.append(current_class)
        
      char_class_list = zip(characters, classes)
      
      context_dict = {
        "profile" : profile,
        "user" : user,
        "characters" : characters,
        "classes" : classes,
        "char_class_list" : char_class_list,
      }
      
      return render(request, 'characters.html', context=context_dict)
    
    else:
      logout(request)
      messages.warning(request, 'Account restricted')
      return redirect(index)  
  
  return redirect(index)  

def characterAddPage(request):
  if request.user.is_authenticated:
    
    profile = Profile.objects.get(user_id=request.user)
    user = request.user
    
    if profile.role != "Restricted":
    
      characters = Character.objects.filter(profile_id=Profile.objects.get(user_id=request.user)).order_by('name')
      all_classes = Class.objects.filter().order_by('name')
      
      spec_dict = defaultdict(list)
      
      spec_dict = {}
      
      for char_class in all_classes:
        spec_list = []
        
        specs_class = Spec.objects.filter(class_id=char_class).order_by('name')
        
        for spec in specs_class:
          spec_list.append(spec.name)
        
        spec_dict[char_class.pk] = spec_list
      
      context_dict = {
        "profile" : profile,
        "user" : user,
        "characters" : characters,
        "all_classes" : all_classes,
        "spec_dict" : spec_dict,
        "dict_iterator" : range(1, len(spec_dict)+1)
      }
      
      if request.method == 'POST': 
      
        if 'add_character' in request.POST:
          
          
          
          name = request.POST['name']
          char_class = request.POST['class']
          specialization = request.POST['specialization']
          role = request.POST['role']
          
          # print(name)
          # print(char_class)
          # print(specialization)
          # print(role)
          if not Character.objects.filter(name__iexact=name).exists():
            
            if not Class.objects.filter(id=char_class).exists():
              messages.success(request, 'Invalid request')
              return redirect(characterAddPage)
            else:
              
              selected_class = Class.objects.filter(id=char_class).first()
            
              #Save the new char
              new_character = Character(
                profile_id=profile,
                name=name,
                class_id=char_class,
                class_name=selected_class.name,
                spec=specialization,
                role=role)
              new_character.save()
              
              messages.success(request, 'Character added succesfully')
              return redirect(characterPage)
          
          else:
            messages.warning(request, 'That character already exists')
          
        else:
          messages.warning(request, 'Invalid request')
          return redirect(characterAddPage)
      
      return render(request, 'add_character.html', context=context_dict)
    
    else:
      logout(request)
      messages.warning(request, 'Account restricted')
      return redirect(index)
  
  return redirect(index)

def characterEditPage(request, char_id):
  
  if request.user.is_authenticated:
    profile = Profile.objects.get(user_id=request.user)
    user = request.user
    
    if profile.role != "Restricted":
    
      characters = Character.objects.filter(profile_id=Profile.objects.get(user_id=request.user)).order_by('name')
      all_classes = Class.objects.filter().order_by('name')
      
      selected_character = Character.objects.get(id=char_id)
      
      current_profile_id = profile.user_id
      selected_class_profile_id = selected_character.profile_id.user_id
      
      if current_profile_id == selected_class_profile_id:
        
        if selected_character.class_id == -1:
          character_class = all_classes.first()
          
          specs_class = Spec.objects.filter(class_id=character_class).order_by('name')
          character_spec = specs_class.first()
          
          character_role = "DPS"
        else:
          character_class = Class.objects.get(id=selected_character.class_id)
          character_spec = selected_character.spec
          character_role = selected_character.role
        
        spec_dict = defaultdict(list)
        
        spec_dict = {}
        
        for char_class in all_classes:
          spec_list = []
          
          specs_class = Spec.objects.filter(class_id=char_class).order_by('name')
          
          for spec in specs_class:
            spec_list.append(spec.name)
          
          spec_dict[char_class.pk] = spec_list
          
        if request.method == 'POST':
          if 'edit_character' in request.POST:
            name = request.POST['name']
            char_class = request.POST['class']
            specialization = request.POST['specialization']
            role = request.POST['role']
            
            if not Class.objects.filter(id=char_class).exists():
              messages.success(request, 'Invalid request')
              return redirect(characterPage)
            else:
              selected_class = Class.objects.filter(id=char_class).first()
            
              selected_character.name = name
              selected_character.class_id = char_class
              selected_character.class_name = selected_class.name
              selected_character.spec = specialization
              selected_character.role = role
              selected_character.save()
              
              messages.success(request, 'Character edited successfully')
              return redirect(characterPage)
          
          elif 'delete_character' in request.POST:
            
            Character.objects.filter(id=char_id).delete()
            messages.warning(request, 'Character deleted successfully')
            return redirect(characterPage)
          
          else:
            messages.warning(request, 'Invalid request')
            return redirect(characterPage)
          
        context_dict = {
            "profile" : profile,
            "user" : user,
            "selected_character" : selected_character,
            "character_class" : character_class,
            "character_spec" : character_spec,
            "character_role" : character_role,
            "characters" : characters,
            "all_classes" : all_classes,
            "spec_dict" : spec_dict,
            "dict_iterator" : range(1, len(spec_dict)+1)
          }
          
        return render(request, 'edit_character.html', context=context_dict)
      
      else:
        messages.warning(request, 'Invalid character')
        return redirect(characterPage)
      
    else:
      logout(request)
      messages.warning(request, 'Account restricted')
      return redirect(index)
  
  return redirect(index)

def classPage(request):
  if request.user.is_authenticated:
    
    profile = Profile.objects.get(user_id=request.user)
    user = request.user
    
    if profile.role != "Restricted":
      
      if profile.role == "Admin" or profile.role == "Officer":
        
        if profile.role == "Admin" or profile.role == "Officer":
          has_permission = 1
        else:
          has_permission = 0
    
        classes = Class.objects.filter().order_by('name')
        
        context_dict = {
          "profile" : profile,
          "user" : user,
          "classes" : classes,
          "has_permission" : has_permission,
        }
        
        if request.method == 'POST': 
          
          if 'delete_class' in request.POST:
            
            selected_class_id = request.POST['selected_class']
            selected_class = Class.objects.get(id=int(selected_class_id))
            
            characters = list(Character.objects.filter(class_id=selected_class.pk).order_by('name'))
            
            for character in characters:
              character.class_id = -1
              character.spec = ""
              character.role = "Unknown"
              character.save()
              
            Class.objects.filter(id=int(selected_class_id)).delete()
            messages.warning(request, 'Class deleted successfully - ' + selected_class.name)

          else:
            messages.warning(request, 'Invalid request')
            return redirect(classPage)
        
        return render(request, 'classes.html', context=context_dict)
      
      else:
        messages.warning(request, 'Access denied')
        return redirect(homePage)
    
    else:
      logout(request)
      messages.warning(request, 'Account restricted')
      return redirect(index)
  
  return redirect(index)

def classAddPage(request):
  
  if request.user.is_authenticated:
    
    profile = Profile.objects.get(user_id=request.user)
    user = request.user
    
    if profile.role != "Restricted":
      
      if profile.role == "Admin" or profile.role == "Officer":
    
        characters = Character.objects.filter(profile_id=Profile.objects.get(user_id=request.user)).order_by('name')
        
        context_dict = {
          "profile" : profile,
          "user" : user,
          "characters" : characters,
        }
        
        if request.method == 'POST': 
        
          if 'add_class' in request.POST:
            
            name = request.POST['name']
            color = request.POST['color']
            
            if not Class.objects.filter(name__iexact=name).exists():
              
              new_class = Class(
                name=name,
                color=color)
              
              new_class.save()
              
              current_class = Class.objects.filter(name=name).first()
              
              specialization_list = request.POST.getlist('specialization[]')
              
              for spec in specialization_list:
                
                new_spec = Spec(
                  class_id=current_class,
                  name=str(spec))
                
                new_spec.save()
              
              messages.success(request, 'Class added successfully')
              return redirect(classPage) 
            
            else:
              messages.warning(request, 'That class already exists')
              return redirect(classPage) 
          
          else:
            messages.warning(request, 'Invalid request')
            return redirect(classAddPage)
              
        return render(request, 'add_class.html', context=context_dict)
      
      else:
        messages.warning(request, 'Access denied')
        return redirect(homePage)
    
    else:
      logout(request)
      messages.warning(request, 'Account restricted')
      return redirect(index)
  
  return redirect(index)

def calendarPage(request):
  
  if request.user.is_authenticated:
    
    profile = Profile.objects.get(user_id=request.user)
    user = request.user
    
    if profile.role != "Restricted":
      
      if profile.role == "Admin" or profile.role == "Officer":
        has_permission = 1
      else:
        has_permission = 0
        
      eventsdb = Event.objects.filter()
      
      events = []
      
      for event in eventsdb:
        
        load_event = {
          "event_id": event.pk,
          "eventName" : event.name,
          "start_date" : ast.literal_eval(event.start_date),
          "end_date" : ast.literal_eval(event.end_date),
          "start_time" : event.start_time,
          "end_time": event.end_time,
          "deadline": event.deadline,
          "description": event.description
        }
        
        events.append(load_event)
      
      events = json.dumps(events)
      
      
      context_dict = {
        "profile" : profile,
        "user" : user,
        "events" : events,
        "has_permission" : has_permission,
      }
      
      return render(request, 'calendar.html', context=context_dict)
    
    else:
      logout(request)
      messages.warning(request, 'Account restricted')
      return redirect(index)
  
  return redirect(index)

def eventAddPage(request):

  if request.user.is_authenticated:
    
    profile = Profile.objects.get(user_id=request.user)
    user = request.user
    
    if profile.role != "Restricted":
      
      if profile.role == "Admin" or profile.role == "Officer":
    
        var_date = request.GET.get('date')

        context_dict = {
          "profile" : profile,
          "user" : user,
          "var_date" : var_date,
        }
        
        if request.method == 'POST': 
          
          if 'add_event' in request.POST:
            
            name = request.POST['name']
            description = request.POST['description']
            start_date = request.POST['start_date']
            end_date = request.POST['end_date']
            start_time = request.POST['start_time']
            end_time = request.POST['end_time']
            deadline = request.POST['deadline']
            
            start_date = start_date.split("-")
            end_date = end_date.split("-")
            
            start_date.reverse()
            end_date.reverse()
            
            start_date_fixed = []
            end_date_fixed = []
            
            for index1, index2 in zip(start_date, end_date):
              
              fixed_date_1 = index1
              fixed_date_2 = index2
              
              for char in index1:
                if char == "0":
                  fixed_date_1 = index1[1:]
                else:
                  start_date_fixed.append(int(fixed_date_1))
                  break
                
              for char in index2:
                if char == "0":
                  fixed_date_2 = index2[1:]
                else:
                  end_date_fixed.append(int(fixed_date_2))
                  break
        
            new_event = Event(
              name=name,
              description=description,
              start_date=start_date_fixed,
              end_date=end_date_fixed,
              start_time=start_time,
              end_time=end_time,
              deadline=deadline,
              )
            
            new_event.save()

            messages.success(request, 'Event added successfully')
            return redirect(calendarPage)
        
          else:
            messages.warning(request, 'Invalid request')
            return redirect(calendarPage)
          
        return render(request, 'add_event.html', context=context_dict)
      
      else:
        messages.warning(request, 'Access denied')
        return redirect(homePage)

    else:
      logout(request)
      messages.warning(request, 'Account restricted')
      return redirect(index)
      
  return redirect(index)

def eventViewPage(request):
  
  if request.user.is_authenticated:
    
    profile = Profile.objects.get(user_id=request.user)
    user = request.user
    
    if profile.role != "Restricted":
    
      characters = list(Character.objects.filter(profile_id=Profile.objects.get(user_id=request.user)).order_by('name'))
      
      event_id = request.GET.get('event_id')
      selected_event = Event.objects.get(id=event_id)
      selected_event_day = ast.literal_eval(selected_event.start_date)[0]
      selected_event_month = ast.literal_eval(selected_event.start_date)[1]
      selected_event_year = ast.literal_eval(selected_event.start_date)[2]
      
      format_start_day = selected_event_day
      fomrat_start_month = selected_event_month
      
      current_status = 0
      current_char_status = "None"
      
      all_participants = Participant.objects.filter(event=selected_event)
      signed_up_participants = Participant.objects.filter(event=selected_event, status=1)
      signed_off_participants = Participant.objects.filter(event=selected_event, status=2)
      backup_participants = Participant.objects.filter(event=selected_event, status=3)
      guest_participants = Participant.objects.filter(event=selected_event, status=4)
      
      if Participant.objects.filter(event=selected_event, profile_id=profile).exists():
        current_participant_model = list(Participant.objects.filter(event=selected_event, profile_id=profile))
        current_status = current_participant_model[0].status
        current_char_status = current_participant_model[0].character.name
      else:
        current_status = 0
        current_char_status = "None"
      
      if selected_event_day < 10:
        format_start_day = "0" + str(selected_event_day)
        
      if selected_event_month < 10:
        fomrat_start_month = "0" + str(selected_event_month)
      
      start_date_format = str(format_start_day) + "." + str(fomrat_start_month) + "." + str(selected_event_year)
      
      end_event_day = ast.literal_eval(selected_event.end_date)[0]
      end_event_month = ast.literal_eval(selected_event.end_date)[1]
      end_event_year = ast.literal_eval(selected_event.end_date)[2]
      
      format_end_day = end_event_day
      fomrat_end_month = end_event_month
      
      if end_event_day < 10:
        format_end_day = "0" + str(end_event_day)
        
      if end_event_month < 10:
        fomrat_end_month = "0" + str(end_event_month)
      
      end_date_format = str(format_end_day) + "." + str(fomrat_end_month) + "." + str(end_event_year)
      
      bg_tz = pytz.timezone('Europe/Sofia')
      BG_time = datetime.datetime.now(bg_tz)
      
      deadline_hour_min = selected_event.deadline.split(":")
      
      deadline_time = bg_tz.localize(datetime.datetime(selected_event_year, selected_event_month, selected_event_day, int(deadline_hour_min[0]), int(deadline_hour_min[1])))
      
      deadline_over = False
      
      if BG_time < deadline_time :
        deadline_over = False
      else:
        deadline_over = True
      
      if request.method == 'POST': 
      
        if 'set_status' in request.POST:
          
          character_name = request.POST['character']
          status_text = request.POST['status']
          
          status_id = 0
          
          match status_text:
            case "signedup":
                status_id = 1
            case "signedoff":
                status_id = 2
            case "backup":
                status_id = 3
            case "guest":
                status_id = 4

            case _:
                status_id = 0
          
          print(character_name)
          print(status_text)
          print(status_id)
          print("-------------------")
          
          if Character.objects.filter(name__iexact=character_name).exists():
            
            selected_character = Character.objects.get(name__iexact=character_name)
            selected_character_profile = selected_character.profile_id
            
            if selected_character_profile == profile :
            
          
              participant_own_list = list(Participant.objects.filter(event=selected_event, profile_id=profile))
              
              print(participant_own_list)
              
              if deadline_over == False:
              
                if len(participant_own_list) != 0 :
                  
                  current_participant = participant_own_list[0]
                  
                  current_participant.character = selected_character
                  current_participant.status = status_id
                  
                  current_participant.save()
                  
                  messages.success(request, 'Status changed successfully')
                
                else:
                  
                  new_participant = Participant(
                      event=selected_event,
                      profile_id=profile,
                      character=selected_character,
                      status=status_id,
                      )
                  
                  new_participant.save()
                  messages.success(request, 'Status set successfully')
              
              else:
                messages.success(request, 'Deadline for this event is over')
              
              return redirect(calendarPage)
            
            else:
              messages.warning(request, 'Invalid request')
              return redirect(calendarPage)
          
          else:
            messages.warning(request, 'Invalid request')
            return redirect(calendarPage)
          
        else:
          messages.warning(request, 'Invalid request')
          return redirect(calendarPage)
        
      classes = Class.objects.filter().order_by('name')
        
          
      context_dict = {
        "profile" : profile,
        "user" : user,
        "selected_event" : selected_event,
        "selected_event_day" : selected_event_day,
        "selected_event_month" : selected_event_month,
        "selected_event_year" : selected_event_year,
        "end_event_day" : end_event_day,
        "end_event_month" : end_event_month,
        "end_event_year" : end_event_year,
        "start_date_format" : start_date_format,
        "end_date_format" : end_date_format,
        "characters" : characters,
        "current_status" : current_status,
        "current_char_status" : current_char_status,
        "all_participants" : all_participants,
        "signed_up_participants" : signed_up_participants,
        "signed_off_participants" : signed_off_participants,
        "backup_participants" : backup_participants,
        "guest_participants" : guest_participants,
        "classes" : classes,
        "deadline_over" : deadline_over,
      }    
              
      return render(request, 'event_view.html', context=context_dict)
    
    else:
      logout(request)
      messages.warning(request, 'Account restricted')
      return redirect(index)

  return redirect(index)

def manageUsersPage(request):
  
  if request.user.is_authenticated:
    
    profile = Profile.objects.get(user_id=request.user)
    user = request.user
    
    if profile.role != "Restricted":
      
      if profile.role == "Admin" or profile.role == "Officer":
    
        all_profiles = Profile.objects.filter().order_by('role')

        context_dict = {
          "profile" : profile,
          "user" : user,
          "all_profiles" : all_profiles,
        }
        
        return render(request, 'manage_users.html', context=context_dict)
      
      else:
        messages.warning(request, 'Access denied')
        return redirect(homePage)
    
    else:
      logout(request)
      messages.warning(request, 'Account restricted')
      return redirect(index)
  
  return redirect(index)
    
def changeUserPage(request):
  
  if request.user.is_authenticated:
    
    profile = Profile.objects.get(user_id=request.user)
    user = request.user
    
    if profile.role != "Restricted":
      
      if profile.role == "Admin" or profile.role == "Officer":
    
        selected_username = request.GET.get('user')
        
        selected_profile = Profile.objects.get(profile_username=selected_username)

        context_dict = {
          "profile" : profile,
          "user" : user,
          "selected_profile" : selected_profile,
        }
        
        if request.method == 'POST': 
        
          if 'change_user' in request.POST:
            
            if profile.role != "Admin" and selected_profile.role == "Admin":
              
              messages.warning(request, 'Access denied')
              return redirect(manageUsersPage) 
              
            else:
            
              profile_email = request.POST['email']
              profile_role = request.POST['role']
              
              if profile.role != "Admin" and profile_role == "Admin":
                
                selected_profile.email = profile_email
                selected_profile.role = profile_role
                selected_profile.save()
                
                messages.warning(request, 'Access denied')
                return redirect(manageUsersPage) 
              
              else:
              
                selected_profile.email = profile_email
                selected_profile.role = profile_role
                selected_profile.save()
                
                messages.success(request, 'User modified successfully')
                return redirect(manageUsersPage) 
            
          else:
            messages.warning(request, 'Invalid request')
            return redirect(manageUsersPage) 
          
        
        return render(request, 'change_user.html', context=context_dict)
      
      else:
        messages.warning(request, 'Access denied')
        return redirect(homePage)

    else:
      logout(request)
      messages.warning(request, 'Account restricted')
      return redirect(index)
      
  
  return redirect(index)
    
def accountPage(request):
  
  if request.user.is_authenticated:
    
    profile = Profile.objects.get(user_id=request.user)
    user = request.user
    
    if profile.role != "Restricted":
      
      context_dict = {
          "profile" : profile,
          "user" : user,
        }
        
      if request.method == 'POST': 
      
        if 'change_password' in request.POST:
          
          old_password = request.POST['old_password']
          
          if user.check_password(old_password):
            
            new_password = request.POST['new_password']
            confirm_password = request.POST['confirm_password']
            
            if new_password == confirm_password:
              
              username = user.username
              
              user.set_password(new_password)
              user.save()
              
              user = authenticate(request, username=username, password=new_password)
              login(request, user)
              
              messages.success(request, 'Password changed successfuly')
              return redirect(accountPage) 
            
            else:
              messages.warning(request, 'New passwords do not match')
              return redirect(accountPage) 
              
          
          else:
            messages.warning(request, 'Wrong password')
            return redirect(accountPage) 
          
        
        elif 'change_email' in request.POST:
          
          email = request.POST['email']
          
          profile.email = email
          profile.save()
          
          messages.success(request, 'Email changed successfuly')
          return redirect(accountPage) 
        
        else:
          messages.warning(request, 'Invalid request')
          return redirect(manageUsersPage) 
      
      return render(request, 'account.html', context=context_dict)
      
    else:
      logout(request)
      messages.warning(request, 'Account restricted')
      return redirect(index)
      
  
  return redirect(index)
  

#Function to logout the user     
def request_logout(request):
  
  logout(request)
  messages.success(request, 'Succesfully logged out')
  return redirect(index)
