import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# -----------------------------------------------------------
#                 Disk Scheduling Algorithms
# -----------------------------------------------------------

def fcfs(requests, head):
    order = requests.copy()
    distance = sum(abs(order[i] - (head if i == 0 else order[i - 1])) for i in range(len(order)))
    return order, distance


def sstf(requests, head):
    pending = requests.copy()
    order, total, curr = [], 0, head
    while pending:
        nearest = min(pending, key=lambda x: abs(x - curr))
        total += abs(nearest - curr)
        order.append(nearest)
        curr = nearest
        pending.remove(nearest)
    return order, total


def scan(requests, head, direction, disk_size=200):
    left = [r for r in requests if r < head]
    right = [r for r in requests if r >= head]
    left.sort()
    right.sort()
    seek_sequence, total, curr = [], 0, head

    if direction == 'left':
        for r in reversed(left):
            total += abs(curr - r)
            seek_sequence.append(r)
            curr = r
        total += curr
        curr = 0
        for r in right:
            total += abs(curr - r)
            seek_sequence.append(r)
            curr = r
    else:
        for r in right:
            total += abs(curr - r)
            seek_sequence.append(r)
            curr = r
        total += abs((disk_size - 1) - curr)
        curr = disk_size - 1
        for r in reversed(left):
            total += abs(curr - r)
            seek_sequence.append(r)
            curr = r

    return seek_sequence, total


def cscan(requests, head, direction, disk_size=200):
    left = [r for r in requests if r < head]
    right = [r for r in requests if r >= head]
    left.sort()
    right.sort()
    seek_sequence, total, curr = [], 0, head

    if direction == 'left':
        for r in reversed(left):
            total += abs(curr - r)
            seek_sequence.append(r)
            curr = r
        total += curr
        curr = disk_size - 1
        for r in reversed(right):
            total += abs(curr - r)
            seek_sequence.append(r)
            curr = r
    else:
        for r in right:
            total += abs(curr - r)
            seek_sequence.append(r)
            curr = r
        total += abs((disk_size - 1) - curr)
        curr = 0
        for r in left:
            total += abs(curr - r)
            seek_sequence.append(r)
            curr = r

    return seek_sequence, total


# -----------------------------------------------------------
#                   Visualization Function
# -----------------------------------------------------------
def plot_schedule(requests, head, order, title):
    points = [head] + order
    x = list(range(len(points)))
    y = points
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(x, y, marker='o', color='#00ADB5', linewidth=2)
    ax.set_facecolor('#EEEEEE')
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_xlabel('Sequence')
    ax.set_ylabel('Cylinder Number')
    ax.grid(True, linestyle='--', alpha=0.6)
    st.pyplot(fig)


# -----------------------------------------------------------
#                    Streamlit Frontend
# -----------------------------------------------------------
st.set_page_config(page_title="Disk Scheduling Simulator", layout="wide")

# ---- Custom CSS ----
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #222831 0%, #393E46 50%, #00ADB5 100%);
        color: white;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #EEEEEE !important;
    }
    .stTextInput, .stNumberInput, .stSelectbox, .stMultiSelect, .stTextArea {
        background-color: #393e46 !important;
        color: black !important;
        border-radius: 10px;
    }
    div[data-testid="stDataFrame"] {
        background-color: white;
        border-radius: 10px;
        padding: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# ---- Title ----
st.title("Disk Scheduling Algorithm Simulator")
st.markdown("""
### About Disk Scheduling
Disk scheduling determines the **order in which I/O requests are processed** on a disk drive.  
Since the disk head moves physically across cylinders, **seek time** (the time it takes to move the head) is critical.  
These algorithms aim to **minimize total seek time** while ensuring fairness and responsiveness.
""")

st.divider()

# ---- Algorithm Descriptions ----
st.markdown("###  Algorithms Overview")

col1, col2 = st.columns(2)
with col1:
    st.markdown("""
    #### 🔹 FCFS (First Come First Serve)
    - Requests are handled in the order they arrive.
    - **Simple but not optimal** in minimizing head movement.
    - Can cause large total seek time.
    """)
    st.markdown("""
    #### 🔹 SSTF (Shortest Seek Time First)
    - Selects the **closest request** to the current head position.
    - Reduces average seek time.
    - Can cause **starvation** for distant requests.
    """)
with col2:
    st.markdown("""
    #### 🔹 SCAN (Elevator Algorithm)
    - The head moves in one direction, servicing all requests,
      then reverses direction (like an elevator).
    - Provides a good tradeoff between fairness and performance.
    """)
    st.markdown("""
    #### 🔹 C-SCAN (Circular SCAN)
    - The head moves in one direction only.
    - After reaching the end, it jumps back to the beginning.
    - Ensures **uniform wait time** for all requests.
    """)

st.divider()

# ---- Input Section ----
st.markdown("### Simulation Parameters")

requests_str = st.text_area("Enter Request Queue (comma-separated):", "82, 170, 43, 140, 24, 16, 190")
colA, colB, colC = st.columns(3)
with colA:
    head = st.number_input("Initial Head Position:", min_value=0, max_value=999, value=50)
with colB:
    direction = st.selectbox("Direction:", ["left", "right"])
with colC:
    disk_size = st.number_input("Disk Size:", min_value=50, max_value=1000, value=200)

algos = st.multiselect("Algorithms to Run:", ["FCFS", "SSTF", "SCAN", "C-SCAN"],
                       default=["FCFS", "SSTF", "SCAN", "C-SCAN"])

st.divider()

# ---- Run Simulation ----
if st.button("Run Simulation"):
    try:
        requests = [int(x.strip()) for x in requests_str.split(",") if x.strip()]
        summary = []

        for algo in algos:
            if algo == "FCFS":
                order, total = fcfs(requests, head)
            elif algo == "SSTF":
                order, total = sstf(requests, head)
            elif algo == "SCAN":
                order, total = scan(requests, head, direction, disk_size)
            elif algo == "C-SCAN":
                order, total = cscan(requests, head, direction, disk_size)

            st.subheader(f"🌀 {algo} Algorithm")
            st.write(f"**Order of Head Movement:** `{order}`")
            st.write(f"**Total Seek Time:** `{total}`")
            st.write(f"**Average Seek Time:** `{total / len(requests):.2f}`")
            plot_schedule(requests, head, order, f"{algo} Disk Scheduling")

            summary.append({
                "Algorithm": algo,
                "Total Seek Time": total,
                "Average Seek Time": total / len(requests)
            })

        st.markdown("###  Summary Comparison")
        df = pd.DataFrame(summary)
        st.dataframe(df, use_container_width=True)

    except Exception as e:
        st.error(f"Error: {e}")

st.divider()

