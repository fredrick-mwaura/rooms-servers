from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Room, Topic, User, Message
from .forms import RoomForm, UserForm
from django.contrib.auth.forms import UserCreationForm


#authentication => session based by default

# Create your views here.

def loginPage(request):

  page = 'login'

  if request.user.is_authenticated:
    return redirect('Home')

  if(request.method == 'POST'):
    username = request.POST.get('username')
    password = request.POST.get('password')

    try:
      user = User.objects.get(username=username)
    except:
      messages.error(request, 'user does not exist!')
    user = authenticate(request, username=username, password=password)
    print(user)
    if user is not None:
      login(request, user)  
      return redirect('update-user')
    else:
      messages.error(request, 'Invalid credentials!') #username or password does not exist
      

  context = {'page': page}
  return render(request, 'base/login_register.html', context)

def logoutUser(request):
  logout(request)
  return redirect('Home')

def registerUser(request):
  form = UserCreationForm()
  context = {'form': form}

  if request.method == 'POST':
    form = UserCreationForm(request.POST)
    if form.is_valid():
      user = form.save(commit=False)
      user.username = user.username.lower()
      user.save()
      login(request, user)
      return redirect('Home')
    else:
      for field, errors in form.errors.items():
        for error in errors:          
          messages.error(request, f"{field.capitalize()}: {error}")
      # messages.error(request, 'An error occured during registration')
  else:
    messages.error(request, 'Error occured - not "POST" boy')    
  return render(request, 'base/login_register.html', context)

def home(request):
  q = request.GET.get('q') if request.GET.get('q') != None else ''

  rooms = Room.objects.filter(
    # searching by 3 different Values
    Q(topic__name__icontains=q) |
    Q(topic__slug__icontains=q) |    
    Q(name__icontains=q) |
    Q(description__icontains=q)
    )

  topics = Topic.objects.all()[0:5]
  room_count = rooms.count()
  room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))

  context = {'rooms': rooms, 'topics': topics, 'room_count': room_count, 'room_messages': room_messages}  
  return render(request, 'base/home.html', context)

def room(request, pk):
  room = Room.objects.get(id=pk)
  room_messages = room.message_set.all()
  participants = room.participants.all()
  if request.method == 'POST':
    message = Message.objects.create(
      user = request.user,
      room = room,
      body = request.POST.get('body')
    )
    room.participants.add(request.user)
    return redirect('room', pk=room.id)
  context = {'room': room, 'room_messages': room_messages, 'participants': participants}    

  return render(request, 'base/room.html', context)

def userProfile(request, pk):
  user = User.objects.get(id=pk)
  rooms = user.room_set.all()
  room_messages = user.message_set.all()
  topics = Topic.objects.all()
  context = {'user': user, 'rooms': rooms, 'topics': topics, 'room_messages': room_messages}
  return render(request, 'base/profile.html', context)

def updateUser(request):
  user = request.user
  form = UserForm(instance=user)
  # print(form)
  if request.method == 'POST':
    form = UserForm(request.POST, request.FILES, instance=user)
    if form.is_valid:
      form.save()
      return redirect('user-profile', pk=user.id)
  return render(request, 'base/update-user.html', {'form':form})
@login_required(login_url='login')
def createRoom(request):
    form =RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
      topic_name = request.POST.get('topic').strip().lower() #normalize to inhibit room duplicates
      topic, created = Topic.objects.get_or_create(
          name__iexact=topic_name,
          defaults={
            'name': topic_name.capitalize()
          }
        )
      
      Room.objects.create(
        host=request.user,
        topic=topic,
        name=request.POST.get('name'),
        description=request.POST.get('description')
      )
      return redirect('Home')

    context = { 'room': room, 'form': form, 'topics': topics, 'mode': 'create' }
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def updateRoom(request, pk):
  room = Room.objects.get(id=pk)
  form = RoomForm(instance=room)
  topics = Topic.objects.all()

  if request.user != room.host:
    return HttpResponse("you a'int allowed here")

  if request.method == 'POST':
    form = RoomForm(request.POST, instance=room)
    topic_name = request.POST.get('topic')
    topic, created = Topic.objects.get_or_create(
      name__iexact=topic_name,
      defaults={
        'name': topic_name.capitalize()
      }
    )
    room.name = request.POST.get('name')
    room.topic = topic
    room.description = request.POST.get('description')
    room.save()
    return redirect('Home')
  context = {'form': form, 'room': room, 'topics': topics, 'mode': 'update'}
  return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def deleteRoom(request, pk):
  room = Room.objects.get(id=pk)

  if request.user != room.host and not request.user.is_superuser:
    return HttpResponse("you a'int allowed here")

  if request.method == 'POST':
    room.delete()
    return redirect('Home')
  return render(request, 'base/delete.html', {'obj': room})


@login_required(login_url='login')
def deleteMessage(request, pk):
  message = Message.objects.get(id=pk)

  if request.user != message.user and not request.user.is_superuser:
    return HttpResponse("you ain't allowed budyy")
  
  if request.method == 'POST':
    message.delete();
    return redirect('Home')
  return render(request, 'base/delete.html', {'obj':message})

def topics(request):
  q = request.GET.get('q') if request.GET.get('q') != None else ''  
  topics = Topic.objects.filter(name__icontains=q)
  for t in topics:
    print(t.slug)
  context = {'topics': topics}  
  return render(request, 'base/topics.html', context)
  
def activity(request):
  room_messages = Message.objects.all()
  context = {
    'room_messages': room_messages,
  }
  return render(request, 'base/activity.html', context)  