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
    }

if 'cart' not in st.session_state:
    st.session_state.cart = []

if 'history' not in st.session_state:
    st.session_state.history = []

st.title("✂️ Система розрахунку послуг")
st.markdown("Робоче місце для оформлення замовлень")

# Повертаємо єдиний зручний пошук-selectbox, який фільтрує варіанти по ходу введення
service_options = list(st.session_state.services.keys())
selected_service = st.selectbox("Пошук послуги (почніть вводити назву):", service_options)

# Автоматично підтягуємо ціну вибраної послуги
default_price = float(st.session_state.services.get(selected_service, 0.0))

qty = st.number_input("Кількість / Години", min_value=0.1, value=1.0, step=0.5)
price = st.number_input("Ціна за одиницю (грн)", min_value=0.0, value=default_price, step=10.0)

# Додатковий блок для додавання абсолютно нових послуг, яких ще немає в списку
with st.expander("➕ Додати абсолютно нову послугу в базу"):
    new_name = st.text_input("Назва нової послуги")
    new_price = st.number_input("Ціна нової послуги (грн)", min_value=0.0, value=0.0)
    if st.button("Зберегти нову послугу в базу"):
        if new_name.strip() and new_price > 0:
            clean_new_name = new_name.strip().lower()
            st.session_state.services[clean_new_name] = new_price
            st.success(f"Послугу '{clean_new_name}' успішно додано!")
            st.rerun()
        else:
            st.error("Введіть назву та коректну ціну.")

# Кнопка додавання до чека
if st.button("Додати до чека", type="primary"):
    if selected_service:
        total = qty * price
        st.session_state.cart.append({
            "name": selected_service, 
            "price": price, 
            "qty": qty, 
            "total": total
        })
        st.success(f"Додано: {selected_service} ({qty} од.)")
    else:
        st.error("Оберіть послугу.")

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
