import streamlit as st
from datetime import datetime

# База послуг та цін
if 'services' not in st.session_state:
    st.session_state.services = {
        "Установка люстри": 520,
        "Монтаж кнопки дзвінка": 190,
        "Установка розетки": 200,
        "Матеріал розетка": 100,
        "Матеріал люстра": 1000,
        "Виїзд майстра": 400
    }

if 'cart' not in st.session_state:
    st.session_state.cart = []

if 'history' not in st.session_state:
    st.session_state.history = []

st.title("✂️ Система розрахунку послуг")
st.markdown("Робоче місце для оформлення замовлень")

# Вибір режиму: обрати з бази чи ввести своє
input_mode = st.radio("Як ви хочете додати послугу?", ["📌 Обрати зі списку", "✏️ Ввести свою назву вручну"], horizontal=True)

service_name = ""
default_price = 0.0

if input_mode == "📌 Обрати зі списку":
    # Список для вибору
    options = ["-- Оберіть послугу --"] + list(st.session_state.services.keys())
    selected = st.selectbox("Список послуг", options)
    
    if selected != "-- Оберіть послугу --":
        service_name = selected
        default_price = float(st.session_state.services[selected])
else:
    # Ручне введення для кастомних послуг
    service_name = st.text_input("Введіть назву нової послуги", placeholder="Наприклад: ботокс волосся")
    # Перевіряємо, чи є вона раптом у базі, щоб підтягнути ціну
    clean_name = service_name.strip().lower()
    if clean_name in st.session_state.services:
        default_price = float(st.session_state.services[clean_name])

# Поля кількості та ціни
qty = st.number_input("Кількість / Години", min_value=0.1, value=1.0, step=0.5)
price = st.number_input("Ціна за одиницю (грн)", min_value=0.0, value=default_price, step=10.0)

# Кнопка додавання до чека
if st.button("Додати до чека", type="primary"):
    final_name = service_name.strip()
    if final_name and final_name != "-- Оберіть послугу --":
        # Зберігаємо в загальну базу на майбутнє
        clean_key = final_name.lower()
        st.session_state.services[clean_key] = price
        
        total = qty * price
        st.session_state.cart.append({
            "name": clean_key, 
            "price": price, 
            "qty": qty, 
            "total": total
        })
        st.success(f"Додано: {clean_key} ({qty} од.)")
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
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sale_info = {"time": now, "items": list(st.session_state.cart), "total": grand_total}
            st.session_state.history.append(sale_info)
            st.session_state.cart.clear()
            st.success("Чек успішно збережено в історію!")
            st.rerun()
            
    with col2:
        if st.button("🗑️ Очистити чек"):
            st.session_state.cart.clear()
            st.rerun()
else:
    st.info("Чек поки що порожній.")

# Історія
if st.session_state.history:
    with st.expander("📂 Історія збережених чеків"):
        for sale in reversed(st.session_state.history):
            st.write(f"**Час:** {sale['time']} | **Сума:** {sale['total']} грн")
            for itm in sale['items']:
                st.write(f"— {itm['name']} ({itm['qty']} x {itm['price']} грн)")
            st.markdown("---")
