from django.contrib import admin
from topology.models import Province, Division, District, Tehsil, Mauza

@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):
  list_display = ['name', 'code', 'database_alias']
  
@admin.register(Division)
class DivisionAdmin(admin.ModelAdmin):
  list_display = ['name', 'code', 'province']
  
@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
  list_display = ['name', 'code', 'division']
  
@admin.register(Tehsil)
class TehsilAdmin(admin.ModelAdmin):
  list_display = ['name', 'code', 'district']
  
@admin.register(Mauza)
class MauzaAdmin(admin.ModelAdmin):
  list_display = ['name', 'code', 'tehsil']