# app/main.py
import os
import time
import random
import humanize
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt
import pwinput

# Import DB functions
from db.sql import (
    register,
    login,
    check_user,
    change_password,
    get_restaurants,
    place_order,
    add_payment,
    retrieve_payment,
    view_orders,
    retrieve_user,
)

# -----------------------
# Utility Setup
# -----------------------
console = Console()
project_name = "Yippee"
clear = lambda: os.system("cls" if os.name == "nt" else "clear")

# -----------------------
# Helper Functions
# -----------------------
def cprint(text="", end="\n"):
    console.print(text, end=end)


def input_prompt(prompt=""):
    return console.input(prompt)


def prompt_choice(prompt, choices=None, default=None):
    return Prompt.ask(prompt, choices=choices, default=default)


def print_table(title, headers, rows):
    table = Table(title=title)
    for h in headers:
        table.add_column(h, overflow="fold")
    for row in rows:
        table.add_row(*[str(x) for x in row])
    console.print(table)


def print_panel(title, content):
    console.print(Panel(content, title=title, expand=False))


# ======================================================
# LOGIN SCREEN
# ======================================================
def loginscreen():
    global loginDetails, user_name

    clear()
    cprint(f"[bold cyan]Welcome to {project_name}![/bold cyan]")
    cprint("Delicious food from Kochi’s best restaurants.\n")

    email = input_prompt("Enter your email address: ")
    exists, name = check_user(email)

    if exists:
        # Existing user
        while True:
            password = pwinput.pwinput(prompt=f"Welcome back {name}!\nEnter your password: ")
            if login(email, password):
                cprint("[green]Login successful![/green]")
                loginDetails = email
                user_name = name
                time.sleep(1)
                break
            else:
                cprint("[red]Incorrect password, please try again.[/red]")
    else:
        # New user
        cprint("\n[bold yellow]New user detected![/bold yellow]")
        name = input_prompt("Enter your name: ")
        password = pwinput.pwinput(prompt="Enter a secure password: ")
        register(email, password, name)
        cprint("[green]Registration and auto-login successful![/green]")
        loginDetails = email
        user_name = name
        time.sleep(1)

    clear()
    cprint(f"[cyan]Welcome, {user_name}![/cyan]")


# ======================================================
# PAYMENT HANDLING
# ======================================================
def handle_payment(cart, delivery_time, total_price):
    cprint("\n[bold cyan]Payment Section[/bold cyan]")
    save = prompt_choice("Save card for future? (1.Yes / 2.No)", choices=["1", "2"], default="1")

    while True:
        card = input_prompt("Enter 16-digit card number: ")
        if len(card) == 16 and card.isdigit():
            break
        cprint("[red]Invalid card number. Try again.[/red]")

    while True:
        cvv = input_prompt("Enter CVV (3-4 digits): ")
        if len(cvv) in (3, 4) and cvv.isdigit():
            break
        cprint("[red]Invalid CVV. Try again.[/red]")

    while True:
        expiry = input_prompt("Enter Expiry (MM/YY): ")
        if "/" in expiry and len(expiry) == 5:
            break
        cprint("[red]Invalid expiry format. Try again.[/red]")

    cardtype = "Visa" if card.startswith("4") else "MasterCard"
    if save == "1":
        add_payment(loginDetails, card, cvv, expiry, cardtype)

    cprint(f"\nPayment successful using {cardtype} ending with {card[-4:]}")
    cprint(f"Order placed for {len(cart)} items. Total = {total_price} INR")
    cprint(f"Estimated delivery: {delivery_time // 60} minutes")


# ======================================================
# MAIN PROGRAM LOOP
# ======================================================
def main_menu():
    while True:
        clear()
        cprint(f"[bold magenta]Welcome to {project_name}, {user_name}![/bold magenta]")
        cprint("1. Place an Order")
        cprint("2. View Previous Orders")
        cprint("3. Account Settings")
        cprint("4. Logout")
        cprint("5. Exit")

        choice = input_prompt("\nEnter your choice: ")

        # --------------------------
        # PLACE ORDER
        # --------------------------
        if choice == "1":
            clear()
            cprint("[bold cyan]Fetching nearby restaurants...[/bold cyan]")
            restaurants = get_restaurants()
            time.sleep(1)
            clear()

            rows = []
            for r in restaurants:
                details = eval(r[2])
                rows.append((r[0], details["Location"], details["Cuisine"], details["Rating"]))
            print_table("Available Restaurants", ["Name", "Location", "Cuisine", "Rating"], rows)

            selected = input_prompt("\nEnter restaurant name: ")
            found = False

            for r in restaurants:
                if r[0].lower() == selected.lower():
                    found = True
                    menu = eval(r[1])
                    cart = []
                    while True:
                        clear()
                        menu_rows = [(dish, f"{price} INR") for dish, price in menu.items()]
                        print_table(f"Menu - {r[0]}", ["Dish", "Price"], menu_rows)

                        choice = input_prompt('Enter dish to add (or "checkout" to proceed): ')
                        if choice.lower() == "checkout":
                            if not cart:
                                cprint("[red]Cart is empty.[/red]")
                                input_prompt("Press Enter to continue...")
                                break

                            total_price = sum([item[2] for item in cart])
                            delivery_time = random.randint(20, 50) * 60
                            unix = (datetime.now() + timedelta(seconds=delivery_time)).timestamp()

                            cprint("\nYour Cart Summary:")
                            cart_rows = [(dish, qty, f"{price} INR") for dish, qty, price in cart]
                            print_table("Cart", ["Dish", "Qty", "Price"], cart_rows)
                            cprint(f"Total = {total_price} INR\n")

                            payment_method = prompt_choice(
                                "Payment Method (1.Cash / 2.Card):", choices=["1", "2"], default="1"
                            )

                            if payment_method == "1":
                                cprint("\n[green]Order placed successfully! Pay on delivery.[/green]")
                            else:
                                saved, details = retrieve_payment(loginDetails)
                                if saved:
                                    use_saved = prompt_choice(
                                        f"Use saved {details['cardtype']} ending {details['card'][-4:]}? (1.Yes / 2.No)",
                                        choices=["1", "2"],
                                        default="1",
                                    )
                                    if use_saved == "1":
                                        cprint(f"Paid using saved {details['cardtype']} ending {details['card'][-4:]}")
                                    else:
                                        handle_payment(cart, delivery_time, total_price)
                                else:
                                    handle_payment(cart, delivery_time, total_price)

                            place_order(loginDetails, r[0], cart, unix, total_price)
                            input_prompt("\nPress Enter to continue...")
                            break

                        elif choice in menu:
                            try:
                                qty = int(input_prompt("Enter quantity: "))
                                price = qty * menu[choice]
                                cart.append((choice, qty, price))
                                cprint(f"Added {choice} x{qty} ({price} INR)")
                                input_prompt("Press Enter to continue...")
                            except Exception:
                                cprint("[red]Invalid quantity.[/red]")
                                input_prompt("Press Enter to continue...")
                        else:
                            cprint("[red]Invalid dish name.[/red]")
                            input_prompt("Press Enter to continue...")
            if not found:
                cprint("[red]Restaurant not found![/red]")
                input_prompt("Press Enter to continue...")

        # --------------------------
        # VIEW ORDERS
        # --------------------------
        elif choice == "2":
            clear()
            success, orders = view_orders(loginDetails)
            if not success:
                cprint("[red]No orders yet.[/red]")
                input_prompt("Press Enter to continue...")
                continue

            for order in orders:
                cprint(f"\n[bold cyan]Order #{order['order_id']}[/bold cyan]")
                cprint(f"Restaurant: {order['restaurant']}")
                cprint(f"Total: {order['total_price']} INR")
                delivery_status = "Delivered" if order["unix_time"] < datetime.now().timestamp() else "Delivering in"
                cprint(f"Status: {delivery_status} {humanize.naturaltime(datetime.fromtimestamp(order['unix_time']))}")
                cprint("Items:")
                for dish, qty, price in order["items"]:
                    cprint(f"  • {dish} x{qty} = {price} INR")

            input_prompt("\nPress Enter to continue...")

        # --------------------------
        # ACCOUNT SETTINGS
        # --------------------------
        elif choice == "3":
            clear()
            user = retrieve_user(loginDetails)
            saved, card = retrieve_payment(loginDetails)
            card_info = f"{card['cardtype']} ending {card['card'][-4:]}" if saved else "None"
            content = f"Name: {user[2]}\nEmail: {user[0]}\nSaved Card: {card_info}"
            print_panel("Account Details", content)

            ch = prompt_choice("Change password? (1.Yes / 2.No)", choices=["1", "2"], default="2")
            if ch == "1":
                old_pw = pwinput.pwinput("Enter old password: ")
                if login(loginDetails, old_pw):
                    new_pw = pwinput.pwinput("Enter new password: ")
                    confirm = pwinput.pwinput("Confirm new password: ")
                    if new_pw == confirm:
                        change_password(loginDetails, new_pw)
                        cprint("[green]Password updated successfully![/green]")
                    else:
                        cprint("[red]Passwords do not match![/red]")
                else:
                    cprint("[red]Incorrect old password![/red]")
                input_prompt("Press Enter to continue...")

        # --------------------------
        # LOGOUT
        # --------------------------
        elif choice == "4":
            cprint("\n[cyan]Logging out...[/cyan]")
            time.sleep(1.5)
            loginscreen()

        # --------------------------
        # EXIT
        # --------------------------
        elif choice == "5":
            cprint(f"\n[bold green]Thank you for using {project_name}![/bold green]")
            time.sleep(2)
            exit()

        else:
            cprint("[red]Invalid choice. Try again.[/red]")
            time.sleep(1)


# ======================================================
# ENTRY POINT
# ======================================================
if __name__ == "__main__":
    loginscreen()
    main_menu()
