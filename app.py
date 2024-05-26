import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

matplotlib.use("MacOSX")
plt.scatter([0, 1], [0, 1])
plt.show()

st.set_page_config(page_icon="📈", page_title="Lifelong Budget")

st.markdown(
    """
    # **Lifelong Budget**
    A simple tool for simulating your private economy based on different scenarios. 
"""
)

mean = st.slider("Mean", min_value=0, max_value=5, step=1)

n = 100
x = mean + np.random.randn(n)

fig, axes = plt.subplots()
axes.hist(x)
axes.set_title(f"Gaussian with mean {mean}")
st.pyplot(fig)
