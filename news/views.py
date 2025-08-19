from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .forms import ArticleForm, CategoryForm
from .models import Article, Category
from django.contrib.auth.decorators import login_required


# --- Artikel ---
@login_required
def create_article(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('new_list')
    else:
        form = ArticleForm()

    categories = Category.objects.all()
    category_list = Category.objects.all()

    category_form = CategoryForm()

    return render(request, 'news/create_article.html', {
        'form': form,
        'categories': categories,
        'category_form': category_form,
        'category_list': category_list,
    })



def article_detail(request, pk):
    article = get_object_or_404(Article, pk=pk)
    article.views += 1
    article.save()
    return render(request, 'news/article_detail.html', {'article': article})


def news_list(request):
    articles = Article.objects.all().order_by('-created_at')

    paginator = Paginator(articles, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    popular_articles = Article.objects.order_by('-views')[:5]
    categories = Category.objects.all()

    context = {
        'page_obj': page_obj,
        'popular_articles': popular_articles,
        'categories': categories,
    }
    return render(request, 'news/news_list.html', context)


# --- Category (AJAX) ---
@login_required
@csrf_exempt
def create_category_ajax(request):
    if request.method == "POST":
        name = request.POST.get("name")
        if name:
            category = Category.objects.create(name=name)
            return JsonResponse({
                "success": True,
                "id": category.id,
                "name": category.name
            })
    return JsonResponse({"success": False})

# --- Hapus Artikel ---
@login_required
def delete_article(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if request.method == "POST":
        article.delete()
        return redirect('new_list')
    return render(request, 'news/confirm_delete.html', {'object': article, 'type': 'Artikel'})

# --- Hapus Kategori ---
@login_required
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    return redirect('create_article')
