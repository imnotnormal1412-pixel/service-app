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

# Робимо перемикач: Вибрати з готового чи Додати свою
tab1, tab2 = st.tabs(["✨ Обрати з прайсу", "➕ Додати нову послугу"])

with tab1:
    st.subheader("Швидкий вибір послуги")
    service_list = list(st.session_state.services.keys())
    
    # Використовуємо звичайний список для мобільних (натискаєш і обираєш зі списку одним пальцем)
    chosen_service = st.selectbox("Оберіть послугу зі списку:", service_list, key="mobile_select")
    
    current_price = float(st.session_state.services[chosen_service])
    qty = st.number_input("Кількість / Години", min_value=0.1, value=1.0, step=0.5, key="qty_1")
    price = st.number_input("Ціна за од. (грн)", min_value=0.0, value=current_price, step=10.0, key="price_1")

    if st.button("Додати до чека", type="primary", key="btn_1"):
        total = qty * price
        st.session_state.cart.append({
            "name": chosen_service, 
            "price": price, 
            "qty": qty, 
            "total": total
        })
        st.success(f"Додано: {chosen_service} ({qty} од.)")
        st.rerun()

with tab2:
    st.subheader("Створення кастомної послуги")
    custom_name = st.text_input("Введіть назву послуги вручну", placeholder="Наприклад: ламінування")
    custom_qty = st.number_input("Кількість / Години", min_value=0.1, value=1.0, step=0.5, key="qty_2")
    custom_price = st.number_input("Ціна за од. (грн)", min_value=0.0, value=0.0, step=10.0, key="price_2")

    if st.button("Зберегти і додати до чека", type="primary", key="btn_2"):
        if custom_name.strip() and custom_price > 0:
            clean_name = custom_name.strip().lower()
            # Додаємо в загальну базу на майбутнє
            st.session_state.services[clean_name] = custom_price
            
            total = custom_qty * custom_price
            st.session_state.cart.append({
                "name": clean_name, 
                "price": custom_price, 
                "qty": custom_qty, 
                "total": total
            })
            st.success(f"Додано нову послугу: {clean_name}")
            st.rerun()
        else:
            st.error("Будь ласка, введіть назву та ціну.")

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
