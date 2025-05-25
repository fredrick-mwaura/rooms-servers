from django.shortcuts import render, redirect
from django.db.models import Q
from .models import Room, Topic
from .forms import RoomForm

#authentication => session based by default

# Create your views here.

# rooms = [
#   { 'id':1, 'name': 'lets learn django bruv'  },
#   { 'id':2, 'name': 'Design with me'  },
#   { 'id':3, 'name': 'lets learn nodejs bruv'  }
# ]

def home(request):
  q = request.GET.get('q') if request.GET.get('q') != None else ''

  rooms = Room.objects.filter(
    # searching by 3 different Values
    Q(topic__name__icontains=q) |
    Q(name__icontains=q) |
    Q(description__icontains=q)
    )

  topics = Topic.objects.all()
  room_count = rooms.count()

  context = {'rooms': rooms, 'topics': topics, 'room_count': room_count}  
  return render(request, 'base/home.html', context)

def room(request, pk):
  room = Room.objects.get(id=pk)
  # for i in rooms:
  #   if i['id'] == int(pk):
  #     room = i
  context = {'room': room}    

  return render(request, 'base/room.html', context)

def createRoom(request):
    if request.method == 'POST':
      form = RoomForm(request.POST)
      if form.is_valid():
        print(request.POST)
        form.save()
        return redirect('Home')
      else:
        print("Form is not valid:", form.errors)
    else:
      form = RoomForm()

    context = { 'form': form }
    return render(request, 'base/room_form.html', context)

def updateRoom(request, pk):
  room = Room.objects.get(id=pk)
  form = RoomForm(instance=room)

  if request.method == 'POST':
    form = RoomForm(request.POST, instance=room)
    if form.is_valid():
      form.save()
      print(request.POST)
      return redirect('Home')
  
  

  context = {'room': form}
  return render(request, 'base/room_form.html', context)

def deleteRoom(request, pk):
  room = Room.objects.get(id=pk)

  if request.method == 'POST':
    room.delete()
    return redirect('Home')
  return render(request, 'base/delete.html', {'obj': room})


#22517