# Generated by Django 3.2.15 on 2022-09-14 19:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipes', '0006_alter_favorite_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShopingCart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shoping_cart', to='recipes.recipe', verbose_name='Рецепт, который добавлен в список покупок')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shoping_cart', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь, который добавляет рецепт в список покупок')),
            ],
        ),
        migrations.AddConstraint(
            model_name='shopingcart',
            constraint=models.UniqueConstraint(fields=('user', 'recipe'), name='unique_chopingcart'),
        ),
    ]