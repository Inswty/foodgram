import csv
import os

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    """Команда загрузки данных из CSV файлов."""

    help = 'Загружает данные из CSV файла в базу данных'

    def add_arguments(self, parser):
        parser.add_argument(
            '--data-dir', type=str, default='./data',
            help='Путь к директории с CSV файлами. По умолчанию: /data'
        )

    def handle(self, *args, **options):
        """Основной метод импорта данных."""
        self.stdout.write(self.style.SUCCESS(
            'Начало загрузки данных из CSV...')
        )
        models_config = {
            'ingredients.csv': Ingredient,
        }
        # Получаем путь к папке с данными через аргументы
        data_dir = options['data_dir']
        for filename, model in models_config.items():
            file_path = os.path.join(data_dir, filename)
            if not os.path.exists(file_path):
                self.stdout.write(
                    self.style.WARNING(f'Файл {filename} не найден!')
                )
                continue
            with open(file_path, encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                objects_to_create = []
                for row in reader:
                    if len(row) >= 2:  # Проверяем, что есть оба значения
                        name = row[0].strip()
                        measurement_unit = row[1].strip()
                        if name:  # Пропускаем пустые строки
                            objects_to_create.append(
                                Ingredient(
                                    name=name,
                                    measurement_unit=measurement_unit
                                )
                            )
                if objects_to_create:
                    Ingredient.objects.bulk_create(
                        objects_to_create, ignore_conflicts=True
                    )
        self.stdout.write(self.style.SUCCESS('Загрузка данных завершена!'))
