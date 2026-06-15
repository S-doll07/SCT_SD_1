import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas as pdf_canvas
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

conversion_history = []

# Colors - Dark theme only
BG1 = "#0F172A"
BG2 = "#1E1B4B"
CARD = "#1E293B"
ACCENT = "#38BDF8"
PURPLE = "#8B5CF6"
TEXT = "#F8FAFC"
ENTRY_BG = "#334155"
GREEN = "#22C55E"
GRID = "#1E293B"
SUBTEXT = "#CBD5E1"

# -----------------------------
# Conversion Logic + Formulas
# -----------------------------
def get_celsius(temp, unit):
    if "Celsius" in unit:
        return temp, "No conversion needed"
    elif "Fahrenheit" in unit:
        formula = f"({temp}°F - 32) × 5/9"
        return (temp - 32) * 5 / 9, formula
    elif "Kelvin" in unit:
        formula = f"{temp}K - 273.15"
        return temp - 273.15, formula
    elif "Rankine" in unit:
        formula = f"({temp}°R - 491.67) × 5/9"
        return (temp - 491.67) * 5 / 9, formula
    elif "Réaumur" in unit:
        formula = f"{temp}°Ré × 5/4"
        return temp * 5 / 4, formula

def convert_from_celsius(celsius, unit):
    if "Celsius" in unit:
        return celsius, "No conversion needed", "°C"
    elif "Fahrenheit" in unit:
        formula = f"({celsius}°C × 9/5) + 32"
        return (celsius * 9 / 5) + 32, formula, "°F"
    elif "Kelvin" in unit:
        formula = f"{celsius}°C + 273.15"
        return celsius + 273.15, formula, "K"
    elif "Rankine" in unit:
        formula = f"({celsius}°C + 273.15) × 9/5"
        return (celsius + 273.15) * 9 / 5, formula, "°R"
    elif "Réaumur" in unit:
        formula = f"{celsius}°C × 4/5"
        return celsius * 4 / 5, formula, "°Ré"

def convert_temperature():
    try:
        temp = float(temp_entry.get())
        from_unit = from_var.get()
        to_unit = to_var.get()

        celsius, formula1 = get_celsius(temp, from_unit)
        result, formula2, symbol = convert_from_celsius(celsius, to_unit)

        result_label.config(text=f"{result:.3f} {symbol}", fg=GREEN)
        detail_label.config(text=f"{temp:.2f} {from_unit} ➜ {result:.3f} {to_unit}")

        if formula1 == "No conversion needed":
            formula_label.config(text=f"Formula: {formula2}")
        elif formula2 == "No conversion needed":
            formula_label.config(text=f"Formula: {formula1}")
        else:
            formula_label.config(text=f"Step 1: {formula1} → {celsius:.2f}°C\nStep 2: {formula2}")

        update_graph(celsius)

        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = f"[{timestamp}] {temp:.2f} {from_unit} → {result:.3f} {to_unit}"
        conversion_history.insert(0, entry)
        if len(conversion_history) > 10:
            conversion_history.pop()
        update_history_display()

    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter a valid number.")

def copy_result():
    result = result_label.cget("text")
    if result:
        root.clipboard_clear()
        root.clipboard_append(result)
        copy_btn.config(text="✅ Copied!")
        root.after(1500, lambda: copy_btn.config(text="📋 Copy"))

def update_graph(celsius):
    ax.clear()
    temps = {
        'Celsius': celsius,
        'Fahrenheit': celsius * 9/5 + 32,
        'Kelvin': celsius + 273.15,
        'Rankine': (celsius + 273.15) * 9/5
    }
    colors = ['#38BDF8', '#F59E0B', '#8B5CF6', '#EF4444']
    bars = ax.bar(temps.keys(), temps.values(), color=colors)
    ax.set_title('Temperature Comparison', color=TEXT, fontsize=11, fontweight='bold')
    ax.tick_params(colors=TEXT, labelsize=9)
    ax.set_ylabel('Value', color=TEXT, fontsize=9)
    fig.patch.set_facecolor(CARD)
    ax.set_facecolor(CARD)
    ax.spines['bottom'].set_color(TEXT)
    ax.spines['left'].set_color(TEXT)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height, f'{height:.1f}',
                ha='center', va='bottom', color=TEXT, fontsize=8)
    canvas.draw()

def update_history_display():
    history_listbox.delete(0, tk.END)
    for item in conversion_history:
        history_listbox.insert(tk.END, item)

# UPDATED: Clear now wipes graph too
def clear_fields():
    temp_entry.delete(0, tk.END)
    result_label.config(text="")
    detail_label.config(text="")
    formula_label.config(text="")
    # Clear the graph
    ax.clear()
    ax.set_facecolor(CARD)
    fig.patch.set_facecolor(CARD)
    ax.set_title('Temperature Comparison', color=TEXT, fontsize=11, fontweight='bold')
    ax.set_ylabel('Value', color=TEXT, fontsize=9)
    ax.tick_params(colors=TEXT, labelsize=9)
    canvas.draw()

def clear_history():
    global conversion_history
    conversion_history = []
    update_history_display()

def export_pdf():
    if not conversion_history:
        messagebox.showinfo("No Data", "Convert some temperatures first!")
        return

    file_path = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF files", "*.pdf")],
        initialfile="DevTemp_Report.pdf"
    )
    if not file_path:
        return

    c = pdf_canvas.Canvas(file_path, pagesize=letter)
    width, height = letter
    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, height - 50, "DevTemp Pro - Conversion Report")
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 70, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 100, "Student Reference Formulas:")
    c.setFont("Helvetica", 9)
    formulas = [
        "°F = (°C × 9/5) + 32 °C = (°F - 32) × 5/9",
        "K = °C + 273.15 °C = K - 273.15",
        "°R = (°C + 273.15) × 9/5 °Ré = °C × 4/5"
    ]
    y = height - 120
    for f in formulas:
        c.drawString(60, y, f)
        y -= 15
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y - 20, "Conversion History:")
    c.setFont("Helvetica", 10)
    y -= 40
    for item in conversion_history:
        c.drawString(60, y, item)
        y -= 15
        if y < 50:
            c.showPage()
            y = height - 50
    c.save()
    messagebox.showinfo("Success", f"PDF saved to:\n{file_path}")

def on_enter(e, btn, color):
    btn.config(bg=color)

def on_leave(e, btn, color):
    btn.config(bg=color)

def create_gradient(canvas):
    width = canvas.winfo_width()
    height = canvas.winfo_height()
    if width <= 1 or height <= 1:
        width, height = 900, 700
    canvas.delete("gradient")
    (r1, g1, b1) = canvas.winfo_rgb(BG1)
    (r2, g2, b2) = canvas.winfo_rgb(BG2)
    r_ratio = float(r2 - r1) / height
    g_ratio = float(g2 - g1) / height
    b_ratio = float(b2 - b1) / height
    for i in range(height):
        nr = int(r1 + (r_ratio * i))
        ng = int(g1 + (g_ratio * i))
        nb = int(b1 + (b_ratio * i))
        color = f"#{nr//256:02x}{ng//256:02x}{nb//256:02x}"
        canvas.create_line(0, i, width, i, fill=color, tags="gradient")

def draw_dev_elements(canvas):
    canvas.delete("grid")
    canvas.delete("devtext")
    width = canvas.winfo_width()
    height = canvas.winfo_height()
    if width <= 1 or height <= 1:
        width, height = 900, 700
    # Grid lines
    for i in range(0, width, 25):
        canvas.create_line(i, 0, i, height, fill=GRID, width=1, tags="grid")
    for i in range(0, height, 25):
        canvas.create_line(0, i, width, i, fill=GRID, width=1, tags="grid")
    # Dev symbols with relative positioning
    elements = ["def()", "{ }", "01", "⚡", "λ", "</>", "const", "++"]
    rel_positions = [(0.07, 0.11), (0.91, 0.17), (0.08, 0.71), (0.89, 0.79),
                     (0.13, 0.43), (0.87, 0.4), (0.06, 0.57), (0.92, 0.64)]
    for elem, (rx, ry) in zip(elements, rel_positions):
        x = int(width * rx)
        y = int(height * ry)
        canvas.create_text(x, y, text=elem, fill="#475569", font=("Consolas", 16, "bold"), tags="devtext")

# -----------------------------
# Main Window - RESIZABLE
# -----------------------------
root = tk.Tk()
root.title("SD Pro Converter 💻 | Student Edition")
root.geometry("900x700")
root.minsize(800, 600)
root.config(bg=BG1)

bg_canvas = tk.Canvas(root, highlightthickness=0)
bg_canvas.pack(fill="both", expand=True)

root.update_idletasks()
create_gradient(bg_canvas)
draw_dev_elements(bg_canvas)

style = ttk.Style()
style.theme_use("clam")
style.configure("Custom.TCombobox", fieldbackground=ENTRY_BG, background=ENTRY_BG,
                foreground=TEXT, arrowcolor=ACCENT, borderwidth=2, font=("Segoe UI", 11))
style.map("Custom.TCombobox", fieldbackground=[("readonly", ENTRY_BG)],
          selectbackground=[("readonly", ENTRY_BG)], selectforeground=[("readonly", TEXT)])
style.configure("Custom.TNotebook", background=BG1, borderwidth=0)
style.configure("Custom.TNotebook.Tab", background=CARD, foreground=TEXT,
                padding=[20, 10], font=("Segoe UI", 11, "bold"))
style.map("Custom.TNotebook.Tab", background=[("selected", ACCENT)], foreground=[("selected", "black")])

# Main container that fills canvas
main_container = tk.Frame(bg_canvas, bg=BG1)
bg_canvas.create_window(0, 0, window=main_container, anchor="nw", tags="main_window")

def resize_handler(event):
    bg_canvas.coords("main_window", 0, 0)
    bg_canvas.itemconfig("main_window", width=event.width, height=event.height)
    create_gradient(bg_canvas)
    draw_dev_elements(bg_canvas)

bg_canvas.bind("<Configure>", resize_handler)

# Header
header_frame = tk.Frame(main_container, bg=BG1)
header_frame.pack(fill="x", pady=10)

title = tk.Label(header_frame, text="💻 SD Pro Temperature Converter ⚡", font=("Segoe UI", 28, "bold"), fg=ACCENT, bg=BG1)
title.pack()

subtitle = tk.Label(header_frame, text="Student Edition • With Formulas & PDF Export",
                   font=("Segoe UI", 12), fg=SUBTEXT, bg=BG1)
subtitle.pack()

# Notebook fills remaining space
notebook = ttk.Notebook(main_container, style="Custom.TNotebook")
notebook.pack(fill="both", expand=True, padx=20, pady=10)

# TAB 1: Converter - CENTERED
convert_frame = tk.Frame(notebook, bg=CARD)
notebook.add(convert_frame, text="🔄 Converter")

# Use grid with weights to center content
convert_frame.grid_rowconfigure(0, weight=1)
convert_frame.grid_rowconfigure(2, weight=1)
convert_frame.grid_columnconfigure(0, weight=1)
convert_frame.grid_columnconfigure(2, weight=1)

center_frame = tk.Frame(convert_frame, bg=CARD)
center_frame.grid(row=1, column=1)

input_frame = tk.Frame(center_frame, bg=CARD)
input_frame.pack(pady=15, padx=30)

tk.Label(input_frame, text="⚡ Temperature", bg=CARD, fg=TEXT, font=("Segoe UI", 12, "bold")).grid(row=0, column=0, sticky="w", pady=8)
temp_entry = tk.Entry(input_frame, font=("Segoe UI", 13), width=18, bg=ENTRY_BG, fg=TEXT,
                     insertbackground=ACCENT, relief="flat", highlightthickness=2, highlightbackground=ACCENT)
temp_entry.grid(row=0, column=1, padx=12, pady=8)

units = ["🌡️ Celsius", "🔥 Fahrenheit", "🧊 Kelvin", "📈 Rankine", "📉 Réaumur"]
from_var = tk.StringVar(value=units[0])
to_var = tk.StringVar(value=units[1])

tk.Label(input_frame, text="📤 From", bg=CARD, fg=TEXT, font=("Segoe UI", 12, "bold")).grid(row=1, column=0, sticky="w", pady=8)
from_combo = ttk.Combobox(input_frame, textvariable=from_var, values=units, state="readonly",
                         width=18, style="Custom.TCombobox")
from_combo.grid(row=1, column=1, padx=12, pady=8)

tk.Label(input_frame, text="📥 To", bg=CARD, fg=TEXT, font=("Segoe UI", 12, "bold")).grid(row=2, column=0, sticky="w", pady=8)
to_combo = ttk.Combobox(input_frame, textvariable=to_var, values=units, state="readonly",
                       width=18, style="Custom.TCombobox")
to_combo.grid(row=2, column=1, padx=12, pady=8)

btn_frame = tk.Frame(center_frame, bg=CARD)
btn_frame.pack(pady=10)

convert_btn = tk.Button(btn_frame, text="⚡ Convert", font=("Segoe UI", 12, "bold"), bg=ACCENT, fg="black",
                       width=12, relief="flat", cursor="hand2", command=convert_temperature)
convert_btn.grid(row=0, column=0, padx=5)
convert_btn.bind("<Enter>", lambda e: on_enter(e, convert_btn, "#0EA5E9"))
convert_btn.bind("<Leave>", lambda e: on_leave(e, convert_btn, ACCENT))

clear_btn = tk.Button(btn_frame, text="🗑️ Clear", font=("Segoe UI", 12, "bold"), bg=PURPLE, fg="white",
                     width=12, relief="flat", cursor="hand2", command=clear_fields)
clear_btn.grid(row=0, column=1, padx=5)
clear_btn.bind("<Enter>", lambda e: on_enter(e, clear_btn, "#7C3AED"))
clear_btn.bind("<Leave>", lambda e: on_leave(e, clear_btn, PURPLE))

copy_btn = tk.Button(btn_frame, text="📋 Copy", font=("Segoe UI", 12, "bold"), bg=GREEN, fg="black",
                    width=12, relief="flat", cursor="hand2", command=copy_result)
copy_btn.grid(row=0, column=2, padx=5)

result_label = tk.Label(center_frame, text="", font=("Segoe UI", 32, "bold"), fg=GREEN, bg=CARD)
result_label.pack(pady=10)

detail_label = tk.Label(center_frame, text="", font=("Segoe UI", 12), fg=TEXT, bg=CARD)
detail_label.pack()

formula_label = tk.Label(center_frame, text="", font=("Consolas", 10), fg=ACCENT, bg=CARD, justify="center")
formula_label.pack(pady=8)

graph_frame = tk.Frame(center_frame, bg=CARD)
graph_frame.pack(pady=10, fill="both", expand=True)

fig, ax = plt.subplots(figsize=(6, 3), dpi=100)
fig.patch.set_facecolor(CARD)
ax.set_facecolor(CARD)
canvas = FigureCanvasTkAgg(fig, master=graph_frame)
canvas.draw()
canvas.get_tk_widget().pack(fill="both", expand=True)

# TAB 2: History - BIGGER FONTS
history_frame = tk.Frame(notebook, bg=CARD)
notebook.add(history_frame, text="📜 History")

tk.Label(history_frame, text="Recent Conversions", bg=CARD, fg=TEXT,
         font=("Segoe UI", 14, "bold")).pack(pady=12)

history_listbox = tk.Listbox(history_frame, bg=ENTRY_BG, fg=TEXT,
                            font=("Consolas", 12), relief="flat", selectbackground=ACCENT)
history_listbox.pack(pady=8, padx=30, fill="both", expand=True)

hist_btn_frame = tk.Frame(history_frame, bg=CARD)
hist_btn_frame.pack(pady=12)

pdf_btn = tk.Button(hist_btn_frame, text="📄 Export PDF", font=("Segoe UI", 11, "bold"),
                   bg=GREEN, fg="black", width=14, relief="flat", cursor="hand2", command=export_pdf)
pdf_btn.pack(side="left", padx=6)

clear_hist_btn = tk.Button(hist_btn_frame, text="🗑️ Clear History", font=("Segoe UI", 11, "bold"),
                          bg="#EF4444", fg="white", width=14, relief="flat", cursor="hand2", command=clear_history)
clear_hist_btn.pack(side="left", padx=6)

# TAB 3: Formulas - BIGGER FONTS
formula_frame = tk.Frame(notebook, bg=CARD)
notebook.add(formula_frame, text="📐 Formulas")

tk.Label(formula_frame, text="Student Reference Sheet", bg=CARD, fg=ACCENT,
         font=("Segoe UI", 16, "bold")).pack(pady=18)

formulas_text = """
🔥 Fahrenheit: °F = (°C × 9/5) + 32 °C = (°F - 32) × 5/9

🧊 Kelvin: K = °C + 273.15 °C = K - 273.15

📈 Rankine: °R = (°C + 273.15) × 9/5 °C = (°R - 491.67) × 5/9

📉 Réaumur: °Ré = °C × 4/5 °C = °Ré × 5/4

💡 Key Points:
- Absolute Zero = 0K = -273.15°C = -459.67°F
- Water Freezes = 0°C = 32°F = 273.15K
- Water Boils = 100°C = 212°F = 373.15K
- Rankine & Kelvin are absolute scales
"""

tk.Label(formula_frame, text=formulas_text, bg=CARD, fg=TEXT,
         font=("Consolas", 12), justify="left").pack(padx=40, pady=15)

# Footer
footer_frame = tk.Frame(main_container, bg=BG2, height=30)
footer_frame.pack(side="bottom", fill="x")
footer = tk.Label(footer_frame, text="SkillCraft Technology • Software Development Internship 💻",
                 font=("Segoe UI", 10), fg=SUBTEXT, bg=BG2)
footer.pack(pady=5)

root.mainloop()