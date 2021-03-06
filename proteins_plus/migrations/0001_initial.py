# Generated by Django 3.2.7 on 2022-05-12 10:44

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MockModel',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MockJob',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('status', models.CharField(choices=[('p', 'pending'), ('r', 'running'), ('s', 'success'), ('f', 'failure')], default='p', max_length=1)),
                ('error', models.TextField(null=True)),
                ('error_detailed', models.TextField(null=True)),
                ('date_created', models.DateField(auto_now_add=True)),
                ('date_last_accessed', models.DateField(auto_now=True)),
                ('hash_value', models.CharField(default=None, max_length=256, null=True, unique=True)),
                ('input_model', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='child_mock_job_set', to='proteins_plus.mockmodel')),
                ('output_model', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='parent_mock_job', to='proteins_plus.mockmodel')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
