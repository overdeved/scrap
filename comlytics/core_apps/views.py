from django.http import HttpResponseRedirect
from django.shortcuts import render, HttpResponse

from .forms import QuerryForm
from .scanner import engine
from .models import SearchResult, SearchQuery

# Create your views here.
def index(request):
    rep = 'This is index page.'
 #   return HttpResponse(rep)
    return render(request, 'core_apps/index.html')


def scanner(request):
    if request.method == 'POST':
        form = QuerryForm(request.POST)
        if form.is_valid():
            keyword = form.cleaned_data['keyword']
            pages = form.cleaned_data['pages']

            engine(keyword,pages)
            last_search = SearchQuery.objects.order_by('pk').last()


            if last_search:
                search_result = SearchResult.objects.filter(search_query=last_search.pk)
                found_offers = len(search_result)
                return render(request, 'core_apps/scanner.html', {'search_result': search_result, 'keyword': keyword, 'last_search': last_search.pk, 'found_offers': found_offers})

    else:
        form = QuerryForm()

    return render(request, 'core_apps/scanner.html', {'form': form})

def download_scanner_results(request):

    queryset = SearchResult.objects.filter(search_query=last_search.pk)
    csv_content = generate_csv_content(queryset)

    response = HttpResponse(csv_content, content_type='text/csv')
    respone['Content-Disposition'] = 'attachment: filename="download.csv"'
    return response
