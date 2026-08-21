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

# Звичайне текстове поле — мобільна клавіатура відкривається і дає друкувати що завгодно!
search_text = st.text_input("✍️ Почніть вводити назву послуги:", placeholder="Наприклад: манікюр...")

# Шукаємо збіги в базі в реальному часі
matched_items = {}
if search_text.strip():
    query = search_text.strip().lower()
    matched_items = {k: v for k, v in st.session_state.services.items() if query in k}

# Якщо користувач щось вводить і є підказки — показуємо їх
selected_name = search_text.strip().lower()
default_price = 0.0

if matched_items:
    st.info("💡 Знайдено в базі (натисніть або введіть далі):")
    # Виводимо найближчі варіанти
    for name, price_val in matched_items.items():
        if st.button(f"📌 {name} — {price_val} грн"):
            selected_name = name
            default_price = float(price_val)
            st.rerun()
elif search_text.strip():
    st.warning("⚠️ Такої послуги немає в базі. Вона буде створена як нова.")

# Поля кількості та ціни
qty = st.number_input("Кількість / Години", min_value=0.1, value=1.0, step=0.5)
price = st.number_input("Ціна за одиницю (грн)", min_value=0.0, value=default_price, step=10.0)

# Кнопка додавання до чека
if st.button("Додати до чека", type="primary"):
    if selected_name:
        # Зберігаємо в загальну базу
        st.session_state.services[selected_name] = price
        
        total = qty * price
        st.session_state.cart.append({
            "name": selected_name, 
            "price": price, 
            "qty": qty, 
            "total": total
        })
        st.success(f"Додано: {selected_name} ({qty} од.)")
        st.rerun()
    else:
        st.error("Введіть назву послуги.")

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
