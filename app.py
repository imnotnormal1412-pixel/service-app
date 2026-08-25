import streamlit as st
from datetime import datetime, timedelta
import os
import pandas as pd

# =========================================================================
# 1. НАЛАШТУВАННЯ ТА СПИСКИ (МАЙСТРИ, ПОСЛУГИ, ЦІНИ, ЗНИЖКИ)
# =========================================================================

ALLOWED_MASTERS = ["Микола", "Олена", "Тато", "Адмін", "Хост"]

if 'services' not in st.session_state:
    st.session_state.services = {
        # --- Послуги ---
        "Установка люстри": {"category": "Послуги", "price": 520},
        "Установка і підключення розетки": {"category": "Послуги", "price": 135},
        "Установка і підключення вимикача": {"category": "Послуги", "price": 135},
        "Встановлення та підключення вхідного дзвінка": {"category": "Послуги", "price": 270},
        "Установка і підключення бойлера": {"category": "Послуги", "price": 2090},

        # --- Матеріали ---
        "Розетка одинарна (склад)": {"category": "Матеріали", "price": 100},
        "Розетка одинарна (магазин)": {"category": "Матеріали", "price": 300},
        "Розетка подвійна (склад)": {"category": "Матеріали", "price": 300},
        "Розетка подвійна (магазин)": {"category": "Матеріали", "price": 500},
        "Лампа світлодіодна (склад)": {"category": "Матеріали", "price": 150},
        "Лампа світлодіодна (магазин)": {"category": "Матеріали", "price": 350},

        # --- Інше ---
        "Виїзд майстра": {"category": "Інше", "price": 500},

        # --- Знижки ---
        "Знижка Пенсіонер": {"category": "Знижки", "price": 200},
        "Знижка Військовий": {"category": "Знижки", "price": 250},
        "Знижка постійному клієнту": {"category": "Знижки", "price": 50, "is_percent": False},
        "Акція вихідного дня": {"category": "Знижки", "price": 100, "is_percent": False},
        "Знижка ВПО": {"category": "Знижки", "price": 15, "is_percent": True},
    }

if 'cart' not in st.session_state:
    st.session_state.cart = []

# =========================================================================
# 2. РОБОТА З БАЗОЮ КЛІЄНТІВ (ФАЙЛ clients_base.xlsx)
# =========================================================================

def load_clients_base():
    clients_file = "clients_base.xlsx"
    expected_columns = ["Телефон", "Ім'я", "Кількість візитів", "Статус", "Коментар майстра", "Внутрішня примітка", "Останній візит", "Останній майстер"]
    
    if os.path.exists(clients_file):
        try:
            df = pd.read_excel(clients_file, dtype=str)
            
            # Примусово переводимо телефон у текст і прибираємо крапки (.0)
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

# =========================================================================
# 3. ІНТЕРФЕЙС ТА АВТОРИЗАЦІЯ
# =========================================================================

st.title("✂️ Система розрахунку послуг")

if 'logged_in_master' not in st.session_state:
    st.session_state.logged_in_master = ""

if not st.session_state.logged_in_master:
    st.warning("👋 Будь ласка, введіть ваше ім'я для входу (або «Адмін» для доступу в Панель хоста).")
    with st.form("login_form"):
        entered_name = st.text_input("Ім'я майстра / Вхід:")
        submit_login = st.form_submit_button("Увійти в систему", type="primary")
        
        if submit_login:
            clean_name = entered_name.strip()
            if any(clean_name.lower() == m.lower() for m in ALLOWED_MASTERS):
                st.session_state.logged_in_master = clean_name
                st.rerun()
            else:
                st.error("❌ Доступ заборонено: такого користувача немає в системі.")
    st.stop()

master_name = st.session_state.logged_in_master

# =========================================================================
# АВТОРИЗАЦІЯ ХОСТА / АДМІНІСТРАТОРА (ОКРЕМУ ПАНЕЛЬ)
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
            st.rerun()

    if enter_admin:
        if admin_password == "1234":
            st.session_state.host_authenticated = True
        else:
            st.error("❌ Неправильний пароль!")
            st.session_state.host_authenticated = False

    if st.session_state.get("host_authenticated", False):
        st.success("✅ Вітаємо в Панелі Хоста!")
        
        if st.button("⬅️ Повернутися до оформлення чеку"):
            st.session_state.logged_in_master = ""
            st.session_state.host_authenticated = False
            st.rerun()

        st.markdown("---")
        
        # БЛОК 1: АНАЛІТИЧНИЙ ДАШБОРД ТА РЕЙТИНГ МАЙСТРІВ
        st.subheader("📊 Аналітика та рейтинг успішності майстрів")
        history_file = "all_sales_history.xlsx"
        
        if os.path.exists(history_file):
            try:
                xls = pd.ExcelFile(history_file)
                all_masters_data = []
                for sheet in xls.sheet_names:
                    df_sh = pd.read_excel(history_file, sheet_name=sheet)
                    if not df_sh.empty:
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

                    df_totals = df_filtered_stat[df_filtered_stat["Категорія"] == "--- ЗАГАЛОМ ЗА ЧЕК ---"]
                    
                    if not df_totals.empty and "Майстер" in df_totals.columns and "Сума (грн)" in df_totals.columns:
                        rating_df = df_totals.groupby("Майстер").agg(
                            Заробіток=("Сума (грн)", "sum"),
                            Кількість_чеків=("№ чека", "nunique")
                        ).reset_index().sort_values(by="Заробіток", ascending=False)
                        
                        st.markdown(f"### 🏆 Рейтинг майстрів ({analytics_period.lower()})")
                        st.dataframe(rating_df, use_container_width=True)
                    else:
                        st.info("Поки недостатньо даних за обраний період.")
            except Exception as e:
                st.info(f"Помилка аналітики: {e}")
        else:
            st.info("Історія продажів поки порожня.")

        st.markdown("---")
        
        # БЛОК 2: КЛІЄНТСЬКА БАЗА
        st.subheader("👥 Клієнтська база")
        clients_file = "clients_base.xlsx"
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
        
        # БЛОК 3: ІСТОРІЯ ТА ПЕРЕГЛЯД ЧЕКІВ
        st.subheader("📁 Перегляд чеків та управління архівом")
        if os.path.exists(history_file):
            if st.button("🗑️ Очистити всю історію чеків"):
                os.remove(history_file)
                st.success("Архів чеків очищено!")
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
            except Exception as e:
                st.info(f"Помилка: {e}")
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
        price = st.number_input("Знижка у відсотках (%)", min_value=0.0, max_value=100.0, value=current_price, step=1.0)
    else:
        price = st.number_input("Сума знижки (грн)", min_value=0.0, value=current_price, step=10.0)
else:
    price = st.number_input("Ціна за одиницю (грн)", min_value=0.0, value=current_price, step=10.0)

if st.button("Додати до чека", type="primary"):
    if not selected_service:
        st.error("Оберіть позицію зі списку.")
    else:
        already_has_discount = any(item['category'] == "Знижки" for item in st.session_state.cart)
        if selected_category == "Знижки" and already_has_discount:
            st.error("❌ У чеку вже є знижка!")
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
            st.rerun()

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
        col_item_info, col_item_del = st.columns([5, 1])
        with col_item_info:
            st.write(f"**{i+1}. [{item['category']}] {item['name']}** — {item['qty']} од. x {item['price_display']} = **{item['total']} грн**")
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
            
            # Стандартизуємо введений номер до формату 380...
            if clean_input_digits.startswith("380"):
                target_search_phone = clean_input_digits
            elif clean_input_digits.startswith("0"):
                target_search_phone = f"380{clean_input_digits[1:]}"
            else:
                target_search_phone = f"380{clean_input_digits}"
            
            df_check = load_clients_base()
            if not df_check.empty and "Телефон" in df_check.columns:
                # Робимо цифрову копію телефону в базі для надійного порівняння без розбіжностей
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
                    st.info(f"💬 **Коментар майстра:** {client_note}")
                client_name = found_client_name
                
                already_has_discount = any(item['category'] == "Знижки" for item in st.session_state.cart)
                if not already_has_discount:
                    status_lower = client_status.lower()
                    
                    # Пріоритет пільговим статусам: показуємо тільки одну відповідну кнопку
                    if "пенсіонер" in status_lower:
                        if st.button("👵 Застосувати Знижка Пенсіонер"):
                            st.session_state.cart.append({"name": "Знижка Пенсіонер", "category": "Знижки", "price": -200, "qty": 1.0, "total": -200, "is_pct": False})
                            st.rerun()
                    elif "військовий" in status_lower:
                        if st.button("🪖 Застосувати Знижка Військовий"):
                            st.session_state.cart.append({"name": "Знижка Військовий", "category": "Знижки", "price": -250, "qty": 1.0, "total": -250, "is_pct": False})
                            st.rerun()
                    elif "впо" in status_lower:
                        if st.button("💙💛 Застосувати Знижка ВПО"):
                            st.session_state.cart.append({"name": "Знижка ВПО (15%)", "category": "Знижки", "price": -15, "qty": 1.0, "total": -15, "is_pct": True})
                            st.rerun()
                    elif client_visits_count >= 2 or "постійний" in status_lower:
                        if st.button("🎁 Застосувати Знижка постійному клієнту"):
                            st.session_state.cart.append({"name": "Знижка постійному клієнту", "category": "Знижки", "price": -50, "qty": 1.0, "total": -50, "is_pct": False})
                            st.rerun()
            else:
                st.info("✅ Знижка вже застосована до цього чека.")
            else:
                st.info("💡 Номер новий. Вкажіть ім'я клієнта:")
                client_name = st.text_input("👤 Ім'я нового клієнта:")
    
    new_master_comment = st.text_input("💬 Коментар майстра щодо візиту:", value=client_note)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Завершити і зберегти чек"):
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
                            if new_master_comment.strip():
                                df_clients.loc[idx, "Коментар майстра"] = new_master_comment.strip()
                        else:
                            new_row = pd.DataFrame([{"Телефон": cleaned_phone, "Ім'я": cleaned_name, "Кількість візитів": 1, "Статус": "Звичайний", "Коментар майстра": new_master_comment.strip(), "Внутрішня примітка": "", "Останній візит": today_date_only, "Останній майстер": master_name}])
                            df_clients = pd.concat([df_clients, new_row], ignore_index=True)
                    else:
                        df_clients = pd.DataFrame([{"Телефон": cleaned_phone, "Ім'я": cleaned_name, "Кількість візитів": 1, "Статус": "Звичайний", "Коментар майстра": new_master_comment.strip(), "Внутрішня примітка": "", "Останній візит": today_date_only, "Останній майстер": master_name}])
                    
                    if "ЧистийТелефон" in df_clients.columns:
                        df_clients = df_clients.drop(columns=["ЧистийТелефон"])
                    df_clients.to_excel(clients_file, index=False)
                
                next_receipt_num = 1
                if os.path.exists(history_file):
                    try:
                        xls = pd.ExcelFile(history_file)
                        if master_name in xls.sheet_names:
                            df_old = pd.read_excel(history_file, sheet_name=master_name)
                            if "№ чека" in df_old.columns and not df_old["№ чека"].dropna().empty:
                                next_receipt_num = int(df_old["№ чека"].dropna().max()) + 1
                    except Exception:
                        pass
                
                new_rows = [{
                    "№ чека": next_receipt_num, "Час": now, "Майстер": master_name, "Телефон клієнта": cleaned_phone,
                    "Ім'я клієнта": cleaned_name, "Категорія": item['category'], "Послуга/Позиція": item['name'],
                    "Кількість": item['qty'], "Ціна за од. / Значення": item['price_display'], "Сума (грн)": item['total']
                } for item in calculated_cart]
                
                new_rows.append({
                    "№ чека": next_receipt_num, "Час": now, "Майстер": master_name, "Телефон клієнта": cleaned_phone,
                    "Ім'я клієнта": cleaned_name, "Категорія": "--- ЗАГАЛОМ ЗА ЧЕК ---", "Послуга/Позиція": f"Підсумок чека №{next_receipt_num}",
                    "Кількість": "", "Ціна за од. / Значення": "", "Сума (грн)": grand_total
                })
                
                df_new = pd.DataFrame(new_rows)
                if os.path.exists(history_file):
                    with pd.ExcelWriter(history_file, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                        try:
                            df_old_m = pd.read_excel(history_file, sheet_name=master_name)
                            df_combined = pd.concat([df_old_m, pd.DataFrame([{col: None for col in df_old_m.columns}]), df_new], ignore_index=True) if "Послуга/Позиція" in df_old_m.columns else df_new
                        except Exception:
                            df_combined = df_new
                        df_combined.to_excel(writer, sheet_name=master_name, index=False)
                else:
                    with pd.ExcelWriter(history_file, engine='openpyxl') as writer:
                        df_new.to_excel(writer, sheet_name=master_name, index=False)
                
                st.success(f"🎉 Чек №{next_receipt_num} збережено!")
                st.session_state.cart.clear()
                st.rerun()
    with col2:
        if st.button("🗑️ Очистити чек"):
            st.session_state.cart.clear()
            st.rerun()
else:
    st.info("Поки що порожній чек.")
