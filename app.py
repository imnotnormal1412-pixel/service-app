import streamlit as st
from datetime import datetime
import os

# База послуг та цін за замовчуванням
if 'services' not in st.session_state:
    st.session_state.services = {
        "Установка люстри": 519,
        "Матеріал люстра": 1500,
        "Установка розетки": 400,
        "Матеріал розетка": 150,
        "Виїзд майстра": 450,

    }

if 'cart' not in st.session_state:
    st.session_state.cart = []

st.title("✂️ Система розрахунку послуг")
st.markdown("Робоче місце для оформлення замовлень")

# Поле для ідентифікації майстра
master_name = st.text_input("👤 Хто оформлює замовлення (Ваше ім'я):", placeholder="Наприклад: Олена")

st.markdown("---")

# Вибір або введення послуги
service_options = list(st.session_state.services.keys())
selected_service = st.selectbox("Оберіть послугу зі списку", service_options)

# Можливість змінити кількість
qty = st.number_input("Кількість / Години", min_value=0.1, value=1.0, step=0.5)

# Блок додавання нової послуги, якщо її немає в базовому списку
with st.expander("➕ Додати нову послугу в базу (якщо немає в списку)"):
    new_name = st.text_input("Назва нової послуги")
    new_price = st.number_input("Ціна за одиницю (грн)", min_value=0.0, value=0.0)
    if st.button("Зберегти нову послугу"):
        if new_name and new_price > 0:
            st.session_state.services[new_name.strip()] = new_price
            st.success(f"Послугу '{new_name}' успішно додано!")
            st.rerun()
        else:
            st.error("Введіть назву та коректну ціну.")

# Кнопка додавання до поточного чека
if st.button("Додати до чека", type="primary"):
    if not master_name.strip():
        st.error("⚠️ Будь ласка, введіть своє ім'я у верхньому полі перед додаванням послуг!")
    else:
        price = st.session_state.services[selected_service]
        total = qty * price
        st.session_state.cart.append({
            "name": selected_service, 
            "price": price, 
            "qty": qty, 
            "total": total
        })
        st.success(f"Додано: {selected_service} ({qty} од.)")

# Відображення поточного чека
st.markdown("---")
st.subheader("🧾 Поточний чек клієнта")

if st.session_state.cart:
    grand_total = 0
    for i, item in enumerate(st.session_state.cart):
        st.write(f"**{i+1}. {item['name']}** — {item['qty']} од. x {item['price']} грн = **{item['total']} грн**")
        grand_total += item['total']
    
    st.markdown(f"### Загальна сума: {grand_total} грн")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Завершити і зберегти чек"):
            if not master_name.strip():
                st.error("⚠️ Введіть ім'я майстра на початку сторінки!")
            else:
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Формуємо запис із ім'ям майстра та чеком
                history_record = f"Час: {now} | Майстер: {master_name} | Сума: {grand_total} грн\n"
                for item in st.session_state.cart:
                    history_record += f"   - {item['name']} ({item['qty']} x {item['price']} грн = {item['total']} грн)\n"
                history_record += "-" * 40 + "\n"
                
                # Зберігаємо у файл на сервері
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
    
    # Можеш змінити "1234" на будь-який інший власний пароль
    if admin_password == "1234":
        st.success("Доступ дозволено!")
        history_file = "all_sales_history.txt"
        if os.path.exists(history_file):
            with open(history_file, "r", encoding="utf-8") as f:
                history_data = f.read()
            
            st.download_button(
                label="📥 Завантажити повну історію чеків файлом",
                data=history_data,
                file_name="istoriya_chekiv.txt",
                mime="text/plain"
            )
            st.text(history_data)
        else:
            st.info("Архів чеків поки що порожній.")
    elif admin_password != "":
        st.error("❌ Неправильний пароль!")
