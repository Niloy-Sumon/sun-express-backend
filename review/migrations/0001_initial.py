# Generated by Django 4.2.7 on 2024-01-15 05:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('viewer', '0001_initial'),
        ('article', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('rating', models.CharField(choices=[('⭐', '⭐'), ('⭐⭐', '⭐⭐'), ('⭐⭐⭐', '⭐⭐⭐'), ('⭐⭐⭐⭐', '⭐⭐⭐⭐'), ('⭐⭐⭐⭐⭐', '⭐⭐⭐⭐⭐')], max_length=10)),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='article.article')),
                ('viewer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='viewer.viewer')),
            ],
        ),
    ]
