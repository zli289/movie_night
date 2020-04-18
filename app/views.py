from django.shortcuts import render, redirect
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
from . import models, forms
import imdb

def index(request):
    if not request.session.get('is_login', None):
        return redirect('/login/')
    return render(request, 'app/movie_info.html')

def search_movie(request):
    if request.method=="GET":
        title= request.GET.get('movie_name')
        if models.Movie.objects.filter(name=title).exists():
            m1= models.Movie.objects.get(name=title)
            return render(request, 'app/movie_info.html',
            {'movie':m1, 'movie_list':models.Movie.objects.all(), 'record':True})
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
            if m1.duration:
                m1.duration= m1.duration[0]
            m1.director= ', '.join(map(str,movie['directors'])) 
            m1.trailer= 'https://www.imdb.com/title/tt'+m_id+'/videogallery/content_type-trailer/'
            m1.review= 'https://www.imdb.com/title/tt'+m_id+'/reviews/'

            return render(request, 'app/movie_info.html',
            {'movie':m1, 'movie_list':models.Movie.objects.all(),  
            'record': models.Movie.objects.filter(name=m1.name).exists()})

def view_movie(request):
    if request.method=="GET":
        m1= models.Movie.objects.get(m_id=request.GET.get('m_id'))
        return render(request, 'app/movie_info.html',
        {'movie':m1, 'movie_list':models.Movie.objects.all(), 'record':True})
  
def add_movie(request):
    if request.method=="GET":
        m_id=request.GET.get('m_id',None)
        name=request.GET.get('title',None)
        director=request.GET.get('director',None)
        year=request.GET.get('year',None)
        duration=request.GET.get('duration',None)
        rating=request.GET.get('rating',None)
        trailer= 'https://www.imdb.com/title/tt'+m_id+'/videogallery/content_type-trailer/'
        review= 'https://www.imdb.com/title/tt'+m_id+'/reviews/'

        m1= models.Movie(m_id=m_id, name=name, director=director,
        year=year, duration=duration, rating=rating, trailer=trailer, review=review)
        m1.save()

        return render(request, 'app/movie_info.html',
        {'movie':m1, 'movie_list':models.Movie.objects.all(), 'record':True})

def movie_info(request):
    if request.method=="GET":    
        return render(request, 'app/movie_info.html', {'movie_list':models.Movie.objects.all()})

def voting(request):
    u1= models.User.objects.get(id=request.session.get('user_id',None))
    if request.method=="GET":
        v1= models.Voting.objects.get(id=request.GET.get('voting_id',None))
        votes= models.Votes.objects.filter(voting=v1)
        status= models.HasVoted.objects.filter(user=u1,voting=v1).exists()
        return render(request, 'app/voting.html', {'voting':v1, 'votes':votes, 'status':status})
    return render(request, 'app/voting.html')

def vote(request):
    u1= models.User.objects.get(id=request.session.get('user_id',None))
    if request.method=="GET":
        v1= models.Voting.objects.get(id=request.GET.get('voting_id',None))
        m1= models.Movie.objects.get(m_id=request.GET.get('movie_id',None))
        vote= models.Votes.objects.get(movie=m1, voting=v1)
        vote.count+=1
        vote.save()
        hasvoted= models.HasVoted(user=u1, voting=v1)
        hasvoted.save()
        votes= models.Votes.objects.filter(voting=v1)
        return render(request, 'app/voting.html', {'voting':v1, 'votes':votes, 'status':True})

def event_info(request):
    u1= models.User.objects.get(id=request.session.get('user_id',None))
    if request.method=="GET":
        g1= models.Group.objects.get(id=request.GET.get('group_id1',None)) 
        all_movie= models.Movie.objects.all()
        if request.GET.get('event_id'):
            e1= models.Event.objects.get(id=request.GET.get('event_id'))
            hasvoting= models.Voting.objects.filter(event=e1).exists()
            return render(request, 'app/event_info.html',{'group':g1, 'event':e1, 'hasvoting':hasvoting, 'all_movie':all_movie} )
        return render(request, 'app/event_info.html',{'group':g1, 'event':None, 'all_movie':all_movie} )

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
            m1= models.Movie.objects.get(m_id=request.GET.get('movie_id',None))
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

        return render(request, 'app/group_info.html',
        {'group_list': group_list, 'membership': membership, 'user_list': user_list, 'movie_list': movie_list})
    return render(request, 'app/group_info.html',{'group_list': group_list})
    
def group_list(request):
    u1= models.User.objects.get(id=request.session.get('user_id',None))
    created= models.Membership.objects.filter(member=u1,title='Moderator')
    joined= models.Membership.objects.filter(member=u1,title='Member')
    other=  models.Group.objects.exclude(user=u1) 
    group_list={'created': created, 'joined':joined, 'other':other}
    return render(request, 'app/group_list.html', group_list)

def create_group(request):
    u1= models.User.objects.get(id=request.session.get('user_id',None))
    if request.method=='GET':
        group_name= request.GET.get('group_name',None)
        new_group= models.Group(name=group_name)
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
        login_form= forms.UserForm(request.POST)
        message= 'Please try again.'
        if login_form.is_valid():
            username= login_form.cleaned_data.get('username')
            password= login_form.cleaned_data.get('password')
            try:
                user= models.User.objects.get(name=username)
            except:
                message= 'User does not exist.'
                return render(request, 'back/login.html')
            
            if user.password== password:
                request.session['is_login']= True
                request.session['user_id']= user.id
                request.session['user_name']= user.name
                return redirect('/index/')
            else:
                message= 'Incorrect password.'
                return render(request, 'back/login.html',locals())
        else:
            return render(request, 'back/login.html',locals())
    
    login_form= forms.UserForm()
    return render(request, 'back/login.html',locals())

def register(request):
    if request.session.get('is_login',None):
        return redirect('/index/')
    
    if request.method== "POST":
        register_form= forms.RegisterForm(request.POST)
        message= 'Plase try again'
        if register_form.is_valid():
            username= register_form.cleaned_data.get('username')
            password1 = register_form.cleaned_data.get('password1')
            password2 = register_form.cleaned_data.get('password2')
            email = register_form.cleaned_data.get('email')

            if password1!= password2:
                message= 'Passwords do not match'
                return render(request, 'back/register.html', locals())
            else:
                same_name_user= models.User.objects.filter(name=username)
                if same_name_user:
                    message= 'Username already exists'
                    return render(request, 'back/register.html', locals())
                same_email_user= models.User.objects.filter(name=email)
                if same_email_user:
                    message= 'Email has been registered'
                    return render(request, 'back/register.html', locals())
                
                new_user= models.User(name= username, password= password1, email= email)
                new_user.save()
                return redirect('/login/')
        else:
            return render(request, 'back/register.html',locals())
    register_form= forms.RegisterForm()
    return render(request, 'back/register.html',locals())

def logout(request):
    if not request.session.get('is_login',None):
        return redirect('/login/')
    request.session.flush()
    return redirect('/login/')



