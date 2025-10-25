"""Migración inicial que crea el modelo de pedido."""

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Order",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("customer_name", models.CharField(help_text="Nombre de la clienta que recibirá las notificaciones.", max_length=100)),
                ("status", models.CharField(choices=[("preparing", "Preparando pedido"), ("shipped", "En camino"), ("delivered", "Entregado")], default="preparing", help_text="Estado actual del pedido mostrado en la interfaz.", max_length=20)),
                ("created_at", models.DateTimeField(auto_now_add=True, help_text="Marca temporal del momento en el que se creó el pedido.")),
                ("updated_at", models.DateTimeField(auto_now=True, help_text="Marca temporal de la última actualización del pedido.")),
            ],
            options={
                "ordering": ("-created_at",),
                "verbose_name": "Pedido",
                "verbose_name_plural": "Pedidos",
            },
        ),
    ]
