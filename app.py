import tkinter as tk
import keyboard
import pyautogui
import customtkinter as ctk
import os
from concurrent.futures import ThreadPoolExecutor
from utils.llm import LLM, LLMApi, LLMApiOpenAI
from utils.prompts import get_task_prompts, get_editor_prompts, get_tasks
import pyperclip
from tkinter import ttk
from pathlib import Path
import json 
import sv_ttk


# This is where the magic happens
fields = [
    {"name":"Content","autoclear":"true"},
    {"name":"Source"},
    {"name":"Keywords"},
    {"name":"Title"},
    {"name":"category"}
]

def get_llm(settings):
    if settings['model_mode'] == 'openai':
        return LLMApiOpenAI(settings)
    else:
        return LLMApi(settings)
    
def validate_settings(root: tk.Tk, settings: dict):
    # either api_key or api_url must be not empty, show message otherwise
    if settings['api_key'] == '' and settings['api_url'] == '' and settings['model_mode'] == 'openai':
        tk.messagebox.showerror("Warning", "Please configure AI endpoint or use local model (GPU recommended) to access AI features")
        return False
    return True

class BinaryIndicatorLabel(ttk.Label):
    def __init__(self, parent, full_icon="\u25A0", empty_icon="\u25A1", **kwargs):
        super().__init__(parent, **kwargs)
        
        self.full_icon = full_icon
        self.empty_icon = empty_icon
        
        self.indicator_state = False
        self.update_indicator()


    def toggle(self):
        self.indicator_state = not self.indicator_state
        self.update_indicator()

    def set_state(self, state):
        self.indicator_state = state
        self.update_indicator()

    def update_indicator(self):
        if self.indicator_state:
            self.config(text=self.full_icon, background="white")
        else:
            self.config(text=self.empty_icon, background="white")

def textarea_on_key_press(event):
    # Prevent hotkeys when typing in the text area
    #if event.widget == text_area:
    return "break"

class CopilotApp:
    """
    CopilotApp is a GUI application that provides a set of buttons to perform various text processing tasks.
    It uses a language model (LLM) to generate responses based on clipboard content and displays the results in a new window.
    """

    def __init__(self, root):
       
        self.prompts = get_task_prompts()
        self.editor_prompts = get_editor_prompts()
        self.root = root

        self.indicator_labels = []
        self._initialize_root_window()
        self._create_layout()
        self._create_buttons()
        self._create_text_areas()
        self.executor = ThreadPoolExecutor(max_workers=5)
        #print('x')
        self.settings = json.loads(Path('settings.json').read_text())
        print(self.settings)
        if validate_settings(self.root, self.settings):
            self.llm = get_llm(self.settings)
        else:
            self.open_settings_window()

        
        # settings validation
        #if 'openai_llm' not in self.settings:
        #    self.settings['openai_llm'] = 'gpt-3.5-turbo-0125'
        self.fields = fields
        self.clipboard = {}
        print('done')
        # self.indicator_labels = []
        #if 'openai_llm' not in self.settings:
        #    self.settings['openai_llm'] = 'gpt-3.5-turbo-0125'
    


    def _initialize_root_window(self):
        """
        Initialize the main application window with specific attributes.
        """
        self.root.title("Button Tree")
        # self.root.geometry("600x400")
        self.root.overrideredirect(False)
        
        self.root.attributes('-type','dialog')
        
        self.root.update_idletasks()
    
        self.root.attributes("-topmost", True)
#        self.root.attributes("-transparentcolor", self.root["bg"])
        self.root.withdraw()  # Hide the window initially

        def on_focus_out(event):
            #if not new_window.focus_get():
                self.root.withdraw()

        #self.root.bind("<FocusOut>", on_focus_out)

    def _create_layout(self):
        """
        Create the layout for the application, including frames for icon and buttons.
        """
        # self.icon_frame = tk.Frame(self.root, width=100, height=100, bg=self.root["bg"])
        # self.icon_frame.grid(row=0, column=0, rowspan=3, padx=5, pady=5)

        self.buttons_frame = tk.Frame(self.root, bg=self.root["bg"])
        self.buttons_frame.grid(row=1, column=0, padx=5, pady=5)

        # self.icon_label = tk.Label(
        #     self.icon_frame,
        #     text="✨",
        #     bg=self.root["bg"],
        #     font=("Roboto", 24),
        #     fg="yellow",
        # )
        # self.icon_label.pack()
        self.text_frame = tk.Frame(self.buttons_frame, bg=self.root["bg"])
        self.text_frame.grid(row=1, column=0, rowspan=1, columnspan=6, padx=10, pady=10)
        
    def save_content(self, field_idx, mode):
        if mode== 'save':
            field = self.fields[field_idx]
            self.clipboard[field_idx] = self.read_text(self.text_area_1)#pyperclip.paste()

        if mode== 'append':
            field = self.fields[field_idx]

            if(self.clipboard.get(field_idx,'')!=''):
                self.clipboard[field_idx]+='\n'
                self.clipboard[field_idx] +=  self.read_text(self.text_area_1)
            else: self.clipboard[field_idx] =  self.read_text(self.text_area_1)
        if self.clipboard[field_idx] != '':
            self.indicator_labels[field_idx].set_state(True)
        if self.clipboard[field_idx] != '':
            self.indicator_labels[field_idx].set_state(True)

    def show_content(self, field_idx):
        self.write_text(self.text_area_1, self.clipboard.get(field_idx,''))
    def clearall(self):
        for i, f in enumerate(fields):
            self.clipboard[i] = ''
            self.indicator_labels[i].set_state(False)
            
    def _create_buttons(self):
        """
        Create buttons for different tasks and add them to the buttons frame.
        """
        button_options = {
            # "width": 50,
          
            # "corner_radius": 10,
            # "fg_color": "white",
            # "font": ("Roboto", 14, "normal"),
            # "text_color": "#212121",
            # "hover_color": "gray",
            # "border_width": 1,
            # "border_color": "#212121",
        }

        tasks = get_tasks()


        # for i, (text, index) in enumerate(tasks):
        #     button = ctk.CTkButton(
        #         self.buttons_frame,
        #         text=text,
        #         command=lambda i=index: self.on_button_click(i),
        #         **button_options,
        #     )
        #     button.grid(row=i % 5, column=i // 5, pady=5, padx=5)

        settings_button = ctk.CTkButton(
            self.buttons_frame,
            text='⚙ Settings',
            command=self.open_settings_window,
            **button_options,
        )
        self.style = ttk.Style(self.root)
        
        # Configure the style for the LabelFrame and its label
        # self.style.configure("White.TLabelframe", background="white")
        # self.style.configure("White.TLabelframe.Label", background="white")

        button_frame1 = ttk.LabelFrame(self.buttons_frame,text="Clipboards",width=5,style="White.TLabelframe")
        button_frame1.grid(row=0, column=0,  sticky='ew', padx=10, pady=15)

        has_content_frame = ttk.LabelFrame(self.buttons_frame,text="Has content",width=5,style="White.TLabelframe")
        has_content_frame.grid(row=0, column=1,  sticky='ew', padx=0, pady=15)
        button_frame_save = ttk.LabelFrame(self.buttons_frame,text="Save",width=5,style="White.TLabelframe")
        button_frame_save.grid(row=0, column=2,  sticky='ew', padx=0, pady=15)
        button_frame_append = ttk.LabelFrame(self.buttons_frame,text="Append",width=5,style="White.TLabelframe")
        button_frame_append.grid(row=0, column=3,  sticky='ew', padx=0, pady=15)
        button_frame_clear = ttk.LabelFrame(self.buttons_frame,text="Clear",width=5,style="White.TLabelframe")
        button_frame_clear.grid(row=0, column=4,  sticky='ew', padx=0, pady=15)
        button_frame_show = ttk.LabelFrame(self.buttons_frame,text="Show",width=5,style="White.TLabelframe")
        button_frame_show.grid(row=0, column=4,  sticky='ew', padx=0, pady=15)

        for i, field in enumerate(fields):
            name = field.get('name')
            local_label = ttk.Label(button_frame1, text=name)
            local_label.grid(row=i+1, column=0, padx=10, pady=15,)

            label_has_content = BinaryIndicatorLabel(has_content_frame)
            label_has_content.grid(row=i+1, padx=10, pady=15)
            # label_has_content.toggle()
            self.indicator_labels.append(label_has_content)
            button_save =  ttk.Button(
                button_frame_save,
                text="Save ("+str(i+1)+')',
                
                command=lambda j=i:self.save_content(j, 'save'),
                **button_options,
            )
            import time
            def click_btn_ev(button):

                def f(ev):   
                    if ev.widget.winfo_class() == 'Text':
                         return "break"
 
                    print('Event', ev, ev.widget)

                    button.event_generate("<ButtonPress-1>")
           
                    button.event_generate("<ButtonRelease-1>")
                   
                return f
            self.root.bind(f'<Key-{i+1}>',click_btn_ev(button_save))
            button_save.grid(row=i+1, column=1, padx=10, pady=10)

            # button =  ttk.Button(
            #     button_frame_clear,
            #     text="(Ctrl+"+(str(i+1))+')',
            #     command=lambda j=i:self.save_content(j, 'append'),
            #     **button_options)
            # button.grid(row=i+1, column=2, padx=10, pady=10)

            button =  ttk.Button(
                button_frame_append,
                text=f'Append (Ctrl+{i+1})',
                command=lambda j=i :self.save_content(j,'append'),
                **button_options)
            button.grid(row=i+1, column=0, padx=10, pady=10)
            self.root.bind(f'<Control-Key-{i+1}>', click_btn_ev(button))


            button_show =  ttk.Button(
                button_frame_show,
                text='Show',
                command=lambda j=i: self.show_content(j),
                **button_options)
            button_show.grid(row=i+1, column=0, padx=10, pady=10)


        # settings_button.grid(row=len(fields) % 5, column=len(fields) // 5, pady=5, padx=5)


    def _create_text_areas(self):
        """
            Create two text areas and add them to the text frame.
            """
        # Text Area 1
        self.text_area_1 = tk.Text(self.text_frame, width=50, height=15, font=("Roboto", 12))
        self.text_area_1.grid(row=0, column=0, padx=5, pady=5, columnspan=5, rowspan=2)

        self.scrollbar_1 = tk.Scrollbar(self.text_frame, command=self.text_area_1.yview)
        self.scrollbar_1.grid(row=0, column=5, sticky='ns', rowspan=2)
        self.text_area_1.config(yscrollcommand=self.scrollbar_1.set)
        button_frame1 = ttk.LabelFrame(self.text_frame,text="Util",width=5,style="White.TLabelframe")
        button_frame1.grid(row=0, column=6, padx=5, pady=5, sticky='ew')
        clear_button = ttk.Button(
            button_frame1,
            text='Clear All',
            command=lambda : self.clearall(),
        )
        clear_button.grid(row=0, column=0,padx=5,pady=5)

        savefile_button = ttk.Button(
            button_frame1,
            text='Save Note (Ctrl-S)',
            command=lambda : print(),
        )
        savefile_button.grid(row=1, column=0,padx=5,pady=5)
        savefile_button = ttk.Button(
            button_frame1,
            text='Append to Note. (Ctrl-A)',
            command=lambda : print(),
        )
        savefile_button.grid(row=2, column=0,padx=5,pady=5)
        settings_button = ttk.Button(
            button_frame1,
            text='⚙ Settings',
            command=lambda : self.open_settings_window(),
        )
        settings_button.grid(row=3, column=0,padx=5,pady=5)
        button_frame2 = ttk.LabelFrame(self.text_frame,text="AI",width=5,style="White.TLabelframe")
        button_frame2.grid(row=1, column=6, padx=5, pady=5,sticky="ew")
        generate_button = ttk.Button(
            button_frame2,
            text='Generate Title & Keywords',
            command=lambda : print(),
        )
        generate_button.grid(row=0, column=0, padx=5, pady=5)

        classify_category = ttk.Button(
            button_frame2,
            text='Classify Category',
            command=lambda : print(),
        )
        classify_category.grid(row=1, column=0, padx=5, pady=5)


        # # Text Area 2
        # self.text_area_2 = tk.Text(self.text_frame, width=50, height=15, font=("Roboto", 12))
        # self.text_area_2.grid(row=1, column=0, padx=5, pady=5)

        # self.scrollbar_2 = tk.Scrollbar(self.text_frame, command=self.text_area_2.yview)
        # self.scrollbar_2.grid(row=1, column=1, sticky='ns')
        # self.text_area_2.config(yscrollcommand=self.scrollbar_2.set)
    def read_text(self, text_area):
            content = text_area.get("1.0", tk.END)  # Get all text from line 1, character 0 to the end
            return content

        # Function to write to the Text widget
    def write_text(self, text_area,new_text):
            text_area.delete("1.0", tk.END)  # Clear existing content
            text_area.insert(tk.END, new_text)  # Insert new text
    def read_text_entry(self, entry):
        # Get text from the Entry widget
        text = entry.get()
        # Display the text in the label
        return text

    def write_text_entry(self, entry, new_text):
        # Clear the Entry widget and insert new text
        entry.delete(0, tk.END)
        entry.insert(0, new_text)

    def toggle_window(self):
        """
        Toggle the visibility of the main application window.
        """
        print('x')
        # print(self.root.state())
        if self.root.state() == "withdrawn":
            x, y = pyautogui.position()
            print(x,y)
            self.root.geometry(f"+{x-50}+{y-100}")
            self.root.deiconify()
            self.write_text(self.text_area_1,pyperclip.paste())
    
        else:
            self.root.withdraw()

    def on_button_click(self, task_index):
        """
        Handle button click events by triggering the corresponding task.
        """
        self.toggle_window()
        self.executor.submit(self.handle_button_click, task_index)

    def handle_button_click(self, task_index):
        """
        Execute the task corresponding to the clicked button.
        """
        print('handle click', task_index)
        prompt = self.prompts[task_index]["prompt"]
        print('template', prompt)
        print('----------------------------')
        prompt = prompt.format(text=pyperclip.paste())
        print(' prompt',prompt)
        print('----------------------------------------------------')
        generated_text = self.llm.generate(prompt)
        if task_index==1:
            path = '/home/krystian/mydocs/mydocsstuff/darwinnotes.bib'
            with open(path, 'a') as fp:
                fp.write('\n')
                fp.write(generated_text)
            os.system('chown krystian ' + path)


        pyperclip.copy(generated_text)
        self.root.after(0, self.show_generated_text, generated_text)

    def show_generated_text(self, text):
        """
        Display the generated text in a new, borderless window near the mouse cursor.
        """
        new_window = tk.Toplevel(self.root)
        new_window.title("Generated Text")
        new_window.geometry("600x450")
        new_window.overrideredirect(False)
        new_window.attributes('-type','dialog')
        #new_window.attributes("-transparentcolor", new_window["bg"])

        center_frame = ctk.CTkFrame(
            new_window,
            fg_color="white",
            corner_radius=10,
            width=580,
            height=430,
        )
        center_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        text_box = ctk.CTkTextbox(
            center_frame,
            wrap=tk.WORD,
            font=("Roboto", 18),
            corner_radius=10,
            border_width=1,
            border_color="#212121",
            width=560,
            height=360,
        )
        text_box.pack(expand=True, fill="both", padx=5, pady=5)
        text_box.insert(tk.END, text)
        text_box.configure(state="disabled")

        # Create buttons for editing text
        edit_buttons_frame = ctk.CTkFrame(center_frame, fg_color="white")
        edit_buttons_frame.pack(padx=5, pady=5)

        edit_button_options = {
            "width": 70,
            "height": 30,
            "corner_radius": 10,
            "fg_color": "white",
            "font": ("Roboto", 12, "normal"),
            "text_color": "#212121",
            "hover_color": "gray",
            "border_width": 2,
            "border_color": "#212121",
        }

        edit_tasks = ["Casual", "Formal", "Professional", "Technical", "Simple"]

        for i, task in enumerate(edit_tasks):
            edit_button = ctk.CTkButton(
                edit_buttons_frame,
                text=task,
                command=lambda t=task: self.edit_text(t, text, text_box),
                **edit_button_options,
            )
            edit_button.grid(row=0, column=i, padx=5)
        close = ctk.CTkButton(
                edit_buttons_frame,
                text='Close',
                command=lambda :new_window.destroy(),
                **edit_button_options,
            )
        close.grid(row=0, column=len(edit_tasks), padx=5)


        x, y = pyautogui.position()
        new_window.geometry(f"+{x-300}+{y-250}")

        def on_focus_out(event):
            #if not new_window.focus_get():
                new_window.destroy()

        new_window.bind("<FocusOut>", on_focus_out)
        new_window.focus_force()

    def edit_text(self, task, text, text_box):
        """
        Handle text editing tasks. Implement the logic as needed.
        """

        editor_prompt = next(
            (item for item in self.editor_prompts if item["editor"] == task), None
        )

        if editor_prompt:
            prompt = editor_prompt["prompt"]
            prompt = prompt.format(text=text)
            generated_text = self.llm.generate(prompt)
            pyperclip.copy(generated_text)
            text_box.configure(state="normal")
            text_box.delete("1.0", tk.END)
            text_box.insert(tk.END, generated_text)
            text_box.configure(state="disabled")


    def open_settings_window(self):
        """
        Open a new window with tabs for configuring settings.
        """
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")

        # tab_control = ttk.Notebook(settings_window)

        # tab1 = ttk.Frame(tab_control)
        # tab2 = ttk.Frame(tab_control)
        # tab3 = ttk.Frame(tab_control)

        # tab_control.add(tab1, text='API Keys')
        # tab_control.add(tab2, text='Prompts')
        # tab_control.add(tab3, text='Save to File')
        # tab_control.pack(expand=1, fill="both")

        # # Tab 1 content (API Keys)


        api_cfg = ttk.LabelFrame(settings_window, text="Configure AI:")
        api_cfg.grid(row=0, column=0, padx=10, pady=10)
        tab1 = api_cfg
        api_label = ttk.Label(tab1, text="OpenAI API Key:")
        api_label.grid(row=0, column=0, padx=10, pady=10)
        api_entry = ttk.Entry(tab1, width=40)
        api_entry.grid(row=0, column=1, padx=10, pady=10)
        self.write_text_entry(api_entry, self.settings['api_key'])


        apiurl_label = ttk.Label(tab1, text="Custom URL (for OpenAI use empty):")
        apiurl_label.grid(row=2, column=0, padx=10, pady=10)


        apiurl_entry = ttk.Entry(tab1, width=40)
        apiurl_entry.grid(row=2, column=1, padx=10, pady=10)
        self.write_text_entry(apiurl_entry, self.settings['api_url'])

        apimodel_label = ttk.Label(tab1, text="API Model:")
        apimodel_label.grid(row=3, column=0, padx=10, pady=10)
        apimodel_entry = ttk.Entry(tab1, width=40)
        apimodel_entry.grid(row=3, column=1, padx=10, pady=10)
        self.write_text_entry(apimodel_entry, self.settings['api_model'])

        # local_label = ttk.Label(tab1, text="Llama_cpp local model:")
        # local_label.grid(row=4, column=0, padx=10, pady=10)
        # local_entry = ttk.Entry(tab1, width=40)
        # local_entry.grid(row=4, column=1, padx=10, pady=10)
        # self.write_text_entry(local_entry, self.settings['local_model'])


        endpoint_var = tk.StringVar()
        endpoint_var.set(self.settings['model_mode'])  # set default selection
        # how to you write
    
        endpoint_label = ttk.LabelFrame(tab1, text="Select Inference Endpoint:")
        endpoint_label.grid(row=5, column=0, padx=10, pady=10, columnspan=2,sticky='ew')

        openai_radio = ttk.Radiobutton(endpoint_label, text="OpenAI/API", variable=endpoint_var, value="openai")
        openai_radio.grid(row=0, column=0, padx=10, pady=2)

        local_radio = ttk.Radiobutton(endpoint_label, text="Local Llama CPP", variable=endpoint_var, value="local")
        local_radio.grid(row=0, column=1, padx=10, pady=2)


                #self.llm = LLMApiOpenAI(settings2)

        util_cfg = ttk.LabelFrame(settings_window, text="General settings:")
        util_cfg.grid(row=1, column=0, padx=10, pady=10, sticky='ew')

        file_label = ttk.Label(util_cfg, text="Note directory:")
        file_label.grid(row=0, column=0, padx=10, pady=10)
        file_entry = ttk.Entry(util_cfg, width=40)
        file_entry.grid(row=0, column=1, padx=10, pady=10)
        self.write_text_entry(file_entry, self.settings['save_dir'])



        filename_label = ttk.Label(util_cfg, text="Note filename:")
        filename_label.grid(row=1, column=0, padx=10, pady=10)
        filename_entry = ttk.Entry(util_cfg, width=40)
        filename_entry.grid(row=1, column=1, padx=10, pady=10)
        self.write_text_entry(filename_entry, self.settings['filename'])
        def update_settings():
            settings2 = {}
            settings2['api_key'] = self.read_text_entry(api_entry)
            settings2['api_url'] = self.read_text_entry(apiurl_entry)
            settings2['api_model'] = self.read_text_entry(apimodel_entry)
            settings2['save_dir'] = self.read_text_entry(file_entry)
            settings2['filename'] = self.read_text_entry(filename_entry)
            # settings2['local_model'] = self.read_text_entry(local_entry)
            settings2['model_mode'] = endpoint_var.get()
            if validate_settings(self.root, settings2):
                Path('settings.json').write_text(json.dumps(settings2))
                # show tk notification that LLM has been updated
                tk.messagebox.showinfo("LLM Update", "LLM is updated")
                self.llm = get_llm(settings2)

                # todo

            self.settings = settings2
        def restore_default_settings():
            settings2 = json.loads(Path('settings_default.json').read_text())
            self.write_text_entry(api_entry, settings2['api_key'])
            self.write_text_entry(apiurl_entry, settings2['api_url'])
            self.write_text_entry(apimodel_entry, settings2['api_model'])
            # self.write_text_entry(local_entry, settings2['local_model'])
            endpoint_var.set(settings2['model_mode'])
            update_settings()

    
        but_label = ttk.LabelFrame(settings_window)
        but_label.grid(row=2, column=0, padx=10, pady=10, columnspan=2,sticky='ew')
        settings_save = ttk.Button(
            but_label,
            text='⚙ Save Settings',
            command=lambda : update_settings(),
        )
        settings_save.grid(row=3, column=0,padx=5,pady=5)
        exit = ttk.Button(
            but_label,
            text='Exit',
            command=lambda : settings_window.destroy(),
        )
        
        exit.grid(row=3, column=1,padx=5,pady=5)
        restore_default = ttk.Button(
            but_label,
            text='Restore Default',
            command=lambda : restore_default_settings(),
        )
        restore_default.grid(row=3, column=2,padx=5,pady=5)
        # # Tab 2 content (Prompts) 
        # # can you write dropdown selector for TK?


        # prompts_label = ttk.Label(tab2, text="Prompt:")
        # prompts_label.grid(row=2, column=0, padx=10, pady=10)
        # prompts_text = tk.Text(tab2, width=150, height=15)
        # prompts_text.grid(row=2,column=1, columnspan=3, padx=10, pady=10)
        
        # label = tk.Label(tab2,text="Select an option:")
        # label.grid(row=0,column=0)
        # # label.pack(pady=10)

        # # Create a dropdown selector (Combobox)
        # options =[t[0]  for t in get_tasks()]#["Option 1", "Option 2", "Option 3", "Option 4"]
        # combo = ttk.Combobox(tab2, values=options)
        # combo.grid(row=0, column=1)
        # check_var = tk.BooleanVar()
        # check_var.set(False)
        # checkbutton = ttk.Checkbutton(tab2, text="Save output to file.", variable=check_var)
        # checkbutton.grid(row=3, column=0, padx=10, pady=10)

        # combo.pack(pady=10)

        # Bind the select event

        # def read_text():
        #     content = prompts_text.get("1.0", tk.END)  # Get all text from line 1, character 0 to the end
        #     return content

        # # Function to write to the Text widget
        # def write_text(new_text):
        #     prompts_text.delete("1.0", tk.END)  # Clear existing content
        #     prompts_text.insert(tk.END, new_text)  # Insert new text


        # def on_select(event):
        #     selected_value = combo.get()
        #     idx = dict(get_tasks()).get(selected_value)
        #     write_text(self.prompts[idx]["prompt"])
        #     print(f"Selected: {selected_value}")
        # combo.bind("<<ComboboxSelected>>", on_select)

        # Create a button
        # button = tk.Button(tab2, text="Print Selection", command=lambda: print(f"Selected: {combo.get()}"))
        # button.pack(pady=10)
        # button.grid(row=0, column=2)


        # Tab 3 content (Save to File)
        # save_label = ttk.Label(tab3, text="Save Directory:")
        # save_label.grid(row=0, column=0, padx=10, pady=10)
        # self.save_entry = ttk.Entry(tab3, width=40)
        # self.save_entry.grid(row=0, column=1, padx=10, pady=10)
        # save_button = ttk.Button(tab3, text="Browse", command=lambda: self.browse_directory(self.save_entry))
        # save_button.grid(row=0, column=2, padx=10, pady=10)

    def browse_directory(self, entry_widget):
        """
        Open a directory selection dialog and update the text entry widget with the selected directory.
        """
        directory = tk.filedialog.askdirectory()
        if directory:
            entry_widget.delete(0, tk.END)  # Clear the current content
            entry_widget.insert(0, directory)




def main():
    root = ctk.CTk()
    app = CopilotApp(root)

    sv_ttk.set_theme("light")

    keyboard.add_hotkey("ctrl+space", app.toggle_window)
    root.mainloop()


if __name__ == "__main__":
    main()
