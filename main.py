import hashlib
import os  # для отображения содержимого директории
import shutil
import sys  # sys нужен для передачи argv в QApplication
import time

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMessageBox

import control  # конвертированный файл дизайна


class ExampleApp(QtWidgets.QMainWindow, control.Ui_MainWindow):
    def __init__(self):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле control.py
        super().__init__()
        self.setupUi(self)  # Это нужно для инициализации дизайна
        self.btnChoosedir.clicked.connect(
            self.choose_dir)  # инициализация для метода по нажатию кнопки "Добавить каталог"
        self.btnChoosefile.clicked.connect(
            self.choose_file)  # инициализация для метода по нажатию кнопки "Добавить файлы"
        self.btnDel.clicked.connect(self.delete_item)  # инициализация для метода по нажатию кнопки "Удалить файлы"
        self.btnControl.clicked.connect(
            self.control_files)  # инициализация для метода по нажатию кнопки "Добавить на КЦ"
        self.timer = QTimer()
        self.btnControl.clicked.connect(self.start_timer)  # Запуск таймера по нажатию кнопки "Добавить на КЦ"
        self.timer.timeout.connect(self.check_files)  # подключили таймер к методу проверить КЦ
        self.timer.setInterval(60000)
        self.pushButton_3.setEnabled(False)
        self.pushButton_3.clicked.connect(self.check_files)  # инициализация для метода по нажатию кнопки "Проверить КЦ"
        self.btnChoosefile_2.setEnabled(False)
        self.btnChoosefile_2.clicked.connect(self.path_dir_choose)  # инициализация для метода по нажатию кнопки
        # "Выбрать каталог"
        self.btnfile_backup.setEnabled(False)
        self.btnfile_backup.clicked.connect(
            self.path_file_choose)  # инициализация для метода по нажатию кнопки "Файл (backup)"
        self.btndir_backup.setEnabled(False)
        self.btndir_backup.clicked.connect(
            self.path_dir2_choose)  # инициализация для метода по нажатию кнопки "Каталог (backup)"
        self.btnRecovery.setEnabled(False)
        self.btnRecovery.clicked.connect(self.recovery_files)  # инициализация для метода по нажатию кнопки
        # "Восстановить"
        self.pushButton.setEnabled(False)
        self.pushButton.clicked.connect(self.stop_timer)  # инициализация для метода по нажатию кнопки "Остановить проверку КЦ"

    # Функция для выбора каталога
    def choose_dir(self):
        path = '/home/spi_729-1/Документы'  # директория с тестовым каталогом
        directory = QtWidgets.QFileDialog.getExistingDirectory(self, "Выберите папку", path)
        # открыть диалог выбора директории и установить значение переменной
        # равной пути к выбранной директории

        # перебор элементов в окне выбора файлов
        item_text_list = [str(self.listWidgetChoose.item(i).text()) for i in range(self.listWidgetChoose.count())]
        path_icon_dir = './icons/dir.png'  # путь к иконке каталога
        path_icon_file = './icons/file.png'  # путь к иконке файла
        # Проверка добавления основного каталога
        if directory in item_text_list:
            QMessageBox.information(self, 'Внимание', f'Ранее каталог {directory} был добавлен', QMessageBox.Ok)
        else:
            # Создаем иконки для каталога
            item = icons(path_icon_dir, directory)
            self.listWidgetChoose.addItem(item)

        # Вывести в окно все файлы и папки рекурсивно
        for dirpath, dirnames, filenames in os.walk(directory):
            # перебрать каталоги
            for dir_name in dirnames:
                dir_res = os.path.join(dirpath, dir_name)
                if dir_res in item_text_list:
                    QMessageBox.information(self, 'Внимание', f'Ранее каталог {dir_res} был добавлен', QMessageBox.Ok)
                else:
                    # Создаем иконки для каталогов
                    item = icons(path_icon_dir, dir_res)
                    self.listWidgetChoose.addItem(item)

            # перебрать файлы
            for file_name in filenames:
                file = os.path.join(dirpath, file_name)
                if file in item_text_list:
                    QMessageBox.information(self, 'Внимание', f'Ранее файл {file} был добавлен', QMessageBox.Ok)
                else:
                    # Создаем иконки для файлов
                    item = icons(path_icon_file, file)
                    self.listWidgetChoose.addItem(item)

    # Функция выбора файла
    def choose_file(self):
        path = '/home/spi_729-1/Документы' # директория с тестовым каталогом
        files, x = QtWidgets.QFileDialog.getOpenFileNames(self, 'Выберите файлы', path)
        path_icon_file = './icons/file.png'  # путь к иконке файла

        for file in files:
            # Проверка на существование файла в окне выбора
            item_text_list = [str(self.listWidgetChoose.item(i).text()) for i in
                              range(self.listWidgetChoose.count())]  # перебор элементов в окне выбора файлов
            if file in item_text_list:
                QMessageBox.information(self, 'Внимание', f'Ранее файл {file} был добавлен', QMessageBox.Ok)
            else:
                # Создаем иконки для файлов
                item = icons(path_icon_file, file)
                self.listWidgetChoose.addItem(item)  # выводим название файла и полный его путь с иконкой

    # Функция удаления файлов из списка
    def delete_item(self):
        try:
            count_items = self.listWidgetChoose.count()  # Находим кол-во элементов в QListWidget
            # Проверка на заполнение QListWidget
            if count_items == 0:
                QMessageBox.warning(self, 'Внимание', 'Список файлов пуст!', QMessageBox.Ok)

            check = 0
            # Если не выбраны файлы для удаления - вывод сообщения
            for rows in range(count_items):  # от 0 до 2
                item_selected = self.listWidgetChoose.item(rows)
                if item_selected.checkState() == QtCore.Qt.Checked:
                    check = check + 1
            #  Сравнение check с кол-ом элементов в QListWidget
            if check == count_items and count_items != 0:
                QMessageBox.warning(self, 'Внимание', 'Вы не выбрали файлы для удаления!', QMessageBox.Ok)

            #  Удаление всех выбранных элементов (не установлен checkbox)
            while check != count_items:
                for rows in range(count_items):  # от 0 до 2
                    item_selected = self.listWidgetChoose.item(rows)
                    if item_selected is None:
                        self.listWidgetChoose.takeItem(rows)
                    elif item_selected.checkState() == QtCore.Qt.Unchecked:
                        self.listWidgetChoose.takeItem(rows)
                check = check + 1
            self.listWidgetControl.clear()
        except Exception as e:
            QMessageBox.critical(self, 'Внимание', f'Возникла ошибка при удалении файла!\n{str(e)}\n'
                                                   f'Обратитесь к администратору', QMessageBox.Ok)

    #  Функция для добавления файлов и каталогов на КЦ
    def control_files(self):
        count_items = self.listWidgetChoose.count()  # Находим кол-во элементов в QListWidget
        # Проверка на заполнение QListWidget
        if count_items == 0:
            QMessageBox.warning(self, 'Внимание', 'Вы не выбрали файлы для добавления на КЦ!\n'
                                                  'Повторите попытку', QMessageBox.Ok)
        else:
            item_text_list = [str(self.listWidgetChoose.item(i).text()) for i in
                              range(self.listWidgetChoose.count())]  # перебор элементов в окне выбора файлов
            self.listWidgetControl.clear()  # очищение поля "Файлы на КЦ"
            backup_file = '/home/spi_729-1/Документы/Backup'  # путь к каталогу с копиями
            if os.path.exists(backup_file):
                shutil.rmtree(backup_file)
                os.makedirs(backup_file)
            else:
                os.makedirs(backup_file)
            # Добавление в файл для сравнения
            try:
                #  запись в файл данных
                output_file = "out.txt"  # текстовый файл для сохранения записей хешей и файлов на КЦ
                with open(output_file, "w") as files_control:
                    for file in item_text_list:
                        if os.path.exists(file) and os.path.isfile(file):
                            path_icon_file = './icons/file.png'
                            shutil.copy2(file, backup_file)  # резервное копирование файлов
                            file_hash = hash_file(file)
                            item = icons(path_icon_file, file)
                            self.listWidgetControl.addItem(item)  # Добавление файлов в поле "Файлы на КЦ"
                            self.pushButton_3.setEnabled(True)
                            print(file, file_hash)
                            files_control.write(f"{file}, {file_hash}\n")  # Запись данных в файл
                        elif os.path.exists(file) and os.path.isdir(file):
                            path_icon_dir = './icons/die.png'
                            backup_file = f'{backup_file}/{os.path.basename(file)}'
                            # Проверка на существование файла для бэкапа
                            shutil.copytree(file, backup_file)
                            dir_hash = hash_dir(file)
                            item = icons(path_icon_dir, file)
                            self.listWidgetControl.addItem(item)  # Добавление каталогов в поле "Файлы на КЦ"
                            self.pushButton_3.setEnabled(True)
                            print(file, dir_hash)
                            files_control.write(f"{file}, {dir_hash}\n")  # Запись данных в файл
                        else:
                            files_control.close()
                            QMessageBox.warning(self, 'Внимание',
                                                f'Проверьте правильность выбранных файлов.\nВозможно вы не добавили'
                                                f' файлы для КЦ\n'
                                                f'Повторите попытку.'
                                                ,
                                                QMessageBox.Ok)
            except Exception as e:
                QMessageBox.critical(self, 'Внимание', f'Ошибка при добавлении файлов на КЦ!\n{str(e)}\n'
                                                       f'Проверьте правильность выбранных данных\n'
                                                       f'Возможно некоторые файлы были удалены или изменены', QMessageBox.Ok)

    # Функция запуска таймера
    def start_timer(self):
        count_items = self.listWidgetChoose.count()  # Находим кол-во элементов в QListWidget
        # Проверка на заполнение QListWidget
        if count_items == 0:
            return
        else:
            self.timer.start()
            QMessageBox.information(self, 'Внимание', 'Запущена автоматическая проверка КЦ\n'
                                                      'Вы можете остановить автоматическую проверку.\n'
                                                      'Для этого нажмите кнопку "Остановить проверку КЦ"')
            self.pushButton.setEnabled(True)

    # Функция остановки таймера
    def stop_timer(self):
        self.timer.stop()
        QMessageBox.information(self, 'Внимание', 'Автоматическая проверка КЦ остановлена!\n'
                                                  'Для её активации добавьте снова файлы на КЦ.', QMessageBox.Ok)
        self.pushButton.setEnabled(False)

    # Функция создания списка файлов для последующей проверки КЦ
    def list_files(self):
        # Функция формирует списки элементов для проверки
        out_file = read_files("out.txt")
        list_in_out_file = [i for i in out_file]  # Список элементов в файле out.txt
        item_text_list = [str(self.listWidgetControl.item(i).text()) for i in
                          range(self.listWidgetControl.count())]  # перебор элементов в окне файлы на КЦ
        list_files = []  # Список для файлов в поле "Добавлены на КЦ" и их хешей
        for file in item_text_list:
            if os.path.exists(file) and os.path.isfile(file):
                file_hash = hash_file(file)  # расчет хеша файлов в окне "Файлы на КЦ"
                list_files.append(f"{file}, {file_hash}")  # Добавление файла в список файлов
            elif os.path.exists(file) and os.path.isdir(file):
                dir_hash = hash_dir(file)
                list_files.append(f"{file}, {dir_hash}")  # Добавление директории в список файлов
            else:
                file = file
                file_hash = 1
                list_files.append(f"{file}, {file_hash}")  # Добавление файла в список файлов
        return list_files, list_in_out_file

    # Функция проверки КЦ
    def check_files(self):
        try:
            list_res = self.list_files()  # Формируем список файлов для проверки
            list_files, list_in_out_file = list_res  # Отделяем сформированный список файлов от списка в out.txt
            count = len(list_in_out_file)
            for item in range(count):
                file_str = str(list_files[item])  # Перевод к строке элементов в новом списке файлов и хешей
                file_res_tuple = tuple(
                    str(item) for item in file_str.split(',') if item != '')  # Отделяем файлы и хеши
                # в общем списке
                name_path_file, sha_hash = file_res_tuple
                if list_files[item] != list_in_out_file[item]:
                    path_icon_error = './icons/error.png'  # путь к иконке ошибки
                    if list_files[item] == f"{name_path_file}, 1":
                        item_res_er = items_out_control(path_icon_error,
                                                        f"Нарушение КЦ файла {name_path_file}. "
                                                        f"Файл "
                                                        f"удален или переименован!", time)
                        self.listWidgetOutput.addItem(item_res_er)
                    else:
                        item_res_er = items_out_control(path_icon_error,
                                                        f"Нарушение КЦ файла {name_path_file}. Файл "
                                                        f"изменен!", time)
                        self.listWidgetOutput.addItem(item_res_er)
                else:
                    path_icon_success = './icons/success.png'  # путь к иконке успещно
                    item_res_suc = items_out_control(path_icon_success, f"КЦ файла {name_path_file} не нарушен",
                                                     time)
                    self.listWidgetOutput.addItem(item_res_suc)
            self.btnChoosefile_2.setEnabled(True)
            self.btnfile_backup.setEnabled(True)
            self.btndir_backup.setEnabled(True)
            self.btnRecovery.setEnabled(True)
            QMessageBox.information(self, 'Внимание', f'Проверка КЦ файлов успешно завершена!', QMessageBox.Ok)
        except Exception as e:
            QMessageBox.critical(self, 'Внимание', f'Ошибка при проверке КЦ файлов!\n{str(e)}\n'
                                                   f'Обратитесь к администратору',
                                 QMessageBox.Ok)

    # Функция для выбора пути к каталогу (куда восстановить)
    def path_dir_choose(self):
        path = '/home/spi_729-1/Документы'
        directory = QtWidgets.QFileDialog.getExistingDirectory(self, "Выберите каталог", path)
        self.textPathIn.setText(directory)

    # Функция для выбора пути к файлу для восстановления
    def path_file_choose(self):
        backup_file = '/home/spi_729-1/Документы/Backup'
        file, x = QtWidgets.QFileDialog.getOpenFileName(self, 'Выберите файлы', backup_file)
        self.textPathOut.setText(file)

    # Функция для выбора пути к каталогу для восстановления
    def path_dir2_choose(self):
        backup_file = '/home/spi_729-1/Документы/Backup'
        directory = QtWidgets.QFileDialog.getExistingDirectory(self, "Выберите каталог", backup_file)
        self.textPathOut.setText(directory)

    # Функция для восстановления файла
    def recovery_files(self):
        try:
            # Функция для восстановления файлов
            text_in = self.textPathIn.toPlainText()
            text_out = self.textPathOut.toPlainText()
            if os.path.exists(text_in) and os.path.exists(text_out) and os.path.isfile(text_out):
                shutil.copy2(text_out, text_in)
                QMessageBox.information(self, 'Внимание', f'Восстановление файла {text_out} выполнено успешно!',
                                        QMessageBox.Ok)
            elif os.path.exists(text_in) and os.path.exists(text_out) and os.path.isdir(text_out):
                base_name = os.path.basename(text_out)
                shutil.copytree(text_out, f'{text_in}/{base_name}')
                QMessageBox.information(self, 'Внимание', f'Восстановление каталога {text_out} выполнено успешно!',
                                        QMessageBox.Ok)
            else:
                QMessageBox.warning(self, 'Внимание', 'Не удалось восстановить файл.\nПроверьте правильность '
                                                      'выбранных данных!\nВозможно вы не выбрали файлы для '
                                                      'восстановления'
                                                      ' данных.\nПовторите попытку.', QMessageBox.Ok)
            self.textPathIn.clear()
            self.textPathOut.clear()
        except Exception as e:
            QMessageBox.critical(self, 'Внимание', f'Не удалось восстановить файл.\n{str(e)}\nПроверьте '
                                                   f'правильность выбранных данных или обратитесь к администратору',
                                 QMessageBox.Ok)


# Функция для вывода иконок и checkbox у файлов
def icons(picture, file):
    # Создаем иконки для файлов
    item = QtWidgets.QListWidgetItem()  # определение item в QListWidget
    icon = QIcon(picture)  # добавляем иконку
    item.setIcon(icon)
    item.setCheckState(QtCore.Qt.Checked)  # устанавливаем checkbox (True)
    item.setText(file)
    return item


# Функция для вывода файлов, прошедших проверку КЦ
def items_out_control(picture, file, timestr):
    # Создаем иконки для файлов
    timestr = timestr.strftime("%d.%m.%Y  %H:%M:%S")
    item = QtWidgets.QListWidgetItem()  # определение item в QListWidget
    icon = QIcon(picture)  # добавляем иконку
    item.setIcon(icon)
    item.setText(f"{file}  Дата: {timestr}")
    return item


# Функция для получения хеш-суммы файла
def hash_file(file_name):
    h = hashlib.sha256()  # Создание объекта хеша

    #  Открытие файла для чтения в двоичном режиме
    with open(file_name, 'rb') as file:
        chunk = 0
        while chunk != b'':
            chunk = file.read(1024)  # Циклом читаем до конца файла только 1024 байта за раз
            h.update(chunk)

    return h.hexdigest()


# Функция для получения хеш-суммы каталога
def hash_dir(dir_path):
    dir_hash = ''
    #  Распечатать все файлы и папки рекурсивно
    for dirpath, dirnames, filenames in os.walk(dir_path):
        # перебрать каталоги
        for dirname in dirnames:
            os.path.join(dirpath, dirname)  # формируем полный путь и название директории
        # перебрать файлы
        for filename in filenames:
            message = hash_file(os.path.join(dirpath, filename))  # хешируем файлы, найденные в каталоге
            dir_hash += message  # складываем хеш-суммы файлов
    return hashlib.sha256(dir_hash.encode('utf8')).hexdigest()


# Функция для чтения файла
def read_files(files):
    file_main = open(files, "r")
    file_string = file_main.read()
    file_tuple = tuple(str(item) for item in file_string.split('\n') if item != '')  # разделила файлы по табуляции
    return file_tuple


# Функция для поиска файла в указанном каталоге
def search_file(filename, directory):
    for root, dirs, files in os.walk(directory):
        if filename in files:
            return os.path.join(root, filename)
    return None


def main():
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = ExampleApp()  # Создаём объект класса ExampleApp
    window.show()  # Показываем окно
    app.exec_()  # и запускаем приложение


if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    main()  # то запускаем функцию main()
