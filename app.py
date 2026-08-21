import streamlit as st
from datetime import datetime
import os

# База послуг та цін
if 'services' not in st.session_state:
    st.session_state.services = {
        "Установка люстри": 520,
        "Монтаж кнопки дзвінка": 190,
        "Установка розетки": 200,
        "Матеріал розетка": 100,
        "Матеріал люстра": 1000,
    }

if 'cart' not in st.session_state:
    st.session_state.cart = []

st.title("✂️ Система розрахунку послуг")

# Поле для ідентифікації майстра/акаунта
master_name = st.text_input("👤 Хто оформлює замовлення (Ваше ім'я):", placeholder="Наприклад: Олена або Адмін")

st.markdown("---")

# Вибір: з наявних чи своя нова
choice_type = st.radio("Дія:", ["Обрати з наявних послуг", "Ввести нову послугу вручну"], horizontal=True)

service_name = ""
default_price = 0.0

if choice_type == "Обрати з наявних послуг":
    services_list = ["-- Виберіть послугу --"] + list(st.session_state.services.keys())
    selected = st.selectbox("Список послуг:", services_list)
    if selected != "-- Виберіть послугу --":
        service_name = selected
        default_price = float(st.session_state.services[selected])
else:
    service_name = st.text_input("Назва нової послуги:", placeholder="Введіть назву...")
    clean_typed = service_name.strip().lower()
    if clean_typed in st.session_state.services:
        default_price = float(st.session_state.services[clean_typed])

qty = st.number_input("Кількість / Години", min_value=0.1, value=1.0, step=0.5)
price = st.number_input("Ціна за одиницю (грн)", min_value=0.0, value=default_price, step=10.0)

# Кнопка додавання до чека
if st.button("Додати до чека", type="primary"):
    if not master_name.strip():
        st.error("⚠️ Будь ласка, введіть своє ім'я зверху перед додаванням послуг!")
    else:
        final_name = service_name.strip().lower()
        if final_name and final_name != "-- виберіть послугу --":
            st.session_state.services[final_name] = price
            
            total = qty * price
            st.session_state.cart.append({
                "name": final_name, 
                "price": price, 
                "qty": qty, 
                "total": total
            })
            st.success(f"Додано: {final_name} ({qty} од.)")
            st.rerun()
        else:
            st.error("Будь ласка, оберіть або введіть назву послуги.")

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
                
                # Формуємо текст запису для файлу
                history_record = f"Час: {now} | Майстер: {master_name} | Сума: {grand_total} грн\n"
                for item in st.session_state.cart:
                    history_record += f"   - {item['name']} ({item['qty']} x {item['price']} грн = {item['total']} грн)\n"
                history_record += "-" * 40 + "\n"
                
                # Записуємо у файл на сервері
                filename = "all_sales_history.txt"
                with open(filename, "a", encoding="utf-8") as f:
                    f.write(history_record)
                
                st.success("🎉 Чек успішно збережено в загальну базу хоста!")
                st.session_state.cart.clear()
                st.rerun()
            
    with col2:
        if st.button("🗑️ Очистити чек"):
            st.session_state.cart.clear()
            st.rerun()
else:
    st.info("Чек поки що порожній.")

# Блок адміністратора / хоста для перегляду та завантаження всіх чеків
st.markdown("---")
st.subheader("🔒 Панель хоста (Історія всіх чеків)")

history_file = "all_sales_history.txt"
if os.path.exists(history_file):
    with open(history_file, "r", encoding="utf-8") as f:
        history_data = f.read()
    
    # Кнопка для скачування файлу з історією на комп'ютер (можна відкрити в блокноті чи Excel)
    st.download_button(
        label="📥 Завантажити повну історію чеків файлом",
        data=history_data,
        file_name="istoriya_chekiv.txt",
        mime="text/plain"
    )
    
    with st.expager("👀 Переглянути історію на екрані") if hasattr(st, "expager") else st.expander("👀 Переглянути історію на екрані"):
        st.text(history_data)
else:
    st.info("Архів чеків поки що порожній. Збережіть перший чек, і він з'явиться тут.")
