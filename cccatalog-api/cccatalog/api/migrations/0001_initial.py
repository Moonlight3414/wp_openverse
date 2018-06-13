# Generated by Django 2.0.5 on 2018-06-05 17:41

from django.conf import settings
import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Favorite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'favorite',
                'ordering': ['-updated_on'],
            },
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('identifier', models.CharField(blank=True, db_index=True, max_length=255, null=True, unique=True)),
                ('perceptual_hash', models.CharField(blank=True, db_index=True, max_length=255, null=True)),
                ('provider', models.CharField(blank=True, db_index=True, max_length=80, null=True)),
                ('source', models.CharField(blank=True, db_index=True, max_length=80, null=True)),
                ('foreign_identifier', models.CharField(blank=True, db_index=True, max_length=80, null=True, unique=True)),
                ('foreign_landing_url', models.CharField(blank=True, max_length=1000, null=True)),
                ('url', models.URLField(max_length=1000, unique=True)),
                ('thumbnail', models.URLField(blank=True, max_length=1000, null=True)),
                ('width', models.IntegerField(blank=True, null=True)),
                ('height', models.IntegerField(blank=True, null=True)),
                ('filesize', models.IntegerField(blank=True, null=True)),
                ('license', models.CharField(max_length=50)),
                ('license_version', models.CharField(blank=True, max_length=25, null=True)),
                ('creator', models.CharField(blank=True, max_length=2000, null=True)),
                ('creator_url', models.URLField(blank=True, max_length=2000, null=True)),
                ('title', models.CharField(blank=True, max_length=2000, null=True)),
                ('tags_list', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=255), blank=True, null=True, size=None)),
                ('last_synced_with_source', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('removed_from_source', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'image',
                'ordering': ['-created_on'],
            },
        ),
        migrations.CreateModel(
            name='ImageTags',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('image', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='api.Image')),
            ],
            options={
                'db_table': 'image_tags',
            },
        ),
        migrations.CreateModel(
            name='List',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=2000)),
                ('creator_displayname', models.CharField(blank=True, max_length=2000, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('is_public', models.BooleanField(default=False)),
                ('slug', models.CharField(blank=True, max_length=255, null=True, unique=True)),
                ('images', models.ManyToManyField(related_name='lists', to='api.Image')),
                ('owner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'list',
                'ordering': ['-updated_on'],
            },
        ),
        migrations.CreateModel(
            name='SyncMetadata',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_sync', models.DateTimeField(default=None, null=True)),
                ('locked', models.BooleanField(default=False)),
                ('postgres_last_id', models.BigIntegerField(default=None, null=True)),
                ('elasticsearch_last_id', models.BigIntegerField(default=None, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('foreign_identifier', models.CharField(blank=True, max_length=255, null=True)),
                ('name', models.CharField(blank=True, max_length=1000, null=True)),
                ('source', models.CharField(blank=True, max_length=255, null=True)),
                ('slug', models.SlugField(blank=True, max_length=255, null=True)),
            ],
            options={
                'db_table': 'tag',
            },
        ),
        migrations.CreateModel(
            name='UserTags',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('image', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_tags', to='api.Image')),
                ('tag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_tags', to='api.Tag')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'user_tags',
            },
        ),
        migrations.AddField(
            model_name='imagetags',
            name='tag',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='api.Tag'),
        ),
        migrations.AddField(
            model_name='image',
            name='tags',
            field=models.ManyToManyField(through='api.ImageTags', to='api.Tag'),
        ),
        migrations.AddField(
            model_name='favorite',
            name='image',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorites', to='api.Image'),
        ),
        migrations.AddField(
            model_name='favorite',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='usertags',
            unique_together={('tag', 'image', 'user')},
        ),
        migrations.AlterUniqueTogether(
            name='list',
            unique_together={('title', 'owner')},
        ),
        migrations.AlterUniqueTogether(
            name='imagetags',
            unique_together={('tag', 'image')},
        ),
        migrations.AlterUniqueTogether(
            name='favorite',
            unique_together={('user', 'image')},
        ),
    ]
