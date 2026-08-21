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

# 1. Поле введення тексту (працює ідеально і з телефона, і з ПК!)
search_query = st.text_input("🔍 Введіть назву послуги (пошук або додавання)", placeholder="Почніть писати...")

# Шукаємо збіги в базі за тим, що вводить користувач
matched_services = {}
if search_query.strip():
    query_clean = search_query.strip().lower()
    matched_services = {name: price for name, price in st.session_state.services.items() if query_clean in name}
else:
    matched_services = st.session_state.services

# 2. Виводимо підказки або вибір на основі того, що вбили
selected_service = ""
default_price = 0.0

if matched_services:
    # Якщо знайшли збіги, даємо можливість обрати з відфільтрованого списку
    service_names = list(matched_services.keys())
    chosen = st.selectbox("Оберіть із підказок:", service_names)
    selected_service = chosen
    default_price = float(matched_services[chosen])
else:
    # Якщо в базі немає такого — це нова послуга
    selected_service = search_query.strip().lower()
    st.info("💡 Такої послуги ще немає в базі. Вона буде додана як нова.")

qty = st.number_input("Кількість / Години", min_value=0.1, value=1.0, step=0.5)
price = st.number_input("Ціна за одиницю (грн)", min_value=0.0, value=default_price, step=10.0)

# Кнопка додавання до чека
if st.button("Додати до чека", type="primary"):
    if selected_service:
        # Зберігаємо/оновлюємо в загальну базу
        clean_key = selected_service.strip().lower()
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
        st.error("Введіть або оберіть послугу.")

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
