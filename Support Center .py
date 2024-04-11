import tkinter as tk
import smtplib
import imaplib
from email.mime.text import MIMEText
from email.header import Header
from tkinter import messagebox
from tkinter import simpledialog

class SupportRequest:
    def __init__(self, sender, subject, message):
        self.sender = sender
        self.subject = subject
        self.message = message
        self.closed = False

class Account:
    def __init__(self, email, password, name, id, image, banned):
        self.email = email
        self.password = password
        self.name = name
        self.id = id
        self.image = image
        self.banned = banned

accounts = []
with open("PSW2.txt", "r") as file:
    for line in file:
        email, password, name, id, image, banned = line.strip().split(",")
        accounts.append(Account(email, password, name, id, image, banned == "True"))

gmail_imap_server = "imap.gmail.com"
gmail_imap_port = 993
gmail_smtp_server = "smtp.gmail.com"
gmail_smtp_port = 587
gmail_username = ""
gmail_password = ""

def send_email(recipient, subject, message):
    msg = MIMEText(message, "plain", "utf-8")
    msg["From"] = Header(gmail_username)
    msg["To"] = Header(recipient)
    msg["Subject"] = Header(subject)

    try:
        with smtplib.SMTP(gmail_smtp_server, gmail_smtp_port) as server:
            server.starttls()
            server.login(gmail_username, gmail_password)
            server.sendmail(gmail_username, recipient, msg.as_string())
        return True
    except Exception as e:
        print("Failed to send email:", str(e))
        return False

def retrieve_support_requests():
    support_requests = []

    try:
        with imaplib.IMAP4_SSL(gmail_imap_server, gmail_imap_port) as server:
            server.login(gmail_username, gmail_password)
            server.select("INBOX")

            _, data = server.search(None, "ALL")
            email_ids = data[0].split()

            for email_id in email_ids:
                _, msg_data = server.fetch(email_id, "(RFC822)")
                msg = msg_data[0][1].decode("utf-8")

                sender = msg.split("From: ", 1)[1].split("\n", 1)[0]
                subject = msg.split("Subject: ", 1)[1].split("\n", 1)[0]
                message = msg.split("\n\n", 1)[1]

                support_requests.append(SupportRequest(sender, subject, message))

        return support_requests
    except Exception as e:
        print("Failed to retrieve support requests:", str(e))
        return []

def handle_support_request():
    selected_index = support_requests_listbox.curselection()
    if selected_index:
        selected_request = support_requests[selected_index[0]]
        recipient = selected_request.sender
        subject = selected_request.subject
        message = selected_request.message

        reply = simpledialog.askstring("Reply to Support Request", "Compose your reply:")
        if reply:
            reply_subject = f"Re: {subject}"
            reply_message = reply

            if send_email(recipient, reply_subject, reply_message):
                messagebox.showinfo("Support Request Handled", "The support request has been handled and a reply has been sent.")
                refresh_support_requests_list()
            else:
                messagebox.showinfo("Failed to Send Email", "Failed to send the email. Please try again.")
    else:
        messagebox.showinfo("No Support Request Selected", "Please select a support request.")

def close_support_request():
    selected_index = support_requests_listbox.curselection()
    if selected_index:
        selected_request = support_requests[selected_index[0]]
        selected_request.closed = True
        messagebox.showinfo("Support Request Closed", "The support request has been closed.")
        refresh_support_requests_list()
    else:
        messagebox.showinfo("No Support Request Selected", "Please select a support request.")

def refresh_support_requests_list():
    support_requests = retrieve_support_requests()

    support_requests_listbox.delete(0, tk.END)
    for request in support_requests:
        support_requests_listbox.insert(tk.END, f"{request.subject} {'(Closed)' if request.closed else ''}")

window = tk.Tk()
window.title("Support Request Handler")
window.geometry("800x600")

support_requests_frame = tk.Frame(window, width=200, height=600)
support_requests_frame.pack(side="left")

support_requests_label = tk.Label(support_requests_frame, text="Incoming Support Requests", font=("Arial", 14, "bold"))
support_requests_label.pack(pady=20)

support_requests_listbox = tk.Listbox(support_requests_frame, width=30, height=20)
support_requests_listbox.pack()

handle_button = tk.Button(window, text="Handle Support Request", command=handle_support_request)
handle_button.pack(side="bottom", pady=10)

close_button = tk.Button(window, text="Close Support Request", command=close_support_request)
close_button.pack(side="bottom", pady=10)

refresh_support_requests_list()

window.mainloop()












