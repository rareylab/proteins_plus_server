# Generated by Django 3.2.7 on 2021-11-25 09:19

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ElectronDensityMap',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('file', models.FileField(upload_to='density_files/')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Protein',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('pdb_code', models.CharField(max_length=4, null=True)),
                ('uniprot_code', models.CharField(max_length=10, null=True)),
                ('file_type', models.CharField(default='pdb', max_length=3)),
                ('file_string', models.TextField()),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_last_accessed', models.DateTimeField(auto_now=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PreprocessorJob',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('status', models.CharField(choices=[('p', 'pending'), ('r', 'running'), ('s', 'success'), ('f', 'failure')], default='p', max_length=1)),
                ('error', models.TextField(null=True)),
                ('error_detailed', models.TextField(null=True)),
                ('date_created', models.DateField(auto_now_add=True)),
                ('date_last_accessed', models.DateField(auto_now=True)),
                ('hash_value', models.CharField(default=None, max_length=256, null=True, unique=True)),
                ('protein_name', models.CharField(max_length=255)),
                ('pdb_code', models.CharField(max_length=4, null=True)),
                ('uniprot_code', models.CharField(max_length=10, null=True)),
                ('protein_string', models.TextField(null=True)),
                ('protein_file_type', models.CharField(default='pdb', max_length=3)),
                ('ligand_string', models.TextField(null=True)),
                ('ligand_file_type', models.CharField(default='sdf', max_length=3)),
                ('output_protein', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='parent_preprocessor_job', to='molecule_handler.protein')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Ligand',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('file_type', models.CharField(default='sdf', max_length=3)),
                ('file_string', models.TextField()),
                ('image', models.ImageField(blank=True, null=True, upload_to='ligands/')),
                ('protein', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='molecule_handler.protein')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
