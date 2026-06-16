#!/user/bin/env python3

from .library import Book, Library
import argparse
import pathlib
import shlex
import os
import zipfile
import subprocess
import sys
from rich.console import Console
from rich.table import Table
from importlib import resources
import json

def main():
    intro = f"""
     ______________________
    /                      \\
    ========================
    |  |      |  |      |  |
    |  |      |  |      |  |
    |  |      |  |      |  |
    Вы зашли в менеджер личной библиотеки.
    Пока доступно создание только excel-библиотек
    Для помощи введите -h. Для помощи по коммандам введите command_name -h. Опции вводятся в ковычках, кроме случаев, когда используются числа.
    """
    
    print(intro)
    
    description = """Домашняя библиотека. Для помощи с коммандой введите command_name -h. """
    book_help = """Комманда для создания книги. Если вы хотите ввести после опции больше одного слова, то вводите их в ковычках"""
    parser = argparse.ArgumentParser(description=description)
    subparser = parser.add_subparsers(dest="command")
    library_parser = subparser.add_parser("library", help="Комманда для работы с библиотекой")
    bookcreate_parser = subparser.add_parser("mkbook", help=book_help)
    filter_parser = subparser.add_parser("filter_set", help="Фильтр для поиска книги")
    book_parser = subparser.add_parser("book", help="Обновление харатеристик книги, с которой идет работа")
    stack_parser = subparser.add_parser("stack", help="Работа со стопкой книг")
    archive_parser = subparser.add_parser("archive", help="Работа с zip-архивом при библиотеке")
    bookchars_parser = subparser.add_parser("book_chars", help="Работа с доступными жанром, поджанром и типом произведения")
    
    parser.add_argument("-sl", "--show_libraries", action="store_true", help="Показывает все библиотеки пользователя")
    parser.add_argument("-curl", "--current_library", action="store_true", help="Показывает библиотеку, с которой идет работа")
    parser.add_argument("-curb", "--current_book", action="store_true", help="Показывает книгу, с которой идет работа")
    parser.add_argument("-curf", "--current_filter", action="store_true", help="Показывает фильтр, с которым идет работа")
    parser.add_argument("-curs", "--current_stack", action="store_true", help="Показывает стопку книг, с которой идет работа")
    parser.add_argument("-exit", "--exit_programm", action="store_true", help="Выход из программы")
    
    library_parser.add_argument("-cl", "--create_or_choose_library", nargs="+", type=str, help = "Создает новую библиотеку в папке на рабочем столе или работает с уже существующей. Принимает название библиотеки, которое может быть введено без ковычек")
    library_parser.add_argument("-la", "--library_add", action="store_true", help="Добавляет книгу, с которой идет работа, в библиотеку")
    library_parser.add_argument("-lf", "--library_filter", action="store_true", help="Фильтрует библиотеку по фильтру, с которым идет работа")
    library_parser.add_argument("-lt", "--library_top", type=int, help="Возвращает n самых высокооцененных книг, выбранных по фильтру, с которым идет работа")
    library_parser.add_argument("-ex", "--exclusive", action="store_true", help="В случае, если у произведения указано несколько жанров, поджанров или авторов, фильтрация и поиск самых высокооцененных книг будет производиться строго по указанным в фильтре параметрам. По дефолту выключен")
    library_parser.add_argument("-lfb", "--library_fetch_book", action="store_true", help="Находит и возвращает как настоющую книгу по фильтру, с которым идет работа. Фильтр должен содержать только автора и название")
    library_parser.add_argument("-ldb", "--library_delete_book", action="store_true", help="Удаляет книгу по фильтру, с которым идет работа. Фильтр должен содержать только автора и название")    
    library_parser.add_argument("-lrb", "--library_replace_book", action="store_true", help="Заменяет книгу в библиотеке. Для замены создайте объект книги с нужным названием, автором и харатктеристиками")    
    library_parser.add_argument("-las", "--library_add_stack", action="store_true", help="Добавляет все книги в стопке, с которй сейчас идет работа, в бибиотеку")
    library_parser.add_argument("-lrn", "--library_rename", help="Переименовывает библиотеку, с которой совершается работа; введите новое название")
    library_parser.add_argument("-tf", "--table_format", action="store_true", help="Выводит результат фильтрации и нахождения лучших в виде таблицы")

    bookcreate_parser.add_argument("-t", "--title", type=str, required=True, help="Название произведения.")
    bookcreate_parser.add_argument("-a", "--author", type=str, required=True, help="Автор произведения. Несколько авторов вводите через запятую.")
    bookcreate_parser.add_argument("-f", "--form", type=str, default=argparse.SUPPRESS, help="Форма. Допускает строго одино значение.")
    bookcreate_parser.add_argument("-g", "--genre", type=str, default=argparse.SUPPRESS, help="Жанр. Несколько жанров вводите через запятую.")
    bookcreate_parser.add_argument("-sg", "--subgenre", type=str, default=argparse.SUPPRESS, help="Поджанр. Несколько поджанров вводите через запятую.")
    bookcreate_parser.add_argument("-r", "--rating", type=int, default=argparse.SUPPRESS, help="Оценка. Допускает число от 0 до 10.")
    bookcreate_parser.add_argument("-y", "--year", type=int, default=argparse.SUPPRESS, help="Год издания, допускает одно число")
    bookcreate_parser.add_argument("-rev", "--review", type=str, default=argparse.SUPPRESS, help="Отзыв")
    bookcreate_parser.add_argument("-st", "--stack", action="store_true", default=None, help = "Добавление созданной книги в стопку")

    book_parser.add_argument("-tu", "--update_title", type=str, default=None, help="Название произведения.")
    book_parser.add_argument("-au", "--update_author", type=str, default=None,help="Автор произведения. Несколько авторов вводите через запятую.")
    book_parser.add_argument("-fu", "--update_form", type=str, default=None, help="Форма. Допускает строго одино значение.")
    book_parser.add_argument("-gu", "--update_genre", type=str, default=None, help="Жанр. Несколько жанров вводите через запятую.")
    book_parser.add_argument("-sgu", "--update_subgenre", type=str, default=None, help="Поджанр. Несколько поджанров вводите через запятую.")
    book_parser.add_argument("-ru", "--update_rating", type=int, default=None, help="Оценка. Допускает число от 0 до 10.")
    book_parser.add_argument("-yu", "--update_year", type=int, default=None, help="Год издания, допускает одно число")
    book_parser.add_argument("-revu", "--update_review", type=str, default=None, help="Отзыв")
    
    filter_parser.add_argument("-t", "--title", type=str, default=argparse.SUPPRESS, help="Название произведения.")
    filter_parser.add_argument("-a", "--author", type=str, default=argparse.SUPPRESS, help="Автор произведения. Несколько авторов вводите через запятую.")
    filter_parser.add_argument("-f", "--form", type=str, default=argparse.SUPPRESS, help="Форма. Допускает строго одино значение.")
    filter_parser.add_argument("-g", "--genre", type=str, default=argparse.SUPPRESS, help="Жанр. Несколько жанров вводите через запятую.")
    filter_parser.add_argument("-sg", "--subgenre", type=str, default=argparse.SUPPRESS, help="Поджанр. Несколько поджанров вводите через запятую.")
    filter_parser.add_argument("-r", "--rating", type=str, default=argparse.SUPPRESS, help="Оценка. Допускает число от 0 до 10.")
    filter_parser.add_argument("-y", "--year", type=str, default=argparse.SUPPRESS, help="Год издания, допускает одно число")
    filter_parser.add_argument("-rev", "--review", type=str, default=argparse.SUPPRESS, help="Отзыв")
   
    stack_parser.add_argument("-sdb", "--stack_delete_book", type=int, help="Удаление книги из стопки. Передайти номер книги, которую хотите удалить")
    stack_parser.add_argument("-scr", "--stack_clear", action="store_true", help="Очищение стопки")

    archive_parser.add_argument("-aa", "--add_to_archive", help="Принимает расширение файла без точки. Добавление файла произведения в zip-архив библиотеки с которой идет работа в папке с библиотекой. Для добавления поместите файл с названием идентичным с названием книги, с которой работают в настоящий момент, на рабочий стол. Если в названии есть пробелы, замените их на нижнее подчеркивание")
    archive_parser.add_argument("-ra", "--read_from_archive", action="store_true",  help="Создает копию файла из архива библиотеки с которой идет работа с названием как у книги, с которой идет работа, и открывает ее")
    archive_parser.add_argument("-cia", "--check_in_archive", action="store_true", help="Проверяет, есть ли книга в архиве библиотеки с которйо идет работа по названию книги, с которой идет работа") 
    
    bookchars_parser.add_argument("-cg", "--current_genres", action="store_true", help="Возвращает доступные на данный момент жанры")
    bookchars_parser.add_argument("-csg", "--current_subgenres", action="store_true", help="Возвращает доступные на данный момент поджанры")
    bookchars_parser.add_argument("-cf", "--current_forms", action="store_true", help="Возвращает доступные на данный момент формы")
    bookchars_parser.add_argument("-ag", "--add_genre", help="Добавляет новый жанр в доступные. Чтобы добавить несколько, введите их речез запятую")
    bookchars_parser.add_argument("-asg", "--add_subgenre", help="Добавляет новый поджанр в доступные. Чтобы добавить несколько, введите их речез запятую")
    bookchars_parser.add_argument("-af", "--add_form", help="Добавляет новую форму в доступные. Чтобы добавить несколько, введите их речез запятую")
    bookchars_parser.add_argument("-dg", "--delete_genre", help="Удаляет жанр из доступных. Чтобы добавить несколько, введите их речез запятую")
    bookchars_parser.add_argument("-dsg", "--delete_subgenre", help="Удаляет поджанр из доступных. Чтобы добавить несколько, введите их речез запятую")
    bookchars_parser.add_argument("-df", "--delete_form", help="Удаляет из формы доступных. Чтобы добавить несколько, введите их речез запятую")
    bookchars_parser.add_argument("-rdg", "--reset_to_default_genres", help="Возвращает доступные жанры, поджанры и формы к дефолту, введите genres, subgenres или forms соотвественно")
    
    book_fields = ["title", "author", "form", "genre", "subgenre", "rating", "year", "review"]
    book_fields_ru = ["название", "автор(ы)", "жанр(ы)", "поджанр(ы)", "форма", "оценка", "год написания", "отзыв"]
    
    stack = []

    
    console = Console()
    
    while True:
        line = input("> ").strip()
        if not line:
            continue
        try:
            args = parser.parse_args(shlex.split(line))
        except SystemExit:
            continue
        except ValueError:
            print("Вы забыли закрыть кавычки")
            continue
        

        if args.show_libraries:
            lib_folder = pathlib.Path.home() / "Desktop/home_library"
            if lib_folder.is_dir():
                libraries = list(lib_folder.rglob("*.xlsx"))
                if len(libraries) == 0:
                    print("Ни одной библиотеки не создано")
                else:
                    for lib in libraries:
                        print(lib.stem)
            else:
                print("Ни одной библиотеки не создано")
        elif args.current_library:
            try:
                print(current_library.name)
            except NameError:
                print("Библиотека не выбрана")
        elif args.current_book:
            try:
                print(current_book)
            except NameError:
                print("Книга не выбрана")
        elif args.current_filter:
            try:
                print(current_filter)
            except NameError:
                print("Фильтр не настроен")
        elif args.current_stack:
            if len(stack) == 0:
                print("Стопка пуста")
            else:
                print("Книги в стопке:")
                i=1
                for stak_elem in stack:
                    print(f"{i}. {stak_elem}")
                    i += 1
        elif args.exit_programm:
            break
  
        if args.command == "mkbook":
            arguments_book = {key: vars(args)[key] for key in book_fields if (key in vars(args) and key != "stack")}
            current_book = Book(**arguments_book)
            if args.stack:
                stack.append(current_book)
        
        elif args.command == "book":
            try:
                if args.update_title:
                    current_book.title_update(args.update_title)
                elif args.update_author:
                    current_book.author_update(args.update_author)
                elif args.update_form:
                    current_book.form_update(args.update_form)
                elif args.update_genre:
                    current_book.genre_update(args.update_genre)
                elif args.update_subgenre:
                    current_book.subgenre_update(args.update_subgenre)
                elif args.update_rating:
                    current_book.rating_update(args.update_rating)
                elif args.update_year:
                    current_book.year_update(args.update_year)
                elif args.update_review:
                    current_book.review_update(args.update_review)
            except UnboundLocalError:
                print("Книга не выбрана")
            
        elif args.command == "library":
            if args.create_or_choose_library:
                current_library = Library(" ".join(args.create_or_choose_library))
            elif args.library_add:
                try:
                    current_library.book_add(current_book)
                except NameError:
                    print("Библиотека или книга не выбраны")
            elif args.library_filter:
                try:
                    if args.exclusive:
                        books = current_library.filter_books(exclusive=True, **current_filter)
                    else:
                        books = current_library.filter_books(**current_filter)
                    if len(books) == 0:
                        print("Не удалось найти книги, удовлетворяющие запросу")
                    else:
                        print(f"{'Удалось найти одну книгу' if len(books) == 1 else 'Удалось найти следующие книги:'}")
                        if args.table_format:
                            table_filtered = Table(show_lines=True)
                            for field in book_fields_ru:
                                table_filtered.add_column(field)
                            for book in books:
                                table_filtered.add_row(book.title, book.author, book.genre if book.genre not in ("", None) else 'не указан(ы)', 
                                book.subgenre if book.subgenre not in ("", None) else 'не указан(ы)', book.form if book.form not in ("", None) else 'не указана', 
                                str(book.rating), str(book.year) if book.year != 0 else 'не указан', book.review if book.review not in ("", None) else 'не указан')
                            console.print(table_filtered)
                        else:
                            for book in books:
                                print(book)     
                except NameError:
                    print("Библиотека или фильтр не выбраны")
            elif args.library_top:
                try:
                    if args.exclusive:
                        top_books = current_library.finding_top(exclusive=True, top=args.library_top, **current_filter)
                    else:
                        top_books = current_library.finding_top(top=args.library_top, **current_filter)
                    if len(top_books) == 0:
                        print("Не удалось найти книги, удовлетворяющие запросу")
                    else:
                        print(f"{'Удалось найти одну книгу' if len(books) == 1 else 'Удалось найти следующие книги:'}")
                        if args.table_format:
                            table_top = Table(show_lines=True)
                            for field in book_fields_ru:
                                table_top.add_column(field)
                            for book in top_books:
                                table_top.add_row(book.title, book.author, book.genre if book.genre not in ("", None) else 'не указан(ы)', 
                                book.subgenre if book.subgenre not in ("", None) else 'не указан(ы)', book.form if book.form not in ("", None) else 'не указана', 
                                str(book.rating), str(book.year) if book.year != 0 else 'не указан', book.review if book.review not in ("", None) else 'не указан')
                            console.print(table_top)
                        else:
                            for book in top_books:
                                print(book) 
                except NameError:
                    print("Бибиотека или фильтр не выбраны")
            elif args.library_fetch_book:
                try:
                    if set(list(current_filter.keys())) ==  set(["title", "author"]):
                        book = current_library.filter_books(**current_filter)
                        if len(book) >= 2:
                            print("Найдено больше одной книги")
                            for boo in book:
                                print(boo)
                        elif len(book) == 0:
                            print("Книги с таким названием и именем не найдено")
                        else:
                            current_book = book[0]
                            print(f"Вы достали книгу {book[0]}")
                    else:
                        print("Фильтр должен содержать только автора и название")
                except NameError:
                    print("Библиотека или фильтр не выбраны")
            elif args.library_replace_book:
                try:
                    current_library.replace_book(current_book)
                except NameError:
                    print("Библиотека или книга не выбраны")
            elif args.library_delete_book:
                try:
                    title = current_filter["title"]
                    author = current_filter["author"] 
                    current_library.delete_book(**{title: author})
                except NameError:
                    print("Библиотека или книга не выбраны")
            elif args.library_add_stack:
                if len(stack) == 0:
                    print("Стопка пуста")
                else:
                    try:
                        for book_of_stack in stack:
                            current_library.book_add(book_of_stack)
                    except NameError:
                        print("Библиотека не выбрана")
            elif args.library_rename:
                try:
                    pathlib.Path(pathlib.Path.home() / f"Desktop/home_library/{current_library.name}.xlsx").rename(pathlib.Path.home() / f"Desktop/home_library/{args.library_rename}.xlsx")
                except UnboundLocalError:
                    print("Библиотека не выбрана")

        elif args.command == "stack":
            if args.stack_delete_book:
                stack_copy = []
                if len(stack) == 0:
                    print("Стопка пуста")
                else:
                    for i in range(1, len(stack)+1):
                        if i != args.stack_delete_book:
                           stack_copy.append(stack[i-1])
                    stack = stack_copy
            elif args.stack_clear:
                stack = []
        
        elif args.command == "filter_set":
            current_filter = {key: vars(args)[key] for key in book_fields if key in vars(args)}
        
        elif args.command == "archive":
            if args.add_to_archive:
                try:
                    name_file = current_book.title.replace(" ", "_")
                    added_file_path = pathlib.Path.home() / f"Desktop/{name_file}.{args.add_to_archive}"
                    with zipfile.ZipFile(str(pathlib.Path.home() / f"Desktop/home_library/{current_library.name.replace(" ", "_")}_archive.zip"), "a") as archive:
                        archive.write(str(added_file_path), arcname=os.path.basename(str(added_file_path)))
                except FileNotFoundError:
                    print("Не удалось найти такой файл. Проверьте правильность названия и расширения")
            elif args.read_from_archive:
                path_to_home = str(pathlib.Path.home() / "Desktop/home_library/")
                try:
                    extention = ""
                    file_named = ""
                    with zipfile.ZipFile(f"{path_to_home}/{current_library.name.replace(" ", "_")}_archive.zip", "r") as archive:
                        list_of_files = archive.namelist()
                        for text in list_of_files:
                            name, ext = os.path.splitext(text)
                            if name == current_book.title.replace(" ", "_"):
                                extention = ext
                                file_named = name
                                archive.extract(f"{name}{extention}", path_to_home)
                            else:
                                pass
                    path_to_text = f"{path_to_home}/{file_named}{extention}"
                    if sys.platform == "win32":
                        os.startfile(path_to_text)
                    elif sys.platform == "darwin":
                        subprocess.run(["open", path_to_text])
                    else:
                        subprocess.run(["xdg-open", path_to_text])
                except FileNotFoundError:
                    print("Тексты пока не добавлены в архив")
            elif args.check_in_archive:
                try:
                    path_to_home = str(pathlib.Path.home() / "Desktop/home_library/")
                    with zipfile.ZipFile(f"{path_to_home}/{current_library.name.replace(" ", "_")}_archive.zip", "r") as archive:
                        list_of_names = archive.namelist()
                        list_corrected = []
                        for text in list_of_names:
                            name, ext = os.path.splitext(text)
                            list_corrected.append(name)
                    if current_book.title.replace(" ", "_") in list_corrected:
                        print("Книга в архиве")
                    else:
                        print("Книга не добавлена в архив")
                except (NameError, FileNotFoundError):
                    if NameError:
                        print("Библиотека или книга не выбраны")
                    elif FileNotFoundError:
                        print("Тексты пока не добавлены в архив")
        elif args.command == "book_chars":
            json_path = resources.files('library_manager') / 'book_chars.json'
            
            def adding_book_chars(form, to_add, add_singular, add_plural):
                change = True
                with json_path.open("r", encoding="utf-8") as file:
                    book_chars = json.load(file)
                if len(to_add) == 1:
                    if to_add[0] in book_chars[form]:
                        change = False
                        print(f"Такой(ая) {add_singular} уже есть")
                    else:
                        book_chars[form].append(to_add[0])
                else:
                    same = list(set(book_chars[form]) & set(to_add))
                    if len(same) == 0:
                        book_chars[form].extend(to_add)
                    else:
                        to_add_final = [elem for elem in to_add if elem not in same]
                        if to_add_final:
                            book_chars[form].extend(to_add_final)
                            print(f"Уже доступные {add_plural} исключены из добавления: {same}")
                        else:
                            change = False
                            print(f"Все введенные {add_plural} уже доступны")
                if change:
                    with json_path.open("w", encoding="utf-8") as file:
                        json.dump(book_chars, file, ensure_ascii=False)
                    Book.update_chars()
                    
            def deleting_book_chars(form, to_delete, delete_singular, delete_plural):
                change = True
                with json_path.open("r", encoding="utf-8") as file:
                    book_chars = json.load(file)
                if len(to_delete) == 1:
                    if to_delete[0] not in book_chars[form]:
                        print(f"Такого(ой) {delete_singular} нет среди доступных")
                        change = False
                    else:
                        book_chars[form].remove(to_delete[0])
                else:
                    same = list(set(book_chars[form]) & set(to_delete))
                    if len(same) == len(to_delete):
                        for el in same:
                            book_chars[form].remove(el)
                    else:
                        to_delete_final = [genre for genre in to_delete if genre in same]
                        if to_delete_final:
                            different = [genre for genre in to_delete if genre not in same]
                            for el in to_delete_final:
                                book_chars[form].remove(el)
                            print(f"Не существующие {delete_plural} не удалены: {different}")
                        else:
                            change = False
                            print(f"Указанные {delete_plural} недоступны")
                if change:
                    with json_path.open("w", encoding="utf-8") as file:
                        json.dump(book_chars, file, ensure_ascii=False)
                    Book.update_chars()
                    
            def resetting_to_default(form):
                with json_path.open("r", encoding="utf-8") as file:
                    book_chars = json.load(file)
                book_chars[form] = book_chars[f"{form}_OG"]
                with json_path.open("w", encoding="utf-8") as file:
                    json.dump(book_chars, file, ensure_ascii=False)
                Book.update_chars()
                
            if args.current_genres:
                print(f"Допустимые на данный момент жанры:\n{', '.join(Book.GENRES)}")
            elif args.current_subgenres:
                print(f"Допустимые на данный момент поджанры:\n{', '.join(Book.SUBGENRES)}")
            elif args.current_forms:
                print(f"Допустимые на данный момент формы:\n{', '.join(Book.FORMS)}")
            elif args.add_genre:
                genre_to_add = [el.strip(" ").lower() for el in args.add_genre.split(",")]
                adding_book_chars("GENRES", genre_to_add, "жанр", "жанры")
            elif args.add_subgenre:
                subgenre_to_add = [el.strip(" ").lower() for el in args.add_subgenre.split(",")]
                adding_book_chars("SUBGENRES", subgenre_to_add, "поджанр", "поджанры")
            elif args.add_form:
                form_to_add = [el.strip(" ").lower() for el in args.add_form.split(",")]
                adding_book_chars("FORMS", form_to_add, "форма", "формы")
            elif args.delete_genre: 
                genre_to_delete = [el.strip(" ").lower() for el in args.delete_genre.split(",")]
                deleting_book_chars("GENRES", genre_to_delete, "жанр", "жанры")
            elif args.delete_subgenre:
                subgenre_to_delete = [el.strip(" ").lower() for el in args.delete_subgenre.split(",")]
                deleting_book_chars("SUBGENRES", subgenre_to_delete, "поджанр", "поджанры")
            elif args.delete_form:
                form_to_delete = [el.strip(" ").lower() for el in args.delete_form.split(",")]
                deleting_book_chars("FORMS", form_to_delete, "форма", "формы")
            elif args.reset_to_default:
                if args.reset_to_default.upper() in ["GENRES", "SUBGENRES", "FORMS"]:
                    resetting_to_default(args.reset_to_default.upper)
                else:
                    print("Введено некорректное значение")
            
                
          
if __name__ == "__main__":
    main()