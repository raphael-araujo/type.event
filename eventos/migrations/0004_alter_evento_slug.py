# Generated by Django 4.2 on 2023-04-14 21:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eventos', '0003_alter_evento_participantes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='evento',
            name='slug',
            field=models.SlugField(unique=True),
        ),
    ]
