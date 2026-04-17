import logging
from app.db.session import SessionLocal
from app.db.models import Group
from app.db.models import Industry

# Настройка логирования, чтобы видеть процесс в консоли
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DEFAULT_GROUPS = [
    {
        "vk_id": 3917270, 
        "screen_name": "kudakrsk", 
        "title": "Афиша Красноярска: куда сходить?", 
        "url": "https://vk.ru/kudakrsk"
    },
     {
        "vk_id": 2612421, 
        "screen_name": "tvknew", 
        "title": "ТВК Красноярск", 
        "url": "https://vk.ru/tvknew"
    },
    {
        "vk_id": 17355786, 
        "screen_name": "prima_tv", 
        "title": "Прима", 
        "url": "https://vk.ru/prima_tv"
    },
    {
        "vk_id": 55065233, 
        "screen_name": "ostrovtatyshev", 
        "title": "Татышев-парк", 
        "url": "https://vk.ru/ostrovtatyshev"
    },
    {
        "vk_id": 213492930, 
        "screen_name": "industry_art", 
        "title": "Сибирский институт развития креативных индустрий", 
        "url": "https://vk.ru/industry_art"
    },
    {
        "vk_id": 13989007, 
        "screen_name": "domkinokrsk", 
        "title": "Дом Кино — Красноярск", 
        "url": "https://vk.ru/domkinokrsk"
    },
    {
        "vk_id": 30684980, 
        "screen_name": "museumkkkm", 
        "title": "Красноярский краевой краеведческий музей", 
        "url": "https://vk.ru/museumkkkm"
    },
    {
        "vk_id": 49566763, 
        "screen_name": "museum_surikov", 
        "title": "Красноярский художественный музей", 
        "url": "https://vk.ru/museum_surikov"
    },
        {
        "vk_id": 5081750, 
        "screen_name": "sibdrama", 
        "title": "Красноярский Театр Пушкина", 
        "url": "https://vk.ru/sibdrama"
    },
    {
        "vk_id": 3724300, 
        "screen_name": "muzteatr24", 
        "title": "Красноярский музыкальный театр", 
        "url": "https://vk.ru/muzteatr24"
    },
    {
        "vk_id": 210964271, 
        "screen_name": "krasgid", 
        "title": "Гид по Красноярску", 
        "url": "https://vk.ru/krasgid"
    },
    {
        "vk_id": 75261020, 
        "screen_name": "bellinimedia", 
        "title": "Bellini Media", 
        "url": "https://vk.ru/bellinimedia"
    },
    {
        "vk_id": 211194385, 
        "screen_name": "galka__mag", 
        "title": "ГАЛКА I Красноярск", 
        "url": "https://vk.ru/galka__mag"
    },
    {
        "vk_id": 121269719, 
        "screen_name": "krasnoyarskrf", 
        "title": "Город Красноярск", 
        "url": "https://vk.ru/krasnoyarskrf"
    },
    {
        "vk_id": 47136765, 
        "screen_name": "nasbori5minut", 
        "title": "5 минут на сборы: Афиша в Красноярске", 
        "url": "https://vk.ru/nasbori5minut"
    },
    {
        "vk_id": 47493956, 
        "screen_name": "ilovekrsk", 
        "title": "Я Люблю Красноярск", 
        "url": "https://vk.ru/ilovekrsk"
    },
    {
        "vk_id": 79613817, 
        "screen_name": "gdemne", 
        "title": "Лучшее в Красноярске", 
        "url": "https://vk.ru/gdemne"
    },
    {
        "vk_id": 37705620, 
        "screen_name": "berrywoodfamily", 
        "title": "Berrywood Family", 
        "url": "https://vk.ru/berrywoodfamily"
    },
    {
        "vk_id": 33409110, 
        "screen_name": "pr.mira", 
        "title": "Проспект Мира", 
        "url": "https://vk.ru/pr.mira"
    },
    {
        "vk_id": 34183390, 
        "screen_name": "live_kras", 
        "title": "Я живу в Красноярске", 
        "url": "https://vk.com/live_kras"
    },
    {
        "vk_id": 17763347, 
        "screen_name": "gorodprima", 
        "title": "Сайт «Город Прима»", 
        "url": "https://vk.com/gorodprima"
    },
    {
        "vk_id": 223470435, 
        "screen_name": "davaite_pereidem", 
        "title": "Давайте перейдём • пространство в Красноярске", 
        "url": "https://vk.com/davaite_pereidem"
    },
    {
        "vk_id": 89881522, 
        "screen_name": "kultura_24", 
        "title": "Культура24 — Минкультуры Красноярского края", 
        "url": "https://vk.com/kultura_24"
    },
    {
        "vk_id": 234322356, 
        "screen_name": "vkusno_em_krsk", 
        "title": "Ем недорого и вам советую - Красноярск", 
        "url": "https://vk.com/vkusno_em_krsk"
    },
    {
        "vk_id": 229582822, 
        "screen_name": "okolo_media", 
        "title": "Около Медиа | Красноярск", 
        "url": "https://vk.com/okolo_media"
    },
    {
        "vk_id": 2140264, 
        "screen_name": "krasafisha", 
        "title": "ГЛАВНЫЙ ПО АФИШЕ: Куда сходить в Красноярске", 
        "url": "https://vk.com/krasafisha"
    },
    {
        "vk_id": 235993102, 
        "screen_name": "eto_komnata_otdyha", 
        "title": "комната отдыха", 
        "url": "https://vk.com/eto_komnata_otdyha"
    },
]

DEFAULT_INDUSTRIES = [
    {"name": "Культура", "description": "События в музеях, театрах, выставки и концерты в Красноярске."},
    {"name": "Городская среда", "description": "Благоустройство, дороги, ЖКХ, транспорт и изменения в инфраструктуре."},
    {"name": "Экология", "description": "Состояние воздуха (НМУ), природа, Столбы и экологические инициативы."},
    {"name": "Спорт", "description": "Местные спортивные команды (Енисей, Сокол), марафоны и спортивные объекты."},
    {"name": "Происшествия", "description": "ДТП, пожары, оперативные сводки и экстренные события."},
    {"name": "Общество", "description": "Социальные новости, образование, праздники и жизнь горожан."},
    {"name": "Экономика", "description": "Бизнес, открытие новых заведений, цены и работа предприятий."},
    {"name": "Гастрономия", "description": "Ресторанная индустрия Красноярска: открытия заведений, гастрофестивали, авторская кухня и обзоры локальных шеф-поваров."},
]

def seed_data():
    db = SessionLocal()
    try:
        logger.info("Начало наполнения базы данных базовыми группами...")
        for g_data in DEFAULT_GROUPS:
            # Проверяем, нет ли уже группы с таким vk_id
            existing_group = db.query(Group).filter(Group.vk_id == g_data["vk_id"]).first()
            
            if not existing_group:
                new_group = Group(
                    vk_id=g_data["vk_id"],
                    screen_name=g_data["screen_name"],
                    title=g_data["title"],
                    url=g_data["url"]
                )
                db.add(new_group)
                logger.info(f"Добавлена новая группа: {g_data['title']}")
            else:
                logger.info(f"Группа '{g_data['title']}' уже есть в базе, пропускаю.")
        
        db.commit()
        logger.info("Наполнение базы завершено успешно.")
    except Exception as e:
        db.rollback()
        logger.error(f"Ошибка при наполнении базы: {e}")
    finally:
        db.close()

def seed_industries():
    db = SessionLocal()
    print("Начало наполнения категорий...")

    for ind_data in DEFAULT_INDUSTRIES:
        # Проверяем, существует ли уже категория с таким именем
        exists = db.query(Industry).filter(Industry.name == ind_data["name"]).first()
        
        if not exists:
            new_industry = Industry(
                name=ind_data["name"],
                description=ind_data["description"]
            )
            db.add(new_industry)
            print(f"Добавлена категория: {ind_data['name']}")
        else:
            print(f"Категория '{ind_data['name']}' уже есть в базе.")

    try:
        db.commit()
        print("Категории успешно сохранены.")
    except Exception as e:
        db.rollback()
        print(f"Ошибка при сохранении категорий: {e}")



if __name__ == "__main__":
    seed_data()
    seed_industries()
