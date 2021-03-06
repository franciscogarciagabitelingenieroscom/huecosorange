# Generated by Django 2.1 on 2018-10-17 14:32

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('actuaciones', '0003_auto_20181017_1532'),
    ]

    operations = [
        migrations.AlterField(
            model_name='actuacion',
            name='aaii_por',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='actuaciones_aaii_realizadas', to=settings.AUTH_USER_MODEL, to_field='username'),
        ),
        migrations.AlterField(
            model_name='actuacion',
            name='preparado_por',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='actuaciones_preparadas', to=settings.AUTH_USER_MODEL, to_field='username'),
        ),
        migrations.AlterField(
            model_name='actuacion',
            name='replanteado_por',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='actuaciones_replanteadas', to=settings.AUTH_USER_MODEL, to_field='username'),
        ),
    ]
