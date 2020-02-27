import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as tm
import lyftRequest
import uberRequest
import database
import openBrowser
import dateCalculate

LARGE_FONT = ("Verdana", 20)
pink = '#ff00bf'

uber_session_requests = None
session_requests = None


def phone_validation(P):
    if (str.isdigit(P) or P == "") and len(P) <= 10:
        return True
    else:
        return False


def verification_code_validation(P):
    if (str.isdigit(P) or P == "") and len(P) <= 6:
        return True
    else:
        return False


class UberLyftApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        tk.Tk.wm_title(self, "Driving Data Collecting")

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (LandingPage, LyftPhone, LyftVerificationCode, LyftDriverLicence, EmailPage):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(LandingPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()
        frame.event_generate("<<ShowFrame>>")


class LandingPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        label = tk.Label(self, text="Welcome Driver!", font=LARGE_FONT)
        label.pack(pady=10, padx=15)

        label = tk.Label(self, text="Do you driver with ?", font=LARGE_FONT)
        label.pack(pady=10, padx=15)

        button1 = ttk.Button(self, text="Uber Only", width=10, command=lambda: self.uber_next(controller))
        button1.pack(pady=10)

        button2 = ttk.Button(self, text="Lyft Only", width=10, command=lambda: controller.show_frame(LyftPhone))
        button2.pack(pady=10)

        button3 = ttk.Button(self, text="Both", width=10, command=lambda: self.uber_both_next(controller))
        button3.pack(pady=10)

    @staticmethod
    def uber_next(controller):
        """
        Uber login here
        :param controller:
        :return:
        """
        global uber_session_requests

        openBrowser.open_browser()
        uber_session_requests = openBrowser.loading_cookies()
        data = uberRequest.checkLoggedin(uber_session_requests)
        if data is None:
            tm.showerror('Error', 'Uber login failed')
        else:
            tm.showinfo("Uber Login", 'Successfully logged into Uber...')
            controller.show_frame(EmailPage)

    @staticmethod
    def uber_both_next(controller):
        """
        Log in uber and then goto lyft login
        :param controller:
        :return:
        """
        global uber_session_requests

        openBrowser.open_browser()
        uber_session_requests = openBrowser.loading_cookies()
        data = uberRequest.checkLoggedin(uber_session_requests)
        if data is None:
            tm.showerror('Error', 'Uber login failed')
        else:
            tm.showinfo("Uber Login", 'Successfully logged into Uber...')
            controller.show_frame(LyftPhone)


class LyftPhone(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        label = tk.Label(self, text="Lyft Login", font=LARGE_FONT, fg=pink)
        label.grid(row=0, padx=15, sticky='nsew')

        tk.Label(self, text="Phone Number:").grid(row=1, sticky='nsew')
        vcmd = (self.register(phone_validation))
        self.phone_entry = tk.Entry(self, validate='key', validatecommand=(vcmd, '%P'))
        self.phone_entry.grid(row=1, column=1)

        confirm = ttk.Button(self, text="Next", width=10, command=lambda: self.next(controller))
        confirm.grid(row=3, pady=10)

        button1 = ttk.Button(self, text="Back to Home", command=lambda: reset(controller))
        button1.grid(row=4, pady=10)
        self.bind("<<ShowFrame>>", self.on_show)

    def on_show(self, _):
        global session_requests
        session_requests = lyftRequest.init()
        lyftRequest.loginReq(session_requests)
        lyftRequest.access_token1(session_requests)
        self.phone_entry.focus()

    def next(self, controller):
        global phone_number
        phone_number = self.phone_entry.get()

        if len(phone_number) == 10:
            lyftRequest.phoneauth1(session_requests)
            if lyftRequest.phoneauth2(phone_number, session_requests):
                controller.show_frame(LyftVerificationCode)
            else:
                tm.showerror("Error", "Your phone number is not recognized")
        else:
            tm.showerror("Error", "This is not a valid phone number")


class LyftVerificationCode(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Lyft Login", font=LARGE_FONT, fg=pink)
        label.grid(row=0, padx=15, sticky='nsew')

        tk.Label(self, text="Verification code:").grid(row=1, sticky='nsew')
        vcmd = (self.register(verification_code_validation))
        self.code_entry = tk.Entry(self, validate='key', validatecommand=(vcmd, '%P'))
        self.code_entry.grid(row=1, column=1)

        confirm = ttk.Button(self, text="Next", width=10, command=lambda: self.next(controller))
        confirm.grid(row=3, pady=10)
        confirm = ttk.Button(self, text="Send again", width=10, command=lambda: self.again())
        confirm.grid(row=4, pady=10)

        button1 = ttk.Button(self, text="Back to Home", command=lambda: reset(controller))
        button1.grid(row=5, pady=10)
        self.bind("<<ShowFrame>>", self.on_show)

    def on_show(self, _):
        self.code_entry.focus()

    @staticmethod
    def again():
        lyftRequest.phoneauth2(phone_number, session_requests)

    def next(self, controller):
        global code
        code = self.code_entry.get()

        if len(code) == 6:
            status = lyftRequest.access_token2(session_requests, phone_number, code)
            if status == 0:
                lyftRequest.save_session(session_requests)
                controller.show_frame(EmailPage)
            elif status == 1:
                controller.show_frame(LyftDriverLicence)
            else:
                tm.showerror("Error", "Your code is not correct")
        else:
            tm.showerror("Error", "Verification code has to be 6 digits")


class LyftDriverLicence(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Lyft Login", font=LARGE_FONT, fg=pink)
        label.grid(row=0, padx=15, sticky='nsew')

        tk.Label(self, text="Driver Licence:").grid(row=1, sticky='nsew')
        self.dl = tk.Entry(self)
        self.dl.grid(row=1, column=1)

        confirm = ttk.Button(self, text="Next", width=10, command=lambda: self.next(controller, self.dl.get()))
        confirm.grid(row=3, pady=10)

        button1 = ttk.Button(self, text="Back to Home", command=lambda: reset(controller))
        button1.grid(row=4, pady=10)
        self.bind("<<ShowFrame>>", self.on_show)

    def on_show(self, _):
        self.dl.focus()

    @staticmethod
    def next(controller, dl):
        status = lyftRequest.access_token3(session_requests, phone_number, code, dl)
        if status:
            lyftRequest.save_session(session_requests)
            controller.show_frame(EmailPage)
        else:
            tm.showerror("Error", "Your driver license number is not correct")


class EmailPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        label = tk.Label(self, text="App Login email", font=LARGE_FONT)
        label.grid(row=0, padx=15, sticky='nsew')

        tk.Label(self, text="Email:").grid(row=1, sticky='nsew')
        self.email = tk.Entry(self)
        self.email.grid(row=1, column=1)

        confirm = ttk.Button(self, text="Next", width=10, command=lambda: self.next(self.email.get()))
        confirm.grid(row=3, pady=10)

        button1 = ttk.Button(self, text="Back to Home", command=lambda: reset(controller))
        button1.grid(row=4, pady=10)
        self.bind("<<ShowFrame>>", self.on_show)

    def on_show(self, _):
        self.email.focus()

    @staticmethod
    def next(email):
        uid = database.check_email(email)
        if uid is not None:
            date_list = dateCalculate.getDate(uid)
            global weeklyData, session_requests, uber_session_requests
            weeklyData = {}

            if session_requests is not None:  # Lyft request
                print("Lyft")
                data = lyftRequest.request_data(session_requests, date_list)
                weeklyData['data'] = data
                weeklyData['type'] = 'lyft'
                print(weeklyData)
                tm.showinfo("Done", "Uploading Data")
                database.send_data(uid, date_list, weeklyData)
                # reset session
                session_requests = None

            weeklyData = {}
            if uber_session_requests is not None:  # Uber request
                print("Uber")
                data = uberRequest.fetch_data(uber_session_requests, date_list)
                weeklyData['data'] = data
                weeklyData['type'] = 'uber'
                print(weeklyData)
                tm.showinfo("Done", "Uploading Data")
                database.send_data(uid, date_list, weeklyData)
                # reset session
                uber_session_requests = None

            database.combine_data(uid, date_list)
            tm.showinfo("Done", "Successfully upload data")
            app.destroy()
        else:
            tm.showerror("Error", "Your email is not correct")


def reset(controller):
    global session_requests, uber_session_requests
    session_requests = None
    uber_session_requests = None
    controller.show_frame(LandingPage)


def on_closing():
    if tm.askokcancel("Quit", "Do you want to quit?"):
        if uber_session_requests:
            uberRequest.save_session(uber_session_requests)
        if session_requests:
            lyftRequest.save_session(session_requests)
        app.destroy()


def center():
    w = 500  # width for the Tk root
    h = 300  # height for the Tk root

    # get screen width and height
    ws = app.winfo_screenwidth()  # width of the screen
    hs = app.winfo_screenheight()  # height of the screen

    x = (ws / 2) - (w / 2)
    y = (hs / 2) - (h / 2)

    app.geometry('%dx%d+%d+%d' % (w, h, x, y))


if __name__ == '__main__':
    app = UberLyftApp()
    app.protocol("WM_DELETE_WINDOW", on_closing)

    center()
    app.lift()
    app.attributes('-topmost', True)
    app.after_idle(app.attributes, '-topmost', False)

    app.deiconify()
    app.mainloop()
