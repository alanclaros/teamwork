from django.urls import path
from pages.views import notificaciones_pagina, index

urlpatterns = [
    path('', index, name='index'),

    # path('productosinicio/', views.productos_inicio, name='productos_inicio'),
    # path('sucursalesempresa/', views.sucursales_empresa, name='sucursales_empresa'),
    # path('acercade/', views.acerca_de, name='acerca_de'),
    # path('contactenos/', views.contactenos, name='contactenos'),
    # path('cambiarpassword/', views.cambiar_password, name='cambiar_password'),
    # path('carrito/', views.carrito, name='carrito'),
    path('notificacionespagina/', notificaciones_pagina, name='notificaciones_pagina'),

    # path('without_permission', views.without_permission, name='without_permission'),
    # path('internal_error', views.internal_error, name='internal_error'),
]
