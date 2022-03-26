# Generated by Django 3.2.7 on 2021-11-25 09:19

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('molecule_handler', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AtomScores',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('scores', models.JSONField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='EdiaJob',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('status', models.CharField(choices=[('p', 'pending'), ('r', 'running'), ('s', 'success'), ('f', 'failure')], default='p', max_length=1)),
                ('error', models.TextField(null=True)),
                ('error_detailed', models.TextField(null=True)),
                ('date_created', models.DateField(auto_now_add=True)),
                ('date_last_accessed', models.DateField(auto_now=True)),
                ('hash_value', models.CharField(default=None, max_length=256, null=True, unique=True)),
                ('density_file_pdb_code', models.CharField(max_length=4, null=True)),
                ('atom_scores', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='edia_job', to='ediascorer.atomscores')),
                ('electron_density_map', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='edia_job', to='molecule_handler.electrondensitymap')),
                ('input_protein', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='child_edia_job_set', to='molecule_handler.protein')),
                ('output_protein', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='parent_edia_job', to='molecule_handler.protein')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]