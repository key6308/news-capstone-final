from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings
from django.db.models import Q


class Migration(migrations.Migration):
    dependencies = [
        ('news', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='publisher',
            name='editors',
            field=models.ManyToManyField(blank=True, related_name='edited_publishers', to='news.user'),
        ),
        migrations.AddField(
            model_name='publisher',
            name='journalists',
            field=models.ManyToManyField(blank=True, related_name='journalist_publishers', to='news.user'),
        ),
        migrations.AddField(
            model_name='user',
            name='subscribed_publishers',
            field=models.ManyToManyField(blank=True, related_name='subscriber_users', to='news.publisher'),
        ),
        migrations.AddField(
            model_name='user',
            name='subscribed_journalists',
            field=models.ManyToManyField(blank=True, related_name='journalist_subscribers', to='news.user', symmetrical=False),
        ),
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=250)),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('approved', models.BooleanField(default=False)),
                ('author', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='independent_articles', to='news.user')),
                ('publisher', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='articles', to='news.publisher')),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='Newsletter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=250)),
                ('description', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='newsletters', to='news.user')),
                ('articles', models.ManyToManyField(blank=True, related_name='newsletters', to='news.article')),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='ApprovedArticleLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('article_title', models.CharField(max_length=250)),
                ('approved_at', models.DateTimeField(auto_now_add=True)),
                ('source', models.CharField(default='internal approval workflow', max_length=100)),
                ('article', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='news.article')),
            ],
        ),
        migrations.AddConstraint(
            model_name='article',
            constraint=models.CheckConstraint(
                condition=(Q(author__isnull=False, publisher__isnull=True) | Q(author__isnull=True, publisher__isnull=False)),
                name='article_exactly_one_owner',
            ),
        ),
    ]
