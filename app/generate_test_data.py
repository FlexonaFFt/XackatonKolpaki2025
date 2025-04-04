import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.database import get_db, User, Post, UserLike, create_tables
from app.auth import get_password_hash

# Константы для генерации данных
NUM_USERS = 50
NUM_POSTS = 200
NUM_CATEGORIES = 5
LIKES_PER_USER_MIN = 5
LIKES_PER_USER_MAX = 20

# Категории постов в числовом виде
CATEGORIES = list(range(NUM_CATEGORIES))  # [0, 1, 2, 3, 4]

# Соответствие числовых категорий текстовым (для удобства)
CATEGORY_NAMES = {
    0: "Технологии",
    1: "Наука",
    2: "Искусство",
    3: "Спорт",
    4: "Кулинария"
}

# Примеры заголовков постов для каждой категории
TITLES = {
    0: [  # Технологии
        "Новый прорыв в искусственном интеллекте",
        "Как блокчейн меняет финансовую индустрию",
        "Обзор последних смартфонов 2023 года",
        "Будущее квантовых компьютеров",
        "Тренды в разработке мобильных приложений"
    ],
    1: [  # Наука
        "Открытие новой экзопланеты в зоне обитаемости",
        "Прорыв в исследовании стволовых клеток",
        "Новые данные о темной материи",
        "Как изменение климата влияет на экосистемы",
        "Последние достижения в генной инженерии"
    ],
    2: [  # Искусство
        "Обзор выставки современного искусства",
        "История импрессионизма в живописи",
        "Влияние цифровых технологий на искусство",
        "Новые тенденции в архитектуре",
        "Как музыка влияет на мозг человека"
    ],
    3: [  # Спорт
        "Итоги чемпионата мира по футболу",
        "Как правильно тренироваться для марафона",
        "Новые рекорды в олимпийских видах спорта",
        "Питание для профессиональных спортсменов",
        "История развития баскетбола"
    ],
    4: [  # Кулинария
        "Лучшие рецепты итальянской кухни",
        "Секреты приготовления идеального стейка",
        "Тренды в веганской кулинарии",
        "Как правильно выбирать специи",
        "История шоколада и его производство"
    ]
}

# Примеры содержания постов
CONTENT_TEMPLATES = [
    "В этой статье мы рассмотрим {topic}. Это очень интересная тема, которая заслуживает внимания.",
    "Сегодня мы поговорим о {topic}. Это важная тема для всех, кто интересуется данной областью.",
    "{topic} - это то, что волнует многих людей. Давайте разберемся в этом вопросе подробнее.",
    "Многие задаются вопросом о {topic}. В этой статье мы постараемся дать исчерпывающий ответ.",
    "Если вы интересуетесь {topic}, то эта статья для вас. Мы собрали самую актуальную информацию."
]

def generate_test_data():
    # Создаем таблицы, если они еще не существуют
    create_tables()
    
    # Получаем сессию базы данных
    db = next(get_db())
    
    try:
        # Очищаем существующие данные
        db.query(UserLike).delete()
        db.query(Post).delete()
        db.query(User).delete()
        db.commit()
        
        print("Генерация пользователей...")
        # Создаем пользователей
        users = []
        for i in range(NUM_USERS):
            is_admin = i == 0  # Первый пользователь - админ
            username = f"user{i}" if i > 0 else "admin"
            password = "password123"
            hashed_password = get_password_hash(password)
            
            user = User(
                username=username,
                password=hashed_password,
                is_admin=is_admin
            )
            db.add(user)
            users.append(user)
        
        db.commit()
        
        print("Генерация постов...")
        # Создаем посты
        posts = []
        start_date = datetime.now() - timedelta(days=365)
        for i in range(NUM_POSTS):
            category_id = random.choice(CATEGORIES)
            title = random.choice(TITLES[category_id])
            content_template = random.choice(CONTENT_TEMPLATES)
            content = content_template.format(topic=title.lower())
            
            # Случайная дата публикации в пределах последнего года
            days_offset = random.randint(0, 365)
            published_at = start_date + timedelta(days=days_offset)
            
            post = Post(
                title=title,
                content=content,
                published_at=published_at,
                category=str(category_id)  # Сохраняем категорию как строку с числом
            )
            db.add(post)
            posts.append(post)
        
        db.commit()
        
        print("Генерация лайков...")
        # Создаем лайки
        for user in users:
            # Каждый пользователь лайкает случайное количество постов
            num_likes = random.randint(LIKES_PER_USER_MIN, LIKES_PER_USER_MAX)
            liked_posts = random.sample(posts, num_likes)
            
            for post in liked_posts:
                like = UserLike(
                    user_id=user.id,
                    post_id=post.id
                )
                db.add(like)
        
        db.commit()
        
        print(f"Успешно создано {NUM_USERS} пользователей, {NUM_POSTS} постов и примерно {NUM_USERS * (LIKES_PER_USER_MIN + LIKES_PER_USER_MAX) // 2} лайков.")
        print("Данные для тестирования:")
        print(f"Логин: admin, Пароль: password123 (Администратор)")
        print(f"Логин: user1, Пароль: password123 (Обычный пользователь)")
        
        # Вывод соответствия категорий для справки
        print("\nСоответствие числовых категорий текстовым:")
        for cat_id, cat_name in CATEGORY_NAMES.items():
            print(f"Категория {cat_id}: {cat_name}")
        
    except Exception as e:
        db.rollback()
        print(f"Ошибка при генерации данных: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    generate_test_data()