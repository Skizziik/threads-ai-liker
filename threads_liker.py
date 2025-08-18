
import asyncio
import random
from pathlib import Path
from playwright.async_api import async_playwright, TimeoutError

# --- Настройки ---
SEARCH_QUERY = "ai"  # Тема для поиска
MAX_LIKES_TO_LIKE = 5  # Максимальное количество лайков у поста, чтобы его лайкнуть
LIKE_COOLDOWN_SECONDS = 20  # Пауза между лайками (20 секунд = 3 лайка в минуту)
USER_DATA_DIR = "./user_data"  # Папка для хранения данных сессии

# --- CSS Селекторы (ВАЖНО: их может потребоваться обновить) ---
# Эти селекторы нужно будет проверить и, возможно, скорректировать с помощью
# инструментов разработчика в браузере (правый клик -> "Проверить" или "Inspect").

# Селектор для отдельного поста в ленте
POST_SELECTOR = "div[data-pressable-container='true']"

# Селектор для кнопки "Нравится" внутри поста.
# Ищем по aria-label, что обычно более надежно.
LIKE_BUTTON_SELECTOR = "button[aria-label='Нравится']" # Может быть 'Like' в англ. версии

# Селектор для элемента, где отображается количество лайков.
# Это самый сложный селектор, так как текст может быть разным.
# Например, "11 отметок "Нравится"" или "11 likes".
# Этот селектор должен указывать на контейнер, из которого можно извлечь число.
LIKE_COUNT_SELECTOR = "a[href$='/likes/']" # Пример: ищем ссылку, ведущую на страницу лайков

# Селектор для поля поиска
search_icon_selector = "svg[aria-label='Поиск']" # Может быть 'Search'

async def main():
    async with async_playwright() as p:
        # Проверяем, существует ли папка с данными пользователя
        if not Path(USER_DATA_DIR).exists():
            print("--- Первый запуск ---")
            print("Папка с данными сессии не найдена. Запускаем браузер для ручного входа.")
            print("Пожалуйста, войдите в свой аккаунт Threads.")
            print("После успешного входа можете закрыть окно браузера.")
            
            # Запускаем браузер без сохранения данных, чтобы пользователь мог войти
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            page = await context.new_page()
            await page.goto("https://www.threads.net")

            # Ждем, пока пользователь закроет страницу (вкладку)
            print("Ожидаем закрытия окна/вкладки браузера...")
            closed_future = asyncio.Future()
            page.on("close", lambda: closed_future.set_result(None))
            await closed_future
            
            # Создаем папку, если ее нет
            Path(USER_DATA_DIR).mkdir(exist_ok=True)
            
            # Сохраняем состояние аутентификации
            await context.storage_state(path=f"{USER_DATA_DIR}/storage_state.json")
            print("Данные сессии сохранены. Перезапустите скрипт для начала работы.")
            return

        # --- Последующие запуски ---
        print("Обнаружены данные сессии. Запускаем в автоматическом режиме.")
        
        browser = await p.chromium.launch(headless=False) # Можно поставить True для скрытого режима
        context = await browser.new_context(storage_state=f"{USER_DATA_DIR}/storage_state.json")
        page = await context.new_page()

        try:
            print(f"Переходим на страницу Threads и ищем '{SEARCH_QUERY}'...")
            await page.goto("https://www.threads.net", wait_until="load", timeout=60000)
            await asyncio.sleep(random.uniform(3, 5))

            # Делаем скриншот для отладки
            await page.screenshot(path="debug_screenshot.png")
            print("Сделан скриншот 'debug_screenshot.png'. Пожалуйста, посмотрите на него, чтобы понять, как выглядит страница и где находится поле поиска.")

            # Кликаем на иконку поиска, чтобы активировать поле ввода
            # На Threads может потребоваться сначала кликнуть на иконку лупы
            search_icon_selector = "a[aria-label='Search']" # Может быть 'Search'
            try:
                await page.locator(search_icon_selector).first.click(timeout=15000)
                print("Кликнули на иконку поиска.")
            except TimeoutError:
                print("Не удалось найти иконку поиска, возможно, поле ввода уже доступно.")

            await page.locator('input[aria-label="Search"]').first.fill(SEARCH_QUERY) # Используем более конкретный селектор для поля ввода
            await page.keyboard.press("Enter")
            print(f"Выполнен поиск по запросу: {SEARCH_QUERY}")
            
            await page.wait_for_load_state("networkidle", timeout=30000)
            await asyncio.sleep(random.uniform(3, 5))

            liked_posts_count = 0
            
            while True:
                posts = await page.query_selector_all(POST_SELECTOR)
                print(f"Найдено {len(posts)} постов на странице. Начинаем проверку...")

                for post in posts:
                    try:
                        # Проверяем, есть ли у поста кнопка "Нравится"
                        like_button = post.locator(LIKE_BUTTON_SELECTOR).first
                        if not await like_button.is_visible():
                            continue

                        # Проверяем количество лайков
                        likes_count = 0
                        like_count_element = post.locator(LIKE_COUNT_SELECTOR).first
                        
                        if await like_count_element.is_visible(timeout=1000):
                            text_content = await like_count_element.text_content()
                            # Извлекаем только цифры из текста
                            numbers = ''.join(filter(str.isdigit, text_content))
                            if numbers:
                                likes_count = int(numbers)

                        print(f"Проверяем пост. Лайков: {likes_count}")

                        if likes_count < MAX_LIKES_TO_LIKE:
                            print(f"  -> Лайков меньше {MAX_LIKES_TO_LIKE}. Ставим лайк.")
                            await like_button.click()
                            liked_posts_count += 1
                            print(f"  -> Лайк поставлен! Всего лайкнуто: {liked_posts_count}. Ждем {LIKE_COOLDOWN_SECONDS} секунд.")
                            await asyncio.sleep(LIKE_COOLDOWN_SECONDS)
                        else:
                            print(f"  -> Слишком много лайков ({likes_count}). Пропускаем.")

                    except Exception as e:
                        # print(f"Не удалось обработать пост: {e}")
                        continue # Игнорируем ошибки для отдельных постов

                # Прокручиваем страницу вниз, чтобы загрузить новые посты
                print("Прокручиваем страницу для загрузки новых постов...")
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(random.uniform(5, 8)) # Ждем загрузки

        except TimeoutError as e:
            print(f"Ошибка времени ожидания: {e}. Возможно, страница не загрузилась или селектор не найден.")
            print("Проверьте CSS селекторы и ваше интернет-соединение.")
        except Exception as e:
            print(f"Произошла непредвиденная ошибка: {e}")
        finally:
            print("Завершение работы.")
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
