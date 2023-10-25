from collections import UserDict
from datetime import datetime
from itertools import islice
import os
import pickle


def deco_error(func):
    def inner(*args):
        try:
            return func(*args)
        except IndexError:
            return "Not enough params"
        except KeyError:
            return f"There is no contact such in phone book. Please, use command 'Add...' first"
        except ValueError:
            return "Not enough params or wrong phone format"

    return inner


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    def __init__(self, value):
        super().__init__(value)

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, name):
        self.__value = name


class Phone(Field):
    def __init__(self, value):
        super().__init__(value)

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, phone):
        if not phone.isdigit() or len(phone) != 10:
            raise ValueError
        self.__value = phone

    def __str__(self):
        return str(self.value)
    

class Birthday(Field):
    def __init__(self, value=None):
        super().__init__(value)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, birthday):
        try:
            if birthday:
                datetime.strptime(birthday, '%Y-%m-%d')
        except ValueError:
            raise ValueError
        self._value = birthday

    def __str__(self):
        return str(self.value)


class Record:
    def __init__(self, name, birthday=None):
        self.name = Name(name)
        self.phones = []
        self.birthday = Birthday(birthday) if birthday else None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                self.phones.remove(p)
                return
        raise ValueError

    def edit_phone(self, old_phone, new_phone):
        found = False
        for phone in self.phones:
            if phone.value == old_phone:
                phone.value = new_phone
                phone.validate_phone()
                found = True
                break

        if not found:
            raise ValueError 

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None
    
    def days_to_birthday(self):
        if self.birthday:
            today = datetime.today()
            birthday = datetime(year=int(self.birthday.value[:4]), month=int(self.birthday.value[5:7]), day=int(self.birthday.value[8:10]))
            next_birthday = datetime(today.year, birthday.month, birthday.day)
            if next_birthday < today:
                next_birthday = datetime(today.year + 1, birthday.month, birthday.day)
            return (next_birthday - today).days
        return None

    def __str__(self):
        string_for_phones = f", phones: {', '.join(str(p) for p in self.phones)}" if len(self.phones) > 0 else ""
        string_for_birthday = f", birthday: {self.birthday}, days to birthday: {self.days_to_birthday()}" if self.birthday else ""
        return f"Contact name: {self.name.value}{string_for_phones}{string_for_birthday}"
       

class AddressBook(UserDict):

    
    def add_record(self, record):
        self.data[record.name.value] = record
        self.idx = 0

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def iterator(self, n=5):
        while self.idx < len(address_book):   
            yield islice(address_book.items(), self.idx, self.idx +n)
            self.idx += n



    

    def __str__(self) -> str:
        return "\n".join(str(r) for r in self.data.values())


def main():



    while True:
        user_input = input(">>>: ")

        if user_input.lower() in ["exit", "close", "good bye"]:
            print("Goodbye!")
            break
        else:
            handler, arguments = parser(user_input)
            print(handler(*arguments))


def parser(user_input: str):
    COMMANDS = {
        "Hello": hello_func,
        "Add": add_func,
        "Change": change_func,
        "Phone": search_func,
        "Show All": show_func,
        "Show Iterated": iter_func,
        "Del": delete_func 
    }

    user_input = user_input.title()

    for kw, command in COMMANDS.items():
        if user_input.startswith(kw):
            return command, user_input[len(kw):].strip().split()
    return unknown_command, []


@deco_error
def add_func(*args):
    if len(args) < 2 or len(args[1]) < 10:
        raise ValueError
    else:
        name = args[0]
        record = Record(name)
        phone_numbers = []
        for arg in args[1:]:
            if arg.isdigit() and len(arg) == 10:
                phone_numbers.append(arg)
            else:
                try:
                    birthday = Birthday(arg)
                    record.birthday = birthday
                except ValueError:
                    pass
        for phone_number in phone_numbers:
            record.add_phone(phone_number)
        address_book.add_record(record)
        save_to_file()
        string_for_phones = f"phone number(s) {', '.join(phone_numbers)}" if len(phone_numbers) > 0 else "no phone numbers"
        string_for_birthday = f" and birthday on {birthday}" if record.birthday else ""
        return f"User {name} has been added to the phone book with {string_for_phones}{string_for_birthday}"


@deco_error
def change_func(*args):
    name = args[0]
    phone_numbers = args[1:]
    record = address_book.find(name)
    if record:
        for phone in phone_numbers:
            record.edit_phone(phone, phone)
            save_to_file()
        return f"Phone number for user {name} has been changed to {', '.join(phone_numbers)}"
    else:
        raise KeyError
    

@deco_error
def delete_func(*args):
    name = args[0]
    address_book.delete(name)
    save_to_file()
    return f"User {name} has been deleted from the phone book"


@deco_error
def iter_func(*args):
    n = int(args[-1])
    for block in address_book.iterator(n):
        input("Press Enter for next records")
        print ("\n".join(str(line[1]) for line in list(block)))    
    return "End of the phone book"



@deco_error
def search_func(*args):
    name = args[0]
    record = address_book.find(name)
    if record:
        return str(record)
    else:
        raise KeyError


@deco_error
def show_func(*args):
    return str(address_book)


def unknown_command():
    return "Unknown command. Try again."


def hello_func():
    return "How can I help you?"


def load_from_file():
    filename = "contacts.txt"
    with open (filename, "rb") as file:
        address_book = pickle.load(file)
    return address_book

def save_to_file():
    filename = "contacts.txt"
    with open (filename, "wb") as file:
        pickle.dump(address_book, file)

stat = os.stat("contacts.txt")
size = stat.st_size
if size > 0:
    address_book = AddressBook(load_from_file())
else:
    address_book = AddressBook()

if __name__ == '__main__':
    main()
