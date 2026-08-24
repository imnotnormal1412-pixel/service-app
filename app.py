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
master_name = st.text_input("👤 Хто оформлює замовлення (Ваше ім'я):", placeholder="Наприклад: Олена")

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
with st.expander("➕ Додати нову послугу або знижку в базу"):
    new_name = st.text_input("Назва (наприклад, 'знижка 10% або назва акції')")
    new_cat = st.selectbox("Категорія:", categories, key="new_cat_select")
    new_price = st.number_input("Сума (грн)", min_value=0.0, value=0.0, key="new_price_input")
    
    if st.button("Зберегти в базу"):
        if new_name.strip() and new_price > 0:
            clean_name = new_name.strip().lower()
            st.session_state.services[clean_name] = {"category": new_cat, "price": new_price}
            st.success(f"Успішно додано до категорії '{new_cat}'!")
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
        if st.button("💾 Завершити і зберегти чек"):
            if not master_name.strip():
                st.error("⚠️ Введіть ім'я майстра на початку сторінки!")
            else:
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                history_record = f"Час: {now} | Майстер: {master_name} | Загалом: {grand_total} грн\n"
                for item in st.session_state.cart:
                    history_record += f"   - [{item['category']}] {item['name']} ({item['qty']} x {item['price']} грн = {item['total']} грн)\n"
                history_record += "-" * 40 + "\n"
                
                filename = "all_sales_history.txt"
                with open(filename, "a", encoding="utf-8") as f:
                    f.write(history_record)
                
                st.success("Чек успішно збережено в загальну базу!")
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
        history_file = "all_sales_history.txt"
        if os.path.exists(history_file):
            with open(history_file, "r", encoding="utf-8") as f:
                history_data = f.read()
            
            st.download_button(
                label="📥 Завантажити повну історію чеків файлом",
                data=history_data,
                file_name="istoriya_chekiv.xls",
                mime="text/plain"
            )
            st.text(history_data)
        else:
            st.info("Архів чеків поки що порожній.")
    elif admin_password != "":
        st.error("❌ Неправильний пароль!")
