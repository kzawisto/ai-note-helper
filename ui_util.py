import platform
import tkinter as tk
def make_tool_window(window):
    if platform.system() == 'Windows':
        window.attributes('-toolwindow',True)
    elif platform.system() == 'Darwin':
        window.attributes('-type','utility')
    elif platform.system() == 'Linux': 
        window.attributes('-type','dialog')

def toast_notification(window, txt):
    try:
        import win10toast
        toaster = win10toast.ToastNotifier()
        toaster.show_toast("Note Helper", txt)
    except Exception as e:
        # try to show Tk notification isntead
        if platform.system() != 'Windows':
            try:
                tk.messagebox.showinfo("Note Helper", txt)
            except Exception as e:
                print("Error showing notification: ", e)