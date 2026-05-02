from collections import UserDict
from datetime import datetime, timedelta

def input_error(func): # Декоратор для обробки помилок, що можуть виникнути при виконанні функції, таких як ValueError, KeyError та IndexError
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return str(e)
        except KeyError:
            return "Contact not found."
        except AttributeError:
            return "Contact not found."
        except IndexError:
            return "Not enough arguments provided."
    return inner

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value): # Перевірка номеру, номер має мати 10 цифер і бути числом
        if not (len(value) == 10 and value.isdigit()):
            raise ValueError("Phone number must contain exactly 10 digits.")
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value):
        try:
            datetime.strptime(value, "%d.%m.%Y") # Перевіка дати та конвертація в datetime, дата має бути у форматі DD.MM.YYYY
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        super().__init__(value)

    @property 
    def date(self):
        return datetime.strptime(self.value, "%d.%m.%Y")
 

class Record: # Клас для зберігання інформації про контакт, включаючи ім'я та список телефонів
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone_number): # Додавання нового номера телефону до контакту
        self.phones.append(Phone(phone_number))

    def remove_phone(self, phone_number): # Видалення номера телефону з контакту
        phone_to_remove = self.find_phone(phone_number)
        if phone_to_remove:
            self.phones.remove(phone_to_remove)

    def edit_phone(self, old_number, new_number):# Редагування існуючого номера телефону в контакті
        phone_to_edit = self.find_phone(old_number)
        if not phone_to_edit:
            raise ValueError(f"Phone number {old_number} not found.")
        
        new_phone = Phone(new_number)
        index = self.phones.index(phone_to_edit)
        self.phones[index] = new_phone

    def find_phone(self, phone_number):# Пошук номера телефону в контакті, повертає об'єкт Phone або None, якщо номер не знайдено
        for phone in self.phones:
            if phone.value == phone_number:
                return phone
        return None
    
    def add_birthday(self, birthday_str):
        """Додає дату народження до контакту у форматі DD.MM.YYYY."""
        self.birthday = Birthday(birthday_str)

    def __str__(self):
        phones_str = '; '.join(p.value for p in self.phones) if self.phones else "no phones"
        birthday_str = self.birthday.value if self.birthday else "not set"
        return (f"Contact name: {self.name.value} | "
                f"Phones: {phones_str} | "
                f"Birthday: {birthday_str}")
        
class AddressBook(UserDict):# Клас для зберігання та керування контактами, реалізує словник для зберігання записів
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def __str__(self):# Повертає рядкове представлення всіх записів у книзі, кожен запис на новому рядку
        if not self.data:
            return "Address book is empty."
        return "\n".join(str(record) for record in self.data.values())
    
    def get_upcoming_birthdays(self):
        today = datetime.today().date()
        upcoming = []
        for record in self.data.values():
            if record.birthday is None:
                continue

            birth_date = record.birthday.date.date()
            try:
                birthday_this_year = birth_date.replace(year=today.year)
            except ValueError:
                birthday_this_year = birth_date.replace(year=today.year, day=28)
 
            if birthday_this_year < today:
                try:
                    birthday_this_year = birth_date.replace(year=today.year + 1)
                except ValueError:
                    birthday_this_year = birth_date.replace(year=today.year + 1, day=28)
            delta = (birthday_this_year - today).days
            if 0 <= delta <= 7:
                # Перенесення на понеділок, якщо вихідний
                weekday = birthday_this_year.weekday()
                if weekday == 5:  # Субота → понеділок
                    congratulation_date = birthday_this_year + timedelta(days=2)
                elif weekday == 6:  # Неділя → понеділок
                    congratulation_date = birthday_this_year + timedelta(days=1)
                else:
                    congratulation_date = birthday_this_year
                upcoming.append({
                    "name": record.name.value,
                    "birthday": congratulation_date.strftime("%d.%m.%Y")
                })
        return upcoming
    
def parse_input(user_input):
    parts = user_input.strip().split()
    if not parts:
        return "", []
    command = parts[0].lower()
    args = parts[1:]
    return command, args

@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message


@input_error
def change_contact(args, book: AddressBook):
    name, old_phone, new_phone, *_ = args
    record = book.find(name)
    record.edit_phone(old_phone, new_phone)
    return "Phone number updated."


@input_error
def show_phone(args, book: AddressBook):
    name, *_ = args
    record = book.find(name)
    if not record.phones:
        return f"{name} has no phone numbers."
    phones = '; '.join(p.value for p in record.phones)
    return f"{name}'s phones: {phones}"


@input_error
def show_all(args, book: AddressBook):
    return str(book)


@input_error
def add_birthday(args, book: AddressBook):
    name, birthday_str, *_ = args
    record = book.find(name)
    record.add_birthday(birthday_str)
    return f"Birthday added for {name}."


@input_error
def show_birthday(args, book: AddressBook):
    name, *_ = args
    record = book.find(name)
    if record.birthday is None:
        return f"{name} has no birthday set."
    return f"{name}'s birthday: {record.birthday.value}"


@input_error
def birthdays(args, book: AddressBook):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No birthdays in the next 7 days."
    lines = ["Upcoming birthdays:"]
    for entry in upcoming:
        lines.append(f"  {entry['name']} — congratulate on {entry['birthday']}")
    return "\n".join(lines)

def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    print("Type 'hello' for greeting or enter a command.")

    while True:
        user_input = input("\nEnter a command: ").strip()
        if not user_input:
            continue

        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            print(show_phone(args, book))

        elif command == "all":
            print(show_all(args, book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(args, book))

        else:
            print("Invalid command. Available commands: add, change, phone, all, "
                  "add-birthday, show-birthday, birthdays, hello, close, exit")

if __name__ == "__main__":
    main()            
            
#if __name__ == "__main__": це автоматичний тест на всі функції, але коли ми його затосовуємо то не працує imput. 
    book = AddressBook() 

    # Додаємо контакти
    john = Record("John")
    john.add_phone("0991234567")
    john.add_phone("0507654321")
    john.add_birthday("30.04.1990")
    book.add_record(john)

    alice = Record("Alice")
    alice.add_phone("0631111111")
    alice.add_birthday("01.05.1995")
    book.add_record(alice)

    bob = Record("Bob")
    bob.add_phone("0992222222")
    bob.add_birthday("15.08.1988")
    book.add_record(bob)

    # Показуємо всі контакти
    print("=== Всі контакти ===")
    print(book)

    # Змінюємо номер
    print("\n=== Змінюємо номер John ===")
    john.edit_phone("0991234567", "0999999999")
    print(book.find("John"))

    # Показуємо телефони
    print("\n=== Телефони Alice ===")
    print(alice.find_phone("0631111111"))

    # Дні народження на найближчі 7 днів
    print("\n=== Найближчі дні народження ===")
    upcoming = book.get_upcoming_birthdays()
    if upcoming:
        for entry in upcoming:
            print(f"  {entry['name']} — {entry['birthday']}")
    else:
        print("Немає днів народження у найближчі 7 днів")

    # Видаляємо контакт
    print("\n=== Видаляємо Bob ===")
    book.delete("Bob")
    print(book)