-- Таблица пользователей
CREATE TABLE IF NOT EXISTS User (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER UNIQUE NOT NULL,
    username TEXT,
    is_admin BOOLEAN DEFAULT FALSE
);

-- Таблица категорий
CREATE TABLE IF NOT EXISTS Category (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

-- Таблица уроков (статей)
CREATE TABLE IF NOT EXISTS Lesson (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL,
    sort_order INTEGER NOT NULL DEFAULT 0,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    FOREIGN KEY (category_id) REFERENCES Category(id) ON DELETE CASCADE
);

-- Таблица вопросов к урокам
CREATE TABLE IF NOT EXISTS Question (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lesson_id INTEGER NOT NULL,
    text TEXT NOT NULL,
    sort_order INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (lesson_id) REFERENCES Lesson(id) ON DELETE CASCADE
);

-- Таблица вариантов ответов
CREATE TABLE IF NOT EXISTS AnswerOption (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id INTEGER NOT NULL,
    text TEXT NOT NULL,
    is_correct BOOLEAN NOT NULL DEFAULT FALSE,
    sort_order INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (question_id) REFERENCES Question(id) ON DELETE CASCADE
);

-- Таблица прогресса пользователя (прохождение уроков)
CREATE TABLE IF NOT EXISTS UserProgress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    lesson_id INTEGER NOT NULL,
    learned BOOLEAN DEFAULT FALSE,
    completed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES User(id) ON DELETE CASCADE,
    FOREIGN KEY (lesson_id) REFERENCES Lesson(id) ON DELETE CASCADE,
    UNIQUE(user_id, lesson_id)
);

-- Таблица ответов пользователя на вопросы тестов
CREATE TABLE IF NOT EXISTS UserAnswer (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    answer_option_id INTEGER NOT NULL,
    is_correct BOOLEAN NOT NULL,
    answered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES User(id) ON DELETE CASCADE,
    FOREIGN KEY (answer_option_id) REFERENCES AnswerOption(id) ON DELETE CASCADE
);


PRAGMA foreign_keys = ON;
BEGIN TRANSACTION;

-- ==================== КАТЕГОРИИ ====================
INSERT INTO Category (id, name) VALUES (1, 'Python: Основы и синтаксис');
INSERT INTO Category (id, name) VALUES (2, 'Python: Структуры данных');
INSERT INTO Category (id, name) VALUES (3, 'Python: Функции и модули');
INSERT INTO Category (id, name) VALUES (4, 'Python: ООП и паттерны');
INSERT INTO Category (id, name) VALUES (5, 'Python: Файлы, ошибки и API');
INSERT INTO Category (id, name) VALUES (6, 'Python: Асинхронность и продвинутые темы');

-- ==================== УРОКИ (Telegram-safe HTML) ====================
INSERT INTO Lesson (id, category_id, sort_order, title, content) VALUES 
(1, 1, 1, 'Переменные, типы и динамическая типизация', '<b>Динамическая типизация</b>\nТип переменной определяется в момент присваивания и может меняться.\n\n<b>Базовые типы:</b>\n• <code>int</code> — целые числа\n• <code>float</code> — дробные числа\n• <code>str</code> — строки (Unicode)\n• <code>bool</code> — True/False\n• <code>NoneType</code> — None\n\n<pre><code>x = 10          # int\nx = "hello"     # теперь str\nprint(type(x))  # &lt;class ''str''&gt;</code></pre>\n\nПеременные в Python — это <b>ссылки на объекты</b>. Присваивание не копирует данные, а создаёт новую ссылку. Для проверки идентичности используйте <code>is</code>, для сравнения значений — <code>==</code>.'),
(2, 1, 2, 'Операторы, выражения и приоритеты', '<b>Приоритет операторов (по убыванию):</b>\n1. Скобки <code>()</code>\n2. Степень <code>**</code>\n3. Унарные <code>+</code>, <code>-</code>, <code>~</code>\n4. Арифметика <code>*</code>, <code>/</code>, <code>//</code>, <code>%</code>\n5. Сложение/вычитание <code>+</code>, <code>-</code>\n6. Сравнение <code>==</code>, <code>!=</code>, <code>&gt;</code>, <code>&lt;</code>\n7. Логические <code>not</code>, <code>and</code>, <code>or</code>\n\n<pre><code>res = 2 + 3 * 4 ** 2  # 50\nprint(5 // 2)         # 2\nprint(5 % 2)          # 1</code></pre>\n\n<code>is</code> сравнивает адреса в памяти, <code>==</code> — значения. Для чисел и строк Python кэширует объекты, поэтому <code>is</code> может вести себя неочевидно.'),
(3, 1, 3, 'Условные конструкции и match/case', '<b>Ветвление</b>\nБлоки кода выделяются отступами (4 пробела).\n\n<pre><code>age = 20\nif age &gt;= 18:\n    status = "adult"\nelif age &gt; 13:\n    status = "teen"\nelse:\n    status = "child"</code></pre>\n\n<b>Тернарный оператор:</b> <code>val = "yes" if condition else "no"</code>\n\n<b>Truthy/Falsy:</b> Пустые коллекции, <code>0</code>, <code>None</code>, <code>False</code> → <code>False</code>. Остальное → <code>True</code>.\n\n<b>match/case (Python 3.10+):</b>\n<pre><code>match cmd:\n    case "start": run()\n    case "stop" | "exit": terminate()\n    case _: print("Unknown")</code></pre>'),
(4, 1, 4, 'Циклы for/while и управление итерациями', '<b>Циклы</b>\n<code>for</code> — для перебора итерируемых объектов.\n<code>while</code> — по условию.\n\n<pre><code>for i, val in enumerate(["a", "b", "c"]):\n    print(i, val)\n\nfor name, age in zip(["A", "B"], [25, 30]):\n    print(name, age)</code></pre>\n\n<b>Управление:</b>\n• <code>break</code> — выход из цикла\n• <code>continue</code> — пропуск итерации\n• <code>else</code> после цикла — выполняется, если цикл завершился <b>без break</b>\n\n<pre><code>for n in range(5):\n    if n == 3: break\nelse:\n    print("Не сработает")</code></pre>'),
(5, 2, 1, 'Списки (list): методы, срезы, генераторы', '<b>Список</b> — изменяемая упорядоченная коллекция.\n\n<pre><code>nums = [1, 2, 3, 4, 5]\nprint(nums[1:4])    # [2, 3, 4]\nprint(nums[::-1])   # реверс\nnums.append(6)      # в конец\nnums.insert(0, 0)   # по индексу\nnums.extend([7, 8]) # распаковка</code></pre>\n\n<b>List Comprehension:</b>\n<pre><code>squares = [x**2 for x in range(10) if x % 2 == 0]</code></pre>\n\n⚠️ Не изменяйте список во время итерации. Используйте копию <code>for x in lst[:]:</code> или создавайте новый список.'),
(6, 2, 2, 'Кортежи (tuple) и множества (set)', '<b>Кортеж</b> — неизменяемый список. Защита данных и ключи словарей.\n<pre><code>point = (10, 20)\nx, y = point  # распаковка\n# point[0] = 5  # TypeError!</code></pre>\n\n<b>Множество</b> — неупорядоченная коллекция <b>уникальных</b> хешируемых элементов.\n<pre><code>a = {1, 2, 3}\nb = {3, 4, 5}\nprint(a | b)  # union: {1, 2, 3, 4, 5}\nprint(a & b)  # intersection: {3}\nprint(a - b)  # difference: {1, 2}</code></pre>\n\n<code>frozenset</code> — неизменяемое множество, может быть ключом словаря.'),
(7, 2, 3, 'Словари (dict): методы и итерация', '<b>Словарь</b> — пары <code>ключ: значение</code>. Ключи хешируемые. С Python 3.7+ сохраняют порядок.\n\n<pre><code>user = {"name": "Alice", "age": 25}\nprint(user.get("role", "guest"))\nuser["email"] = "a@b.com"\ndel user["age"]</code></pre>\n\n<b>Итерация:</b>\n<pre><code>for k, v in user.items():\n    print(k, v)\n\nsquares = {x: x**2 for x in range(5)}</code></pre>\n\nДля группировки используйте <code>collections.defaultdict(list)</code>.'),
(8, 2, 4, 'Строки и регулярные выражения', '<b>Строки</b> неизменяемы. Любая операция создаёт новую строку.\n<pre><code>s = "  Hello, World!  "\nprint(s.strip().lower())\nprint(s.replace("World", "Py"))\nprint(",".join(["a", "b"]))</code></pre>\n\n<b>f-строки (Python 3.6+):</b>\n<pre><code>name, age = "Bob", 30\nmsg = f"{name} is {age}. Next: {age + 1}"</code></pre>\n\n<b>Регулярные выражения (re):</b>\n<pre><code>import re\ntext = "Call 123-456 or 987-654"\nphones = re.findall(r"\d{3}-\d{3}", text)\n# [''123-456'', ''987-654'']</code></pre>\nКомпилируйте паттерны через <code>re.compile()</code> при повторном использовании.'),
(9, 3, 1, 'Функции, аргументы и type hints', '<b>Функции</b> определяются через <code>def</code>.\n<pre><code>def greet(name: str, times: int = 1) -&gt; list[str]:\n    return [f"Hi {name}" for _ in range(times)]</code></pre>\n\n<b>Виды аргументов:</b>\n• Позиционные\n• Именованные: <code>func(a=1)</code>\n• <code>*args</code>: кортеж позиционных\n• <code>**kwargs</code>: словарь именованных\n\n⚠️ <b>Ловушка изменяемых значений по умолчанию:</b>\n<pre><code># ПЛОХО: def add(item, lst=[]):\n# ХОРОШО:\ndef add(item, lst=None):\n    if lst is None: lst = []\n    lst.append(item)\n    return lst</code></pre>'),
(10, 3, 2, 'Области видимости (LEGB) и замыкания', '<b>LEGB:</b>\n1. <b>L</b>ocal — внутри функции\n2. <b>E</b>nclosing — во внешних функциях\n3. <b>G</b>lobal — уровень модуля\n4. <b>B</b>uilt-in — встроенные\n\n<pre><code>x = 10  # Global\ndef outer():\n    y = 5  # Enclosing\n    def inner():\n        z = 2  # Local\n        return x + y + z\n    return inner</code></pre>\n\n<b>Замыкание</b> запоминает переменные из внешней области. Используется в декораторах и фабриках.\n<code>global</code> и <code>nonlocal</code> позволяют изменять внешние переменные, но используйте их осторожно.'),
(11, 3, 3, 'Декораторы и functools.wraps', '<b>Декоратор</b> расширяет поведение функции без изменения её кода.\n<pre><code>import functools, time\n\ndef timer(func):\n    @functools.wraps(func)\n    def wrapper(*args, **kwargs):\n        start = time.perf_counter()\n        res = func(*args, **kwargs)\n        print(f"{func.__name__}: {time.perf_counter()-start:.4f}s")\n        return res\n    return wrapper\n\n@timer\ndef heavy_calc():\n    sum(i**2 for i in range(10**6))</code></pre>\n\n<code>@functools.wraps</code> сохраняет <code>__name__</code> и <code>__doc__</code>. Декораторы применяются снизу вверх.'),
(12, 3, 4, 'Модули, пакеты и venv', '<b>Модуль</b> — файл <code>.py</code>. <b>Пакет</b> — директория.\n<pre><code>if __name__ == "__main__":\n    print("Запущен напрямую")</code></pre>\nКонструкция позволяет запускать код только при прямом вызове файла.\n\n<b>Виртуальные окружения:</b>\n<pre><code>python -m venv venv\nsource venv/bin/activate  # Linux/macOS\nvenv\\Scripts\\activate     # Windows\npip install requests\npip freeze &gt; requirements.txt</code></pre>\nВсегда изолируйте зависимости проектов.'),
(13, 4, 1, 'Классы, объекты и методы', '<b>Класс</b> — чертёж. <b>Объект</b> — экземпляр с данными и поведением.\n<pre><code>class User:\n    role = "guest"  # атрибут класса\n\n    def __init__(self, name: str):\n        self.name = name  # атрибут экземпляра\n\n    def greet(self) -&gt; str:\n        return f"Hello, {self.name}"\n\nu = User("Alice")\nprint(u.greet())</code></pre>\n\n<code>self</code> — ссылка на экземпляр.\n• <code>@staticmethod</code> — обычная функция в классе\n• <code>@classmethod</code> — получает <code>cls</code>, для альтернативных конструкторов'),
(14, 4, 2, 'Наследование, MRO и super()', '<b>Наследование</b> переиспользует и расширяет функционал.\n<pre><code>class Animal:\n    def speak(self): return "..."\n\nclass Dog(Animal):\n    def speak(self): return "Woof!"</code></pre>\n\n<code>super()</code> вызывает метод родителя, соблюдая <b>MRO</b> (C3 линеаризация).\n<pre><code>class Admin(User):\n    def __init__(self, name, level):\n        super().__init__(name)\n        self.level = level</code></pre>\n\nПроверяйте типы через <code>isinstance(obj, Class)</code> и <code>issubclass(Sub, Base)</code>.'),
(15, 4, 3, 'Инкапсуляция и @property', '<b>Соглашения доступа:</b>\n• <code>public</code> — доступен везде\n• <code>_protected</code> — внутренний\n• <code>__private</code> — name mangling\n\n<b>@property</b> для контролируемого доступа:\n<pre><code>class BankAccount:\n    def __init__(self, balance: float):\n        self._balance = balance\n\n    @property\n    def balance(self) -&gt; float:\n        return self._balance\n\n    @balance.setter\n    def balance(self, value: float):\n        if value &lt; 0: raise ValueError("Negative!")\n        self._balance = value</code></pre>\nПозволяет добавить валидацию без изменения внешнего API.'),
(16, 4, 4, 'Магические методы (dunder)', 'Переопределяют поведение встроенных операций.\n<pre><code>class Vector:\n    def __init__(self, x, y):\n        self.x, self.y = x, y\n\n    def __repr__(self):\n        return f"Vector({self.x}, {self.y})"\n\n    def __add__(self, other):\n        return Vector(self.x + other.x, self.y + other.y)\n\n    def __eq__(self, other):\n        return self.x == other.x and self.y == other.y</code></pre>\n\nЧастые: <code>__len__</code>, <code>__getitem__</code>, <code>__call__</code>, <code>__enter__</code>/<code>__exit__</code>. Вызывайте их через встроенные функции и операторы, а не напрямую.'),
(17, 5, 1, 'Файловая система и pathlib', '<b>pathlib</b> (Python 3.4+) заменил <code>os.path</code>.\n<pre><code>from pathlib import Path\n\np = Path("data/logs")\np.mkdir(parents=True, exist_ok=True)\n\nfile = p / "app.txt"\nfile.write_text("Hello", encoding="utf-8")\nprint(file.read_text(encoding="utf-8"))\n\nfor f in Path(".").glob("**/*.py"):\n    print(f.name)</code></pre>\nДля бинарных файлов: <code>"rb"</code>/<code>"wb"</code>. Всегда указывайте <code>encoding="utf-8"</code>.'),
(18, 5, 2, 'JSON, CSV и сериализация', '<b>JSON:</b>\n<pre><code>import json\ndata = {"users": [{"id": 1, "active": True}]}\njson_str = json.dumps(data, indent=2, ensure_ascii=False)\nparsed = json.loads(json_str)</code></pre>\n\n<b>CSV:</b>\n<pre><code>import csv\nwith open("out.csv", "w", newline="", encoding="utf-8") as f:\n    writer = csv.DictWriter(f, fieldnames=["id", "name"])\n    writer.writeheader()\n    writer.writerow({"id": 1, "name": "Alice"})</code></pre>\n\n⚠️ <code>pickle</code> небезопасен для непроверенных данных. Используйте только для внутреннего кэша.'),
(19, 5, 3, 'Обработка исключений', 'Предотвращают крах программы.\n<pre><code>try:\n    res = 10 / int(user_input)\nexcept ValueError:\n    print("Введите число!")\nexcept ZeroDivisionError:\n    print("Деление на ноль!")\nexcept Exception as e:\n    print(f"Ошибка: {e}")\nelse:\n    print(f"Результат: {res}")\nfinally:\n    print("Выполняется всегда")</code></pre>\n\n<b>Свои исключения:</b>\n<pre><code>class PaymentError(Exception):\n    def __init__(self, code, msg):\n        self.code = code\n        super().__init__(msg)\n\nraise PaymentError(402, "Insufficient funds")</code></pre>'),
(20, 5, 4, 'HTTP-запросы и API', '<b>requests</b> — стандарт для HTTP.\n<pre><code>import requests\n\nresp = requests.get(\n    "https://api.example.com/users",\n    params={"page": 1},\n    headers={"Authorization": "Bearer TOKEN"},\n    timeout=5\n)\nresp.raise_for_status()\ndata = resp.json()\nprint(data["results"])</code></pre>\n\nPOST с JSON: <code>requests.post(url, json=payload)</code>\nВсегда используйте <code>timeout</code>. Для ретраев применяйте <code>HTTPAdapter</code> + <code>urllib3.Retry</code>.'),
(21, 6, 1, 'Итераторы и генераторы (yield)', '<b>Генераторы</b> создают итераторы лениво, экономя память.\n<pre><code>def fibonacci(n):\n    a, b = 0, 1\n    for _ in range(n):\n        yield a\n        a, b = b, a + b\n\nfor num in fibonacci(5):\n    print(num)  # 0, 1, 1, 2, 3</code></pre>\n\n<b>Generator Expression:</b> <code>(x**2 for x in range(1000000))</code> не грузит память.\nМодуль <code>itertools</code>: <code>chain</code>, <code>cycle</code>, <code>islice</code>, <code>product</code>.'),
(22, 6, 2, 'Контекстные менеджеры', 'Гарантируют освобождение ресурсов.\n<pre><code>with open("file.txt", "r") as f:\n    data = f.read()\n# f.close() вызван автоматически</code></pre>\n\n<b>Свой менеджер:</b>\n<pre><code>class Timer:\n    def __enter__(self):\n        self.start = time.perf_counter()\n        return self\n    def __exit__(self, *args):\n        print(f"Elapsed: {time.perf_counter()-self.start:.3f}s")\n        return False</code></pre>\n\n<b>@contextlib.contextmanager</b> через <code>yield</code> упрощает создание.'),
(23, 6, 3, 'Асинхронность (asyncio)', 'I/O-bound задачи конкурентно в одном потоке.\n<pre><code>import asyncio, httpx\n\nasync def fetch(url):\n    async with httpx.AsyncClient() as client:\n        resp = await client.get(url)\n        return resp.status_code\n\nasync def main():\n    urls = ["https://example.com", "https://python.org"]\n    results = await asyncio.gather(*[fetch(u) for u in urls])\n    print(results)\n\nasyncio.run(main())</code></pre>\n\n⚠️ Правила:\n• Вызывать <code>async def</code> только через <code>await</code>\n• Не использовать блокирующие вызовы (<code>time.sleep</code>, <code>requests</code>)\n• Для CPU-bound задач asyncio не подходит'),
(24, 6, 4, 'Многопоточность и GIL', '<b>GIL</b> позволяет выполнять один поток байткода одновременно.\n\n<b>Когда что использовать:</b>\n• <code>threading</code> — I/O-bound (сеть, диск)\n• <code>multiprocessing</code> — CPU-bound (вычисления, ML)\n• <code>asyncio</code> — тысячи I/O соединений\n\n<pre><code>from concurrent.futures import ProcessPoolExecutor\n\ndef heavy_cpu(n):\n    return sum(i*i for i in range(n))\n\nwith ProcessPoolExecutor() as executor:\n    results = executor.map(heavy_cpu, [10**7, 10**7])\n    print(list(results))</code></pre>\nПроцессы обходят GIL, но IPC дороже.');

-- ==================== ВОПРОСЫ ====================
INSERT INTO Question (id, lesson_id, text, sort_order) VALUES 
(1, 1, 'Что произойдёт при выполнении x = 10; x = "text"; в Python?', 0),
(2, 2, 'Чему равно выражение 2 + 3 * 4 ** 2?', 0),
(3, 3, 'Когда выполняется блок else после цикла for?', 0),
(4, 4, 'Что вернёт list(zip([1, 2], ["a", "b", "c"]))?', 0),
(5, 5, 'Какой метод списка добавляет элементы из другого итерируемого объекта в конец?', 0),
(6, 6, 'Какое свойство отличает множество (set) от списка?', 0),
(7, 7, 'Что вернёт user.get("role", "guest"), если ключа "role" нет в словаре?', 0),
(8, 8, 'Какой способ форматирования строк считается самым быстрым в современном Python?', 0),
(9, 9, 'Почему опасно использовать изменяемый объект (например, []) в качестве значения аргумента по умолчанию?', 0),
(10, 10, 'В каком порядке Python ищет переменные по правилу LEGB?', 0),
(11, 11, 'Для чего нужен @functools.wraps внутри декоратора?', 0),
(12, 12, 'Что делает конструкция if __name__ == "__main__":?', 0),
(13, 13, 'Чем отличается атрибут класса от атрибута экземпляра?', 0),
(14, 14, 'Что определяет MRO (Method Resolution Order) в Python?', 0),
(15, 15, 'Какое преимущество даёт использование @property вместо публичного атрибута?', 0),
(16, 16, 'Какой магический метод вызывается при использовании оператора +?', 0),
(17, 17, 'Какой модуль рекомендуется использовать для работы с путями в современном Python?', 0),
(18, 18, 'Почему не рекомендуется использовать pickle для данных из непроверенных источников?', 0),
(19, 19, 'Когда выполняется блок else в конструкции try/except/else?', 0),
(20, 20, 'Что делает метод response.raise_for_status() в библиотеке requests?', 0),
(21, 21, 'Какое ключевое слово превращает обычную функцию в генератор?', 0),
(22, 22, 'Что должен вернуть метод __exit__ контекстного менеджера, чтобы подавить исключение?', 0),
(23, 23, 'Почему нельзя использовать time.sleep() внутри async-функции?', 0),
(24, 24, 'Для каких задач в Python лучше всего подходит multiprocessing?', 0);

-- ==================== ВАРИАНТЫ ОТВЕТОВ ====================
INSERT INTO AnswerOption (id, question_id, text, is_correct, sort_order) VALUES 
(1, 1, 'Ошибка TypeError из-за смены типа', 0, 0),
(2, 1, 'x станет строкой, тип определится динамически', 1, 1),
(3, 1, 'x останется числом, строка проигнорируется', 0, 2),
(4, 1, 'Создастся кортеж (10, "text")', 0, 3),
(5, 2, '400', 0, 0),
(6, 2, '50', 1, 1),
(7, 2, '20', 0, 2),
(8, 2, '14', 0, 3),
(9, 3, 'Всегда после завершения цикла', 0, 0),
(10, 3, 'Только если цикл завершился без break', 1, 1),
(11, 3, 'Только при возникновении исключения', 0, 2),
(12, 3, 'Никогда, else не работает с циклами', 0, 3),
(13, 4, '[(1, "a"), (2, "b"), (3, "c")]', 0, 0),
(14, 4, '[(1, "a"), (2, "b")]', 1, 1),
(15, 4, 'Ошибка ValueError', 0, 2),
(16, 4, '[1, 2, "a", "b", "c"]', 0, 3),
(17, 5, 'append()', 0, 0),
(18, 5, 'insert()', 0, 1),
(19, 5, 'extend()', 1, 2),
(20, 5, 'update()', 0, 3),
(21, 6, 'Сохраняет порядок элементов', 0, 0),
(22, 6, 'Хранит только уникальные хешируемые элементы', 1, 1),
(23, 6, 'Поддерживает индексацию по номеру', 0, 2),
(24, 6, 'Является изменяемым словарём', 0, 3),
(25, 7, 'KeyError', 0, 0),
(26, 7, 'None', 0, 1),
(27, 7, '"guest"', 1, 2),
(28, 7, 'Пустую строку', 0, 3),
(29, 8, 'str.format()', 0, 0),
(30, 8, 'Конкатенация через +', 0, 1),
(31, 8, 'f-строки (f"...")', 1, 2),
(32, 8, 'Оператор %', 0, 3),
(33, 9, 'Это ускоряет выполнение функции', 0, 0),
(34, 9, 'Объект создаётся один раз и используется во всех вызовах', 1, 1),
(35, 9, 'Python автоматически очищает память после вызова', 0, 2),
(36, 9, 'Это вызывает SyntaxError', 0, 3),
(37, 10, 'Global → Local → Built-in → Enclosing', 0, 0),
(38, 10, 'Local → Enclosing → Global → Built-in', 1, 1),
(39, 10, 'Built-in → Global → Enclosing → Local', 0, 2),
(40, 10, 'Local → Global → Enclosing → Built-in', 0, 3),
(41, 11, 'Ускоряет выполнение декоратора', 0, 0),
(42, 11, 'Сохраняет __name__ и __doc__ оригинальной функции', 1, 1),
(43, 11, 'Разрешает передачу *args и **kwargs', 0, 2),
(44, 11, 'Делает декоратор асинхронным', 0, 3),
(45, 12, 'Запускает код только при импорте модуля', 0, 0),
(46, 12, 'Запускает код только при прямом выполнении файла', 1, 1),
(47, 12, 'Останавливает выполнение программы', 0, 2),
(48, 12, 'Создаёт виртуальное окружение', 0, 3),
(49, 13, 'Атрибут класса общий для всех экземпляров, экземплярный уникален', 1, 0),
(50, 13, 'Атрибут класса нельзя изменить', 0, 1),
(51, 13, 'Экземплярный атрибут доступен без создания объекта', 0, 2),
(52, 13, 'Разницы нет, это синонимы', 0, 3),
(53, 14, 'Порядок создания объектов в памяти', 0, 0),
(54, 14, 'Порядок поиска методов при множественном наследовании', 1, 1),
(55, 14, 'Скорость выполнения методов класса', 0, 2),
(56, 14, 'Приоритет операторов внутри класса', 0, 3),
(57, 15, 'Ускоряет доступ к данным в 2 раза', 0, 0),
(58, 15, 'Позволяет добавить валидацию/логику без изменения внешнего API', 1, 1),
(59, 15, 'Делает атрибут полностью приватным', 0, 2),
(60, 15, 'Разрешает множественное наследование', 0, 3),
(61, 16, '__str__', 0, 0),
(62, 16, '__add__', 1, 1),
(63, 16, '__sum__', 0, 2),
(64, 16, '__plus__', 0, 3),
(65, 17, 'os.path', 0, 0),
(66, 17, 'pathlib', 1, 1),
(67, 17, 'sys.files', 0, 2),
(68, 17, 'shutil', 0, 3),
(69, 18, 'Он работает слишком медленно', 0, 0),
(70, 18, 'Он может выполнить произвольный код при десериализации', 1, 1),
(71, 18, 'Он не поддерживает кириллицу', 0, 2),
(72, 18, 'Он устарел и удалён из Python 3.12', 0, 3),
(73, 19, 'Всегда, независимо от ошибок', 0, 0),
(74, 19, 'Только если в блоке try не возникло исключений', 1, 1),
(75, 19, 'Только при возникновении исключения', 0, 2),
(76, 19, 'Никогда, else не используется с try', 0, 3),
(77, 20, 'Возвращает JSON-ответ', 0, 0),
(78, 20, 'Выбрасывает HTTPError при статусе 4xx или 5xx', 1, 1),
(79, 20, 'Закрывает соединение с сервером', 0, 2),
(80, 20, 'Повторяет запрос 3 раза при ошибке', 0, 3),
(81, 21, 'return', 0, 0),
(82, 21, 'yield', 1, 1),
(83, 21, 'generate', 0, 2),
(84, 21, 'async', 0, 3),
(85, 22, 'None', 0, 0),
(86, 22, 'False', 0, 1),
(87, 22, 'True', 1, 2),
(88, 22, 'Любое строковое значение', 0, 3),
(89, 23, 'Он вызывает SyntaxError', 0, 0),
(90, 23, 'Он блокирует весь event loop, останавливая другие задачи', 1, 1),
(91, 23, 'Он не поддерживается в Python 3.10+', 0, 2),
(92, 23, 'Он автоматически превращается в await', 0, 3),
(93, 24, 'Для сетевых запросов и работы с БД', 0, 0),
(94, 24, 'Для CPU-нагруженных вычислений, обходящих GIL', 1, 1),
(95, 24, 'Для создания графических интерфейсов', 0, 2),
(96, 24, 'Для асинхронной обработки веб-сокетов', 0, 3);

COMMIT;
