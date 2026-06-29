#!/user/bin/env python3

from .library_classes import Book, Library, BookException
from .misc_functions import is_initialized
from .misc_functions import stack_delete_book
from .misc_functions import add_to_archive, read_from_archive, check_in_archive
from .misc_functions import adding_book_chars, deleting_book_chars, resetting_to_default
import argparse
import pathlib
import shlex
import zipfile
from rich.console import Console
from rich.table import Table
from importlib import resources
import numpy as np
import heapq



def main():
    intro = """
     ______________________
    /                      \\
    ========================
    |  |      |  |      |  |
    |  |      |  |      |  |
    |  |      |  |      |  |
    Вы зашли в менеджер личной библиотеки.
    Пока доступно создание только excel-библиотек
    Для помощи введите -h. Для помощи по командам введите command_name -h. Опции вводятся в кавычках, кроме случаев, когда используются числа.
    """
    
    print(intro)
    
    description = """Домашняя библиотека. Для помощи с коммандой введите command_name -h. """
    book_help = """Команда для создания книги. Если вы хотите ввести после опции больше одного слова, то вводите их в кавычках"""
    parser = argparse.ArgumentParser(description=description)
    subparser = parser.add_subparsers(dest="command")
    library_parser = subparser.add_parser("library", help="Команда для работы с библиотекой")
    sharing_parser = subparser.add_parser("sharing", help="Команда для того, чтобы поделиться фильтрованными книгами. Создает список или zip-файл")
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
    parser.add_argument("-q", "--quit_programm", action="store_true", help="Выход из программы")
    
    library_parser.add_argument("-cl", "--create_or_choose_library", nargs="+", type=str, help = "Создает новую библиотеку в папке на рабочем столе или работает с уже существующей. Принимает название библиотеки, которое может быть введено без ковычек")
    library_parser.add_argument("-la", "--library_add", action="store_true", help="Добавляет книгу, с которой идет работа, в библиотеку")
    library_parser.add_argument("-lf", "--library_filter", action="store_true", help="Фильтрует библиотеку по фильтру, с которым идет работа. Если вы хотите фильтровать о=по диапазону оценок и лет, введите их в фильтре через дефиз")
    library_parser.add_argument("-lt", "--library_top", type=int, help="Возвращает n самых высокооцененных книг, выбранных по фильтру, с которым идет работа. Укажите после library_filter")
    library_parser.add_argument("-ex", "--exclusive", action="store_true", help="В случае, если у произведения указано несколько жанров, поджанров или авторов, фильтрация и поиск самых высокооцененных книг будет производиться строго по указанным в фильтре параметрам. По дефолту выключен")
    library_parser.add_argument("-lfb", "--library_fetch_book", action="store_true", help="Находит и возвращает как настоющую книгу по фильтру, с которым идет работа. Фильтр должен содержать только автора и название")
    library_parser.add_argument("-ldb", "--library_delete_book", action="store_true", help="Удаляет книгу по фильтру, с которым идет работа. Фильтр должен содержать только автора и название")    
    library_parser.add_argument("-lrb", "--library_replace_book", action="store_true", help="Заменяет книгу в библиотеке. Для замены создайте объект книги с нужным названием, автором и харатктеристиками")    
    library_parser.add_argument("-las", "--library_add_stack", action="store_true", help="Добавляет все книги в стопке, с которй сейчас идет работа, в бибиотеку")
    library_parser.add_argument("-lrn", "--library_rename", help="Переименовывает библиотеку, с которой совершается работа; введите новое название")
    library_parser.add_argument("-tf", "--table_format", action="store_true", help="Выводит результат фильтрации и нахождения лучших в виде таблицы")

    sharing_parser.add_argument("-ct", "--create_txt", help="Создает txt-файл с результатами фильтрафии. Принимает название. По умолчанию содержит только автора и название")
    sharing_parser.add_argument("-ex", "--exclusive", action="store_true", help="В txt-файл или в txt-файл в zip-файле записываются результаты эксклюзивного поиска")
    sharing_parser.add_argument("-v", "--verbouse", action ="store_true", help="Добавляет полные характеристики книги (жанры, отзыв и тд) в txt-файл или txt-файл в zip-файле")
    sharing_parser.add_argument("-st", "--share_with_text", help="Создает zip-файл с txt_файлом и содержащимися в архиве текстами из числа отфильтрованных. Принимает название zip-файла")

    bookcreate_parser.add_argument("-t", "--title", type=str, required=True, help="Название произведения.")
    bookcreate_parser.add_argument("-a", "--author", type=str, required=True, help="Автор произведения. Несколько авторов вводите через запятую.")
    bookcreate_parser.add_argument("-f", "--form", type=str, default=argparse.SUPPRESS, help="Форма. Допускает строго одино значение.")
    bookcreate_parser.add_argument("-g", "--genre", type=str, default=argparse.SUPPRESS, help="Жанр. Несколько жанров вводите через запятую.")
    bookcreate_parser.add_argument("-sg", "--subgenre", type=str, default=argparse.SUPPRESS, help="Поджанр. Несколько поджанров вводите через запятую.")
    bookcreate_parser.add_argument("-r", "--rating", type=float, default=argparse.SUPPRESS, help="Оценка. Допускает число, целое или десятичное, от 0 до 10.")
    bookcreate_parser.add_argument("-y", "--year", type=int, default=argparse.SUPPRESS, help="Год издания, допускает одно целое число")
    bookcreate_parser.add_argument("-rev", "--review", type=str, default=argparse.SUPPRESS, help="Отзыв")
    bookcreate_parser.add_argument("-st", "--stack", action="store_true", default=None, help = "Добавление созданной книги в стопку")

    book_parser.add_argument("-tu", "--update_title", type=str, default=None, help="Название произведения.")
    book_parser.add_argument("-au", "--update_author", type=str, default=None,help="Автор произведения. Несколько авторов вводите через запятую.")
    book_parser.add_argument("-fu", "--update_form", type=str, default=None, help="Форма. Допускает строго одино значение.")
    book_parser.add_argument("-gu", "--update_genre", type=str, default=None, help="Жанр. Несколько жанров вводите через запятую.")
    book_parser.add_argument("-sgu", "--update_subgenre", type=str, default=None, help="Поджанр. Несколько поджанров вводите через запятую.")
    book_parser.add_argument("-ru", "--update_rating", type=float, default=None, help="Оценка. Допускает число от 0 до 10.")
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
    bookchars_parser.add_argument("-ach", "--add_char", help="Добавляет новую характеристику в доступные. Чтобы добавить несколько, введите их речез запятую. Перед характеристиками укажите, что именно хотите обновить, введя перед списком добавлений 'жанр', 'поджанр' или 'форма'")
    bookchars_parser.add_argument("-dch", "--delete_char", help="Удаляет характеристики из доступных. Чтобы удалить несколько, введите их речез запятую. Перед характеристиками укажите, что именно хотите обновить, введя перед списком добавлений 'жанр', 'поджанр' или 'форма'")
    bookchars_parser.add_argument("-rch", "--reset_to_default_char", help="Возвращает доступные жанры, поджанры и формы к дефолту, введите 'жанр', 'поджанр' или 'форма' соотвественно")
    
    book_fields = ["title", "author", "form", "genre", "subgenre", "rating", "year", "review"]
    book_fields_ru = ["название", "автор(ы)", "жанр(ы)", "поджанр(ы)", "форма", "оценка", "год написания", "отзыв"]
    
    stack = []
    current_book = None
    current_library = None
    current_filter = None 

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
        except BookException:
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
            if current_library:
                print(current_library.name)
            else:
                print("Библиотека не выбрана")
        elif args.current_book:
            if current_book:
                print(current_book)
            else:
                print("Книга не выбрана")
        elif args.current_filter:
            if current_filter:
                print(current_filter)
            else:
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
        elif args.quit_programm:
            break
  
        if args.command == "mkbook":
            arguments_book = {key: vars(args)[key] for key in book_fields if (key in vars(args) and key != "stack")}
            try:
                current_book = Book(**arguments_book)
            except BookException as e:
                print(e)
            if args.stack:
                stack.append(current_book)
        
        elif args.command == "book":
            if current_book:
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
            else:
                print("Книга не выбрана")
            
        elif args.command == "library":
            if args.create_or_choose_library:
                current_library = Library(" ".join(args.create_or_choose_library))
            elif args.library_add:
                result = is_initialized({"библиотека": current_library, "книга": current_book})
                if result:
                    current_library.book_add(current_book) 
            elif args.library_filter:
                result = is_initialized({"библиотека": current_library, "фильтр": current_filter})
                if result:
                    books = []
                    rating_several_check = "rating" in current_filter and len(current_filter["rating"].split("-")) > 1
                    year_several_check = "year" in current_filter and len(current_filter["year"].split("-")) > 1
                    if rating_several_check:
                        rating_several = [float(el.strip()) for el in current_filter["rating"].split("-")]
                    if year_several_check:
                        year_several = [int(el.strip()) for el in current_filter["year"].split("-")]
                    filter_copy = current_filter.copy()
                    if rating_several_check and year_several_check:
                        del filter_copy["year"]
                        del filter_copy["rating"]
                        if args.exclusive:
                            books_iter = current_library.filter_books(exclusive=True, **filter_copy)
                        else:
                            books_iter = current_library.filter_books(**filter_copy)
                        for book in books_iter:
                            if rating_several[0] <= book.rating <= rating_several[1] and year_several[0] <= book.year <= year_several[1]:
                                books.append(book)
                    elif rating_several_check:
                        del filter_copy["rating"]         
                        if args.exclusive:
                            books_iter = current_library.filter_books(exclusive=True, **filter_copy)
                        else:
                            books_iter = current_library.filter_books(**filter_copy)
                        for book in books_iter:
                            if rating_several[0] <= book.rating <= rating_several[1]:
                                books.append(book)
                    elif year_several_check:
                        del filter_copy["year"]       
                        if args.exclusive:
                            books_iter = current_library.filter_books(exclusive=True, **filter_copy)
                        else:
                            books_iter = current_library.filter_books(**filter_copy)
                        for book in books_iter:
                            if year_several[0] <= book.year <= year_several[1]:
                                books.append(book)
                    else:
                        if args.exclusive:
                            books= current_library.filter_books(exclusive=True, **current_filter)
                        else:
                            books = current_library.filter_books(**current_filter)
                    if args.library_top:
                        books = heapq.nlargest(args.library_top, books, key = lambda book: book.rating)
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
            elif args.library_fetch_book:
                result = is_initialized({"библиотека": current_library, "книга": current_book})
                if result:
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
            elif args.library_replace_book:
                result = is_initialized({"библиотека": current_library, "книга": current_book})
                if result:
                    current_library.replace_book(current_book)
            elif args.library_delete_book:
                result = is_initialized({"библиотека": current_library, "книга": current_book})
                if result:
                    title = current_filter["title"]
                    author = current_filter["author"] 
                    current_library.delete_book(**{title: author})
            elif args.library_add_stack:
                if len(stack) == 0:
                    print("Стопка пуста")
                else:
                    if current_library:
                        for book_of_stack in stack:
                            current_library.book_add(book_of_stack)
                    else:
                        print("Библиотека не выбрана")
            elif args.library_rename:
                if current_library:
                    pathlib.Path(pathlib.Path.home() / f"Desktop/home_library/{current_library.name}.xlsx").rename(pathlib.Path.home() / f"Desktop/home_library/{args.library_rename}.xlsx")
                    pathlib.Path(pathlib.Path.home() / f"Desktop/home_library/{current_library.name.replace(" ", "_")}_archive.zip").rename(pathlib.Path.home() / f"Desktop/home_library/{args.library_rename.replace(" ", "_")}_archive.zip")
                    current_library.name = args.library_rename
                else:
                    print("Библиотека не выбрана")
                    
        elif args.command == "sharing":
            result = is_initialized({"библиотека": current_library, "фильтр": current_filter})
            if result:
                if args.exclusive:
                    books = current_library.filter_books(exclusive=True, **current_filter)
                else:
                    books = current_library.filter_books(**current_filter)
                if args.create_txt:
                    if len(books) == 0:
                        print("Не удаловь найти книги, удовленворяющие запросу")
                    else:
                        path = pathlib.Path.home() / f"Desktop/{args.create_txt}.txt"
                        if args.verbouse:
                            with open(path, "w") as file:
                                for book in books:
                                    file.write(f"{str(book)}\n")
                        else:
                            with open(path, "w") as file:
                                for book in books:
                                    file.write(f"{book.author}. {book.title}\n")
                elif args.share_with_text:
                    if len(books) == 0:
                        print("Не удаловь найти книги, удовленворяющие запросу")
                    else:
                        txt_content = ""
                        if args.verbouse:
                            for book in books:
                                txt_content = txt_content + str(book) + "\n"
                        else:
                            for book in books:
                                to_append = f"{book.author}. {book.title}"
                                txt_content = txt_content + to_append + "\n"
                        path = pathlib.Path.home() / f"Desktop/home_library/{current_library.name}_archive.zip"
                        path_to_new = pathlib.Path.home() / f"Desktop/{args.share_with_text}.zip"
                        with zipfile.ZipFile(path, "r") as archive, zipfile.ZipFile(path_to_new, "w") as new_zip:
                            list_to_write = [book.title.replace(" ", "_") for book in books]
                            for name_to_write in list_to_write:
                                for file_temp in archive.namelist():
                                    if pathlib.Path(file_temp).stem == name_to_write:
                                        file_data = archive.read(file_temp)
                                        new_zip.writestr(file_temp, file_data)
                            new_zip.writestr("Список литературы.txt", txt_content)

        elif args.command == "stack":
            if args.stack_delete_book:
                stack = stack_delete_book(stack, args.stack_delete_book)
            elif args.stack_clear:
                stack = []
        
        elif args.command == "filter_set":
            current_filter = {key: vars(args)[key] for key in book_fields if key in vars(args)}
        
        elif args.command == "archive":
            result = is_initialized({"книга": current_book, "библиотека": current_library})
            if args.add_to_archive:
                if result:
                    add_to_archive(current_book.title, current_library.name, args.add_to_archive)
            elif args.read_from_archive:
                if result:
                    read_from_archive(current_book.title, current_library.name)
            elif args.check_in_archive:
                if result:
                    check_in_archive(current_book.title, current_library.name)
                        
        elif args.command == "book_chars":
            dict_chars = {"жанр": ["GENRES", "жанр", "жанры"], "поджанр": ["SUBGENRES", "поджанр", "поджанры"], 
                          "форма": ["FORMS", "форма", "формы"]}
            if args.current_genres:
                print(f"Допустимые на данный момент жанры:\n{', '.join(Book.GENRES)}")
            elif args.current_subgenres:
                print(f"Допустимые на данный момент поджанры:\n{', '.join(Book.SUBGENRES)}")
            elif args.current_forms:
                print(f"Допустимые на данный момент формы:\n{', '.join(Book.FORMS)}")
            elif args.add_char:
                type_of_char = [el.strip(" ").lower() for el in args.add_char.split(",")][0]
                chars_to_add = [el.strip(" ").lower() for el in args.add_char.split(",")][1:]
                if type_of_char.lower() in dict_chars.keys():
                    adding_book_chars(dict_chars[type_of_char.lower()][0], chars_to_add, dict_chars[type_of_char.lower()][1], dict_chars[type_of_char.lower()][2])
                else:
                    print("Проверьте правильность написания введенной характеристики")
            elif args.delete_char: 
                type_of_char = [el.strip(" ").lower() for el in args.delete_char.split(",")][0]
                chars_to_delete = [el.strip(" ").lower() for el in args.delete_char.split(",")]
                if type_of_char.lower() in dict_chars.keys():
                    deleting_book_chars(dict_chars[type_of_char.lower()][0], chars_to_delete, dict_chars[type_of_char.lower()][1], dict_chars[type_of_char.lower()][2])
                else:
                    print("Проверьте правильность написания введенной характеристики")
            elif args.reset_to_default:
                if args.reset_to_default.lower() in dict_chars:
                    resetting_to_default(dict_chars[args.reset_to_default.lower()][0])
                else:
                    print("Введено некорректное значение")
                          
          
if __name__ == "__main__":
    main()