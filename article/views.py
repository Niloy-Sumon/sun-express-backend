from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import viewsets
from . import models
from . import serializers
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string
from rest_framework.response import Response
from rest_framework import filters
from rest_framework import generics
from . import forms
from . import models
from editor.models import Editor
from django.views.generic import DetailView
from django.db.models import Avg
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
# Create your views here.
def send_transaction_email(user, amount, subject, template):
        message = render_to_string(template, {
            'user' : user,
            'amount' : amount,
        })
        send_email = EmailMultiAlternatives(subject, '', to=[user.email])
        send_email.attach_alternative(message, "text/html")
        send_email.send()

class ArticleViewSet(viewsets.ModelViewSet):
    queryset = models.Article.objects.all()
    serializer_class =  serializers.ArticleSerializer
    filter_backends = [filters.SearchFilter]
    # print(filter_backends)
    # search_fields = ['headline', 'body', 'category__name', 'editor__user']
    search_fields = [ 'category__name', 'category__slug', 'ratings']
    

class articleForSpecific(filters.BaseFilterBackend):
    def filter_queryset(self, request, query_set, view):
        article_id = request.query_params.get("article_id")
        if article_id:
            return query_set.filter(article_id = article_id)
        return query_set
@method_decorator(login_required, name='dispatch')
class DetailArticleView(DetailView):
    model = models.Article
    pk_url_kwarg = 'id'
    template_name = 'article_details.html'
    def post(self, request, *args, **kwargs):
        comment_form = forms.CommentForm(data=self.request.POST)
        post = self.get_object()
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.save()
            
        return self.get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.object
        comments = post.comments.all()
        comment_form = forms.CommentForm()

        # Calculate the average rating
        average_rating = comments.aggregate(Avg('rating'))['rating__avg']

        context['comments'] = comments
        context['comment_form'] = comment_form
        context['average_rating'] = round(average_rating, 2) if average_rating else None
        return context

# @method_decorator(login_required, name='dispatch')
# class DetailArticleView(DetailView):
#     model = models.Article
#     pk_url_kwarg = 'id'
#     template_name = 'article_details.html'

#     def post(self, request, *args, **kwargs):
#         comment_form = forms.CommentForm(data=self.request.POST)
#         post = self.get_object()

#         if comment_form.is_valid():
#             new_comment = comment_form.save(commit=False)
#             new_comment.post = post
#             new_comment.save()

#             # Calculate the average rating
#             comments = post.comments.all()
#             average_rating = comments.aggregate(Avg('rating'))['rating__avg']

#             # Send email only if there are comments and the average rating is not None
#             if comments.exists() and average_rating is not None:
#                 send_transaction_email(
#                     request.user,
#                     average_rating,
#                     "Rating Update",
#                     "rating_update_email_template.html"
#                 )

#         return self.get(request, *args, **kwargs)

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         post = self.object
#         comments = post.comments.all()
#         comment_form = forms.CommentForm()

#         # Calculate the average rating
#         average_rating = comments.aggregate(Avg('rating'))['rating__avg']

#         context['comments'] = comments
#         context['comment_form'] = comment_form
#         context['average_rating'] = round(average_rating, 2) if average_rating else None
#         return context
# class ReviewCreateView(generics.CreateAPIView):
#     queryset = models.Review.objects.all()
#     serializer_class = serializers.ReviewSerializer

class ReviewViewset(viewsets.ModelViewSet):
    
    queryset = models.Review.objects.all()
    serializer_class = serializers.ReviewSerializer
    # filter_backends = [filters.SearchFilter]
    filter_backends = [filters.SearchFilter,articleForSpecific]
    search_fields = ['rating']

    # def list(self, request, *args, **kwargs):
    #     for review in self.get_queryset():
    #         viewer_email = review.viewer.user
    #         email_subject = "Review"
    #         email_body = render_to_string('review_email.html')
    #         email = EmailMultiAlternatives(email_subject , '', to=[viewer_email.email])
    #         email.attach_alternative(email_body, "text/html")
    #         email.send()
    #         return Response("Check your mail for confirmation")
    #     return super().list(request, *args, **kwargs)
@login_required
def add_article(request):
    if request.method == 'POST':
        post_form = forms.AritcleForm(request.POST)
        if post_form.is_valid():
            editor_instance, created = Editor.objects.get_or_create(user=request.user)
            post_form.instance.editor = editor_instance
            post_form.save()
            return redirect('add_article')
    else:
        post_form = forms.AritcleForm()
    return render(request, 'add_article.html', {'form': post_form})
@login_required
def edit_article(request, id):
    post = get_object_or_404(models.Article, pk=id) 
    post_form = forms.AritcleForm(instance=post)

    if request.method == 'POST':
        post_form = forms.AritcleForm(request.POST, instance=post)
        if post_form.is_valid():
            # Ensure the Editor instance exists for the current user
            editor_instance, created = Editor.objects.get_or_create(user=request.user)
            post_form.instance.editor = editor_instance
            post_form.save()
            return redirect('homepage')

    return render(request, 'edit_article.html', {'form': post_form, 'post': post})
# def edit_article(request, id):
#     article = models.Article.objects.get(pk=id) 
#     article_form = forms.AritcleForm(instance=article)
#     if request.method == 'POST':
#         article = forms.AritcleForm(request.POST, instance=article) 
#         if article_form.is_valid():
#             article_form.save() 
#             return redirect('homepage')
    
#     return render(request, 'add_article.html', {'form' : article_form})

def delete_article(request, id):
    article = models.Article.objects.get(pk=id) 
    article.delete()
    return redirect('homepage')