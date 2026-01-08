import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import sympy as sp

# Inicializar estado de sesión
if 'show_plot' not in st.session_state:
    st.session_state.show_plot = False

if 'equation' not in st.session_state:
    st.session_state.equation = "x^2 + y^2 = t"  # Default inicial

# Título de la app
st.title("Gráfico de Función Implícita f(x, y, t) = g(x, y, t)")

# Input para la ecuación, usando session_state para controlarla
equation = st.text_input("Ecuación f(x, y, t) = g(x, y, t) (ej. x^2 + y^2 = t, usa ^ para potencias)", value=st.session_state.equation)

# Actualizar session_state con el valor ingresado (para persistencia)
st.session_state.equation = equation

# Opciones para límites de x, y, t
st.subheader("Límites para X")
x_min = st.number_input("X mínimo", value=-7.0)
x_max = st.number_input("X máximo", value=7.0)
num_points_x = st.number_input("Número de puntos en X (para precisión)", value=400, min_value=100, max_value=1000, step=50)

st.subheader("Límites para Y")
y_min = st.number_input("Y mínimo", value=-7.0)
y_max = st.number_input("Y máximo", value=7.0)
num_points_y = st.number_input("Número de puntos en Y (para precisión)", value=400, min_value=100, max_value=1000, step=50)

st.subheader("Límites para T")
t_min = st.number_input("T mínimo", value=0.0)
t_max = st.number_input("T máximo", value=20.0)
t_step = st.number_input("Paso para T", value=0.1, min_value=0.01)

# Barra deslizante para t, usando los límites definidos
t = st.slider("Valor de t", min_value=t_min, max_value=t_max, value=(t_min + t_max)/2, step=t_step)

# Botón para graficar
if st.button("Graficar"):
    st.session_state.show_plot = True

# Función para parsear y evaluar la expresión
def parse_and_evaluate(X, Y, t, eq_str):
    try:
        # Reemplazar ^ por ** para compatibilidad con Python/SymPy
        eq_str = eq_str.replace("^", "**")

        # Definir símbolos
        x, y, t_sym = sp.symbols('x y t')

        # Dividir por '=' si existe, sino asumir = 0
        if '=' in eq_str:
            left, right = eq_str.split('=', 1)
            expr = sp.sympify(left.strip()) - sp.sympify(right.strip())
        else:
            expr = sp.sympify(eq_str.strip())

        # Lambdify para evaluación numérica con NumPy
        func = sp.lambdify((x, y, t_sym), expr, modules='numpy')

        # Evaluar
        return func(X, Y, t)
    except Exception as e:
        st.error(f"Error al parsear la ecuación: {str(e)}. Asegúrate de usar sintaxis matemática válida (ej. x**2 o x^2, sin, cos, etc.).")
        return None

# Si se debe mostrar el gráfico
if st.session_state.show_plot:
    # Crear una malla de puntos para x e y con precisión personalizada
    x_vals = np.linspace(x_min, x_max, num_points_x)
    y_vals = np.linspace(y_min, y_max, num_points_y)
    X, Y = np.meshgrid(x_vals, y_vals)

    # Calcular Z = f(X, Y, t) - g(X, Y, t)
    Z = parse_and_evaluate(X, Y, t, equation)

    if Z is not None:
        # Crear la figura cuadrada y el gráfico de contorno en nivel 0
        fig, ax = plt.subplots(figsize=(8, 8))  # Figura cuadrada
        ax.contour(X, Y, Z, levels=[0], colors='b')

        # Configurar ejes cartesianos clásicos con flechas y etiquetas enumeradas
        ax.spines['left'].set_position('zero')
        ax.spines['bottom'].set_position('zero')
        ax.spines['right'].set_color('none')
        ax.spines['top'].set_color('none')
        ax.xaxis.set_ticks_position('bottom')
        ax.yaxis.set_ticks_position('left')

        # Establecer límites explícitamente
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_min, y_max)

        # Hacer los ejes cuadrados (aspect ratio igual)
        ax.set_aspect('equal', adjustable='box')

        # Etiquetas al final de los ejes
        ax.text(x_max, 0, 'x', va='center', ha='right', fontsize=12)
        ax.text(0, y_max, 'y', va='bottom', ha='center', fontsize=12)

        # Flechas al final de los ejes (usando transAxes para posicionar)
        ax.plot(1, 0, ">k", transform=ax.transAxes, clip_on=False)
        ax.plot(0, 1, "^k", transform=ax.transAxes, clip_on=False)

        # Ticks enumerados en enteros
        xticks = np.arange(np.ceil(x_min), np.floor(x_max) + 1, 1)
        yticks = np.arange(np.ceil(y_min), np.floor(y_max) + 1, 1)
        if len(xticks) > 0:
            ax.set_xticks(xticks)
        if len(yticks) > 0:
            ax.set_yticks(yticks)

        # Grid
        ax.grid(True)

        # Título
        ax.set_title(f'Curva implícita para t = {t}')

        # Mostrar el gráfico en Streamlit
        st.pyplot(fig)
else:
    # Mensaje cuando no hay gráfico (después de reset o al inicio)
    st.info("Inserta una ecuación y diviértete")

# Botón para reset/stop
if st.button("Reset"):
    st.session_state.show_plot = False
    st.session_state.equation = ""  # Borrar la ecuación (o pon el default si prefieres)
    st.rerun()  # Recarga la app para actualizar los cambios