# Generated by Django 5.1.5 on 2025-03-10 18:20

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loja', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameField(
            model_name='pedido',
            old_name='data_criacao',
            new_name='criado_em',
        ),
        migrations.AddField(
            model_name='pedido',
            name='usuario',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='itempedido',
            name='pedido',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='loja.pedido'),
        ),
        migrations.AlterField(
            model_name='pedido',
            name='status',
            field=models.CharField(choices=[('pendente', 'Pendente'), ('pago', 'Pago'), ('cancelado', 'Cancelado')], default='pendente', max_length=10),
        ),
        migrations.AlterField(
            model_name='pedido',
            name='total',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
    ]
