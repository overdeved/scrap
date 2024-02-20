from django.db import models

# Create your models here.
class SearchQuery(models.Model):
    keyword = models.CharField(max_length=120)
    date = models.DateTimeField(auto_now_add=True)




    def __str__(self):
        infor = f'Keyword:{self.keyword} | Date: {self.date} {str(self.pk)}'
        return infor

class SearchResult(models.Model):
    search_query = models.ForeignKey(SearchQuery, on_delete=models.CASCADE, null=True)
    search_id = models.CharField(max_length=20, default='0')
    item_id = models.CharField(max_length=20)
    item_title = models.CharField(max_length=150)
    item_promoted = models.CharField(max_length=20)
    item_ean = models.CharField(max_length=20)
    item_price = models.CharField(max_length=20)
    seller_id = models.CharField(max_length=20)
    seller_name = models.CharField(max_length=20)
    seller_url = models.CharField(max_length=25)
    seller_feedback = models.CharField(max_length=10)
    seller_supperSeller = models.CharField(max_length=10)
    item_best_price_guarantee = models.CharField(max_length=20)
    item_rating = models.CharField(max_length=10)
    item_rating_count = models.CharField(max_length=10)
    item_isSmart = models.CharField(max_length=10)
    item_offers_count = models.CharField(max_length=5)
    item_units_sold = models.CharField(max_length=20)
    item_sales_value = models.CharField(max_length=20)
    item_url = models.CharField(max_length=100)