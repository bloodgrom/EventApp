import json
import os
from tkinter import messagebox
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, UserModel, User, AuthenticationForm
from django.views.decorators.csrf import csrf_exempt
from django.db.models.functions import Lower
from django.http import JsonResponse
from collections import defaultdict
import random
import ast
import datetime
from datetime import datetime as datetime_c
import pytz


from wowcalendar.models import Profile
from wowcalendar.models import Character
from wowcalendar.models import Class
from wowcalendar.models import Spec
from wowcalendar.models import Event
from wowcalendar.models import Participant
from wowcalendar.models import Template

def index(request):
  
  if request.user.is_authenticated:
    return redirect(homePage)
   
  if request.method == 'POST': 
    
    if 'login_form' in request.POST:
      
      username = request.POST['username_login']
      password = request.POST['password_login']
      
      username = request.POST.get('username_login', "-2")
      password = request.POST.get('password_login', "-2")
  
      if username == "-2" or password == "-2":
          
        messages.warning(request, 'Invalid request 1')
        return redirect(index)
      
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
      messages.warning(request, 'Invalid request 2')
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
     
      email = request.POST.get('email', "-2")
      username = request.POST.get('username', "-2")
      password1 = request.POST.get('password1', "-2")
      password2 = request.POST.get('password2', "-2")
  
      if email == "-2" or username == "-2" or password1 == "-2" or password2 == "-2":
          
        messages.warning(request, 'Invalid request')
        return redirect(createAccount)
      
      
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
                
          name = request.POST.get('name', "-2")
          char_class = request.POST.get('class', "-2")
          specialization = request.POST.get('specialization', "-2")
          role = request.POST.get('role', "-2")
      
          if name == "-2" or char_class == "-2" or specialization == "-2" or role == "-2":
              
            messages.warning(request, 'Invalid request')
            return redirect(characterAddPage)
          

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
      
      if Character.objects.filter(id=char_id).exists():
      
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
              
              name = request.POST.get('name', "-2")
              char_class = request.POST.get('class', "-2")
              specialization = request.POST.get('specialization', "-2")
              role = request.POST.get('role', "-2")
          
              if name == "-2" or char_class == "-2" or specialization == "-2" or role == "-2":
                
                messages.warning(request, 'Invalid request')
                return redirect(characterPage)
              
              if not Class.objects.filter(id=char_class).exists():
                messages.warning(request, 'Invalid request')
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
              
              
              Character.objects.get(id=char_id).delete()        
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
        messages.warning(request, 'Character does not exist')
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
          
          if profile.role == "Admin" or profile.role == "Officer":
          
            if 'delete_class' in request.POST:
                        
              selected_class_id = request.POST.get('selected_class', "-2")
          
              if selected_class_id == "-2":
                  
                messages.warning(request, 'Invalid request')
                return redirect(classPage)
              
              if Class.objects.filter(id=int(selected_class_id)).exists():
                
                # at least one object satisfying query exists
                  
                selected_class = Class.objects.get(id=int(selected_class_id))
              
                characters = list(Character.objects.filter(class_id=selected_class.pk).order_by('name'))
                
                for character in characters:
                  character.class_id = -1
                  character.spec = ""
                  character.role = "Unknown"
                  character.save()
                  
                Class.objects.get(id=int(selected_class_id)).delete()
                messages.warning(request, 'Class deleted successfully - ' + selected_class.name)
                
              else:
                # no object satisfying query exists
                messages.warning(request, 'Class does not exist')
                return redirect(classPage)
              
              

            else:
              messages.warning(request, 'Invalid request')
              return redirect(classPage)
            
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
          
          if profile.role == "Admin" or profile.role == "Officer":
        
            if 'add_class' in request.POST:
                        
              name = request.POST.get('name', "-2")
              color = request.POST.get('color', "-2")
          
              if name == "-2" or color == "-2":
                  
                messages.warning(request, 'Invalid request')
                return redirect(classAddPage)
              
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
        
        current_participant = Participant.objects.filter(event=event, profile_id=profile)
        
        #current_date = str(ast.literal_eval(event.start_date)[0]) + "-" + str(ast.literal_eval(event.start_date)[1]) + "-" + str(ast.literal_eval(event.start_date)[2])
        
        if current_participant.count() > 0:
        
          event_status = current_participant.first().status_set
          
        else:
          
          event_status = 0
        
        load_event = {
          "event_id": event.pk,
          "eventName" : event.name,
          "start_date" : ast.literal_eval(event.start_date),
          "end_date" : ast.literal_eval(event.end_date),
          "start_time" : event.start_time,
          "end_time": event.end_time,
          "deadline": event.deadline,
          "description": event.description,
          "event_status": event_status
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

def templatePage(request):
  
  if request.user.is_authenticated:
    
    profile = Profile.objects.get(user_id=request.user)
    user = request.user
    
    if profile.role != "Restricted":
      
      if profile.role == "Admin" or profile.role == "Officer":
        
        if profile.role == "Admin" or profile.role == "Officer":
          has_permission = 1
        else:
          has_permission = 0
          
        templates = Template.objects.filter().order_by('-created_at')
          
        context_dict = {
          "profile" : profile,
          "user" : user,
          "templates" : templates,
          "has_permission" : has_permission,
        }
          
        if request.method == 'POST': 
          
          if profile.role == "Admin" or profile.role == "Officer":
            
            if 'delete_template' in request.POST:
              
              selected_template_id = request.POST.get('selected_template', "-2")
          
              if selected_template_id == "-2":
                  
                messages.warning(request, 'Invalid request')
                return redirect(classPage)
              
              if Template.objects.filter(id=int(selected_template_id)).exists():
                
                selected_template = Template.objects.get(id=int(selected_template_id))
                
                Template.objects.get(id=int(selected_template_id)).delete()
                messages.warning(request, 'Template deleted successfully - ' + selected_template.name)
                
              else:
                # no object satisfying query exists
                messages.warning(request, 'Template does not exist')
                return redirect(templatePage)
               
              
            else:
              messages.warning(request, 'Invalid request')
              return redirect(templatePage)

          else:
            messages.warning(request, 'Access denied')
            return redirect(homePage)  

        return render(request, 'templates.html', context=context_dict)
      
      else:
        messages.warning(request, 'Access denied')
        return redirect(homePage)
         
    else:
      logout(request)
      messages.warning(request, 'Account restricted')
      return redirect(index)
  
  return redirect(index)

def templateAddPage(request):
  
  if request.user.is_authenticated:
    
    profile = Profile.objects.get(user_id=request.user)
    user = request.user
    
    if profile.role != "Restricted":
      
      if profile.role == "Admin" or profile.role == "Officer":
        
        if profile.role == "Admin" or profile.role == "Officer":
          has_permission = 1
        else:
          has_permission = 0
          
 
        context_dict = {
          "profile" : profile,
          "user" : user,    
          "has_permission" : has_permission,
        }
          
        if request.method == 'POST': 
          
          if profile.role == "Admin" or profile.role == "Officer":
            
            if 'add_template' in request.POST:
              
              name = request.POST.get('name', "-2")
              description = request.POST.get('description', "-2")
              start_time = request.POST.get('start_time', "-2")
              end_time = request.POST.get('end_time', "-2")
              deadline = request.POST.get('deadline', "-2")     
          
              if name == "-2" or description == "-2" or start_time == "-2" or end_time == "-2" or deadline == "-2":
                            
                messages.warning(request, 'Invalid request')
                return redirect(templateAddPage)
              
              new_template = Template(
                  name=name,
                  description=description,
                  start_time=start_time,
                  end_time=end_time,
                  deadline=deadline,
                  )
                
              new_template.save()
              
              messages.success(request, 'Template created successfully')
              return redirect(templatePage)
            
            else:
              messages.warning(request, 'Invalid request')
              return redirect(templateAddPage)

          else:
            messages.warning(request, 'Access denied')
            return redirect(homePage)  

        return render(request, 'add_template.html', context=context_dict)
      
      else:
        messages.warning(request, 'Access denied')
        return redirect(homePage)
         
    else:
      logout(request)
      messages.warning(request, 'Account restricted')
      return redirect(index)
  
  return redirect(index)

def templateEditPage(request, template_id):
  
  if request.user.is_authenticated:
    
    profile = Profile.objects.get(user_id=request.user)
    user = request.user 
    
    if profile.role != "Restricted":
      
      if profile.role == "Admin" or profile.role == "Officer":
        
        if profile.role == "Admin" or profile.role == "Officer":
          has_permission = 1
        else:
          has_permission = 0
          
        selected_template_id = template_id
        
        if selected_template_id == "-2":
            
          messages.warning(request, 'Invalid request')
          return redirect(classPage)
        
        if Template.objects.filter(id=int(selected_template_id)).exists():
          
          selected_template = Template.objects.get(id=int(selected_template_id)) 

        else:
          # no object satisfying query exists
          messages.warning(request, 'Template does not exist')
          return redirect(templatePage)
          
        context_dict = {
          "profile" : profile,
          "user" : user,
          "has_permission" : has_permission,
          "selected_template" : selected_template,
        }
          
        if request.method == 'POST': 
          
          if profile.role == "Admin" or profile.role == "Officer":
            
            if 'edit_template' in request.POST:
              
              if Template.objects.filter(id=int(selected_template_id)).exists():
              
                name = request.POST.get('name', "-2")
                description = request.POST.get('description', "-2")
                start_time = request.POST.get('start_time', "-2")
                end_time = request.POST.get('end_time', "-2")
                deadline = request.POST.get('deadline', "-2")     
            
                if name == "-2" or description == "-2" or start_time == "-2" or end_time == "-2" or deadline == "-2":
                              
                  messages.warning(request, 'Invalid request')
                  return redirect(templatePage)
                
                selected_template.name = name
                selected_template.description = description
                selected_template.start_time = start_time
                selected_template.end_time = end_time
                selected_template.deadline = deadline
                  
                selected_template.save()
                
                messages.success(request, 'Template changed successfuly')
                return redirect(templatePage)
              
              else:
                # no object satisfying query exists
                messages.warning(request, 'Template does not exist')
                return redirect(templatePage)
        
            else:
              messages.warning(request, 'Invalid request')
              return redirect(templatePage)

          else:
            messages.warning(request, 'Access denied')
            return redirect(homePage)  

        return render(request, 'edit_template.html', context=context_dict)
      
      else:
        messages.warning(request, 'Access denied')
        return redirect(homePage)
         
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
        
        templates = list(Template.objects.filter().order_by('-created_at'))
        
        if len(templates) > 0:
          latest_template = templates[0]
          show_templates = 1
        else:
          latest_template = "None"
          show_templates = 0
        
        context_dict = {
          "profile" : profile,
          "user" : user,
          "var_date" : var_date,
          "templates" : templates,
          "latest_template" : latest_template,
          "show_templates" : show_templates
        }
        
        if request.method == 'POST': 
          
          if 'add_event' in request.POST:
            
            name = request.POST.get('name', "-2")
            description = request.POST.get('description', "-2")
            start_date = request.POST.get('start_date', "-2")
            end_date = request.POST.get('end_date', "-2")
            start_time = request.POST.get('start_time', "-2")
            end_time = request.POST.get('end_time', "-2")
            deadline = request.POST.get('deadline', "-2")
            weekly_event = request.POST.getlist('weekly_event', ["-1"])
            
        
            if name == "-2" or description == "-2" or start_date == "-2" or end_date == "-2" or start_time == "-2" or end_time == "-2" or deadline == "-2":
                
              messages.warning(request, 'Invalid request')
              return redirect(calendarPage)
            
            # Create array to hold future dates for start_date
            start_weekday_dates = []
            # Create array to hold future dates for end_date
            end_weekday_dates = []
            
            if weekly_event[0] == "weekly":
              
              start_weekday_dates.append(start_date)
              end_weekday_dates.append(end_date)
              
              # Get the datetime object for start_date
              start_datetime = datetime.datetime.strptime(start_date, "%Y-%m-%d")
              # Get the weekday for start_date
              start_weekday = start_datetime.weekday()

              # Get the first day of the current month
              first_day = datetime.datetime(start_datetime.year, start_datetime.month, 1)

              # Calculate how many days to add to the first day of the month to get the next desired weekday for start_date
              add_days = (start_weekday - first_day.weekday()) % 7
              if add_days < 0: 
                  add_days += 7
              next_weekday_date = first_day + datetime.timedelta(days=add_days)

              # Append the date to the array if it is in the future
              if next_weekday_date > start_datetime:
                  start_weekday_dates.append(next_weekday_date.strftime("%Y-%m-%d"))

              # Iterate through the remaining days of the month
              while next_weekday_date.month == start_datetime.month:
                  next_weekday_date += datetime.timedelta(days=7)
                  if next_weekday_date > start_datetime:
                      start_weekday_dates.append(next_weekday_date.strftime("%Y-%m-%d"))

              # Get the datetime object for end_date
              end_datetime = datetime.datetime.strptime(end_date, "%Y-%m-%d")
              # Get the weekday for end_date
              end_weekday = end_datetime.weekday()

              # Get the first day of the current month
              first_day = datetime.datetime(end_datetime.year, end_datetime.month, 1)

              # Calculate how many days to add to the first day of the month to get the next desired weekday for end_date
              add_days = (end_weekday - first_day.weekday()) % 7
              if add_days < 0: 
                  add_days += 7
              next_weekday_date = first_day + datetime.timedelta(days=add_days)

              # Append the date to the array if it is in the future
              if next_weekday_date > end_datetime:
                  end_weekday_dates.append(next_weekday_date.strftime("%Y-%m-%d"))

              # Iterate through the remaining days of the month
              while next_weekday_date.month == end_datetime.month:
                  next_weekday_date += datetime.timedelta(days=7)
                  if next_weekday_date > end_datetime:
                      end_weekday_dates.append(next_weekday_date.strftime("%Y-%m-%d"))
                          
            else:
              start_weekday_dates.append(start_date)
              end_weekday_dates.append(end_date)
            
            if len(start_weekday_dates) == len(end_weekday_dates):
              
              events_num = len(start_weekday_dates)
            
              for event_index in range(events_num):
                
                start_date = start_weekday_dates[event_index].split("-")
                end_date = end_weekday_dates[event_index].split("-")
                
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

              if events_num > 0:
                messages.success(request, 'Event added successfully')
              else:
                messages.warning(request, 'No events were specified')
                
              return redirect(calendarPage)
        
            else:
              messages.warning(request, 'Invalid request')
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

def eventEditPage(request, event_id):
  
  if request.user.is_authenticated:
    
    profile = Profile.objects.get(user_id=request.user)
    user = request.user
    
    if profile.role != "Restricted":
      
      if profile.role == "Admin" or profile.role == "Officer":
        
        selected_event_id = event_id
        
        if selected_event_id == "-2":
            
          messages.warning(request, 'Invalid request')
          return redirect(classPage)
        
        if Event.objects.filter(id=int(selected_event_id)).exists():
          
          selected_event = Event.objects.get(id=int(selected_event_id)) 

        else:
          # no object satisfying query exists
          messages.warning(request, 'Event does not exist')
          return redirect(calendarPage)
        
        start_day = str(ast.literal_eval(selected_event.start_date)[0])
        start_month = str(ast.literal_eval(selected_event.start_date)[1])
        start_year = str(ast.literal_eval(selected_event.start_date)[2])
        
        end_day = str(ast.literal_eval(selected_event.end_date)[0])
        end_month = str(ast.literal_eval(selected_event.end_date)[1])
        end_year = str(ast.literal_eval(selected_event.end_date)[2])
        
        if len(start_day) == 1:
          start_day = "0" + start_day
          
        if len(start_month) == 1:
          start_month = "0" + start_month
          
        if len(end_day) == 1:
          end_day = "0" + end_day
          
        if len(end_month) == 1:
          end_month = "0" + end_month
    

        selected_event_start_date = start_year + "-" + start_month  + "-" + start_day
        selected_event_end_date = end_year  + "-" +  end_month  + "-" +  end_day
        
        templates = list(Template.objects.filter().order_by('-created_at'))
        
        if len(templates) > 0:
          show_templates = 1
        else:
          show_templates = 0
        
        context_dict = {
          "profile" : profile,
          "user" : user,
          "templates" : templates,
          "show_templates" : show_templates,
          "selected_event" : selected_event,
          "selected_event_start_date" : selected_event_start_date,
          "selected_event_end_date" : selected_event_end_date,
        }
        
        
        if request.method == 'POST': 
          
          if 'edit_event' in request.POST:
            
            name = request.POST.get('name', "-2")
            description = request.POST.get('description', "-2")
            start_date = request.POST.get('start_date', "-2")
            end_date = request.POST.get('end_date', "-2")
            start_time = request.POST.get('start_time', "-2")
            end_time = request.POST.get('end_time', "-2")
            deadline = request.POST.get('deadline', "-2")
            
        
            if name == "-2" or description == "-2" or start_date == "-2" or end_date == "-2" or start_time == "-2" or end_time == "-2" or deadline == "-2":
                
              messages.warning(request, 'Invalid request')
              return redirect(calendarPage)
                        
                
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

            selected_event.name=name
            selected_event.description=description
            selected_event.start_date=start_date_fixed
            selected_event.end_date=end_date_fixed
            selected_event.start_time=start_time
            selected_event.end_time=end_time
            selected_event.deadline=deadline
            
            selected_event.save()
            
            messages.success(request, 'Event edited successfully')
            return redirect(calendarPage)
        
          else:
            messages.warning(request, 'Invalid request')
            return redirect(calendarPage)
         
        return render(request, 'edit_event.html', context=context_dict)
      
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
      
      if profile.role == "Admin" or profile.role == "Officer":
        has_permission = 1
      else:
        has_permission = 0
    
      characters = list(Character.objects.filter(profile_id=Profile.objects.get(user_id=request.user)).order_by('name'))
      
      event_id = request.GET.get('event_id', -1)
      
      if event_id == -1 or not Event.objects.filter(id=event_id).exists():
        messages.warning(request, 'Event does not exist')
        return redirect(calendarPage)
      
      selected_event = Event.objects.get(id=event_id)
      selected_event_day = ast.literal_eval(selected_event.start_date)[0]
      selected_event_month = ast.literal_eval(selected_event.start_date)[1]
      selected_event_year = ast.literal_eval(selected_event.start_date)[2]
      
      format_start_day = selected_event_day
      fomrat_start_month = selected_event_month
      
      current_status = 0
      current_char_status = "None"
      
      all_participants = Participant.objects.filter(event=selected_event)
      signed_up_participants = Participant.objects.filter(event=selected_event, status_set=1)
      signed_off_participants = Participant.objects.filter(event=selected_event, status_set=2)
      backup_participants = Participant.objects.filter(event=selected_event, status_set=3)
      guest_participants = Participant.objects.filter(event=selected_event, status_set=4)
      confirmed_participants = Participant.objects.filter(event=selected_event, status_set=5)
      
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
        
        if Event.objects.filter(id=event_id).exists():
      
          if 'set_status' in request.POST:
                
            character_name = request.POST.get('character', "-2")
            status_text = request.POST.get('status', "-2")
        
            if character_name == "-2" or status_text == "-2":

              messages.warning(request, 'Invalid request')
              return redirect(calendarPage)
            
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
          
            
            if Character.objects.filter(name__iexact=character_name).exists():
              
              selected_character = Character.objects.get(name=character_name)
              selected_character_profile = selected_character.profile_id
              
              
              if selected_character_profile == profile :
              
            
                participant_own_list = list(Participant.objects.filter(event=selected_event, profile_id=selected_character_profile))
                

                if deadline_over == False:
                
                  if len(participant_own_list) != 0 :
                    
                    current_participant = participant_own_list[0]
                    
                    current_participant.character = selected_character
                    current_participant.status = status_id
                    current_participant.status_set = status_id
                    
                    current_participant.save()
                    
                    messages.success(request, 'Status changed successfully')
                  
                  else:
                    
                    new_participant = Participant(
                        event=selected_event,
                        profile_id=selected_character_profile,
                        character=selected_character,
                        status=status_id,
                        status_set=status_id,
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
            
          elif 'confirm_status' in request.POST:
            
            if profile.role == "Admin" or profile.role == "Officer":
                      
              confirmed_char_list = request.POST.getlist('confirmed_char')
              
              for character_name in confirmed_char_list:
                
                
                if Character.objects.filter(name__iexact=character_name).exists():
                  
                  selected_character = Character.objects.get(name=character_name)
                  selected_character_profile = selected_character.profile_id
                  
                  participant_own_list_2 = list(Participant.objects.filter(event=selected_event, profile_id=selected_character_profile))
                  
                  
                  if len(participant_own_list_2) != 0 :
                    
                    current_participant_2 = participant_own_list_2[0]
                    
                    current_participant_2.character = selected_character
                    current_participant_2.status_set = 5
                    current_participant_2.save()
                    
                    messages.success(request, 'Characters confirmed successfully')  
                    
                    
                  else:
                    messages.warning(request, 'Invalid request')
                    return redirect(calendarPage)
            
            else:
              messages.warning(request, 'Invalid request')
              return redirect(calendarPage)     
                
          elif 'unconfirm_status' in request.POST:
            
            if profile.role == "Admin" or profile.role == "Officer":
                  
              confirmed_char_list = request.POST.getlist('unconfirmed_char')
              
              for character_name in confirmed_char_list:
                
                if Character.objects.filter(name__iexact=character_name).exists():
                  
                  selected_character = Character.objects.get(name__iexact=character_name)
                  selected_character_profile = selected_character.profile_id
                  
                  participant_own_list_3 = list(Participant.objects.filter(event=selected_event, profile_id=selected_character_profile))
                  
                  if len(participant_own_list_3) != 0 :
                    
                    current_participant_3 = participant_own_list_3[0]
                    
                    current_participant_3.character = selected_character
                    current_participant_3.status_set = current_participant_3.status
                    current_participant_3.save()

                    messages.success(request, 'Characters unconfirmed successfully')      
                    
                    
                  else:
                    messages.warning(request, 'Invalid request')
                    return redirect(calendarPage)  
            
            else:
              messages.warning(request, 'Invalid request')
              return redirect(calendarPage)
            
          elif 'all_change_status' in request.POST:
            
            if profile.role == "Admin" or profile.role == "Officer":
              
              changed_char_list = request.POST.getlist('all_char_status')
              
              status_text = request.POST.get('status_all', "-2")
        
              if status_text == "-2":

                messages.warning(request, 'Invalid request')
                return redirect(calendarPage)
              
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
                case "confirmed":
                    status_id = 5

                case _:
                    status_id = 0

              for character_name in changed_char_list:
                
                if Character.objects.filter(name__iexact=character_name).exists():
                  
                  selected_character = Character.objects.get(name__iexact=character_name)
                  selected_character_profile = selected_character.profile_id
                                  
                  participant_own_list = list(Participant.objects.filter(event=selected_event, profile_id=selected_character_profile))
                  
                  if len(participant_own_list) != 0 :                 
                      
                    current_participant = participant_own_list[0]
                    
                    current_participant.character = selected_character
                    current_participant.status_set = status_id
                    
                    current_participant.save()
                    
                    messages.success(request, 'Status set successfully')      

                  else:
                    
                    new_participant = Participant(
                        event=selected_event,
                        profile_id=selected_character_profile,
                        character=selected_character,
                        status=0,
                        status_set=status_id,
                        )
                    
                    new_participant.save()
                    messages.success(request, 'Status set successfully') 
            
            else:
              messages.warning(request, 'Invalid request')
              return redirect(calendarPage)
                      
          elif 'delete_event' in request.POST:
            
            if profile.role == "Admin" or profile.role == "Officer":
            
              selected_event.delete()
              messages.warning(request, 'Event deleted successfully')
              return redirect(calendarPage)
            
            else:
              messages.warning(request, 'Invalid request')
              return redirect(calendarPage)
            
            
          else:
            messages.warning(request, 'Invalid request')
            return redirect(calendarPage)
        
        else:
          messages.warning(request, 'Event does not exist')
          return redirect(calendarPage)
      
      classes = Class.objects.filter().order_by(Lower('name'))
      
      characters_by_class = []
      classes_list = list(classes)
      
      for char_class in classes_list:
        
        chars_mathing_class_list = list(Character.objects.filter(class_name=char_class.name).order_by(Lower('name')))
        
        char_active_list = []
        
        for char in chars_mathing_class_list:
          
          temp_character_profile = char.profile_id
   
          if temp_character_profile.role != "Restricted" and temp_character_profile.role != "Inactive":
          
            char_active_list.append(char)
             
        characters_by_class.append(char_active_list)
         
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
        "confirmed_participants" : confirmed_participants,
        "classes" : classes,
        "characters_by_class" : characters_by_class,
        "deadline_over" : deadline_over,
        "has_permission" :has_permission,
      }    
              
      return render(request, 'event_view.html', context=context_dict)
    
    else:
      logout(request)
      messages.warning(request, 'Account restricted')
      return redirect(index)

  return redirect(index)

def eventListPage(request):
  
  if request.user.is_authenticated:
    
    profile = Profile.objects.get(user_id=request.user)
    user = request.user
      
    if profile.role != "Restricted":
      
      characters = Character.objects.filter(profile_id=Profile.objects.get(user_id=request.user)).order_by('name')
      
      eventsdb = Event.objects.filter()
        
      events = []
      
      for event in eventsdb:
        
        selected_event = event
        selected_event_day = ast.literal_eval(selected_event.start_date)[0]
        selected_event_month = ast.literal_eval(selected_event.start_date)[1]
        selected_event_year = ast.literal_eval(selected_event.start_date)[2]
        
        bg_tz = pytz.timezone('Europe/Sofia')
        BG_time = datetime.datetime.now(bg_tz)
        
        deadline_hour_min = selected_event.deadline.split(":")
        
        deadline_time = bg_tz.localize(datetime.datetime(selected_event_year, selected_event_month, selected_event_day, int(deadline_hour_min[0]), int(deadline_hour_min[1])))
        
        deadline_over = False
        
        if BG_time < deadline_time :
          deadline_over = False
        else:
          deadline_over = True
          
        if deadline_over == False:
        
          current_participant = Participant.objects.filter(event=event, profile_id=profile)
          
          current_date = str(ast.literal_eval(event.start_date)[0]) + "." + str(ast.literal_eval(event.start_date)[1]) + "." + str(ast.literal_eval(event.start_date)[2])
          
          if current_participant.count() > 0:
          
            event_status = current_participant.first().status_set
            
          else:
            
            event_status = 0
            
          event_day = int(ast.literal_eval(event.start_date)[0])
          event_month = int(ast.literal_eval(event.start_date)[1])
          event_year = int(ast.literal_eval(event.start_date)[2])
          
          event_date = datetime.datetime(event_year, event_month, event_day, 12, 00)
          
          event_week_day = event_date.strftime('%A')

          load_event = {
            "event_id": event.pk,
            "eventName" : event.name,
            "start_date" : ast.literal_eval(event.start_date),
            "end_date" : ast.literal_eval(event.end_date),
            "start_time" : event.start_time,
            "end_time": event.end_time,
            "deadline": event.deadline,
            "description": event.description,
            "event_status": event_status,
            "event_date": current_date,
            "week_day": event_week_day
          }
          
          events.append(load_event)
          
          sorted_events = sorted(events, key=custom_sort_key)
          
          events = sorted_events
        
      
      if request.method == 'POST': 
        
        if 'set_multile_status' in request.POST:
          
          character_name = request.POST.get('character', "-2")
          status_text = request.POST.get('status', "-2")
      
          if character_name == "-2" or status_text == "-2":

            messages.warning(request, 'Invalid request')
            return redirect(calendarPage)
          
          else:
            
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
                  
            if Character.objects.filter(name__iexact=character_name).exists():
              
              selected_character = Character.objects.get(name=character_name)
              selected_character_profile = selected_character.profile_id
              
              if selected_character_profile == profile :
                
                event_id_list = request.POST.getlist('event_identifier')
                
                if len(event_id_list) > 0:
                
                  for event_id in event_id_list:
                    
                    if Event.objects.filter(id=event_id).exists():
                      
                      selected_event = Event.objects.get(id=event_id)
                      selected_event_day = ast.literal_eval(selected_event.start_date)[0]
                      selected_event_month = ast.literal_eval(selected_event.start_date)[1]
                      selected_event_year = ast.literal_eval(selected_event.start_date)[2]
                      
                      bg_tz = pytz.timezone('Europe/Sofia')
                      BG_time = datetime.datetime.now(bg_tz)
                      
                      deadline_hour_min = selected_event.deadline.split(":")
                      
                      deadline_time = bg_tz.localize(datetime.datetime(selected_event_year, selected_event_month, selected_event_day, int(deadline_hour_min[0]), int(deadline_hour_min[1])))
                      
                      deadline_over = False
                      
                      if BG_time < deadline_time :
                        deadline_over = False
                      else:
                        deadline_over = True
                        
                      participant_own_list = list(Participant.objects.filter(event=selected_event, profile_id=selected_character_profile))
                      
                      if deadline_over == False:
                    
                        if len(participant_own_list) != 0 :
                          
                          current_participant = participant_own_list[0]
                          
                          current_participant.character = selected_character
                          current_participant.status = status_id
                          current_participant.status_set = status_id
                          
                          current_participant.save()
                  
                        else:
                          
                          new_participant = Participant(
                              event=selected_event,
                              profile_id=selected_character_profile,
                              character=selected_character,
                              status=status_id,
                              status_set=status_id,
                              )
                          
                          new_participant.save()
                      
                      else:
                        messages.success(request, 'Deadline for this event is over')
                        
                      messages.success(request, 'Status set successfully')

                  messages.success(request, 'Status set successfully')

                else:
                  messages.warning(request, 'No event has been selected')  

                return redirect(eventListPage)
              
              else:
                messages.warning(request, 'Invalid request')
                return redirect(eventListPage)  
              
            else:
              messages.warning(request, 'Invalid request')
              return redirect(eventListPage)  
        
        else:
          messages.warning(request, 'Invalid request')
          return redirect(calendarPage)
        
      event_count = len(events)
        
      context_dict = {
          "profile" : profile,
          "user" : user,
          "events" : events,
          "event_count" : event_count,
          "characters" : characters,
      }
        
      return render(request, 'event_list.html', context=context_dict)
    
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
    
        selected_user_username = request.GET.get('user', "-1")
        
        if Profile.objects.filter(profile_username=selected_user_username).exists():  
          selected_profile = Profile.objects.get(profile_username=selected_user_username)
        else:
          # no object satisfying query exists
          messages.warning(request, 'Invalid request')
          return redirect(manageUsersPage) 

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
              
              profile_email = request.POST.get('email', "-1")
              profile_role = request.POST.get('role', "-1")
              profile_password = request.POST.get('password', "-1")    
              selected_user_username = request.GET.get('user', "-1")
          
              if profile_email == "-1" or profile_role == "-1" or profile_password == "-1" or selected_user_username == "-1":
                  
                messages.warning(request, 'Invalid request')
                return redirect(manageUsersPage)
              
              if profile.role != "Admin" and profile_role == "Admin":
                
                messages.warning(request, 'Access denied')
                return redirect(manageUsersPage) 
              
              else:
                
                if User.objects.filter(username__exact=selected_user_username).exists():
                  # at least one object satisfying query exists
                  selected_user = User.objects.get(username__exact=selected_user_username)
                else:
                  # no object satisfying query exists
                  messages.warning(request, 'Invalid request')
                  return redirect(manageUsersPage) 

                if profile_password != "":
                  selected_user.set_password(profile_password)
                  selected_user.save()

                if profile_email != "":
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
          
          old_password = request.POST.get('old_password', "-1")
          
          if old_password == "-1":
              
            messages.warning(request, 'Invalid request')
            return redirect(accountPage)
          
          if user.check_password(old_password):
            
            new_password = request.POST.get('new_password', "-1")
            confirm_password = request.POST.get('confirm_password', "-1")
          
            if new_password == "-1" or confirm_password == "-1":
              
              messages.warning(request, 'Invalid request')
              return redirect(accountPage)
            
            else:
            
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
          
          email = request.POST.get('email', "-1")
          
          if email == "-1":
            
            messages.warning(request, 'Invalid request')
            return redirect(accountPage)
          else:
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

@csrf_exempt
def getTemplateData(request):
  
  if request.user.is_authenticated:
    
    profile = Profile.objects.get(user_id=request.user)
    user = request.user
    
    if profile.role != "Restricted":
      
      if profile.role == "Admin" or profile.role == "Officer":

        if request.method == 'GET':
          template_id = request.GET.get('template_id', -1)
          
          if Template.objects.filter(id=template_id).exists():  
            
            template = Template.objects.get(id=template_id)
            data = {
              'name': template.name,
              'description': template.description,
              'start_time': template.start_time,
              'end_time': template.end_time,
              'deadline': template.deadline
            }
          else:
            
            data = {
              'name': "",
              'description': "",
              'start_time': "21:00",
              'end_time': "00:00",
              'deadline': "16:30"
            }
          
          return JsonResponse(data)
      
      else:
        messages.warning(request, 'Access denied')
        return redirect(homePage)

    else:
      logout(request)
      messages.warning(request, 'Account restricted')
      return redirect(index)
      
  return redirect(index)

def custom_sort_key(event):
  event_date_str = event["event_date"]
  date_parts = [int(part) for part in event_date_str.split(".")]
  event_date = datetime_c(date_parts[2], date_parts[1], date_parts[0])
  return (event_date, event["start_time"], event["eventName"])