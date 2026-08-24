import streamlit as st
from datetime import datetime, timedelta
import os
import pandas as pd

# Список дозволених майстрів (White List)
ALLOWED_MASTERS = ["Микола", "Олена", "Тато", "Адмін"]

# База послуг із категоріями та цінами за замовчуванням
if 'services' not in st.session_state:
    st.session_state.services = {
        "Установка люстри": {"category": "Послуги", "price": 520},
        "Установка і підключення розетки": {"category": "Послуги", "price": 135},
        "Установка і підключення вимикача": {"category": "Послуги", "price": 135},
        "Встановлення та підключення вхідного дзвінка": {"category": "Послуги", "price": 270},
        "Установка і підключення бойлера": {"category": "Послуги", "price": 2090},
        "Розетка одинарна (склад)": {"category": "Матеріали", "price": 100},
        "Розетка одинарна (магазин)": {"category": "Матеріали", "price": 300},
        "Розетка подвійна (склад)": {"category": "Матеріали", "price": 300},
        "Розетка подвійна (магазин)": {"category": "Матеріали", "price": 500},
        "Лампа світлодіодна (склад)": {"category": "Матеріали", "price": 150},
        "Лампа світлодіодна (магазин)": {"category": "Матеріали", "price": 350},
        "Виїзд майстра": {"category": "Інше", "price": 500},
        "Знижка пенсіонер": {"category": "Знижки", "price": 200},
        "Знижка військовий": {"category": "Знижки", "price": 250},
        "Знижка постійному клієнту": {"category": "Знижки", "price": 50, "is_percent": False},
        "Знижка ВПО": {"category": "Знижки", "price": 15, "is_percent": True},  # Автоматично у відсотках!
        "Акція вихідного дня": {"category": "Знижки", "price": 100, "is_percent": False} # Автоматично у гривнях!
    }

if 'cart' not in st.session_state:
    st.session_state.cart = []

# Допоміжна функція для безпечного завантаження/створення бази клієнтів із колоночкою «Статус»
def load_clients_base():
    clients_file = "clients_base.xlsx"
    expected_columns = ["Телефон", "Ім'я", "Кількість візитів", "Статус", "Останній візит", "Останній майстер"]
    
    if os.path.exists(clients_file):
        try:
            df = pd.read_excel(clients_file)
            # Перевіряємо, чи є всі колонки, якщо чогось немає — додаємо
            for col in expected_columns:
                if col not in df.columns:
                    if col == "Статус":
                        df["Статус"] = "Звичайний"
                    elif col == "Кількість візитів":
                        df["Кількість візитів"] = 1
                    else:
                        df[col] = ""
            return df
        except Exception:
            pass
    
    # Якщо файлу немає або він пошкоджений — створюємо новий базовий
    return pd.DataFrame(columns=expected_columns)

st.title("✂️ Система розрахунку послуг")
st.markdown("Робоче місце для оформлення замовлень")

# Авторизація через Білий список
if 'logged_in_master' not in st.session_state:
    st.session_state.logged_in_master = ""

if not st.session_state.logged_in_master:
    st.warning("👋 Будь ласка, введіть ваше ім'я для входу.")
    with st.form("login_form"):
        entered_name = st.text_input("Ім'я майстра:")
        submit_login = st.form_submit_button("Увійти в систему", type="primary")
        
        if submit_login:
            clean_name = entered_name.strip()
            if any(clean_name.lower() == m.lower() for m in ALLOWED_MASTERS):
                st.session_state.logged_in_master = clean_name
                st.rerun()
            else:
                st.error("❌ Доступ заборонено: такого майстра немає в системі.")
    st.stop()

col_user1, col_user2 = st.columns([3, 1])
with col_user1:
    st.success(f"Працює майстер: **{st.session_state.logged_in_master}**")
with col_user2:
    if st.button("Змінити майстра"):
        st.session_state.logged_in_master = ""
        st.rerun()

master_name = st.session_state.logged_in_master

# Блок «Статистика за сьогодні» для майстра
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
                    df_totals_today = df_today[df_today["Категорія"] == "--- ЗАГАЛОМ ЗА ЧЕК ---"]
                    if not df_totals_today.empty:
                        today_revenue = df_totals_today["Сума (грн)"].sum()
    except Exception:
        pass

col_stat1, col_stat2 = st.columns(2)
with col_stat1:
    st.metric(label="📊 Ваших чеків сьогодні", value=today_receipts_count)
with col_stat2:
    st.metric(label="💰 Ваша виручка за сьогодні", value=f"{today_revenue} грн")

st.markdown("---")

# 1. Вибираємо категорію
categories = ["Послуги", "Матеріали", "Інше", "Знижки"]
selected_category = st.selectbox("Оберіть категорію:", categories)

filtered_services = {name: data for name, data in st.session_state.services.items() if data["category"] == selected_category}
service_options = list(filtered_services.keys())

is_percentage_service = False
if service_options:
    selected_service = st.selectbox("Оберіть послугу зі списку", service_options)
    service_data = filtered_services[selected_service]
    current_price = float(service_data["price"])
    is_percentage_service = service_data.get("is_percent", False)
else:
    selected_service = None
    current_price = 0.0
    st.info("У цій категорії поки немає позицій.")

qty = st.number_input("Кількість / Години", min_value=0.1, value=1.0, step=0.5)

if selected_category == "Знижки":
    if is_percentage_service:
        st.info(f"💡 Ця знижка за замовчуванням у **відсотках (%)** згідно з базою.")
        price = st.number_input("Знижка у відсотках (%)", min_value=0.0, max_value=100.0, value=current_price, step=1.0)
    else:
        st.info(f"💡 Ця знижка за замовчуванням у **гривнях (грн)** згідно з базою.")
        price = st.number_input("Сума знижки (грн)", min_value=0.0, value=current_price, step=10.0)
else:
    price = st.number_input("Ціна за одиницю (грн)", min_value=0.0, value=current_price, step=10.0)

with st.expander("➕ Додати нову послугу або знижку до чека"):
    custom_name = st.text_input("Назва позиції або знижки")
    custom_cat = st.selectbox("Категорія:", categories, key="custom_cat_select")
    
    if custom_cat == "Знижки":
        custom_is_pct = st.checkbox("Це знижка у відсотках (%)?")
        custom_price = st.number_input("Значення (грн або %)", min_value=0.0, value=0.0, key="custom_price_input")
    else:
        custom_is_pct = False
        custom_price = st.number_input("Сума (грн)", min_value=0.0, value=0.0, key="custom_price_input")
    
    if st.button("Додати цю позицію до чека"):
        if custom_name.strip() and custom_price > 0:
            if custom_cat == "Знижки":
                if custom_is_pct:
                    item_price = -custom_price
                    item_name_display = f"{custom_name.strip()} ({custom_price}%)"
                else:
                    item_price = -custom_price
                    item_name_display = custom_name.strip()
            else:
                item_price = custom_price
                item_name_display = custom_name.strip()
            
            st.session_state.cart.append({
                "name": item_name_display, 
                "category": custom_cat,
                "price": item_price, 
                "qty": 1.0, 
                "total": item_price,
                "is_pct": custom_is_pct if custom_cat == "Знижки" else False
            })
            st.success(f"Успішно додано до поточного чека: {item_name_display}!")
            st.rerun()
        else:
            st.error("Введіть назву та коректне значення.")

if st.button("Додати до чека", type="primary"):
    if not selected_service:
        st.error("Оберіть позицію зі списку.")
    else:
        if selected_category == "Знижки" and is_percentage_service:
            item_price = -price
            item_name_display = f"{selected_service} ({price}%)"
            total = -price
        else:
            item_price = -price if selected_category == "Знижки" else price
            item_name_display = selected_service
            total = qty * item_price
        
        st.session_state.cart.append({
            "name": item_name_display, 
            "category": selected_category,
            "price": item_price, 
            "qty": qty, 
            "total": total,
            "is_pct": (selected_category == "Знижки" and is_percentage_service)
        })
        st.success(f"Додано до чека: {item_name_display}")

st.markdown("---")
st.subheader("🧾 Поточний чек клієнта")

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
            "name": item['name'],
            "category": item['category'],
            "price_display": item_display_price,
            "qty": item['qty'],
            "total": item_total
        })
        grand_total += item_total

    for i, item in enumerate(calculated_cart):
        st.write(f"**{i+1}. [{item['category']}] {item['name']}** — {item['qty']} од. x {item['price_display']} = **{item['total']} грн**")
    
    st.markdown(f"### Загальна сума до сплати: {grand_total} грн")
    
    st.markdown("---")
    
    is_anon = st.checkbox("👤 Клієнт без номера телефону (анонім)")
    
    client_phone = ""
    client_name = ""
    client_status = "Звичайний"
    is_existing_client = False
    found_client_name = ""
    client_visits_count = 0
    
    if not is_anon:
        col_p1, col_p2 = st.columns([1, 4])
        with col_p1:
            st.text_input("Код", value="+380", disabled=True)
        with col_p2:
            entered_digits = st.text_input("📞 Номер телефону (без 380):", placeholder="681234567")
        
        if entered_digits.strip():
            clean_digits = "".join(filter(str.isdigit, entered_digits.strip()))
            client_phone = f"380{clean_digits}"
            
            df_check = load_clients_base()
            
            if not df_check.empty and "Телефон" in df_check.columns:
                df_check["ЧистийТелефон"] = df_check["Телефон"].astype(str).apply(lambda x: "".join(filter(str.isdigit, x)))
                
                match = df_check[df_check["ЧистийТелефон"] == client_phone]
                if not match.empty:
                    is_existing_client = True
                    found_client_name = str(match.iloc[0]["Ім'я"])
                    client_visits_count = int(match.iloc[0]["Кількість візитів"])
                    if "Статус" in match.columns:
                        client_status = str(match.iloc[0]["Статус"])
            
            if is_existing_client:
                st.success(f"🌟 Знайдено в базі! Клієнт: **{found_client_name}** | Статус: **{client_status}** (Візитів: {client_visits_count})")
                client_name = found_client_name
                
                # ---- ПЕРЕВІРКА: чи знижка вже додана в чек ----
                already_has_discount = any("знижка" in str(item["name"]).lower() for item in st.session_state.cart)
                
                if not already_has_discount:
                    # Якщо пенсіонер — пропонуємо пенсійну знижку
                    if client_status.lower() == "пенсіонер":
                        if st.button("👵 Застосувати пенсійну знижку (-100 грн)"):
                            disc_data = st.session_state.services.get("знижка пенсійна", {"price": 100, "is_percent": False})
                            disc_val = float(disc_data["price"])
                            
                            st.session_state.cart.append({
                                "name": "знижка пенсійна", 
                                "category": "Знижки",
                                "price": -disc_val, 
                                "qty": 1.0, 
                                "total": -disc_val,
                                "is_pct": False
                            })
                            st.success("✨ Пенсійну знижку успішно застосовано!")
                            st.rerun()
                    
                    # Якщо постійний клієнт
                    elif client_visits_count >= 2 or client_status.lower() == "постійний":
                        if st.button("🎁 Застосувати знижку постійному клієнту (-50 грн)"):
                            disc_data = st.session_state.services.get("знижка постійному клієнту", {"price": 50, "is_percent": False})
                            disc_val = float(disc_data["price"])
                            
                            st.session_state.cart.append({
                                "name": "знижка постійному клієнту", 
                                "category": "Знижки",
                                "price": -disc_val, 
                                "qty": 1.0, 
                                "total": -disc_val,
                                "is_pct": False
                            })
                            st.success("✨ Знижку постійного клієнта успішно застосовано!")
                            st.rerun()
                else:
                    st.info("✅ Знижка вже застосована до цього чека.")
            else:
                st.info("💡 Номер новий для системи. Будь ласка, вкажіть ім'я клієнта нижче:")
                client_name = st.text_input("👤 Ім'я нового клієнта:", placeholder="Наприклад: Олена")
    
    receipt_comment = st.text_input("💬 Коментар або примітка до чека (необов'язково):", placeholder="Особливі побажання...")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Завершити і зберегти чек"):
            if not is_anon and not entered_digits.strip():
                st.error("❌ Помилка: Введіть номер телефону клієнта або позначте «Анонім»!")
            elif not is_anon and not is_existing_client and not client_name.strip():
                st.error("❌ Помилка: Введіть ім'я нового клієнта!")
            else:
                now = (datetime.now() + timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S")
                today_date_only = (datetime.now() + timedelta(hours=3)).strftime("%Y-%m-%d")
                master = st.session_state.logged_in_master
                history_file = "all_sales_history.xlsx"
                clients_file = "clients_base.xlsx"
                
                if is_anon:
                    cleaned_phone = "Анонім"
                    cleaned_name = "Анонім"
                else:
                    cleaned_phone = f"'{client_phone}"
                    cleaned_name = client_name.strip() if client_name.strip() else found_client_name
                
                # --- ОНОВЛЕННЯ / ЗБЕРЕЖЕННЯ БАЗИ КЛІЄНТІВ ---
                if not is_anon:
                    df_clients = load_clients_base()
                    
                    if not df_clients.empty and "Телефон" in df_clients.columns:
                        df_clients["ЧистийТелефон"] = df_clients["Телефон"].astype(str).apply(lambda x: "".join(filter(str.isdigit, x)))
                        
                        if client_phone in df_clients["ЧистийТелефон"].values:
                            idx = df_clients[df_clients["ЧистийТелефон"] == client_phone].index[0]
                            current_visits = int(df_clients.loc[idx, "Кількість візитів"])
                            df_clients.loc[idx, "Кількість візитів"] = current_visits + 1
                            df_clients.loc[idx, "Останній візит"] = today_date_only
                            df_clients.loc[idx, "Останній майстер"] = master
                            if cleaned_name and cleaned_name != "Без імені":
                                df_clients.loc[idx, "Ім'я"] = cleaned_name
                            if "Статус" not in df_clients.columns or pd.isna(df_clients.loc[idx, "Статус"]):
                                df_clients.loc[idx, "Статус"] = "Звичайний"
                        else:
                            new_client_row = pd.DataFrame([{
                                "Телефон": cleaned_phone,
                                "Ім'я": cleaned_name,
                                "Кількість візитів": 1,
                                "Статус": "Звичайний",
                                "Останній візит": today_date_only,
                                "Останній майстер": master
                            }])
                            df_clients = pd.concat([df_clients, new_client_row], ignore_index=True)
                    else:
                        df_clients = pd.DataFrame([{
                            "Телефон": cleaned_phone,
                            "Ім'я": cleaned_name,
                            "Кількість візитів": 1,
                            "Статус": "Звичайний",
                            "Останній візит": today_date_only,
                            "Останній майстер": master
                        }])
                    
                    if "ЧистийТелефон" in df_clients.columns:
                        df_clients = df_clients.drop(columns=["ЧистийТелефон"])
                        
                    df_clients.to_excel(clients_file, index=False)
                
                # --- ЗБЕРЕЖЕННЯ ЧЕКА В ІСТОРІЮ МАЙСТРА ---
                next_receipt_num = 1
                if os.path.exists(history_file):
                    try:
                        xls = pd.ExcelFile(history_file)
                        if master in xls.sheet_names:
                            df_master_old = pd.read_excel(history_file, sheet_name=master)
                            if "№ чека" in df_master_old.columns:
                                valid_nums = df_master_old["№ чека"].dropna()
                                if not valid_nums.empty:
                                    next_receipt_num = int(valid_nums.max()) + 1
                    except Exception:
                        pass
                
                new_rows = []
                for item in calculated_cart:
                    new_rows.append({
                        "№ чека": next_receipt_num,
                        "Час": now,
                        "Майстер": master,
                        "Телефон клієнта": cleaned_phone,
                        "Ім'я клієнта": cleaned_name,
                        "Категорія": item['category'],
                        "Послуга/Позиція": item['name'],
                        "Кількість": item['qty'],
                        "Ціна за од. / Значення": item['price_display'],
                        "Сума (грн)": item['total'],
                        "Коментар": receipt_comment.strip()
                    })
                
                new_rows.append({
                    "№ чека": next_receipt_num,
                    "Час": now,
                    "Майстер": master,
                    "Телефон клієнта": cleaned_phone,
                    "Ім'я клієнта": cleaned_name,
                    "Категорія": "--- ЗАГАЛОМ ЗА ЧЕК ---",
                    "Послуга/Позиція": f"Підсумок чека №{next_receipt_num}",
                    "Кількість": "",
                    "Ціна за од. / Значення": "",
                    "Сума (грн)": grand_total,
                    "Коментар": receipt_comment.strip()
                })
                
                df_new = pd.DataFrame(new_rows)
                
                if os.path.exists(history_file):
                    with pd.ExcelWriter(history_file, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                        try:
                            df_old_master = pd.read_excel(history_file, sheet_name=master)
                            if "Послуга/Позиція" not in df_old_master.columns:
                                df_combined = df_new
                            else:
                                empty_row = {col: None for col in df_old_master.columns}
                                df_empty = pd.DataFrame([empty_row])
                                df_combined = pd.concat([df_old_master, df_empty, df_new], ignore_index=True)
                        except Exception:
                            df_combined = df_new
                        
                        df_combined.to_excel(writer, sheet_name=master, index=False)
                else:
                    with pd.ExcelWriter(history_file, engine='openpyxl') as writer:
                        df_new.to_excel(writer, sheet_name=master, index=False)
                    
                st.success(f"🎉 Чек №{next_receipt_num} успішно збережено!")
                st.session_state.cart.clear()
                st.rerun()
            
    with col2:
        if st.button("🗑️ Очистити чек"):
            st.session_state.cart.clear()
            st.rerun()
else:
    st.info("Поки що порожній чек.")

# --- ЗАХИЩЕНА ПАНЕЛЬ ХОСТА ---
st.markdown("---")
with st.expander("🔒 Панель хоста (Історія та аналітика за майстрами)"):
    admin_password = st.text_input("Введіть пароль адміністратора:", type="password")
    
    if admin_password == "1234":
        st.success("Доступ дозволено!")
        history_file = "all_sales_history.xlsx"
        clients_file = "clients_base.xlsx"
        
        st.subheader("👥 Клієнтська база")
        
        # Кнопка для оновлення файлу бази клієнтів із новими колонками якщо треба
        if st.button("🔄 Оновити структуру бази клієнтів (додати колонку Статус)"):
            df_fix = load_clients_base()
            df_fix.to_excel(clients_file, index=False)
            st.success("Структуру бази успішно оновлено!")
            st.rerun()
            
        if os.path.exists(clients_file):
            with open(clients_file, "rb") as f:
                client_excel_bytes = f.read()
            st.download_button(
                label="📥 Завантажити повну базу клієнтів (.xlsx)",
                data=client_excel_bytes,
                file_name="basa_klientiv.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            try:
                df_cl_view = pd.read_excel(clients_file)
                st.dataframe(df_cl_view, use_container_width=True)
            except Exception:
                pass
        else:
            st.info("Клієнтська база поки що пуста.")
        
        st.markdown("---")
        if st.button("🗑️ Очистити всю історію чеків (файл продажів)"):
            if os.path.exists(history_file):
                os.remove(history_file)
                st.success("Архів чеків успішно очищено!")
                st.rerun()
            else:
                st.warning("Файл історії вже порожній.")
        
        if os.path.exists(history_file):
            with open(history_file, "rb") as f:
                excel_bytes = f.read()
            
            st.download_button(
                label="📥 Завантажити всю історію чеків в Excel (.xlsx)",
                data=excel_bytes,
                file_name="istoriya_chekiv.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            st.markdown("---")
            st.subheader("📊 Перегляд аркушів майстрів в Excel")
            
            try:
                xls = pd.ExcelFile(history_file)
                sheet_names = xls.sheet_names
                
                selected_sheet = st.selectbox("👤 Оберіть аркуш майстра:", sheet_names)
                
                if selected_sheet:
                    df_sheet = pd.read_excel(history_file, sheet_name=selected_sheet)
                    
                    if "Час" in df_sheet.columns and not df_sheet.empty:
                        df_sheet["Дата"] = pd.to_datetime(df_sheet["Час"], errors='coerce').dt.strftime("%Y-%m-%d")
                        available_dates = df_sheet["Дата"].dropna().unique().tolist()
                        available_dates.sort(reverse=True)
                        
                        selected_date = st.selectbox("📅 Фільтр за датою:", ["Усі дати"] + available_dates)
                        if selected_date != "Усі дати":
                            df_sheet = df_sheet[df_sheet["Дата"] == selected_date]
                        df_sheet = df_sheet.drop(columns=["Дата"])
                    
                    if "Сума (грн)" in df_sheet.columns:
                        total_rev = df_sheet["Сума (грн)"].sum()
                        st.metric(label=f"💰 Загальна сума (Майстер: {selected_sheet})", value=f"{total_rev} грн")
                    
                    st.dataframe(df_sheet, use_container_width=True)
            except Exception as e:
                st.info(f"Помилка читання файлу: {e}")
        else:
            st.info("Архів чеків поки що порожній.")
            
    elif admin_password != "":
        st.error("❌ Неправильний пароль!")
