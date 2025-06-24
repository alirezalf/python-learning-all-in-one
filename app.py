import tkinter as tk
from tkinter import scrolledtext
import io
import sys
import asyncio
from pygments import lex
from pygments.lexers import PythonLexer
from pygments.token import Token
import json
with open("sections.json", "r", encoding="utf-8") as f:
    SECTIONS = json.load(f)

def run_code(code):
    output_box.config(state='normal')
    output_box.delete("1.0", tk.END)
    old_stdout = sys.stdout
    sys.stdout = mystdout = io.StringIO()

    try:
        local_env = {'asyncio': asyncio}  # اضافه کردن asyncio به محیط اجرا

        if "async def" in code:
            # اجرای کد برای تعریف توابع
            exec(code, local_env, local_env)

            # پیدا کردن تابع main
            main_func = local_env.get('main')
            if main_func and asyncio.iscoroutinefunction(main_func):
                asyncio.run(main_func())
            else:
                # اگر تابع main وجود نداشت، سعی می‌کنیم هر تابع async دیگری را پیدا کنیم
                for name, obj in local_env.items():
                    if asyncio.iscoroutinefunction(obj):
                        asyncio.run(obj())
                        break
        else:
            # اجرای عادی کدهای غیر async
            exec(code, local_env, local_env)

        result = mystdout.getvalue()
        output_box.insert(tk.END, result)
    except Exception as e:
        output_box.insert(tk.END, f"Error: {e}")
    finally:
        sys.stdout = old_stdout
        output_box.config(state='disabled')
    output_box.see(tk.END)


def on_section_select(event):
    if not section_list.curselection():
        return
    selection = section_list.get(section_list.curselection())
    example_list.delete(0, tk.END)
    examples = SECTIONS.get(selection, [])
    for example in examples:
        example_list.insert(tk.END, example["title"])
    if examples:
        example_list.select_set(0)
        example_list.event_generate("<<ListboxSelect>>")

    description_box.config(state='normal')
    description_box.delete("1.0", tk.END)
    code_box.config(state='normal')
    code_box.delete("1.0", tk.END)
    output_box.config(state='normal')
    output_box.delete("1.0", tk.END)
    output_box.config(state='disabled')


def on_example_select(event):
    if not example_list.curselection():
        return

    selected_item = example_list.get(example_list.curselection()[0])

    # حالت پیش‌فرض: نام بخش را از لیست بخش‌ها بگیریم
    section = section_list.get(
        section_list.curselection()) if section_list.curselection() else None
    example_name = selected_item

    # اگر فرمت انتخاب‌شده از جستجو باشد، یعنی شامل " : "
    if " : " in selected_item:
        section, example_name = selected_item.split(" : ", 1)

    # حالا دنبال کد و توضیح بگرد
    if section:
        examples = SECTIONS.get(section, [])
        for example in examples:
            if example["title"] == example_name.strip():
                description_box.config(state='normal')
                description_box.delete("1.0", tk.END)
                description_box.insert(tk.END, example["description"])
                description_box.config(state='disabled')

                code_box.config(state='normal')
                code_box.delete("1.0", tk.END)
                code_box.insert(tk.END, example["code"])
                code_box.config(state='normal')

                run_code(example["code"])
                break




window = tk.Tk()
window.title("آموزش کامل پایتون - مقدماتی- نوشته علیرضا لباف")
window.geometry("1100x700")
window.configure(bg="#f8f9fa")

right_frame = tk.Frame(window, bg="#f8f9fa")
right_frame.pack(side="right", fill="y", padx=10, pady=10)

section_label = tk.Label(right_frame, text="بخش‌ها",
                         font=("Tahoma", 14, "bold"), bg="#f8f9fa")
section_label.pack(pady=(0, 5))

section_list = tk.Listbox(right_frame, justify="right", font=(
    "Tahoma", 13), width=40, height=12, exportselection=False)


section_list.pack(pady=(0, 10))
section_list.bind("<<ListboxSelect>>", on_section_select)

example_label = tk.Label(right_frame, text="مثال‌ها",
                         font=("Tahoma", 14, "bold"), bg="#f8f9fa")
example_label.pack(pady=(10, 5))

example_list = tk.Listbox(right_frame, font=(
    "Tahoma", 12), justify="right", width=40, height=12, exportselection=False)
example_list.pack()
example_list.bind("<<ListboxSelect>>", on_example_select)

# جستجو
search_frame = tk.Frame(right_frame, bg="#f8f9fa")
search_frame.pack(pady=(10, 5))

# خط اول: کادر جستجو و دکمه جستجو
search_top_frame = tk.Frame(search_frame, bg="#f8f9fa")
search_top_frame.pack(fill="x")

search_entry = tk.Entry(search_top_frame, font=("Tahoma", 12))
search_entry.pack(side="left", expand=True, fill="x", padx=(0, 5))


def filter_examples():
    search_term = search_entry.get().lower()
    example_list.delete(0, tk.END)

    if search_all_var.get():  # اگر جستجو در همه بخش‌ها فعال باشد
        for section, examples in SECTIONS.items():
            for example in examples:
                if (search_term in example["title"].lower() or
                    search_term in example["description"].lower() or
                    search_term in example["code"].lower()):
                    example_list.insert(tk.END, f"{section} : {example['title']}")
    else:  # جستجو فقط در بخش انتخاب شده
        if section_list.curselection():
            section = section_list.get(section_list.curselection())
            examples = SECTIONS.get(section, [])
            for example in examples:
                if (search_term in example["title"].lower() or
                    search_term in example["description"].lower() or
                    search_term in example["code"].lower()):
                    example_list.insert(tk.END, example["title"])

    if example_list.size() > 0:
        example_list.select_set(0)
        example_list.event_generate("<<ListboxSelect>>")



def reset_search():
    search_entry.delete(0, tk.END)
    search_all_var.set(False)
    if section_list.curselection():
        on_section_select(None)  # برای نمایش مثال‌های بخش انتخاب شده


search_button = tk.Button(
    search_top_frame,
    text="جستجو",
    font=("Tahoma", 12),
    command=filter_examples
)
search_button.pack(side="left")
search_bottom_frame = tk.Frame(search_frame, bg="#f8f9fa")
search_bottom_frame.pack(fill="x")
search_all_var = tk.BooleanVar(value=True)
search_all_check = tk.Checkbutton(
    search_bottom_frame,
    text="جستجو در همه بخش‌ها",
    variable=search_all_var,
    font=("Tahoma", 10),
    bg="#f8f9fa"
)
search_all_check.pack(side="right", padx=(0, 10))

reset_button = tk.Button(
    search_bottom_frame,
    text="بازنشانی",
    font=("Tahoma", 12),
    command=reset_search
)
reset_button.pack(side="left")


left_frame = tk.Frame(window, bg="#f8f9fa")
left_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

description_label = tk.Label(left_frame, text="توضیح:", font=(
    "Tahoma", 14, "bold"), bg="#f8f9fa")
description_label.pack(anchor="w")

description_box = tk.Text(left_frame, font=(
    "Tahoma", 13), height=8, wrap="word", bg="#fffbe7", state="disabled")
description_box.pack(fill="x", pady=(0, 10))

code_label = tk.Label(left_frame, text="کد:", font=(
    "Consolas", 13, "bold"), bg="#f8f9fa")
code_label.pack(anchor="w")

code_box = tk.Text(left_frame, font=("Consolas", 12), height=12, bg="#e8e8e8")
code_box.pack(fill="both", expand=True, pady=(0, 10))

output_label = tk.Label(left_frame, text="خروجی:",
                        font=("Tahoma", 14, "bold"), bg="#f8f9fa")
output_label.pack(anchor="w")

output_box = tk.Text(left_frame, font=("Consolas", 12),
                     height=8, bg="#d7f0d7", state="disabled")
output_box.pack(fill="both", expand=True)

for section in SECTIONS.keys():
    section_list.insert(tk.END, section)


window.update_idletasks()

width = window.winfo_width()
height = window.winfo_height()

screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()

x = (screen_width // 2) - (width // 2)
y = (screen_height // 2) - (height // 2)

window.geometry(f"{width}x{height}+{x}+{y}")
window.state('zoomed')
window.mainloop()
