# Generated manually for adding account, status and descricao fields

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_alter_account_id_conta'),
        ('resources', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='resource',
            name='account',
            field=models.ForeignKey(
                default='default-account',
                help_text='Conta cloud onde o recurso está hospedado',
                on_delete=django.db.models.deletion.CASCADE,
                to='accounts.account',
                verbose_name='Conta Cloud'
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='resource',
            name='status',
            field=models.IntegerField(
                choices=[(0, 'Ativo'), (1, 'Inativo'), (2, 'Em Manutenção')],
                default=0,
                verbose_name='Status'
            ),
        ),
        migrations.AddField(
            model_name='resource',
            name='descricao',
            field=models.TextField(
                blank=True,
                null=True,
                verbose_name='Descrição'
            ),
        ),
        migrations.AlterModelOptions(
            name='resource',
            options={
                'ordering': ['-data_cad'],
                'verbose_name': 'Recurso',
                'verbose_name_plural': 'Recursos'
            },
        ),
    ] 