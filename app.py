import streamlit as st

# Cấu hình trang
st.set_page_config(
    page_title="Tính Lãi Gửi Tiết Kiệm",
    page_icon="💰",
    layout="centered"
)

st.title("💰 Ứng Dụng Tính Lãi Gửi Tiết Kiệm")
st.write("Nhập thông tin tiền gửi bên dưới để tính toán lãi tiết kiệm theo **lãi đơn** hoặc **lãi kép**.")

st.divider()

# Chia layout nhập liệu thành 2 cột
col1, col2 = st.columns(2)

with col1:
    so_tien_gui = st.number_input(
        "Số tiền gửi (VNĐ):", 
        min_value=1_000_000, 
        value=100_000_000, 
        step=5_000_000,
        format="%d"
    )
    
    ky_han_thang = st.number_input(
        "Kỳ hạn gửi (Tháng):", 
        min_value=1, 
        value=12, 
        step=1
    )

with col2:
    lai_suat_nam = st.number_input(
        "Lãi suất (%/năm):", 
        min_value=0.1, 
        max_value=20.0, 
        value=6.0, 
        step=0.1,
        format="%.1f"
    )
    
    loai_lai = st.selectbox(
        "Phương thức tính lãi:",
        options=["Lãi đơn", "Lãi kép"]
    )

hinh_thuc_lanh = st.selectbox(
    "Hình thức lãnh lãi:",
    options=["Lãnh lãi theo tháng", "Lãnh lãi theo quý", "Lãnh lãi cuối kỳ"]
)

# Nút tính toán
if st.button("🚀 Tính Tiền Lãi", type="primary", use_container_width=True):
    r_thang = (lai_suat_nam / 100) / 12  # Lãi suất theo tháng
    
    # Xác định chu kỳ lãnh lãi (số tháng)
    if hinh_thuc_lanh == "Lãnh lãi theo tháng":
        m = 1
    elif hinh_thuc_lanh == "Lãnh lãi theo quý":
        m = 3
    else:  # Lãnh lãi cuối kỳ
        m = ky_han_thang

    # Kiểm tra tính hợp lệ của kỳ hạn với hình thức lãnh lãi
    if ky_han_thang % m != 0 and hinh_thuc_lanh != "Lãnh lãi cuối kỳ":
        st.warning(f"⚠️ Kỳ hạn gửi ({ky_han_thang} tháng) không chia hết cho chu kỳ {hinh_thuc_lanh.lower()}. Kết quả tính theo số chu kỳ chẵn.")

    so_chu_ky = ky_han_thang // m
    
    if loai_lai == "Lãi đơn":
        # Lãi đơn: Lãi định kỳ cố định dựa trên vốn gốc ban đầu
        lai_dinh_ky = so_tien_gui * r_thang * m
        tong_lai = lai_dinh_ky * so_chu_ky
        tong_tien = so_tien_gui + tong_lai
    else:
        # Lãi kép: Lãi nhập gốc qua từng chu kỳ
        r_chu_ky = r_thang * m
        tong_tien = so_tien_gui * ((1 + r_chu_ky) ** so_chu_ky)
        tong_lai = tong_tien - so_tien_gui
        # Lãi định kỳ trung bình/chu kỳ đối với lãi kép
        lai_dinh_ky = tong_lai / so_chu_ky if so_chu_ky > 0 else 0

    st.divider()
    st.subheader("📊 Kết Quả Tính Toán")

    # Hiển thị số liệu dạng thẻ Metric
    res_col1, res_col2 = st.columns(2)
    
    with res_col1:
        st.metric(
            label=f"Tài sản cuối kỳ ({ky_han_thang} tháng)", 
            value=f"{tong_tien:,.0f} VNĐ".replace(",", ".")
        )
        st.metric(
            label="Tổng tiền lãi nhận được", 
            value=f"{tong_lai:,.0f} VNĐ".replace(",", ".")
        )

    with res_col2:
        st.metric(
            label="Tiền gốc ban đầu", 
            value=f"{so_tien_gui:,.0f} VNĐ".replace(",", ".")
        )
        label_dinh_ky = "Tiền lãi nhận mỗi kỳ" if loai_lai == "Lãi đơn" else "Lãi nhận trung bình/kỳ"
        st.metric(
            label=f"{label_dinh_ky} ({m} tháng/kỳ)", 
            value=f"{lai_dinh_ky:,.0f} VNĐ".replace(",", ".")
        )

    # Hiển thị bảng chi tiết các kỳ nhận lãi
    with st.expander("📝 Xem bảng chi tiết nhận lãi qua từng kỳ"):
        lich_trinh = []
        goc_dau_ky = so_tien_gui
        
        for i in range(1, so_chu_ky + 1):
            if loai_lai == "Lãi đơn":
                lai_ky = lai_dinh_ky
                goc_cuoi_ky = so_tien_gui
            else:
                lai_ky = goc_dau_ky * r_chu_ky
                goc_cuoi_ky = goc_dau_ky + lai_ky
                
            lich_trinh.append({
                "Kỳ": f"Kỳ {i} (Tháng {i * m})",
                "Tiền gốc đầu kỳ (VNĐ)": f"{goc_dau_ky:,.0f}".replace(",", "."),
                "Lãi nhận được (VNĐ)": f"{lai_ky:,.0f}".replace(",", "."),
                "Tổng tích lũy (VNĐ)": f"{(goc_cuoi_ky if loai_lai == 'Lãi kép' else so_tien_gui + lai_ky * i):,.0f}".replace(",", ".")
            })
            goc_dau_ky = goc_cuoi_ky

        st.dataframe(lich_trinh, use_container_width=True)
