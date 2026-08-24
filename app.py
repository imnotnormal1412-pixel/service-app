import streamlit as st
from datetime import datetime
import os

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
        "Знижка постійному клієнту": {"category": "Знижки", "price": 100},
        "Акція вихідного дня": {"category": "Знижки", "price": 120},
        "Знижка пенсіонер": {"category": "Знижки", "price": 200},
        "Знижка військовий": {"category": "Знижки", "price": 250},
        "Знижка ВПО": {"category": "Знижки", "price": 250},
    }

if 'cart' not in st.session_state:
    st.session_state.cart = []

st.title("✂️ Система розрахунку послуг")
st.markdown("Робоче місце для оформлення замовлень")

# Поле для ідентифікації майстра
st.title("✂️ Система розрахунку послуг")
st.markdown("Робоче місце для оформлення замовлень")

# --- ПУНКТ 4: Авторизація на початку ---
# Перевіряємо, чи ми вже знаємо ім'я майстра в цій сесії
if 'logged_in_master' not in st.session_state:
    st.session_state.logged_in_master = ""

# Якщо ім'я ще не введене, показуємо віконце авторизації
if not st.session_state.logged_in_master:
    st.warning("👋 Будь ласка, представтеся перед початком роботи.")
    with st.form("login_form"):
        entered_name = st.text_input("Введіть ваше ім'я")
        submit_login = st.form_submit_button("Увійти в систему", type="primary")
        
        if submit_login:
            if entered_name.strip():
                st.session_state.logged_in_master = entered_name.strip()
                st.rerun() # Перезавантажуємо сторінку, щоб відкрити касу
            else:
                st.error("Будь ласка, введіть ім'я.")
    
    # Зупиняємо виконання решти коду, доки не здійснено вхід
    st.stop()

# Якщо вхід виконано, виводимо привітання і кнопку виходу збоку
col_user1, col_user2 = st.columns([3, 1])
with col_user1:
    st.success(f"Працює майстер: **{st.session_state.logged_in_master}**")
with col_user2:
    if st.button("Змінити майстра"):
        st.session_state.logged_in_master = ""
        st.rerun()

# Далі в коді скрізь замість старого `master_name` використовуємо `st.session_state.logged_in_master`
master_name = st.session_state.logged_in_master

st.markdown("---")

# 1. Вибираємо категорію (тепер тут є і "Знижки")
categories = ["Послуги", "Матеріали", "Інше", "Знижки"]
selected_category = st.selectbox("Оберіть категорію:", categories)

# Фільтруємо послуги за обраною категорією
filtered_services = {name: data for name, data in st.session_state.services.items() if data["category"] == selected_category}
service_options = list(filtered_services.keys())

if service_options:
    selected_service = st.selectbox("Оберіть послугу зі списку", service_options)
    current_price = float(filtered_services[selected_service]["price"])
else:
    selected_service = None
    current_price = 0.0
    st.info("У цій категорії поки немає позицій.")

# Можливість змінити кількість та ціну
qty = st.number_input("Кількість / Години", min_value=0.1, value=1.0, step=0.5)
price = st.number_input("Ціна за одиницю (грн)", min_value=0.0, value=current_price, step=10.0)

# Блок додавання нової послуги чи знижки
with st.expander("➕ Додати нову послугу або знижку до чеку"):
    custom_name = st.text_input("Назва позиції")
    custom_price = st.number_input("Сума (грн)", min_value=0.0, value=0.0, key="cust_p")
    is_discount = st.checkbox("Це знижка (віднімати від суми)?", key="cust_d")

    if st.button("Додати цю позицію до чека"):
        if custom_name.strip() and custom_price > 0:
            p_val = -custom_price if is_discount else custom_price
            st.session_state.cart.append({
                "name": custom_name.strip(),
                "category": "Знижки" if is_discount else "Кастомні",
                "price": p_val,
                "qty": 1.0,
                "total": p_val
            } )
            st.success(f"Позицію '{custom_name}' додано до чека!")
            st.rerun()
        else:
            st.error("Введіть назву та коректну суму.")

# Кнопка додавання до поточного чека
if st.button("Додати до чека", type="primary"):
    if not master_name.strip():
        st.error("⚠️ Будь ласка, введіть своє ім'я у верхньому полі перед додаванням послуг!")
    elif not selected_service:
        st.error("Оберіть позицію зі списку.")
    else:
        # Якщо це знижка, робимо суму мінусовою автоматично!
        item_price = -price if selected_category == "Знижки" else price
        total = qty * item_price
        
        st.session_state.cart.append({
            "name": selected_service, 
            "category": selected_category,
            "price": item_price, 
            "qty": qty, 
            "total": total
        })
        st.success(f"Додано до чека: {selected_service}")

# Відображення поточного чека
st.markdown("---")
st.subheader("🧾 Поточний чек клієнта")

if st.session_state.cart:
    grand_total = 0
    for i, item in enumerate(st.session_state.cart):
        st.write(f"**{i+1}. [{item['category']}] {item['name']}** — {item['qty']} од. x {item['price']} грн = **{item['total']} грн**")
        grand_total += item['total']
    
    st.markdown(f"### Загальна сума до сплати: {grand_total} грн")
    
    col1, col2 = st.columns(2)
    with col1:
# Кнопка збереження чека (перевір, щоб під `if` був правильний відступ праворуч)
if st.button("💾 Завершити і зберегти чек"):
    if not st.session_state.get('logged_in_master'):
        st.error("⚠️ Введіть ім'я майстра на початку сторінки!")
    else:
        from datetime import datetime, timedelta
        import pandas as pd
        
        now = (datetime.now() + timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S")
        master = st.session_state.logged_in_master
        
        new_rows = []
        for item in st.session_state.cart:
            new_rows.append({
                "Час": now,
                "Майстер": master,
                "Категорія": item['category'],
                "Послуга/Позиція": item['name'],
                "Кількість": item['qty'],
                "Ціна за од. (грн)": item['price'],
                "Сума (грн)": item['total']
            })
        
        excel_file = "all_sales_history.xlsx"
        
        if os.path.exists(excel_file):
            df_old = pd.read_excel(excel_file)
            df_new = pd.DataFrame(new_rows)
            df_combined = pd.concat([df_old, df_new], ignore_index=True)
            df_combined.to_excel(excel_file, index=False)
        else:
            df_new = pd.DataFrame(new_rows)
            df_new.to_excel(excel_file, index=False)
            
        st.success("🎉 Чек успішно збережено в Excel-базу!")
        st.session_state.cart.clear()
        st.rerun()
            
    with col2:
        if st.button("🗑️ Очистити чек"):
            st.session_state.cart.clear()
            st.rerun()
else:
    st.info("Чек поки що порожній.")

# --- ЗАХИЩЕНА ПАНЕЛЬ ХОСТА ---
st.markdown("---")
with st.expander("🔒 Панель хоста (Історія всіх чеків)"):
    admin_password = st.text_input("Введіть пароль адміністратора:", type="password")
    
    if admin_password == "1111":
        st.success("Доступ дозволено!")
        history_file = "all_sales_history.xlsx"
        
        if os.path.exists(history_file):
            with open(history_file, "rb") as f:
                excel_bytes = f.read()
            
            st.download_button(
                label="📥 Завантажити всю історію в Excel (.xlsx)",
                data=excel_bytes,
                file_name="istoriya_chekiv.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            import pandas as pd
            df_display = pd.read_excel(history_file)
            st.dataframe(df_display)
        else:
            st.info("Архів чеків поки що порожній.")
    elif admin_password != "":
        st.error("❌ Неправильний пароль!")
            
            # Також виведемо саму таблицю на екран для зручності хоста
            import pandas as pd
            df_display = pd.read_excel(history_file)
            st.dataframe(df_display)
        else:
            st.info("Архів чеків поки що порожній.")
    elif admin_password != "":
        st.error("❌ Неправильний пароль!")
