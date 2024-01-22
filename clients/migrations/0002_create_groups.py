# Generated by Django 4.2.9 on 2024-01-21 18:39

from django.db import migrations


def create_group(apps, schema_editor):
    Permission = apps.get_model('auth', 'Permission')
    group = apps.get_model('auth', 'Group').objects.create(name='Admins')
    codenames = [
        'add_product',
        'change_product',
        'delete_product',
        'view_product',
        'add_slot',
        'change_slot',
        'delete_slot',
        'view_slot',
        'add_vmachine',
        'change_vmachine',
        'delete_vmachine',
        'view_vmachine',
        'add_card',
        'change_card',
        'delete_card',
        'view_card',
        'view_transaction',
        'add_user',
        'change_user',
        'delete_user',
        'view_user'
    ]
    group.permissions.set(Permission.objects.filter(codename__in=codenames))


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_group)
    ]
