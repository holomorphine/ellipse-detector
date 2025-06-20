# EllipseDetector

Приложение для обнаружения эллиптических объектов на изображениях.

## Установка и запуск

### Требования

- Python 3.7 или выше
- Windows, macOS или Linux

### Установка

#### Linux:
1. **Установка зависимостей:**
    ```bash
    sudo apt install python3-numpy python3-opencv python3-pil python3-ttkthemes python3-pil.imagetk python3-tk
    ```

2. **Запуск приложения:**
    ```bash
    python3 main.py
    ```


#### Windows:
1. **Установка зависимостей:**
   ```bash
   pip install numpy opencv-python pillow ttkthemes
   ```

2. **Запуск приложения:**
   ```bash
   python main.py
   ```

## Описание приложения

### Основной интерфейс

Программа имеет графический интерфейс с двумя вкладками:

#### Вкладка "Предобработка"

Содержит параметры для настройки предобработки изображения перед поиском эллиптических объектов:

**Пороговая обработка:**
- **Порог** - значение порога для бинаризации изображения (0-255)

**Детектор границ Canny:**
- **Размер окна** - размер апертуры для оператора Собеля:
  - 3×3 (детально) - для выделения мелких деталей
  - 5×5 (средне) - для более сильного подавления шума
  - 7×7 (гладко) - для сильного подавления шума

**Морфологические операции:**
- **Эрозия** - уменьшение размера объектов
- **Дилатация** - увеличение размера объектов

**Фильтры:**

- Билатеральный фильтр
- Гауссово размытие
- Медианный фильтр

#### Вкладка "Фильтрация"

Содержит параметры для фильтрации найденных объектов

**Метод подсчета ошибки:**
- **Алгебраический** - при подсчете ошибки аппроксимации использует алгебраическую ошибку
- **Геометрический (метод Ньютона)** - при подсчете ошибки аппроксимации использует геометрическую ошибку, которая вычисляется с помощью метода Ньютона
- **Геометрический (упрощенный)** - упрощенная версия геометрического метода, вычисляет приближенную геометрическую ошибку

**Опции отображения:**
- **Закрасить эллиптические контуры** - заливка найденных контуров цветом
- **Отображать эллипсы** - показывать аппроксимирующие эллипсы для контуров, прошедших фильтрацию

**Метод выделения контуров:**
- **Внешние контуры** - только внешние границы объектов
- **Все контуры** - все найденные контуры, включая внутренние

**Параметры фильтрации:**
- **Error Exponent** - порядок максимально допустимой ошибки аппроксимации
- **Error Exponent** - величина, на которую умножается максимально допустимая ошибка аппроксимации, позволяет более точно настроить пороговое значение ошибки
- **Min Area** - минимально допустимая площадь аппроксимирующего эллипса 
- **Max Aspect Ratio** - максимально допустимое отношение большей полуоси эллипса к его меньшей полуоси
- **Area Error** - максимально допустимая относительная ошибка между площадью аппроксимирующего эллипса и площадью контура объекта 

### Использование

1. **Загрузка изображения:** Нажмите кнопку "Загрузить изображение" и выберите файл
2. **Настройка параметров:** Используйте элементы управления на вкладках для настройки предобработки изображения и фильтрации найденных объектов
3. **Просмотр результатов:** Программа автоматически обновляет результаты при изменении параметров, результаты отображаются в окнах:
    - **Обработанное изображение** - результат бинаризации изображения после всех предобработок (запускается в свернутом виде)
    - **Границы объектов** - результат детекции границ (запускается в свернутом виде)
    - **Итоговое изображение** - исходное изображение с найденными эллипсами и выделенными контурами
4. **Сохраненить изображение:** Нажмите "Сохранить изображение" для сохранения обработанного изображения
5. **Сбросить параметры:** Нажмите кнопку "Сбросить параметры" для возвращения всех настроек к значениям по умолчанию

## Настройка параметров по умолчанию

Все параметры по умолчанию и константы хранятся в файле `defaults.py`. Вы можете изменить их, отредактировав соответствующие значения.

## Медленная работа
При изменении параметров предобработки с включенным отображением эллипсов приложение может медленно работать. Для улучшения скорости работы отключайте отображение эллипсов при изменении настроек предобработки.