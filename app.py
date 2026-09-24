import streamlit as st
from datetime import datetime, timedelta
import os
import pandas as pd

# =========================================================================
# 1. НАЛАШТУВАННЯ ТА СПИСКИ (НАПРЯМИ, ПОСЛУГИ, ЦІНИ, ЗНИЖКИ)
# =========================================================================

ALLOWED_MASTERS = ["Микола", "Олена", "Тато", "Адмін", "Хост"]

if 'services' not in st.session_state:
    st.session_state.services = {
        # --- НАПРЯМ: Електромонтажні роботи ---
        # Підкатегорія: Штроблення та отвори
        "Штроблення під проводку в бетоні, глибина штроби 2 см": {"category": "Послуги", "field": "⚡ Електромонтажні роботи", "subcategory": "Штроблення та отвори", "price": 200, "unit": "м.пог"},
        "Штроблення під проводку в цеглі, глибина штроби 2 см": {"category": "Послуги", "field": "⚡ Електромонтажні роботи", "subcategory": "Штроблення та отвори", "price": 140, "unit": "м.пог"},
        "Влаштування ніші (цегла)": {"category": "Послуги", "field": "⚡ Електромонтажні роботи", "subcategory": "Штроблення та отвори", "price": 990, "unit": "шт"},
        "Влаштування ніші (бетон)": {"category": "Послуги", "field": "⚡ Електромонтажні роботи", "subcategory": "Штроблення та отвори", "price": 1650, "unit": "шт"},
        "Вирізка отвору та встановлення распредкоробки (бетон)": {"category": "Послуги", "field": "⚡ Електромонтажні роботи", "subcategory": "Штроблення та отвори", "price": 260, "unit": "шт"},
        "Вирізка отвору та встановлення распредкоробки (цегла)": {"category": "Послуги", "field": "⚡ Електромонтажні роботи", "subcategory": "Штроблення та отвори", "price": 190, "unit": "шт"},
        "Вирізка отвору та встановлення распредкоробки (гіпсокартон)": {"category": "Послуги", "field": "⚡ Електромонтажні роботи", "subcategory": "Штроблення та отвори", "price": 150, "unit": "шт"},
        "Свердління наскрізних отворів у стіні до 25 мм (бетон, цегла)": {"category": "Послуги", "field": "⚡ Електромонтажні роботи", "subcategory": "Штроблення та отвори", "price": 160, "unit": "шт"},
        "Влаштування отвору під вентилятор": {"category": "Послуги", "field": "⚡ Електромонтажні роботи", "subcategory": "Штроблення та отвори", "price": 545, "unit": "шт"},
        "Заделка штроби": {"category": "Послуги", "field": "⚡ Електромонтажні роботи", "subcategory": "Штроблення та отвори", "price": 60, "unit": "м.пог"},

        # Підкатегорія: Щитки, автомати, лічильники
        "Установка електрощитка": {"category": "Послуги", "field": "⚡ Електромонтажні роботи", "subcategory": "Щитки, автомати, лічильники", "price": 700, "unit": "шт"},
        "Підключення електролічильника": {"category": "Послуги", "field": "⚡ Електромонтажні роботи", "subcategory": "Щитки, автомати, лічильники", "price": 660, "unit": "шт"},
        "Установка автоматів, 1 фаза": {"category": "Послуги", "field": "⚡ Електромонтажні роботи", "subcategory": "Щитки, автомати, лічильники", "price": 190, "unit": "шт"},
        "Установка автомата, 3 фази": {"category": "Послуги", "field": "⚡ Електромонтажні роботи", "subcategory": "Щитки, автомати, лічильники", "price": 490, "unit": "шт"},
        "Встановлення силових вимикачів, ПЗВ": {"category": "Послуги", "field": "⚡ Електромонтажні роботи", "subcategory": "Щитки, автомати, лічильники", "price": 340, "unit": "шт"},
        "Монтаж та підключення стабілізатора напруги": {"category": "Послуги", "field": "⚡ Електромонтажні роботи", "subcategory": "Щитки, автомати, лічильники", "price": 1425, "unit": "шт"},
        "Перенос електрощитка в квартиру": {"category": "Послуги", "field": "⚡ Електромонтажні роботи", "subcategory": "Щитки, автомати, лічильники", "price": 2700, "unit": "шт"},
        "Установка реле напруги": {"category": "Послуги", "field": "⚡ Електромонтажні роботи", "subcategory": "Щитки, автомати, лічильники", "price": 480, "unit": "шт"},
        "Монтаж і підключення ДБЖ": {"category": "Послуги", "field": "⚡ Електромонтажні роботи", "subcategory": "Щитки, автомати, лічильники", "price": 11725, "unit": "точка"},

        # Підкатегорія: Кабелі та проводка
        "Складання розпредкоробки, розпаювання проводів": {"category": "Послуги", "field": "⚡ Електромонтажні роботи", "subcategory": "Кабелі та проводка", "price": 350, "unit": "шт"},
        "Підведення дроту та його закріплення, відкрите проведення": {"category": "Послуги", "field": "⚡ Електромонтажні роботи", "subcategory": "Кабелі та проводка", "price": 45, "unit": "м.пог"},
        "Підведення дроту та його закріплення, гофротруба тощо": {"category": "Послуги", "field": "⚡ Електромонтажні роботи", "subcategory": "Кабелі та проводка", "price": 65, "unit": "м.пог"},
        "Підведення кабелю перетином вище 4мкв.м., відкрита проводка": {"category": "Послуги", "field": "⚡ Електромонтажні роботи", "subcategory": "Кабелі та проводка", "price": 60, "unit": "м.пог"},
        "Підведення кабелю перетином вище 10 кв.м., відкрита проводка": {"category": "Послуги", "field": "⚡ Електромонтажні роботи", "subcategory": "Кабелі та проводка", "price": 80, "unit": "м.пог"},
        "Монтаж пластикового короба": {"category": "Послуги", "field": "⚡ Електромонтажні роботи", "subcategory": "Кабелі та проводка", "price": 70, "unit": "м.пог"},
        "Влаштування контуру заземлення, комплекс робіт": {"category": "Послуги", "field": "⚡ Електромонтажні роботи", "subcategory": "Кабелі та проводка", "price": 7200, "unit": "шт"},
        "Розробка схеми електропроводки": {"category": "Послуги", "field": "⚡ Електромонтажні роботи", "subcategory": "Кабелі та проводка", "price": 170, "unit": "м²"},
        "Прозвонка проводки в приміщенні": {"category": "Послуги", "field": "⚡ Електромонтажні роботи", "subcategory": "Кабелі та проводка", "price": 125, "unit": "м²"},
        "Монтаж стрічки LED освітлення в коробі": {"category": "Послуги", "field": "⚡ Електромонтажні роботи", "subcategory": "Кабелі та проводка", "price": 250, "unit": "м.пог"},

        # Підкатегорія: Розетки, вимикачі, коробки
        "Встановлення та підключення розеток та вимикачів": {"category": "Послуги", "field": "⚡ Електромонтажні роботи", "subcategory": "Розетки, вимикачі, коробки", "price": 140, "unit": "шт"},
        "Заміна електричної розетки (демонтаж + монтаж)": {"category": "Послуги", "field": "⚡ Електромонтажні роботи", "subcategory": "Розетки, вимикачі, коробки", "price": 200, "unit": "шт"},
        "Монтаж кнопки дзвінка": {"category": "Послуги", "field": "⚡ Електромонтажні роботи", "subcategory": "Розетки, вимикачі, коробки", "price": 200, "unit": "шт"},
        "Установка і підключення вхідного дзвінка": {"category": "Послуги", "field": "⚡ Електромонтажні роботи", "subcategory": "Розетки, вимикачі, коробки", "price": 290, "unit": "шт"},
        "Монтаж і установка домофона": {"category": "Послуги", "field": "⚡ Електромонтажні роботи", "subcategory": "Розетки, вимикачі, коробки", "price": 1270, "unit": "шт"},

        # Підкатегорія: Освітлення та прилади
        "Встановлення та підключення стельового світильника Армстронг": {"category": "Послуги", "field": "⚡ Електромонтажні роботи", "subcategory": "Освітлення та прилади", "price": 300, "unit": "шт"},
        "Встановлення люстри": {"category": "Послуги", "field": "⚡ Електромонтажні роботи", "subcategory": "Освітлення та прилади", "price": 535, "unit": "шт"},
        "Монтаж світильника настінного, бра": {"category": "Послуги", "field": "⚡ Електромонтажні роботи", "subcategory": "Освітлення та прилади", "price": 345, "unit": "шт"},
        "Монтаж точкового світильника (без трансформатора)": {"category": "Послуги", "field": "⚡ Електромонтажні роботи", "subcategory": "Освітлення та прилади", "price": 240, "unit": "шт"},
        "Встановлення та підключення трансформатора": {"category": "Послуги", "field": "⚡ Електромонтажні роботи", "subcategory": "Освітлення та прилади", "price": 240, "unit": "шт"},
        "Установка різних датчиків, слаботочка": {"category": "Послуги", "field": "⚡ Електромонтажні роботи", "subcategory": "Освітлення та прилади", "price": 250, "unit": "шт"},
        "Установка світильників в ступені, бетон": {"category": "Послуги", "field": "⚡ Електромонтажні роботи", "subcategory": "Освітлення та прилади", "price": 515, "unit": "шт"},
        "Установка світильників ґрунтових (без бетонної основи)": {"category": "Послуги", "field": "⚡ Електромонтажні роботи", "subcategory": "Освітлення та прилади", "price": 320, "unit": "шт"},
        "Установка світильників підводних": {"category": "Послуги", "field": "⚡ Електромонтажні роботи", "subcategory": "Освітлення та прилади", "price": 460, "unit": "шт"},
        "Установка, підключення прожектора для підсвічування будівель": {"category": "Послуги", "field": "⚡ Електромонтажні роботи", "subcategory": "Освітлення та прилади", "price": 440, "unit": "шт"},
        "Установка світлодіодних світильників": {"category": "Послуги", "field": "⚡ Електромонтажні роботи", "subcategory": "Освітлення та прилади", "price": 250, "unit": "шт"},
        "Установка врізного або канального вентилятора": {"category": "Послуги", "field": "⚡ Електромонтажні роботи", "subcategory": "Освітлення та прилади", "price": 415, "unit": "шт"},
        "Монтаж і підключення рушникосушарки електричного": {"category": "Послуги", "field": "⚡ Електромонтажні роботи", "subcategory": "Освітлення та прилади", "price": 725, "unit": "шт"},

        # Підкатегорія: Демонтаж та інше
        "Демонтаж силового кабелю": {"category": "Послуги", "field": "⚡ Електромонтажні роботи", "subcategory": "Демонтаж та інше", "price": 125, "unit": "м.пог"},
        "Демонтаж відкритої електропроводки": {"category": "Послуги", "field": "⚡ Електромонтажні роботи", "subcategory": "Демонтаж та інше", "price": 20, "unit": "м.пог"},
        "Демонтаж інших кабелів і проводки, відкритих": {"category": "Послуги", "field": "⚡ Електромонтажні роботи", "subcategory": "Демонтаж та інше", "price": 20, "unit": "м.пог"},
        "Відключення і демонтаж розеток, вимикачів, світильників": {"category": "Послуги", "field": "⚡ Електромонтажні роботи", "subcategory": "Демонтаж та інше", "price": 60, "unit": "шт"},

        # --- НАПРЯМ: Сантехнічні роботи ---
        "Монтаж змішувача": {"category": "Послуги", "field": "🚿 Сантехнічні роботи", "subcategory": "Сантехнічні прилади", "price": 450, "unit": "шт"},
        "Установка ванни / душової кабіни": {"category": "Послуги", "field": "🚿 Сантехнічні роботи", "subcategory": "Сантехнічні прилади", "price": 1500, "unit": "шт"},
        "Підключення пральної/сушильної машини": {"category": "Послуги", "field": "🚿 Сантехнічні роботи", "subcategory": "Підключення техніки", "price": 600, "unit": "шт"},
        "Розведення труб водопостачання": {"category": "Послуги", "field": "🚿 Сантехнічні роботи", "subcategory": "Монтаж труб", "price": 300, "unit": "м.пог"},

        # --- НАПРЯМ: Системи опалення ---
        "Встановлення радіатора опалення": {"category": "Послуги", "field": "🔥 Системи опалення", "subcategory": "Радіатори", "price": 800, "unit": "шт"},
        "Монтаж теплої підлоги (водяної/електричної)": {"category": "Послуги", "field": "🔥 Системи опалення", "subcategory": "Тепла підлога", "price": 250, "unit": "м²"},
        "Підключення опалювального котла": {"category": "Послуги", "field": "🔥 Системи опалення", "subcategory": "Котельня", "price": 3500, "unit": "шт"},

        # --- Матеріали ---
        "Розетка одинарна (склад)": {"category": "Матеріали", "field": "Матеріали", "subcategory": "Складські", "price": 100, "unit": "шт"},
        "Розетка одинарна (магазин)": {"category": "Матеріали", "field": "Матеріали", "subcategory": "Магазинні", "price": 300, "unit": "шт"},
        "Розетка подвійна (склад)": {"category": "Матеріали", "field": "Матеріали", "subcategory": "Складські", "price": 300, "unit": "шт"},
        "Розетка подвійна (магазин)": {"category": "Матеріали", "field": "Матеріали", "subcategory": "Магазинні", "price": 500, "unit": "шт"},
        "Лампа світлодіодна (склад)": {"category": "Матеріали", "field": "Матеріали", "subcategory": "Складські", "price": 150, "unit": "шт"},
        "Лампа світлодіодна (магазин)": {"category": "Матеріали", "field": "Матеріали", "subcategory": "Магазинні", "price": 350, "unit": "шт"},

        # --- Інше ---
        "Виїзд майстра": {"category": "Інше", "field": "Інше", "subcategory": "Інше", "price": 500, "unit": "шт"},

        # --- Знижки ---
        "Знижка Пенсіонер": {"category": "Знижки", "field": "Знижки", "subcategory": "Знижки", "price": 200, "unit": "грн"},
        "Знижка Військовий": {"category": "Знижки", "field": "Знижки", "subcategory": "Знижки", "price": 250, "unit": "грн"},
        "Знижка постійному клієнту": {"category": "Знижки", "field": "Знижки", "subcategory": "Знижки", "price": 50, "is_percent": False, "unit": "грн"},
        "Акція вихідного дня": {"category": "Знижки", "field": "Знижки", "subcategory": "Знижки", "price": 100, "is_percent": False, "unit": "грн"},
        "Знижка ВПО": {"category": "Знижки", "field": "Знижки", "subcategory": "Знижки", "price": 15, "is_percent": True, "unit": "%"},
    }

if 'cart' not in st.session_state:
    st.session_state.cart = []

if 'confirm_clear_history' not in st.session_state:
    st.session_state.confirm_clear_history = False

if 'pending_split_item' not in st.session_state:
    st.session_state.pending_split_item = None

if 'item_qty' not in st.session_state:
    st.session_state.item_qty = 1.0

# =========================================================================
# 2. РОБОТА З БАЗОЮ КЛІЄНТІВ, СКЛАДОМ ТА ІСТОРІЄЮ
# =========================================================================

def load_clients_base():
    clients_file = "clients_base.xlsx"
    expected_columns = ["Телефон", "Ім'я", "Кількість візитів", "Статус", "Коментар майстра", "Внутрішня примітка", "Останній візит", "Останній майстер"]
    
    if os.path.exists(clients_file):
        try:
            df = pd.read_excel(clients_file, dtype=str)
            if "Телефон" in df.columns:
                df["Телефон"] = df["Телефон"].astype(str).str.split('.').str[0].str.strip()
            
            if "Коментар клієнта" in df.columns and "Коментар майстра" not in df.columns:
                df = df.rename(columns={"Коментар клієнта": "Коментар майстра"})
                
            for col in expected_columns:
                if col not in df.columns:
                    if col == "Статус":
                        df["Статус"] = "Звичайний"
                    elif col == "Кількість візитів":
                        df["Кількість візитів"] = 1
                    else:
                        df[col] = ""
            df["Кількість візитів"] = pd.to_numeric(df["Кількість візитів"], errors='coerce').fillna(1).astype(int)
            return df
        except Exception:
            pass
    
    return pd.DataFrame(columns=expected_columns)

def load_warehouse_stock():
    warehouse_file = "warehouse_stock.xlsx"
    materials_list = [name for name, data in st.session_state.services.items() if data["category"] == "Матеріали" and "(склад)" in name.lower()]
    
    if os.path.exists(warehouse_file):
        try:
            df = pd.read_excel(warehouse_file, dtype=str)
            df["Залишок (шт)"] = pd.to_numeric(df["Залишок (шт)"], errors='coerce').fillna(15).astype(int)
            
            existing_materials = df["Матеріал"].tolist()
            new_rows = []
            for mat in materials_list:
                if mat not in existing_materials:
                    new_rows.append({"Матеріал": mat, "Залишок (шт)": 15})
            if new_rows:
                df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
                df.to_excel(warehouse_file, index=False)
            return df
        except Exception:
            pass
    
    initial_data = [{"Матеріал": mat, "Залишок (шт)": 15} for mat in materials_list]
    df = pd.DataFrame(initial_data)
    df.to_excel(warehouse_file, index=False)
    return df

def update_warehouse_after_sale(cart_items):
    warehouse_file = "warehouse_stock.xlsx"
    df_stock = load_warehouse_stock()
    
    for item in cart_items:
        if item["category"] == "Матеріали" and "(склад)" in item["name"].lower():
            mat_name = item["name"]
            sold_qty = item["qty"]
            if mat_name in df_stock["Матеріал"].values:
                idx = df_stock[df_stock["Матеріал"] == mat_name].index[0]
                current_qty = int(df_stock.loc[idx, "Залишок (шт)"])
                new_qty = max(0, current_qty - int(sold_qty))
                df_stock.loc[idx, "Залишок (шт)"] = new_qty
                
    df_stock.to_excel(warehouse_file, index=False)

def save_photos_locally(uploaded_files, receipt_id, master_name):
    photo_dir = "receipt_photos"
    if not os.path.exists(photo_dir):
        os.makedirs(photo_dir)
        
    saved_filenames = []
    for idx, file in enumerate(uploaded_files):
        ext = file.name.split('.')[-1]
        filename = f"chek_{receipt_id}_{master_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{idx+1}.{ext}"
        filepath = os.path.join(photo_dir, filename)
        with open(filepath, "wb") as f:
            f.write(file.getbuffer())
        saved_filenames.append(filename)
        
    return ", ".join(saved_filenames)

# =========================================================================
# 3. ІНТЕРФЕЙС ТА АВТОРИЗАЦІЯ
# =========================================================================

st.title("✂️ Система розрахунку послуг")

if 'logged_in_master' not in st.session_state:
    st.session_state.logged_in_master = ""

if not st.session_state.logged_in_master:
    st.warning("👋 Будь ласка, введіть ваше ім'я для входу (або «Адмін» для доступу в Панель хоста / «Склад» для управління залишками).")
    with st.form("login_form"):
        entered_name = st.text_input("Ім'я майстра / Вхід:")
        submit_login = st.form_submit_button("Увійти в систему", type="primary")
        
        if submit_login:
            clean_name = entered_name.strip().capitalize()
            allowed_check = ALLOWED_MASTERS + ["Склад"]
            if any(clean_name.lower() == m.lower() for m in allowed_check):
                exact_name = next(m for m in allowed_check if m.lower() == clean_name.lower())
                st.session_state.logged_in_master = "Склад" if exact_name.lower() == "склад" else exact_name
                st.rerun()
            else:
                st.error("❌ Доступ заборонено: такого користувача немає в системі.")
    st.stop()

master_name = st.session_state.logged_in_master

# =========================================================================
# АВТОРИЗАЦІЯ ПАНЕЛІ "СКЛАД / ІНВЕНТАРИЗАЦІЯ" (ІЗ ПАРОЛЕМ)
# =========================================================================
if master_name.lower() == "склад":
    st.markdown("---")
    st.subheader("🛡️ Авторизація Панелі Складу")
    warehouse_password = st.text_input("Введіть секретний пароль доступу до складу:", type="password")
    
    col_w_back1, col_w_back2 = st.columns(2)
    with col_w_back1:
        enter_warehouse = st.button("Увійти в Панель складу", type="primary")
    with col_w_back2:
        if st.button("⬅️ Вийти / Змінити користувача"):
            st.session_state.logged_in_master = ""
            st.rerun()

    if enter_warehouse:
        if warehouse_password == "1234":
            st.session_state.warehouse_authenticated = True
        else:
            st.error("❌ Неправильний пароль!")
            st.session_state.warehouse_authenticated = False

    if st.session_state.get("warehouse_authenticated", False):
        st.success("✅ Вітаємо в Панелі Складу!")
        
        col_w1, col_w2 = st.columns([2, 1])
        with col_w1:
            if st.button("⬅️ Повернутися до оформлення чеку"):
                st.session_state.logged_in_master = ""
                st.session_state.warehouse_authenticated = False
                st.rerun()
        with col_w2:
            if st.button("🔄 Оновити дані складу"):
                st.cache_data.clear()
                st.rerun()

        st.markdown("---")
        
        st.subheader("📋 Поточні залишки матеріалів на полицях")
        df_stock_view = load_warehouse_stock()
        
        def stock_status(qty):
            if qty <= 1:
                return "🔴 КРИТИЧНО (Треба докупити!)"
            elif qty <= 4:
                return "🟡 Закінчується"
            else:
                return "🟢 Достатньо"
                
        df_stock_view["Статус"] = df_stock_view["Залишок (шт)"].apply(stock_status)
        st.dataframe(df_stock_view, use_container_width=True)
        
        st.markdown("---")
        st.subheader("➕ Поповнити склад (Прихід партії)")
        with st.form("restock_form"):
            mat_to_restock = st.selectbox("Оберіть матеріал для поповнення:", df_stock_view["Матеріал"].tolist())
            qty_added = st.number_input("Кількість од. для додавання:", min_value=1, value=10, step=1)
            submit_restock = st.form_submit_button("Збільшити залишок на складі", type="primary")
            
            if submit_restock:
                idx = df_stock_view[df_stock_view["Матеріал"] == mat_to_restock].index[0]
                current_val = int(df_stock_view.loc[idx, "Залишок (шт)"])
                df_stock_view.loc[idx, "Залишок (шт)"] = current_val + int(qty_added)
                df_stock_view.to_excel("warehouse_stock.xlsx", index=False)
                st.success(f"🎉 Склад успішно поповнено! Додано {qty_added} шт. до «{mat_to_restock}».")
                st.rerun()

        st.markdown("---")
        st.subheader("🏆 Рейтинг популярності матеріалів (Списання)")
        history_file = "all_sales_history.xlsx"
        if os.path.exists(history_file):
            try:
                xls = pd.ExcelFile(history_file)
                all_history_sheets = []
                for sh in xls.sheet_names:
                    df_sh = pd.read_excel(history_file, sheet_name=sh)
                    if not df_sh.empty and "Категорія" in df_sh.columns:
                        all_history_sheets.append(df_sh)
                
                if all_history_sheets:
                    df_all_h = pd.concat(all_history_sheets, ignore_index=True)
                    df_materials_only = df_all_h[df_all_h["Категорія"] == "Матеріали"]
                    
                    if not df_materials_only.empty and "Послуга/Позиція" in df_materials_only.columns and "Кількість" in df_materials_only.columns:
                        df_materials_only["Кількість"] = pd.to_numeric(df_materials_only["Кількість"].astype(str).str.split().str[0], errors='coerce').fillna(1)
                        mat_rating = df_materials_only.groupby("Послуга/Позиція").agg(
                            Всього_списано=("Кількість", "sum"),
                            Кількість_продажів=("№ чека", "count")
                        ).reset_index().sort_values(by="Всього_списано", ascending=False)
                        
                        st.dataframe(mat_rating, use_container_width=True)
                    else:
                        st.info("Поки немає даних про списання матеріалів в чеках.")
            except Exception as e:
                st.info(f"Помилка формування рейтингу матеріалів: {e}")
        else:
            st.info("Історія чеків порожня, рейтинг матеріалів сформується після перших продажів.")

    st.stop()

# =========================================================================
# АВТОРИЗАЦІЯ ХОСТА / АДМІНІСТРАТОРА (ПАНЕЛЬ ХОСТА)
# =========================================================================
if master_name.lower() in ["адмін", "хост"]:
    st.markdown("---")
    st.subheader("🛡️ Авторизація Панелі Хоста")
    admin_password = st.text_input("Введіть секретний пароль адміністратора:", type="password")
    
    col_back1, col_back2 = st.columns(2)
    with col_back1:
        enter_admin = st.button("Увійти в Панель хоста", type="primary")
    with col_back2:
        if st.button("⬅️ Вийти / Змінити користувача"):
            st.session_state.logged_in_master = ""
            st.session_state.confirm_clear_history = False
            st.rerun()

    if enter_admin:
        if admin_password == "1234":
            st.session_state.host_authenticated = True
        else:
            st.error("❌ Неправильний пароль!")
            st.session_state.host_authenticated = False

    if st.session_state.get("host_authenticated", False):
        st.success("✅ Вітаємо в Панелі Хоста!")
        
        col_nav1, col_nav2 = st.columns([2, 1])
        with col_nav1:
            if st.button("⬅️ Повернутися до оформлення чеку"):
                st.session_state.logged_in_master = ""
                st.session_state.host_authenticated = False
                st.session_state.confirm_clear_history = False
                st.rerun()
        with col_nav2:
            if st.button("🔄 Оновити історію чеків та базу"):
                st.cache_data.clear()
                st.rerun()

        st.markdown("---")
        
        st.subheader("📊 Аналітика та рейтинг успішності майстрів")
        history_file = "all_sales_history.xlsx"
        
        if os.path.exists(history_file):
            try:
                xls = pd.ExcelFile(history_file)
                all_masters_data = []
                for sheet in xls.sheet_names:
                    df_sh = pd.read_excel(history_file, sheet_name=sheet)
                    if not df_sh.empty and "Сума (грн)" in df_sh.columns:
                        df_sh["Майстер_Аркуш"] = sheet
                        all_masters_data.append(df_sh)
                
                if all_masters_data:
                    df_all_sales = pd.concat(all_masters_data, ignore_index=True)
                    if "Час" in df_all_sales.columns:
                        df_all_sales["datetime_obj"] = pd.to_datetime(df_all_sales["Час"], errors='coerce')
                        df_all_sales["Дата"] = df_all_sales["datetime_obj"].dt.strftime("%Y-%m-%d")
                        
                        analytics_period = st.selectbox("📅 Оберіть період аналітики:", ["За весь час", "Сьогодні", "Тиждень", "Місяць"])
                        now_dt = datetime.now()
                        if analytics_period == "Сьогодні":
                            today_date_str = (now_dt + timedelta(hours=3)).strftime("%Y-%m-%d")
                            df_filtered_stat = df_all_sales[df_all_sales["Дата"] == today_date_str]
                        elif analytics_period == "Тиждень":
                            week_ago = now_dt - timedelta(days=7)
                            df_filtered_stat = df_all_sales[df_all_sales["datetime_obj"] >= week_ago]
                        elif analytics_period == "Місяць":
                            month_ago = now_dt - timedelta(days=30)
                            df_filtered_stat = df_all_sales[df_all_sales["datetime_obj"] >= month_ago]
                        else:
                            df_filtered_stat = df_all_sales
                    else:
                        df_filtered_stat = df_all_sales

                    df_totals = df_filtered_stat[df_filtered_stat["Категорія"].astype(str).str.contains("ЗАГАЛОМ", case=False, na=False)]
                    if not df_totals.empty and "Майстер" in df_totals.columns and "Сума (грн)" in df_totals.columns:
                        df_totals["Сума (грн)"] = pd.to_numeric(df_totals["Сума (грн)"], errors='coerce').fillna(0)
                        rating_df = df_totals.groupby("Майстер").agg(
                            Заробіток=("Сума (грн)", "sum"),
                            Кількість_чеків=("№ чека", "nunique")
                        ).reset_index().sort_values(by="Заробіток", ascending=False)
                        st.markdown(f"### 🏆 Рейтинг майстрів ({analytics_period.lower()})")
                        st.dataframe(rating_df, use_container_width=True)
            except Exception as e:
                st.info(f"Помилка аналітики: {e}")
        else:
            st.info("Історія продажів поки порожня.")

        st.markdown("---")
        
        st.subheader("👥 Клієнтська база")
        clients_file = "clients_base.xlsx"
        if os.path.exists(clients_file):
            df_cl_view = load_clients_base()
            search_query = st.text_input("🔍 Швидкий пошук клієнта (за ім'ям або телефоном):", placeholder="Введіть ім'я або цифри номера...")
            if search_query.strip():
                query_lower = search_query.strip().lower()
                df_cl_view = df_cl_view[
                    df_cl_view["Ім'я"].astype(str).str.lower().str.contains(query_lower, na=False) | 
                    df_cl_view["Телефон"].astype(str).str.contains(query_lower, na=False)
                ]
            with open(clients_file, "rb") as f:
                client_excel_bytes = f.read()
            st.download_button(
                label="📥 Завантажити повну базу клієнтів (.xlsx)",
                data=client_excel_bytes,
                file_name="basa_klientiv.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            st.dataframe(df_cl_view, use_container_width=True)
        else:
            st.info("Клієнтська база поки пуста.")
            
        st.subheader("📤 Завантажити оновлену базу клієнтів (Excel)")
        uploaded_client_file = st.file_uploader("Оберіть файл `clients_base.xlsx`:", type=["xlsx"])
        if uploaded_client_file is not None:
            if st.button("💾 Застосувати та замінити базу на сервері"):
                try:
                    df_uploaded = pd.read_excel(uploaded_client_file)
                    df_uploaded.to_excel(clients_file, index=False)
                    st.success("🎉 Базу успішно оновлено! Сторінка перезапуститься.")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Помилка: {e}")

        st.markdown("---")
        
        # 📁 Перегляд чеків та управління архівом
        if os.path.exists(history_file):
            if st.button("📊 Сформувати місячний звіт (зведений звіт за поточний місяць)"):
                try:
                    xls_rep = pd.ExcelFile(history_file)
                    rep_totals = []
                    for sh in xls_rep.sheet_names:
                        df_sh = pd.read_excel(history_file, sheet_name=sh)
                        if not df_sh.empty and "Час" in df_sh.columns and "Сума (грн)" in df_sh.columns:
                            df_sh["datetime_obj"] = pd.to_datetime(df_sh["Час"], errors='coerce')
                            current_month = datetime.now().month
                            current_year = datetime.now().year
                            df_month = df_sh[(df_sh["datetime_obj"].dt.month == current_month) & (df_sh["datetime_obj"].dt.year == current_year)]
                            if not df_month.empty:
                                df_check_totals = df_month[df_month["Категорія"].astype(str).str.contains("ЗАГАЛОМ", case=False, na=False)].copy()
                                if not df_check_totals.empty:
                                    df_check_totals["Майстер"] = sh
                                    df_check_totals["Дата"] = df_check_totals["datetime_obj"].dt.strftime("%Y-%m-%d")
                                    clean_registry = df_check_totals[["Дата", "Майстер", "№ чека", "Ім'я клієнта", "Сума (грн)"]].rename(columns={"Сума (грн)": "Сума чека (грн)"})
                                    rep_totals.append(clean_registry)
                    
                    if rep_totals:
                        df_full_registry = pd.concat(rep_totals, ignore_index=True)
                        df_summary_masters = df_full_registry.groupby("Майстер").agg(
                            Кількість_чеків=("№ чека", "nunique"),
                            Загальна_виручка=("Сума чека (грн)", "sum")
                        ).reset_index()
                        total_row = pd.DataFrame([{
                            "Майстер": "ВСЬОГО ПО МАЙСТЕРНІ",
                            "Кількість_чеків": df_full_registry["№ чека"].nunique(),
                            "Загальна_виручка": df_full_registry["Сума чека (грн)"].sum()
                        }])
                        df_summary_masters = pd.concat([df_summary_masters, total_row], ignore_index=True)
                        report_filename = f"zvedeny_misyachny_zvit_{datetime.now().strftime('%Y_%m')}.xlsx"
                        with pd.ExcelWriter(report_filename, engine='openpyxl') as writer:
                            df_summary_masters.to_excel(writer, sheet_name="Звіт по майстрах", index=False)
                            df_full_registry.to_excel(writer, sheet_name="Реєстр чеків", index=False)
                        with open(report_filename, "rb") as rf:
                            st.download_button(
                                label="📥 Завантажити зведений місячний звіт (.xlsx)",
                                data=rf.read(),
                                file_name=report_filename,
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                type="primary"
                            )
                        st.success("🎉 Зведений місячний звіт успішно сформовано!")
                    else:
                        st.warning("⚠️ За поточний місяць ще немає збережених чеків.")
                except Exception as e:
                    st.error(f"Помилка формування звіту: {e}")

            st.markdown("---")
            st.warning("⚠️ **Зона адміністратора:** Очищення історії чеків видалить усі дані назавжди.")
            if not st.session_state.confirm_clear_history:
                if st.button("🗑️ Очистити всю історію чеків"):
                    st.session_state.confirm_clear_history = True
                    st.rerun()
            else:
                st.error("❗ УВАГА: Ви дійсно хочете видалити всі чеки?")
                clear_pass = st.text_input("Пароль адміністратора:", type="password", key="clear_history_pass_input")
                col_c1, col_c2 = st.columns(2)
                with col_c1:
                    if st.button("🔴 ТАК, ВИДАЛИТИ", type="primary"):
                        if clear_pass == "1234":
                            log_time = (datetime.now() + timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S")
                            log_msg = f"[{log_time}] АДМІНІСТРАТОР очистив всю історію чеків.\n"
                            with open("action_audit_log.txt", "a", encoding="utf-8") as log_file:
                                log_file.write(log_msg)
                            os.remove(history_file)
                            st.session_state.confirm_clear_history = False
                            st.success("Архів чеків очищено!")
                            st.rerun()
                        else:
                            st.error("❌ Неправильний пароль!")
                with col_c2:
                    if st.button("✖️ Скасувати"):
                        st.session_state.confirm_clear_history = False
                        st.rerun()
            
            with open(history_file, "rb") as f:
                excel_bytes = f.read()
            st.download_button(
                label="📥 Завантажити всю історію чеків в Excel (.xlsx)",
                data=excel_bytes,
                file_name="istoriya_chekiv.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            try:
                xls = pd.ExcelFile(history_file)
                sheet_names = xls.sheet_names
                selected_sheet = st.selectbox("👤 Оберіть аркуш майстра для перегляду:", sheet_names)
                if selected_sheet:
                    df_sheet = pd.read_excel(history_file, sheet_name=selected_sheet)
                    if "Час" in df_sheet.columns and not df_sheet.empty:
                        df_sheet["Дата"] = pd.to_datetime(df_sheet["Час"], errors='coerce').dt.strftime("%Y-%m-%d")
                        available_dates = df_sheet["Дата"].dropna().unique().tolist()
                        available_dates.sort(reverse=True)
                        selected_date_filter = st.selectbox("📅 Фільтр чеків за датою:", ["Усі дати"] + available_dates)
                        if selected_date_filter != "Усі дати":
                            df_sheet = df_sheet[df_sheet["Дата"] == selected_date_filter]
                        df_sheet = df_sheet.drop(columns=["Дата"])
                    st.dataframe(df_sheet, use_container_width=True)
                    
                    # --- ПОКРАЩЕНИЙ БЛОК ВИБОРУ ЦІЛІСНОГО ЧЕКА ДЛЯ ПЕРЕГЛЯДУ ФОТО ---
                    st.markdown("---")
                    st.subheader("🔍 Перегляд фото та деталей конкретного чека")
                    
                    if not df_sheet.empty and "№ чека" in df_sheet.columns:
                        receipt_numbers = df_sheet["№ чека"].dropna().unique().tolist()
                        receipt_numbers = [r for r in receipt_numbers if str(r).strip() != "" and str(r).lower() != "nan"]
                        
                        if receipt_numbers:
                            selected_r_num = st.selectbox(
                                "Оберіть чек для перегляду:",
                                receipt_numbers,
                                format_func=lambda r: f"Чек № {r}"
                            )
                            
                            df_single_receipt = df_sheet[df_sheet["№ чека"] == selected_r_num]
                            st.dataframe(df_single_receipt, use_container_width=True)
                            
                            photo_col_val = ""
                            for p_col in ["Фото", "Фото (Drive)"]:
                                if p_col in df_single_receipt.columns:
                                    for val in df_single_receipt[p_col].dropna():
                                        s_val = str(val).strip()
                                        if s_val and s_val.lower() != "nan":
                                            photo_col_val = s_val
                                            break
                                    if photo_col_val:
                                        break
                                        
                            photo_dir = "receipt_photos"
                            if photo_col_val:
                                st.success(f"📷 Знайдено дані прикріплення: `{photo_col_val}`")
                                if "http://" in photo_col_val or "https://" in photo_col_val:
                                    st.markdown(f"🔗 **Посилання:** [{photo_col_val}]({photo_col_val})")
                                else:
                                    filenames = [fn.strip() for fn in photo_col_val.split(",")]
                                    for fn in filenames:
                                        full_path = os.path.join(photo_dir, fn)
                                        if os.path.exists(full_path):
                                            st.image(full_path, caption=f"Фото до чека № {selected_r_num} — {fn}", use_container_width=True)
                                            with open(full_path, "rb") as pf:
                                                st.download_button(
                                                    label=f"📥 Завантажити файл: {fn}",
                                                    data=pf.read(),
                                                    file_name=fn,
                                                    mime="image/jpeg",
                                                    key=f"dl_ph_{selected_r_num}_{fn}"
                                                )
                                        else:
                                            st.warning(f"⚠️ Файл `{fn}` зазначено в базі, але на сервері у папці його немає.")
                            else:
                                st.info("ℹ️ До цього чека фотографії не прикріплювались.")
                        else:
                            st.info("На цьому аркуші немає чеків з номерами.")
                    else:
                        st.info("Архів цього майстра порожній або немає колонки з номерами чеків.")
            except Exception as e:
                st.info(f"Помилка завантаження аркуша: {e}")
        else:
            st.info("Архів чеків порожній.")

    st.stop()

# =========================================================================
# РОБОЧЕ МІСЦЕ ЗВІЧАЙНОГО МАЙСТРА
# =========================================================================
col_user1, col_user2 = st.columns([3, 1])
with col_user1:
    st.success(f"Працює майстер: **{master_name}**")
with col_user2:
    if st.button("Змінити майстра"):
        st.session_state.logged_in_master = ""
        st.rerun()

history_file = "all_sales_history.xlsx"
today_str = (datetime.now() + timedelta(hours=3)).strftime("%Y-%m-%d")
today_receipts_count = 0
today_revenue = 0

if os.path.exists(history_file):
    try:
        xls = pd.ExcelFile(history_file)
        if master_name in xls.sheet_names:
            df_m = pd.read_excel(history_file, sheet_name=master_name)
            if "Час" in df_m.columns and "Сума (грн)" in df_m.columns and not df_m.empty:
                df_m["Дата"] = pd.to_datetime(df_m["Час"], errors='coerce').dt.strftime("%Y-%m-%d")
                df_today = df_m[df_m["Дата"] == today_str]
                if not df_today.empty:
                    if "№ чека" in df_today.columns:
                        today_receipts_count = df_today["№ чека"].nunique()
                    df_totals_today = df_today[df_today["Категорія"].astype(str).str.contains("ЗАГАЛОМ", case=False, na=False)]
                    if not df_totals_today.empty:
                        today_revenue = pd.to_numeric(df_totals_today["Сума (грн)"], errors='coerce').sum()
    except Exception:
        pass

col_stat1, col_stat2 = st.columns(2)
with col_stat1:
    st.metric(label="📊 Ваших чеків сьогодні", value=today_receipts_count)
with col_stat2:
    st.metric(label="💰 Ваша виручка за сьогодні", value=f"{today_revenue} грн")

st.markdown("---")

# 🔘 КНОПКИ ДЛЯ КАТЕГОРІЙ
categories = ["Послуги", "Матеріали", "Інше", "Знижки"]
selected_category = st.pills("Оберіть категорію:", categories, default="Послуги")

# ЛОГІКА ВИБОРУ ДЛЯ ПОСЛУГ (КНОПКИ НАПРЯМІВ + КНОПКИ РОЗДІЛІВ)
if selected_category == "Послуги":
    available_fields = list(set(data["field"] for name, data in st.session_state.services.items() if data["category"] == "Послуги"))
    available_fields.sort()
    
    # 🔘 Кнопки вибору напряму
    selected_field = st.pills("Оберіть напрям робіт:", available_fields, default=available_fields[0] if available_fields else None)
    
    if selected_field:
        subcategories = list(set(data["subcategory"] for name, data in st.session_state.services.items() if data["category"] == "Послуги" and data["field"] == selected_field))
        subcategories.sort()
        
        # 🔘 Кнопки вибору розділу (підкатегорії)
        selected_subcategory = st.pills("Оберіть розділ:", subcategories, default=subcategories[0] if subcategories else None)
        
        if selected_subcategory:
            filtered_services = {name: data for name, data in st.session_state.services.items() if data["category"] == "Послуги" and data["field"] == selected_field and data["subcategory"] == selected_subcategory}
        else:
            filtered_services = {}
    else:
        filtered_services = {}
else:
    filtered_services = {name: data for name, data in st.session_state.services.items() if data["category"] == selected_category}

service_options = list(filtered_services.keys())

is_percentage_service = False
current_unit = "шт"
if service_options:
    selected_service = st.selectbox("Оберіть позицію зі списку", service_options)
    service_data = filtered_services[selected_service]
    current_price = float(service_data["price"])
    is_percentage_service = service_data.get("is_percent", False)
    current_unit = service_data.get("unit", "шт")
else:
    selected_service = None
    current_price = 0.0
    st.info("У цій категорії поки немає позицій (або оберіть усі фільтри вище).")

available_stock_qty = None
if selected_category == "Матеріали" and selected_service and "(склад)" in selected_service.lower():
    df_stock_check = load_warehouse_stock()
    if selected_service in df_stock_check["Матеріал"].values:
        available_stock_qty = int(df_stock_check.loc[df_stock_check["Матеріал"] == selected_service, "Залишок (шт)"].values[0])
        if available_stock_qty > 0:
            st.info(f"📦 **На складі в наявності:** {available_stock_qty} шт.")
        else:
            st.warning(f"⚠️ **На складі в наявності:** 0 шт. (Товар повністю закінчився, буде додано з магазину)")

# --- КАСТОМНИЙ БЛОК КІЛЬКОСТІ З КНОПКАМИ ---
st.markdown(f"**Кількість ({current_unit}):**")

qc1, qc2, qc3 = st.columns([1, 2, 1])
with qc1:
    if st.button("➖", use_container_width=True, key="btn_minus_custom"):
        st.session_state.item_qty = max(0.1, round(st.session_state.item_qty - 0.5, 2))
        st.rerun()
with qc2:
    entered_qty_str = st.text_input("Кількість", value=str(st.session_state.item_qty), label_visibility="collapsed", key="qty_txt_box")
    try:
        st.session_state.item_qty = float(entered_qty_str.replace(',', '.'))
    except ValueError:
        pass
with qc3:
    if st.button("➕", use_container_width=True, key="btn_plus_custom"):
        st.session_state.item_qty = round(st.session_state.item_qty + 0.5, 2)
        st.rerun()

# Швидкі кнопки додавання кількості
st.markdown("⚡ **Швидке додавання:**")
sc1, sc2, sc3, sc4, sc5 = st.columns(5)
with sc1:
    if st.button("+0.1", use_container_width=True, key="sq_01"):
        st.session_state.item_qty = round(st.session_state.item_qty + 0.1, 2)
        st.rerun()
with sc2:
    if st.button("+0.5", use_container_width=True, key="sq_05"):
        st.session_state.item_qty = round(st.session_state.item_qty + 0.5, 2)
        st.rerun()
with sc3:
    if st.button("+1", use_container_width=True, key="sq_1"):
        st.session_state.item_qty = round(st.session_state.item_qty + 1.0, 2)
        st.rerun()
with sc4:
    if st.button("+5", use_container_width=True, key="sq_5"):
        st.session_state.item_qty = round(st.session_state.item_qty + 5.0, 2)
        st.rerun()
with sc5:
    if st.button("🔄 Скин.", use_container_width=True, key="sq_reset"):
        st.session_state.item_qty = 1.0
        st.rerun()

qty = st.session_state.item_qty

# ЦІНА ЗА ОДИНИЦЮ (один чистий блок без дублів у звичному вигляді)
if selected_category == "Знижки":
    if is_percentage_service:
        price = st.number_input("Знижка у відсотках (%)", min_value=0.0, max_value=100.0, value=current_price, step=1.0, key="price_discount_percent")
    else:
        price = st.number_input("Сума знижки (грн)", min_value=0.0, value=current_price, step=10.0, key="price_discount_uah")
else:
    price = st.number_input("Ціна за одиницю (грн)", min_value=0.0, value=current_price, step=10.0, key="price_regular_service")

if st.session_state.pending_split_item is not None:
    p_item = st.session_state.pending_split_item
    st.warning(f"⚠️ **На складі є лише {p_item['stock_qty']} шт. «{p_item['mat_name']}».** Ви запросили {p_item['requested_qty']} шт.")
    st.markdown("Оберіть дію:")
    
    col_sp1, col_sp2 = st.columns(2)
    with col_sp1:
        if st.button("🛒 Розділити: залишок зі складу + решта з магазину"):
            stock_part_total = p_item['stock_qty'] * p_item['stock_price']
            st.session_state.cart.append({
                "name": p_item['mat_name'], "category": "Матеріали", "price": p_item['stock_price'],
                "qty": float(p_item['stock_qty']), "unit": "шт", "total": stock_part_total, "is_pct": False
            })
            
            shop_mat_name = p_item['mat_name'].replace("(склад)", "(магазин)")
            shop_price = st.session_state.services.get(shop_mat_name, {}).get("price", p_item['stock_price'] * 3)
            diff_qty = p_item['requested_qty'] - p_item['stock_qty']
            shop_part_total = diff_qty * shop_price
            
            st.session_state.cart.append({
                "name": shop_mat_name, "category": "Матеріали", "price": shop_price,
                "qty": float(diff_qty), "unit": "шт", "total": shop_part_total, "is_pct": False
            })
            st.session_state.pending_split_item = None
            st.success("🎉 Успішно розділено між складом та магазином і додано до чека!")
            st.rerun()
            
    with col_sp2:
        if st.button("📦 Взяти тільки те, що є на складі"):
            stock_part_total = p_item['stock_qty'] * p_item['stock_price']
            st.session_state.cart.append({
                "name": p_item['mat_name'], "category": "Матеріали", "price": p_item['stock_price'],
                "qty": float(p_item['stock_qty']), "unit": "шт", "total": stock_part_total, "is_pct": False
            })
            st.session_state.pending_split_item = None
            st.success("🎉 Додано наявний залишок зі складу до чека!")
            st.rerun()

    if st.button("✖️ Скасувати додавання"):
        st.session_state.pending_split_item = None
        st.rerun()
        
    st.stop()

if st.button("Додати до чека", type="primary"):
    if not selected_service:
        st.error("Оберіть позицію зі списку.")
    else:
        already_has_discount = any(item['category'] == "Знижки" for item in st.session_state.cart)
        if selected_category == "Знижки" and already_has_discount:
            st.error("❌ У чеку вже є знижка!")
        else:
            if selected_category == "Матеріали" and selected_service and "(склад)" in selected_service.lower():
                df_stock_check = load_warehouse_stock()
                if selected_service in df_stock_check["Матеріал"].values:
                    stk_qty = int(df_stock_check.loc[df_stock_check["Матеріал"] == selected_service, "Залишок (шт)"].values[0])
                    if qty > stk_qty:
                        if stk_qty > 0:
                            st.session_state.pending_split_item = {
                                "mat_name": selected_service, "stock_qty": stk_qty,
                                "requested_qty": int(qty), "stock_price": price
                            }
                            st.rerun()
                        else:
                            shop_mat_name = selected_service.replace("(склад)", "(магазин)")
                            shop_price = st.session_state.services.get(shop_mat_name, {}).get("price", price * 3)
                            st.session_state.cart.append({
                                "name": shop_mat_name, "category": "Матеріали", "price": shop_price,
                                "qty": qty, "unit": "шт", "total": qty * shop_price, "is_pct": False
                            })
                            st.warning(f"⚠️ Товар «{selected_service}» на складі закінчився (0 шт.). Автоматично додано як версію з магазину!")
                            st.rerun()

            if selected_category == "Знижки" and is_percentage_service:
                item_price = -price
                item_name_display = f"{selected_service} ({price}%)"
                total = -price
            else:
                item_price = -price if selected_category == "Знижки" else price
                item_name_display = selected_service
                total = qty * item_price
            
            st.session_state.cart.append({
                "name": item_name_display, "category": selected_category,
                "price_display": item_price, "price": item_price, "qty": qty, "unit": current_unit,
                "total": total, "is_pct": (selected_category == "Знижки" and is_percentage_service)
            })
            st.success(f"Додано до чека: {item_name_display}")
            st.rerun()

st.markdown("---")
st.subheader("🧾 Поточний кошик / чек")

if st.session_state.cart:
    subtotal = sum(item['total'] for item in st.session_state.cart if not item.get('is_pct'))
    grand_total = 0
    calculated_cart = []
    
    for item in st.session_state.cart:
        if item.get('is_pct'):
            pct_value = abs(item['price'])
            item_total = -round(subtotal * (pct_value / 100.0), 2)
            item_display_price = f"-{pct_value}%"
        else:
            item_total = item['total']
            item_display_price = f"{item['price']} грн"
            
        calculated_cart.append({
            "name": item['name'], "category": item['category'],
            "price_display": item_display_price, "qty": item['qty'],
            "unit": item.get('unit', 'шт'), "total": item_total
        })
        grand_total += item_total

    for i, item in enumerate(calculated_cart):
        col_item_info, col_item_del = st.columns([5, 1])
        with col_item_info:
            st.write(f"**{i+1}. [{item['category']}] {item['name']}** — {item['qty']} {item['unit']} x {item['price_display']} = **{item['total']} грн**")
        with col_item_del:
            if st.button("❌", key=f"del_item_{i}"):
                st.session_state.cart.pop(i)
                st.rerun()
    
    st.markdown(f"### Загальна сума до сплати: {grand_total} грн")
    st.markdown("---")
    
    is_anon = st.checkbox("👤 Клієнт без номера телефону (анонім)")
    client_name = ""
    client_status = "Звичайний"
    client_note = ""
    client_host_note = ""
    is_existing_client = False
    client_visits_count = 1
    
    if not is_anon:
        entered_phone = st.text_input("📞 Номер телефону клієнта:", placeholder="0681234567")
        if entered_phone.strip():
            clean_input_digits = "".join(filter(str.isdigit, entered_phone.strip()))
            if clean_input_digits.startswith("380"):
                target_search_phone = clean_input_digits
            elif clean_input_digits.startswith("0"):
                target_search_phone = f"380{clean_input_digits[1:]}"
            else:
                target_search_phone = f"380{clean_input_digits}"
            
            df_check = load_clients_base()
            if not df_check.empty and "Телефон" in df_check.columns:
                df_check["ЧистийТелефон"] = df_check["Телефон"].astype(str).apply(lambda x: "".join(filter(str.isdigit, x)))
                match = df_check[df_check["ЧистийТелефон"] == target_search_phone]
                if not match.empty:
                    is_existing_client = True
                    found_client_name = str(match.iloc[0]["Ім'я"])
                    client_visits_count = int(match.iloc[0]["Кількість візитів"])
                    client_status = str(match.iloc[0]["Статус"]).strip()
                    client_note = str(match.iloc[0]["Коментар майстра"]).strip() if pd.notna(match.iloc[0]["Коментар майстра"]) else ""
                    client_host_note = str(match.iloc[0]["Внутрішня примітка"]).strip() if pd.notna(match.iloc[0]["Внутрішня примітка"]) else ""
            
            if is_existing_client:
                st.success(f"🌟 Знайдено в базі! Клієнт: **{found_client_name}** | Статус: **{client_status}** (Візитів: {client_visits_count})")
                if client_host_note:
                    st.warning(f"⚠️ **Внутрішня примітка хоста:** {client_host_note}")
                if client_note:
                    st.info(f"💬 **Коментар майстра (історія):** {client_note}")
                client_name = found_client_name
            else:
                st.info("💡 Номер новий. Вкажіть ім'я клієнта:")
                client_name = st.text_input("👤 Ім'я нового клієнта:")
    
    master_current_comment = st.text_input("💬 Приватний коментар майстра до роботи (необов'язково):", placeholder="Наприклад: складні умови, арматура...")
    
    st.markdown("📸 **Фотофіксація робіт / об'єкта (необов'язково):**")
    uploaded_photos = st.file_uploader("Зробіть фото або оберіть з галереї:", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

    st.markdown("---")
    
    col_action1, col_action2, col_action3 = st.columns([2, 2, 1])
    
    with col_action1:
        df_estimate = pd.DataFrame([{
            "№": i+1,
            "Категорія": item['category'],
            "Найменування": item['name'],
            "Кількість": f"{item['qty']} {item['unit']}",
            "Ціна за од.": item['price_display'],
            "Сума (грн)": item['total']
        } for i, item in enumerate(calculated_cart)])
        
        estimate_filename = f"poperedniy_koshtorys_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
        with pd.ExcelWriter(estimate_filename, engine='openpyxl') as writer:
            df_estimate.to_excel(writer, sheet_name="Кошторис", index=False)
            
        with open(estimate_filename, "rb") as ef:
            estimate_bytes = ef.read()
            
        st.download_button(
            label="📥 Завантажити попередній кошторис (.xlsx)",
            data=estimate_bytes,
            file_name=estimate_filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="secondary"
        )
            
    with col_action2:
        if st.button("💾 Завершити і закрити чек в роботу", type="primary"):
            if not is_anon and not entered_phone.strip():
                st.error("❌ Введіть телефон або оберіть аноніма!")
            elif not is_anon and not is_existing_client and not client_name.strip():
                st.error("❌ Введіть ім'я клієнта!")
            else:
                now = (datetime.now() + timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S")
                today_date_only = (datetime.now() + timedelta(hours=3)).strftime("%Y-%m-%d")
                history_file = "all_sales_history.xlsx"
                clients_file = "clients_base.xlsx"
                
                cleaned_phone = "Анонім" if is_anon else f"'{''.join(filter(str.isdigit, entered_phone))}"
                cleaned_name = "Анонім" if is_anon else (client_name.strip() or found_client_name)
                
                next_receipt_num = 1
                if os.path.exists(history_file):
                    try:
                        xls = pd.ExcelFile(history_file)
                        existing_sheet = next((sh for sh in xls.sheet_names if sh.lower() == master_name.lower()), None)
                        if existing_sheet:
                            df_old = pd.read_excel(history_file, sheet_name=existing_sheet)
                            if "№ чека" in df_old.columns and not df_old["№ чека"].dropna().empty:
                                next_receipt_num = int(df_old["№ чека"].dropna().max()) + 1
                    except Exception:
                        pass

                photo_filenames_str = ""
                if uploaded_photos:
                    photo_filenames_str = save_photos_locally(uploaded_photos, next_receipt_num, master_name)
                
                if not is_anon:
                    full_phone_num = "".join(filter(str.isdigit, entered_phone))
                    df_clients = load_clients_base()
                    if not df_clients.empty and "Телефон" in df_clients.columns:
                        df_clients["ЧистийТелефон"] = df_clients["Телефон"].astype(str).apply(lambda x: "".join(filter(str.isdigit, x)))
                        if full_phone_num in df_clients["ЧистийТелефон"].values:
                            idx = df_clients[df_clients["ЧистийТелефон"] == full_phone_num].index[0]
                            df_clients.loc[idx, "Кількість візитів"] = int(df_clients.loc[idx, "Кількість візитів"]) + 1
                            df_clients.loc[idx, "Останній візит"] = today_date_only
                            df_clients.loc[idx, "Останній майстер"] = master_name
                            if cleaned_name != "Без імені":
                                df_clients.loc[idx, "Ім'я"] = cleaned_name
                            if master_current_comment.strip():
                                df_clients.loc[idx, "Коментар майстра"] = master_current_comment.strip()
                        else:
                            new_row = pd.DataFrame([{
                                "Телефон": cleaned_phone, "Ім'я": cleaned_name, "Кількість візитів": 1, 
                                "Статус": "Звичайний", "Коментар майстра": master_current_comment.strip(), 
                                "Внутрішня примітка": "", "Останній візит": today_date_only, "Останній майстер": master_name
                            }])
                            df_clients = pd.concat([df_clients, new_row], ignore_index=True)
                    else:
                        df_clients = pd.DataFrame([{
                            "Телефон": cleaned_phone, "Ім'я": cleaned_name, "Кількість візитів": 1, 
                            "Статус": "Звичайний", "Коментар майстра": master_current_comment.strip(), 
                            "Внутрішня примітка": "", "Останній візит": today_date_only, "Останній майстер": master_name
                        }])
                    
                    if "ЧистийТелефон" in df_clients.columns:
                        df_clients = df_clients.drop(columns=["ЧистийТелефон"])
                    df_clients.to_excel(clients_file, index=False)
                
                update_warehouse_after_sale(st.session_state.cart)
                
                new_rows = [{
                    "№ чека": next_receipt_num, "Час": now, "Майстер": master_name, "Телефон клієнта": cleaned_phone,
                    "Ім'я клієнта": cleaned_name, "Категорія": item['category'], "Послуга/Позиція": item['name'],
                    "Кількість": f"{item['qty']} {item.get('unit', 'шт')}", "Ціна за од. / Значення": item['price_display'], 
                    "Сума (грн)": item['total'], "Коментар майстра": master_current_comment.strip(), "Фото": photo_filenames_str
                } for item in calculated_cart]
                
                new_rows.append({
                    "№ чека": next_receipt_num, "Час": now, "Майстер": master_name, "Телефон клієнта": cleaned_phone,
                    "Ім'я клієнта": cleaned_name, "Категорія": "--- ЗАГАЛОМ ЗА ЧЕК ---", "Послуга/Позиція": f"Підсумок чека №{next_receipt_num}",
                    "Кількість": "", "Ціна за од. / Значення": "", "Сума (грн)": grand_total, "Коментар майстра": "", "Фото": ""
                })
                
                df_new = pd.DataFrame(new_rows)
                
                if os.path.exists(history_file):
                    xls_check = pd.ExcelFile(history_file)
                    existing_sheet = next((sh for sh in xls_check.sheet_names if sh.lower() == master_name.lower()), None)
                    target_sheet_name = existing_sheet if existing_sheet else master_name

                    with pd.ExcelWriter(history_file, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                        try:
                            df_old_m = pd.read_excel(history_file, sheet_name=target_sheet_name)
                            if "Послуга/Позиція" not in df_old_m.columns:
                                df_combined = df_new
                            else:
                                empty_row = {col: None for col in df_old_m.columns}
                                df_combined = pd.concat([df_old_m, pd.DataFrame([empty_row]), df_new], ignore_index=True)
                        except Exception:
                            df_combined = df_new
                        
                        df_combined.to_excel(writer, sheet_name=target_sheet_name, index=False)
                else:
                    with pd.ExcelWriter(history_file, engine='openpyxl') as writer:
                        df_new.to_excel(writer, sheet_name=master_name, index=False)
                
                st.success(f"🎉 Чек №{next_receipt_num} успішно закрито в роботу! Матеріали списано, а фото збережено на сервері.")
                st.session_state.cart.clear()
                st.rerun()

    with col_action3:
        if st.button("🗑️ Очистити кошик"):
            st.session_state.cart.clear()
            st.rerun()
else:
    st.info("Кошик порожній. Оберіть послуги або матеріали вище.")
