import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_remove_emailcategory_default_action_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserCustomCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='custom_categories', to=settings.AUTH_USER_MODEL)),
            ],
            options={'unique_together': {('user', 'slug')}},
        ),
        migrations.CreateModel(
            name='ClassificationJob',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('scope', models.CharField(max_length=32)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('running', 'Running'), ('done', 'Done'), ('error', 'Error')], default='pending', max_length=16)),
                ('total', models.IntegerField(default=0)),
                ('processed', models.IntegerField(default=0)),
                ('already_done', models.IntegerField(default=0)),
                ('error_msg', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='classification_jobs', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='classifiedemail',
            name='custom_category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='accounts.usercustomcategory'),
        ),
    ]
