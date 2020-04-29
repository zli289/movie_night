from django.shortcuts import render, redirect
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
from . import models
import imdb

def index(request):
    if not request.session.get('is_login', None):
        return redirect('/login/')
    return redirect('/movie_info/')

def search_movie(request):
    if request.method=="GET":
        title= request.GET.get('movie_name')
        if models.Movie.objects.filter(name__icontains=title).exists():
            m1= models.Movie.objects.filter(name__icontains =title)[0]
            return render(request, 'main/movie_info.html',
            {'movie':m1, 'movie_list':models.Movie.objects.all()})
        else:
            moviesDB= imdb.IMDb()
            movies= moviesDB.search_movie(title)
            movie= moviesDB.get_movie(movies[0].getID())

            m_id= movie.getID()
            m1= models.Movie(m_id=m_id)
            m1.name= movie.get('title',None)
            m1.year=  movie.get('year',None)
            m1.rating= movie.get('rating',None)
            m1.duration= movie.get('runtimes',None)
            m1.cover=movie.get('cover url',None)
            if movie.get('runtimes',None):
                m1.duration= m1.duration[0]
            if movie.get('directors',None):
                m1.director= ', '.join(map(str,movie['directors'])) 
            m1.trailer= 'https://www.imdb.com/title/tt'+m_id+'/videogallery/content_type-trailer/'
            m1.review= 'https://www.imdb.com/title/tt'+m_id+'/reviews/'
            return render(request, 'main/movie_info.html',
            {'movie':m1, 'movie_list':models.Movie.objects.all(), 'record': not models.Movie.objects.filter(name=m1.name).exists()})

def view_movie(request):
    if request.method=="GET":
        movie= models.Movie.objects.get(m_id=request.GET.get('m_id'))
        movie_list= models.Movie.objects.all()
        return render(request, 'main/movie_info.html', locals())
  
def add_movie(request):
    if request.method=="GET":
        m_id=request.GET.get('m_id',None)
        name=request.GET.get('title',None)
        m1= models.Movie(m_id=m_id, name=name)
        m1.director=request.GET.get('director',None)
        m1.year=request.GET.get('year',None)
        m1.duration=request.GET.get('duration',None)
        m1.rating=request.GET.get('rating',None)
        m1.trailer= 'https://www.imdb.com/title/tt'+m_id+'/videogallery/content_type-trailer/'
        m1.review= 'https://www.imdb.com/title/tt'+m_id+'/reviews/'
        m1.cover= request.GET.get('cover',None)
        m1.save()

        return render(request, 'main/movie_info.html',
        {'movie':m1, 'movie_list':models.Movie.objects.all()})

def movie_info(request):
    if request.method=="GET":    
        return render(request, 'main/movie_info.html', {'movie_list':models.Movie.objects.all()})

def vote(request):
    u1= models.User.objects.get(id=request.session.get('user_id',None))
    if request.method=="GET":
        v1= models.Voting.objects.get(id=request.GET.get('voting_id',None))
        m1= models.Movie.objects.get(m_id=request.GET.get('voting_movie',None))
        vote= models.Votes.objects.get(movie=m1, voting=v1)
        vote.count+=1
        vote.save()

        hasvoted= models.HasVoted(user=u1, voting=v1)
        hasvoted.save()

        votes= models.Votes.objects.filter(voting=v1)
        event= models.Event.objects.get(voting=v1)
        all_movie= models.Movie.objects.all()
        return render(request, 'main/event_info.html', 
        {'voting':v1, 'votes':votes, 'status':True, 'hasvoting':True,
        'event':event, 'group':event.group, 'all_movie':all_movie})

def event_info(request):
    u1= models.User.objects.get(id=request.session.get('user_id',None))
    if request.method=="GET":
        group= models.Group.objects.get(id=request.GET.get('group_id1',None)) 
        all_movie= models.Movie.objects.all()
        if request.GET.get('event_id'):
            event= models.Event.objects.get(id=request.GET.get('event_id'))
            if event.voting_set.exists():
                voting= models.Voting.objects.get(event=event)
                votes= models.Votes.objects.filter(voting=voting)
                status= models.HasVoted.objects.filter(user=u1,voting=voting).exists()
        return render(request, 'main/event_info.html', locals())

def add_event(request):
    if request.method=="GET":
        g1= models.Group.objects.get(id=request.GET.get('group_id',None))
        e1= models.Event(name=request.GET.get('event_name',None), group=g1)
        e1.start=request.GET.get('start',None)
        e1.end=request.GET.get('end',None)
        e1.save()
        if request.GET.getlist('hasvoting'):
            v1= models.Voting(event=e1, group=g1)
            v1.save()
            selected_movies= request.GET.getlist('selected_movies')
            for m_id in selected_movies:
                m1= models.Movie.objects.get(m_id=m_id)
                v1.movies.add(m1)
            v1.save()
        else:
            if 'TBD'==request.GET.get('event_movie',None):
                e1.delete()
                message="Please choose a movie or a voting event"
                return render(request, 'main/event_info.html', locals())
            m1= models.Movie.objects.get(m_id=request.GET.get('event_movie',None))
            e1.movie=m1
            e1.save()
        return HttpResponseRedirect('/group_info/')

def group_info(request):
    u1= models.User.objects.get(id=request.session.get('user_id',None))
    group_list= models.Membership.objects.filter(member=u1)

    if request.method=="GET" and request.GET.get('group_id',None):
        g1= models.Group.objects.get(id=request.GET.get('group_id',None))
        membership= models.Membership.objects.get(member=u1, group=g1)
        user_list= models.Membership.objects.filter(group=g1)
        movie_list= models.Movie.objects.all()

        # remove user 
        if request.GET.get('user_id',None):
            u2= models.User.objects.get(id=request.GET.get('user_id',None))
            u2.members.remove(g1)
            u2.save()

    return render(request, 'main/group_info.html', locals())
    
def group_list(request):
    u1= models.User.objects.get(id=request.session.get('user_id',None))
    created= u1.members.filter(membership__title='Moderator')   
    joined= u1.members.filter(membership__title='Member')   
    other=  models.Group.objects.exclude(user=u1) 
    return render(request, 'main/group_list.html', locals())

def create_group(request):
    u1= models.User.objects.get(id=request.session.get('user_id',None))
    if request.method=='GET':
        group_name= request.GET.get('group_name',None)
        new_group= models.Group(name=group_name, moderator= u1.name)
        new_group.save()

        m1= models.Membership(member=u1,group=new_group)
        m1.title= "Moderator"
        m1.save()
    return HttpResponseRedirect('/group_list/')

def join_group(request):
    u1= models.User.objects.get(id=request.session.get('user_id',None))
    if request.method=='GET':
        g1= models.Group.objects.get(id=request.GET.get('group_id',None))
        m1= models.Membership(member=u1,group=g1)
        m1.save()
    return HttpResponseRedirect('/group_list/')

def quit_group(request):
    u1= models.User.objects.get(id=request.session.get('user_id',None))
    if request.method=='GET':
        g1= models.Group.objects.get(id=request.GET.get('group_id',None))
        m1= models.Membership.objects.get(member=u1,group=g1)
        m1.delete()
    return HttpResponseRedirect('/group_list/')

def gentella_html(request):
    context = {}
    # The template to be loaded as per gentelella.
    # All resource paths for gentelella end in .html.

    # Pick out the html file name from the url. And load that template.
    load_template = request.path.split('/')[-1]
    template = loader.get_template('app/' + load_template)
    return HttpResponse(template.render(context, request))

def login(request):
    if request.session.get('is_login',None):
        return redirect('/index/')
    
    if request.method == "POST":
        message= 'Please try again.'
        username= request.POST.get('username')
        password= request.POST.get('password')
        try:
            user= models.User.objects.get(name=username)
        except:
            message= 'User does not exist.'
            return render(request, 'login/login.html',locals())
            
        if user.password== password:
            request.session['is_login']= True
            request.session['user_id']= user.id
            request.session['user_name']= user.name
            return redirect('/index/')
        else:
            message= 'Incorrect password.'
            return render(request, 'login/login.html',locals())
    else:
        return render(request, 'login/login.html',locals())   
    return render(request, 'login/login.html',locals())

def register(request):
    if request.session.get('is_login',None):
        return redirect('/index/')  
    
    if request.method== "POST":
        message= 'Plase try again'
        username= request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        email = request.POST.get('email')

        if password1!= password2:
            message= 'Passwords do not match'
            return render(request, 'login/register.html', locals())
        else:
            same_name_user= models.User.objects.filter(name=username)
            if same_name_user:
                message= 'Username already exists'
                return render(request, 'login/register.html', locals())
            same_email_user= models.User.objects.filter(name=email)
            if same_email_user:
                message= 'Email has been registered'
                return render(request, 'login/register.html', locals())
                
            new_user= models.User(name= username, password= password1, email= email)
            new_user.save()
            message= 'registration success'
            return redirect('/login/')
    else:
        return render(request, 'login/register.html',locals())


def logout(request):
    if not request.session.get('is_login',None):
        return redirect('/login/')
    request.session.flush()
    return redirect('/login/')



