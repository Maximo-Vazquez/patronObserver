from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="status",
            field=models.CharField(
                choices=[
                    ("preparing", "Preparando pedido"),
                    ("shipped", "En camino"),
                    ("outside", "Afuera"),
                    ("delivered", "Entregado"),
                ],
                default="preparing",
                help_text="Estado actual del pedido mostrado en la interfaz.",
                max_length=20,
            ),
        ),
    ]
