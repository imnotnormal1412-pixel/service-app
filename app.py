import streamlit as st
from datetime import datetime

# База послуг та цін за замовчуванням
if 'services' not in st.session_state:
    st.session_state.services = {
        "стрижка": 300,
        "фарбування": 800,
        "манікюр": 400,
        "матеріал_фарба": 150,
        "миття_голови": 50,
        "укладка": 250
    }

if 'cart' not in st.session_state:
    st.session_state.cart = []

if 'history' not in st.session_state:
    st.session_state.history = []

st.title("✂️ Система розрахунку послуг")
st.markdown("Робоче місце для оформлення замовлень")

# Вибір або введення послуги
service_options = list(st.session_state.services.keys())
selected_service = st.selectbox("Оберіть послугу зі списку", service_options)

# Можливість ввести щось своє або змінити кількість
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

# Перегляд історії збережених чеків (для адміністратора)
if st.session_state.history:
    with st.expander("📂 Історія збережених чеків"):
        for sale in reversed(st.session_state.history):
            st.write(f"**Час:** {sale['time']} | **Сума:** {sale['total']} грн")
            for itm in sale['items']:
                st.write(f"— {itm['name']} ({itm['qty']} x {itm['price']} грн)")
            st.markdown("---")
