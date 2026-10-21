import os
import pandas as pd
import streamlit as st

# =========================================================
# SAVEQUEST — HÀNH TRÌNH CHINH PHỤC MỤC TIÊU
# =========================================================

st.set_page_config(
    page_title="SaveQuest | Hành trình chinh phục mục tiêu",
    page_icon="💰",
    layout="centered",
)

st.title("💰 CONG CU TINH LAI TIET KIEM_TRAN NGOC THUY VY")
st.subheader("Hành trình chinh phục mục tiêu")
st.write(
    "Không chỉ tính lãi tiết kiệm — SaveQuest giúp bạn lập mục tiêu, tính toán"
    " và theo dõi hành trình tích lũy."
)

# Giữ ảnh gốc nếu có file avatar.jpg
if os.path.exists("avatar.jpg"):
  st.image("avatar.jpg", use_container_width=True)

st.caption(
    "Lưu ý: Đây là công cụ mô phỏng. Kết quả thực tế có thể khác do quy định"
    " sản phẩm và điều kiện ngân hàng."
)

st.divider()


# =========================================================
# HÀM HỖ TRỢ
# =========================================================


def format_vnd(value):
  return f"{value:,.0f}".replace(",", ".") + " VNĐ"


def calculate_monthly_plan(current_savings, monthly_saving, annual_rate, months):
  """Mô phỏng khoản tiền hiện có sinh lãi hàng tháng.

  Khoản tiết kiệm định kỳ được thêm vào cuối mỗi tháng.
  """
  monthly_rate = annual_rate / 100 / 12
  balance = float(current_savings)
  rows = []

  for month in range(1, months + 1):
    interest = balance * monthly_rate
    balance += interest
    balance += monthly_saving

    rows.append({
        "Tháng": month,
        "Lãi mô phỏng (VNĐ)": round(interest),
        "Tiết kiệm thêm (VNĐ)": round(monthly_saving),
        "Số dư dự kiến (VNĐ)": round(balance),
    })

  return balance, pd.DataFrame(rows)


# =========================================================
# KHỞI TẠO DỮ LIỆU PHIÊN
# =========================================================

if "saved_plans" not in st.session_state:
  st.session_state.saved_plans = []

if "goal_data" not in st.session_state:
  st.session_state.goal_data = None


# =========================================================
# ĐIỀU HƯỚNG (Đã loại bỏ Phòng thí nghiệm)
# =========================================================

page = st.radio(
    "Chọn chức năng",
    ["🎯 Mục tiêu của tôi", "💰 Máy tính lãi", "🏆 Thành tích & kế hoạch đã lưu"],
)

# =========================================================
# 1. MỤC TIÊU TÀI CHÍNH
# =========================================================

if page == "🎯 Mục tiêu của tôi":

  st.header("🎯 Thiết lập mục tiêu tài chính")
  st.write(
      "Bạn muốn tiết kiệm cho điều gì? Hãy nhập thông tin để SaveQuest xây"
      " dựng hành trình cho bạn."
  )

  with st.form("goal_form"):

    goal_name = st.text_input(
        "Tên mục tiêu", value="Mua laptop phục vụ học tập"
    )

    goal_category = st.selectbox(
        "Nhóm mục tiêu",
        [
            "Mua laptop",
            "Đóng học phí",
            "Học ngoại ngữ",
            "Học thiết kế",
            "Du lịch",
            "Mục tiêu khác",
        ],
    )

    col1, col2 = st.columns(2)

    with col1:
      target_amount = st.number_input(
          "Số tiền mục tiêu (VNĐ)",
          min_value=100_000,
          value=20_000_000,
          step=500_000,
      )

      current_savings = st.number_input(
          "Số tiền đã có (VNĐ)", min_value=0, value=2_000_000, step=100_000
      )

    with col2:
      monthly_saving = st.number_input(
          "Tiết kiệm mỗi tháng (VNĐ)",
          min_value=0,
          value=1_500_000,
          step=100_000,
      )

      target_months = st.number_input(
          "Thời hạn mong muốn (tháng)",
          min_value=1,
          max_value=600,
          value=12,
          step=1,
      )

    annual_rate_goal = st.number_input(
        "Lãi suất giả định (%/năm)",
        min_value=0.0,
        max_value=20.0,
        value=4.5,
        step=0.1,
        format="%.1f",
    )

    submitted_goal = st.form_submit_button(
        "🚀 Lập hành trình của tôi", type="primary", use_container_width=True
    )

  if submitted_goal:
    st.session_state.goal_data = {
        "name": goal_name.strip() or goal_category,
        "category": goal_category,
        "target": target_amount,
        "current": current_savings,
        "monthly": monthly_saving,
        "months": int(target_months),
        "rate": annual_rate_goal,
    }

  if st.session_state.goal_data is not None:

    goal = st.session_state.goal_data

    target = goal["target"]
    current = goal["current"]
    monthly = goal["monthly"]
    months = goal["months"]
    rate = goal["rate"]

    projected, schedule = calculate_monthly_plan(
        current, monthly, rate, months
    )

    progress = min(current / target, 1.0)
    projected_progress = min(projected / target, 1.0)

    st.divider()
    st.subheader(f"🗺️ Bản đồ mục tiêu: {goal['name']}")

    col1, col2 = st.columns(2)

    col1.metric("Mục tiêu", format_vnd(target))
    col2.metric("Đã tích lũy", format_vnd(current))

    st.write("**Tiến độ hiện tại**")
    st.progress(progress)
    st.caption(f"Đã hoàn thành {progress * 100:.1f}% mục tiêu.")

    st.write(f"**Dự kiến sau {months} tháng:** {format_vnd(projected)}")
    st.progress(projected_progress)

    st.caption(
        f"Theo mô phỏng, bạn có thể hoàn thành {projected_progress * 100:.1f}%"
        " mục tiêu."
    )

    if current >= target:
      st.success("🎉 Bạn đã đạt mục tiêu tài chính!")
    elif projected >= target:
      st.success("🌟 Kế hoạch có thể đạt mục tiêu theo các giả định đã nhập.")
    else:
      st.warning(
          f"Bạn có thể còn thiếu {format_vnd(target - projected)} so với mục"
          " tiêu vào cuối thời hạn."
      )

    # Tính khoản tiết kiệm hàng tháng cần thiết
    monthly_rate = rate / 100 / 12

    if current >= target:
      needed_monthly = 0

    elif monthly_rate > 0:
      future_current = current * ((1 + monthly_rate) ** months)

      annuity_factor = ((1 + monthly_rate) ** months - 1) / monthly_rate

      needed_monthly = max((target - future_current) / annuity_factor, 0)

    else:
      needed_monthly = max((target - current) / months, 0)

    st.info(
        f"Để hướng tới mục tiêu trong {months} tháng, bạn cần tiết kiệm khoảng"
        f" **{format_vnd(needed_monthly)} mỗi tháng** theo mô hình hiện tại."
    )

    # Biểu đồ tiến độ
    st.subheader("📈 Tiến trình tích lũy dự kiến")

    st.line_chart(schedule.set_index("Tháng")[["Số dư dự kiến (VNĐ)"]])

    with st.expander("📝 Xem bảng chi tiết từng tháng"):

      display_df = schedule.copy()

      for column in [
          "Lãi mô phỏng (VNĐ)",
          "Tiết kiệm thêm (VNĐ)",
          "Số dư dự kiến (VNĐ)",
      ]:
        display_df[column] = display_df[column].map(format_vnd)

      st.dataframe(display_df, use_container_width=True, hide_index=True)

    # Lưu kế hoạch
    if st.button("💾 Lưu kế hoạch này", use_container_width=True):

      plan = {
          "Tên mục tiêu": goal["name"],
          "Số tiền mục tiêu": target,
          "Số tiền hiện có": current,
          "Tiết kiệm/tháng": monthly,
          "Thời hạn (tháng)": months,
          "Lãi suất giả định (%/năm)": rate,
          "Dự kiến cuối kỳ": round(projected),
      }

      st.session_state.saved_plans.append(plan)

      st.success("Đã lưu kế hoạch trong phiên hiện tại.")

    # Trợ lý đồng hành
    st.subheader("🤝 Trợ lý đồng hành")

    if projected >= target:

      st.write(
          "Kế hoạch hiện tại có vẻ phù hợp với mục tiêu theo các giả định đã"
          " nhập. Hãy kiểm tra lại khả năng tiết kiệm thực tế và duy trì khoản"
          " dự phòng cần thiết."
      )

    elif monthly == 0:

      st.write(
          "Bạn chưa đặt khoản tiết kiệm định kỳ. Hãy thử nhập một khoản phù hợp"
          " với ngân sách hoặc kéo dài thời hạn để xem kế hoạch thay đổi thế"
          " nào."
      )

    else:

      gap = max(target - projected, 0)

      st.write(
          f"Theo mô phỏng, bạn có thể cần điều chỉnh kế hoạch để bù khoảng"
          f" {format_vnd(gap)}. Hãy cân nhắc tăng khoản tiết kiệm nếu ngân sách"
          " cho phép, kéo dài thời hạn hoặc điều chỉnh mục tiêu. Không nên cắt"
          " giảm các nhu cầu thiết yếu."
      )

    # Huy hiệu tiến độ
    badges = []

    if progress >= 0.25:
      badges.append("🌱 Khởi đầu vững vàng — đạt 25% mục tiêu")

    if progress >= 0.5:
      badges.append("🌿 Nửa chặng đường — đạt 50% mục tiêu")

    if progress >= 0.75:
      badges.append("🌳 Gần cán đích — đạt 75% mục tiêu")

    if current >= target:
      badges.append("🏆 Chinh phục mục tiêu — đã đủ số tiền")

    if badges:
      st.subheader("🏅 Huy hiệu hiện tại")

      for badge in badges:
        st.success(badge)


# =========================================================
# 2. MÁY TÍNH LÃI GỬI TIẾT KIỆM
# =========================================================

elif page == "💰 Máy tính lãi":

  st.header("💰 Máy tính lãi gửi tiết kiệm")

  st.write("Phần máy tính kế thừa từ ứng dụng ban đầu của bạn.")

  col1, col2 = st.columns(2)

  with col1:

    so_tien_gui = st.number_input(
        "Số tiền gửi (VNĐ):",
        min_value=1_000_000,
        value=100_000_000,
        step=5_000_000,
        format="%d",
        key="calc_principal",
    )

    ky_han_thang = st.number_input(
        "Kỳ hạn gửi (tháng):",
        min_value=1,
        max_value=600,
        value=12,
        step=1,
        key="calc_months",
    )

  with col2:

    lai_suat_nam = st.number_input(
        "Lãi suất (%/năm):",
        min_value=0.1,
        max_value=20.0,
        value=6.0,
        step=0.1,
        format="%.1f",
        key="calc_rate",
    )

    loai_lai = st.selectbox(
        "Phương thức tính lãi:", options=["Lãi đơn", "Lãi kép"], key="calc_type"
    )

  hinh_thuc_lanh = st.selectbox(
      "Hình thức lãnh lãi:",
      options=[
          "Lãnh lãi theo tháng",
          "Lãnh lãi theo quý",
          "Lãnh lãi cuối kỳ",
      ],
      key="calc_payout",
  )

  if st.button("🚀 Tính tiền lãi", type="primary", use_container_width=True):

    r_thang = (lai_suat_nam / 100) / 12

    if hinh_thuc_lanh == "Lãnh lãi theo tháng":
      m = 1
    elif hinh_thuc_lanh == "Lãnh lãi theo quý":
      m = 3
    else:
      m = int(ky_han_thang)

    if ky_han_thang % m != 0 and hinh_thuc_lanh != "Lãnh lãi cuối kỳ":
      st.warning(
          f"Kỳ hạn {ky_han_thang} tháng không chia hết cho chu kỳ {m} tháng."
          " Kết quả chỉ tính các chu kỳ trọn vẹn."
      )

    so_chu_ky = int(ky_han_thang) // m
    r_chu_ky = r_thang * m

    if loai_lai == "Lãi đơn":

      lai_dinh_ky = so_tien_gui * r_thang * m
      tong_lai = lai_dinh_ky * so_chu_ky
      tong_tien = so_tien_gui + tong_lai

    else:

      tong_tien = so_tien_gui * ((1 + r_chu_ky) ** so_chu_ky)

      tong_lai = tong_tien - so_tien_gui

      lai_dinh_ky = tong_lai / so_chu_ky if so_chu_ky > 0 else 0

    st.divider()
    st.subheader("📊 Kết quả tính toán")

    res_col1, res_col2 = st.columns(2)

    res_col1.metric(
        f"Tài sản sau {ky_han_thang} tháng", format_vnd(tong_tien)
    )

    res_col1.metric("Tổng tiền lãi mô phỏng", format_vnd(tong_lai))

    res_col2.metric("Tiền gốc ban đầu", format_vnd(so_tien_gui))

    label = (
        "Tiền lãi mỗi kỳ" if loai_lai == "Lãi đơn" else "Lãi trung bình mỗi kỳ"
    )

    res_col2.metric(f"{label} ({m} tháng/kỳ)", format_vnd(lai_dinh_ky))

    with st.expander("📝 Xem bảng chi tiết"):

      rows = []
      balance = float(so_tien_gui)

      for i in range(1, so_chu_ky + 1):

        if loai_lai == "Lãi đơn":

          interest = so_tien_gui * r_chu_ky
          opening_balance = so_tien_gui
          ending_balance = so_tien_gui + interest * i

        else:

          opening_balance = balance
          interest = opening_balance * r_chu_ky
          balance = opening_balance + interest
          ending_balance = balance

        rows.append({
            "Kỳ": f"Kỳ {i} (tháng {i * m})",
            "Gốc đầu kỳ": format_vnd(opening_balance),
            "Lãi kỳ này": format_vnd(interest),
            "Tổng tích lũy": format_vnd(ending_balance),
        })

      st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    if st.button("💾 Lưu kết quả tính lãi"):

      st.session_state.saved_plans.append({
          "Tên mục tiêu": "Máy tính lãi",
          "Số tiền mục tiêu": None,
          "Số tiền hiện có": so_tien_gui,
          "Tiết kiệm/tháng": None,
          "Thời hạn (tháng)": int(ky_han_thang),
          "Lãi suất giả định (%/năm)": lai_suat_nam,
          "Dự kiến cuối kỳ": round(tong_tien),
      })

      st.success("Đã lưu kết quả tính lãi.")


# =========================================================
# 3. THÀNH TÍCH VÀ KẾ HOẠCH ĐÃ LƯU
# =========================================================

else:

  st.header("🏆 Thành tích & kế hoạch đã lưu")

  st.write("Các kế hoạch bạn đã lưu trong phiên sử dụng hiện tại.")

  if not st.session_state.saved_plans:

    st.info(
        "Bạn chưa lưu kế hoạch nào. Hãy tạo mục tiêu hoặc dùng máy tính lãi trước"
        " nhé."
    )

  else:

    saved_df = pd.DataFrame(st.session_state.saved_plans)

    st.dataframe(saved_df, use_container_width=True, hide_index=True)

    csv_data = saved_df.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        "⬇️ Tải kế hoạch xuống CSV",
        data=csv_data,
        file_name="savequest_ke_hoach.csv",
        mime="text/csv",
        use_container_width=True,
    )

    if st.button("🗑️ Xóa toàn bộ kế hoạch đã lưu"):

      st.session_state.saved_plans = []
      st.rerun()

  st.divider()

  st.subheader("🌟 Hành trình của bạn")

  st.write(
      "Hãy đặt mục tiêu dựa trên khả năng tài chính thực tế, giữ khoản dự"
      " phòng cho nhu cầu thiết yếu và xem lãi suất trong ứng dụng là giả"
      " định."
  )


# =========================================================
# CHÂN TRANG
# =========================================================

st.divider()

st.caption(
    "SaveQuest • Công cụ mô phỏng học tập • Không phải tư vấn đầu tư hay cam"
    " kết lãi suất."
)
