from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.image import Image
import random

# Shared order list (acts as a queue for kitchen)
orders_list = []

# 📜 Menu items
MENU_ITEMS = [
    {"Name": "Classic Cheeseburger", "Price": "₱95"},
    {"Name": "Margherita Pizza", "Price": "₱440"},
    {"Name": "Grilled Chicken Caesar Salad", "Price": "₱200"},
    {"Name": "Spicy Chicken Tacos (2pcs)", "Price": "₱140"},
    {"Name": "Vegetable Stir-Fry", "Price": "₱140"},
    {"Name": "Fish and Chips", "Price": "₱120"},
    {"Name": "Mushroom Risotto", "Price": "₱180"},
    {"Name": "BBQ Pulled Pork Sandwich", "Price": "₱120"},
    {"Name": "Caprese Panini", "Price": "₱80"},
    {"Name": "Chocolate Lava Cake", "Price": "₱200"},
]

# 🛒 Order System
class Order:
    def __init__(self):
        self.orders = []

    def add_order(self, item):
        self.orders.append(item)
        orders_list.append(item)  # Also send to kitchen

    def get_orders(self):
        return self.orders

    def remove_order(self, item):
        if item in self.orders:
            self.orders.remove(item)
            orders_list.remove(item)  # Remove from kitchen orders

    def clear_orders(self):
        self.orders.clear()

# 📜 Customer Screen
class CustomerScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", **kwargs)
        self.order = Order()

        self.add_widget(Label(text="📜 Quick-Eats Menu", font_size=20, bold=True))

        scroll = ScrollView()
        menu_layout = GridLayout(cols=1, spacing=5, size_hint_y=None)
        menu_layout.bind(minimum_height=menu_layout.setter('height'))

        for item in MENU_ITEMS:
            btn = Button(text=f"{item['Name']} - {item['Price']}", size_hint_y=None, height=50)
            btn.bind(on_press=lambda btn, i=item: self.add_to_order(i))
            menu_layout.add_widget(btn)

        scroll.add_widget(menu_layout)
        self.add_widget(scroll)

        # 🛒 View Order & Checkout Buttons
        self.view_order_btn = Button(text="🛒 View Order", size_hint=(1, 0.1))
        self.view_order_btn.bind(on_press=self.view_order)
        self.add_widget(self.view_order_btn)

        self.checkout_btn = Button(text="💳 Checkout", size_hint=(1, 0.1))
        self.checkout_btn.bind(on_press=self.checkout)
        self.add_widget(self.checkout_btn)

    def add_to_order(self, item):
        self.order.add_order(item)
        popup = Popup(title="✅ Order Added", content=Label(text=f"{item['Name']} added!"), size_hint=(0.5, 0.3))
        popup.open()

    def view_order(self, instance):
        popup_content = BoxLayout(orientation="vertical")
        total_price = sum(int(i["Price"][1:]) for i in self.order.get_orders())

        for item in self.order.get_orders():
            item_label = Label(text=f"{item['Name']} - {item['Price']}")
            popup_content.add_widget(item_label)

        popup_content.add_widget(Label(text=f"\n💰 Total: ₱{total_price}"))
        
        close_btn = Button(text="Close", size_hint=(1, 0.2))
        close_btn.bind(on_press=lambda x: order_popup.dismiss())
        popup_content.add_widget(close_btn)

        order_popup = Popup(title="🛒 Your Order", content=popup_content, size_hint=(0.7, 0.7))
        order_popup.open()

    def checkout(self, instance):
        checkout_layout = BoxLayout(orientation="vertical")

        # 🏧 Payment Buttons (Cash & GCash)
        cash_btn = Button(text="💵 Pay with Cash", size_hint=(1, 0.3))
        cash_btn.bind(on_press=lambda x: self.complete_checkout("Cash"))

        gcash_btn = Button(text="📱 Pay with GCash", size_hint=(1, 0.3))
        gcash_btn.bind(on_press=lambda x: self.show_qr())

        checkout_layout.add_widget(cash_btn)
        checkout_layout.add_widget(gcash_btn)

        checkout_popup = Popup(title="💰 Choose Payment Method", content=checkout_layout, size_hint=(0.6, 0.4))
        checkout_popup.open()

    def show_qr(self):
        qr_layout = BoxLayout(orientation="vertical")
        qr_layout.add_widget(Image(source="gcash_qr.png"))  # ⚠️ Add your QR image file
        close_btn = Button(text="Close", size_hint=(1, 0.2))
        qr_layout.add_widget(close_btn)

        qr_popup = Popup(title="📱 Scan GCash QR", content=qr_layout, size_hint=(0.6, 0.6))
        close_btn.bind(on_press=qr_popup.dismiss)
        qr_popup.open()

    def complete_checkout(self, method):
        self.order.clear_orders()
        orders_list.clear()

        popup = Popup(title="✅ Checkout Successful", content=Label(text=f"Payment done via {method}!"), size_hint=(0.6, 0.4))
        popup.open()

# 👨‍🍳 Kitchen Screen
class KitchenScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical")

        self.add_widget(Label(text="👨‍🍳 Kitchen Orders", font_size=20, bold=True))
        self.order_list_layout = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.scroll = ScrollView()
        self.scroll.add_widget(self.order_list_layout)
        self.add_widget(self.scroll)

        # 🔄 Refresh & Complete Order Buttons
        refresh_btn = Button(text="🔄 Refresh Orders", size_hint=(1, 0.1))
        refresh_btn.bind(on_press=self.update_orders)
        self.add_widget(refresh_btn)

    def update_orders(self, instance):
        self.order_list_layout.clear_widgets()

        for item in orders_list:
            order_btn = Button(text=f"{item['Name']} - {item['Price']}", size_hint_y=None, height=50)
            order_btn.bind(on_press=lambda btn, i=item: self.complete_order(i))
            self.order_list_layout.add_widget(order_btn)

    def complete_order(self, item):
        orders_list.remove(item)
        self.update_orders(None)
        popup = Popup(title="✅ Order Completed", content=Label(text=f"{item['Name']} is ready!"), size_hint=(0.5, 0.3))
        popup.open()

# 📱 Main App
class RestaurantApp(App):
    def build(self):
        root_layout = BoxLayout(orientation="horizontal")

        customer_screen = CustomerScreen(size_hint=(0.5, 1))
        kitchen_screen = KitchenScreen(size_hint=(0.5, 1))

        root_layout.add_widget(customer_screen)
        root_layout.add_widget(kitchen_screen)

        return root_layout

# 🚀 Run App
if __name__ == "__main__":
    RestaurantApp().run()
