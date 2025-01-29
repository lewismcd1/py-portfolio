import reflex as rx
import re
from reflex.style import set_color_mode, color_mode
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

class State(rx.State):
    name: str = ""
    email: str = ""
    message: str = ""
    status: str = ""
    is_dark_mode: bool = True

    def toggle_theme(self):
        """Toggle between light and dark themes."""
        self.is_dark_mode = not self.is_dark_mode

    def on_mount(self):
        self.status = ""
        self.reset_form()

    def send_email(self):
        """Send an email using Gmail SMTP."""
        try:
            load_dotenv(override=True)
            # Get credentials from environment variables
            smtp_password = os.getenv("GMAIL_APP_PASSWORD")
            sender_email = os.getenv("GMAIL_ADDRESS")
            receiver_email = os.getenv("RECEIVER_EMAIL")

            if not all([smtp_password, sender_email, receiver_email]):
                self.status = "Missing server email configuration, could not submit your message."

            # Create the email message
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = receiver_email
            msg['Subject'] = f"New Contact Form Submission from {self.name}"

            body = f"""
            <b>Name:</b> {self.name}<br>
            <b>Email:</b> {self.email}<br>
            <b>Message:</b> {self.message}
            """
            msg.attach(MIMEText(body, 'html'))

            # Connect to Gmail SMTP server
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(sender_email, smtp_password)
                server.send_message(msg)
            
            self.status = "Your message has been sent successfully!"
            self.reset_form()
        except Exception as e:
            self.status = f"Failed to send your message: {str(e)}"
            self.reset_form()
    
    def reset_form(self):
        """Reset the form fields and status."""
        self.name = ""
        self.email = ""
        self.message = ""

    def handle_submit(self):
        """Handle form submission with basic validation."""

        if not self.name or not self.email or not self.message:
            self.status = "All fields are required!"
            return
        
        # Simple email validation
        email_regex = r"[^@]+@[^@]+\.[^@]+"
        if not re.match(email_regex, self.email):
            self.status = "Please enter a valid email address!"
            return
        
        # Simple message validation (e.g., too short or generic)
        if len(self.message) < 10:
            self.status = "Your message is too short! Please provide more details."
            return
        
        self.send_email()
    
    def scroll_to_top(self):
        """Scroll to the top of the page."""
        return rx.call_script("window.scrollTo({top: 0, behavior: 'smooth'})")

hover_animation: dict = {
    "transition": "transform 0.3s ease",
    "_hover": {
        "transform": "scale(1.05)",
    },
}

dots: dict = {
   "@keyframes dots": {
       "0%": {"background_position":"0 0"},
       "100%": {"background_position": "40px 40px"},
   },
   "animation": "dots 4s linear infinite alternate-reverse both",
    "background": "radial-gradient(circle, rgba(128,128,128,0.3) 1px, transparent 1px)",
    "background_size": "25px 25px",
}

wave: dict = {
   "@keyframes wave": {
       "0%": {"transform":"rotate(45deg)"},
       "100%": {"transform":"rotate(-15deg)"},
   },
   "animation": "wave 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94) infinite alternate-reverse both",
}
cursor_blink: dict = {
    "@keyframes blink": {
        "0%": {"opacity": "0"},
        "50%": {"opacity": "1"},
        "100%": {"opacity": "0"},
    },
    "animation": "blink 1s step-end infinite",
}

css: dict = {
    "app": {
        "dark": {"bg": "#15171b", "color": "white"},
        "light": {"bg": "white", "color": "black"},
    },
    "header":{
        "width": "100%",
        "height": "50px",
        "padding":[
            "0rem 1rem", 
            "0rem 1rem", 
            "0rem 1rem", 
            "0rem 8rem", 
            "0rem 8rem",
            ],
        "transition": "all 550ms ease",
    },
    "main":{
        "property": {
            "width":"100%",
            "minHeight":"84vh",
            "padding":"15rem 0rem",
            "align_items": "center",
            "justify_content":"start",
        }
    },
    "footer":{
        "width":"100%",
        "height": "50px",
        "align_items": "center",
        "justify_content": "center",
    }
}

# Dark Mode Toggle Component
def dark_mode_toggle() -> rx.Component:
    return rx.segmented_control.root(
        rx.segmented_control.item(
            rx.icon(tag="sun", size=15),
            value="light",
        ),
        rx.segmented_control.item(
            rx.icon(tag="moon", size=15),
            value="dark",
        ),
        on_change=set_color_mode,
        variant="classic",
        radius="large",
        spacing="2",
        value=color_mode,
    )

def scroll_to_top_component() -> rx.Component:
    return rx.box(
        rx.button(
            "↑", 
            on_click=State.scroll_to_top,
            position="fixed",
            bottom="2rem",
            right="2rem",
            padding="0.5rem",
            font_size="1.5rem",
            border_radius="50%", 
            background="rgba(0, 0, 0, 0.6)",
            color="white",  
            box_shadow="0 2px 10px rgba(0, 0, 0, 0.2)",
            transition="background 0.3s ease",
            _hover={"background": "rgba(0, 0, 0, 0.8)"},
            _active={"background": "rgba(0, 0, 0, 0.9)"},
        )
    )

# header class
class Header:
    def __init__(self) -> None:
        self.header: rx.Hstack = rx.hstack(style=css.get("header"), position="sticky", top="0", z_index="1000", margin_top="0.5rem")
        self.theme: rx.Component = rx.box(dark_mode_toggle())

    def compile_component(self):
        return[rx.spacer(), self.theme]
    
    def build(self):
         self.header.children = self.compile_component()
         return self.header

# main content area
class Main:
    def __init__(self) -> None:
        self.box: rx.Box = rx.box(width="100%")

        # Header Section
        self.name: rx.Hstack = rx.hstack(
            rx.heading(
                "Hi, I'm Lewis",
                font_size=["2rem", "2.85rem", "4rem", "5rem", "5rem"],
                font_weight="900",
                style={
                    "background": "linear-gradient(to right, rgba(169, 169, 169, 0.8), rgba(105, 105, 105, 0.8))",
                    "background_clip": "text",
                    "-webkit-background-clip": "text",
                    "-moz-background-clip": "text",  
                    "color": "transparent",
                    "display": "inline-block",  
                    "white_space": "nowrap", 
                    "line_height": "1.2", 
                    "padding": "0.2em 0", 
                    "vertical_align": "middle",
                },
            ),
            rx.heading(
                "👋🏻",
                font_size="2rem",
                font_weight="900",
                vertical_align="middle",
                style=wave,
            ),
            spacing="2",
            align_items="center",  # Ensure both headings are aligned vertically
        )

        # Badges Section
        titles = ["Cloud Security Engineer", "Security Engineer", "Systems Admin"]
        self.badge_stack_max = rx.hstack(*[self.create_badge(title) for title in titles], spacing="3")
        self.badge_stack_min = rx.hstack(*[self.create_badge(title) for title in titles], spacing="1")

        # Sections
        self.crumbs = self.create_custom_breadcrumb()
        self.whoami = self.create_whoami_section()
        self.skills_section = self.create_skills_section()
        self.contact: rx.Component = self.create_contact_form()
        self.cloud_security_section = self.create_cloud_security_section()

        self.scroll_to_top_button = scroll_to_top_component()
    
    def create_badge(self, title: str) -> rx.Component:
        return rx.badge(
            title,
            variant="solid",
            padding=["0.15rem 0.35rem", "0.15rem 0.35rem", "0.15rem 1rem", "0.15rem 1rem", "0.15rem 1rem"],
        )

    def create_skills_section(self) -> rx.Component:
        skills = [
            {"name": "Python", "icon": "🐍"},
            {"name": "PowerShell", "icon": "💻"},
            {"name": "AWS/Azure", "icon": "☁️"},
            {"name": "CloudFormation", "icon": "🛠️"},
        ]
        skill_items = [
            rx.vstack(
                rx.text(skill["icon"], font_size="36px", dark={"color": "rgba(255,255,255,0.7)"}),
                rx.text(skill["name"], font_size="14px", dark={"color": "rgba(255,255,255,0.7)"}, text_align="center"),
                spacing="2",
                align_items="center"
            )
            for skill in skills
        ]
        return rx.hstack(*skill_items, spacing="4", justify_content="center", align_items="center")

    def create_contact_form(self) -> rx.Component:
        return rx.box(
            rx.vstack(
            rx.heading(
                "Contact",
                font_size=["1.5rem", "2rem", "2rem"],
                font_weight="600",
                font_family="monospace",
                color="rgba(0, 255, 0, 0.8)",
                margin_bottom="0.5rem",
                text_align="center",
            ),
            rx.input(placeholder="Name", value=State.name, on_change=State.set_name, width=["90%", "80%", "80%"], spacing="2"),
            rx.input(placeholder="Email", type="email", value=State.email, on_change=State.set_email, width=["90%", "80%", "80%"], spacing="2"),
            rx.text_area(placeholder="Message", value=State.message, on_change=State.set_message, width=["90%", "80%", "80%"], spacing="2"),
            rx.button("Send", on_click=State.handle_submit, color_scheme="blue", width=["90%", "80%", "80%"], spacing="2"),
            rx.cond(
                State.status.contains("successfully"),
                rx.text(
                State.status,
                color="green",
                margin_top="1rem",
                ),
                rx.text(
                State.status,
                color="red",
                margin_top="1rem",
                )
            ),
                align_items="center",
                justify_content="center",
            ),
            spacing="6",
            align_items="center",
            justify_content="center",
            padding="5",
            margin_top="20rem",
            width="100%",
            max_width="600px",
        )

    def create_whoami_section(self) -> rx.Component:
        return rx.vstack(
            rx.box(
                rx.hstack(
                    rx.heading(
                        "whoami",
                        font_size="2rem",
                        font_weight="700",
                        font_family="monospace",
                        color="rgba(0, 255, 0, 0.8)",
                    ),
                    rx.text(
                        "_",
                        font_size="2rem",
                        font_weight="700",
                        font_family="monospace",
                        color="rgba(0, 255, 0, 0.8)",
                        style={**cursor_blink, "position": "relative", "top": "-11px"},  # Adjust position
                    ),
                    spacing="1",
                ),
                background="black",
                padding="1rem",
                border_radius="5px",
                box_shadow="0 0 10px rgba(0, 255, 0, 0.3)",
                style={"animation": "fadeIn 2s ease-out"},
                height="4rem",
            ),
            rx.text(
                "I am a Cloud Security Engineer specialising in securing and automating infrastructure. "
                "I work with various cloud platforms to design, implement, and manage security measures "
                "that ensure the confidentiality, integrity, and availability of various environments.",
                font_size="1rem",
                dark={"color": "rgba(255, 255, 255, 0.7)"},
                line_height="1.5",
                spacing="3",
                text_align="center",
                width="80%",
            ),
            spacing="6",
            align_items="center",
            justify_content="center",
            padding="6",
            margin_top="20rem",
        )

    def create_custom_breadcrumb(self) -> rx.Component:
        data = [
            ["github", "GitHub", "https://github.com/lewismcd1"],
            ["linkedin", "LinkedIn", "https://www.linkedin.com/in/lewis-mcdonald-6083b3153"],
        ]
        breadcrumb_items = []

        for i, (icon_name, title, url) in enumerate(data):
            breadcrumb_items.append(
                rx.link(
                    rx.vstack(
                        rx.icon(tag=icon_name, box_size="24px", dark={"color": "rgba(255,255,255,0.7)"}),
                        rx.text(title, font_size="12px", dark={"color": "rgba(255,255,255,0)"}, text_align="center"),
                        spacing="2",
                        align_items="center"
                    ),
                    href=url,
                    target="_blank",
                    style={"textDecoration": "none"},
                )
            )
            if i < len(data) - 1:
                breadcrumb_items.append(rx.text("", margin="0 8px", dark={"color": "rgba(255,255,255,0)"}))

        return rx.hstack(
            *breadcrumb_items,
            align_items="center",
            justify_content="start",
            spacing="2",
        )
    
    def create_cloud_security_section(self) -> rx.Component:
        projects = [
            {
                "title": "AWS Security Architecture",
                "description": "Implemented a multi-layer security architecture for a large-scale AWS deployment.",
                "image": "https://media.licdn.com/dms/image/D4D12AQG49qCkkRk6aw/article-cover_image-shrink_720_1280/0/1691813758023?e=2147483647&v=beta&t=P-f10sxwCtfIc0lWnyFTf9z_7Z14jtsT8K2XcXx1DxQ",  # Replace with actual image URL
            },
            {
                "title": "Automated Firewall Policy Checks",
                "description": "Developed automated security compliance checks using ServiceNow API, Lambda and various other aws services.",
                "image": "https://www.eqs.com/assets/2021/03/EQS-Blog_Compliance-Management.jpg",  # Replace with actual image URL
            },
            {
                "title": "Cyberark PAM Implementation",
                "description": "Designed and deployed a secure CyberArk PAM environment. This was fully automated within AWS.",
                "image": "https://mms.businesswire.com/media/20241113416461/en/1950794/23/CyberArk_Logo_November_2023.jpg",  # Replace with actual image URL
            },
        ]

        project_cards = [
            rx.box(
                rx.image(src=project["image"], alt=project["title"], width="100%", height="auto", style=hover_animation),
                rx.box(
                    rx.heading(project["title"], size="5"),
                    rx.text(project["description"]),
                    padding="1rem",
                ),
                width="300px",
                margin="1rem",
                box_shadow="0 4px 8px rgba(0, 0, 0, 0.2)",
                border_radius="10px",
                overflow="hidden",
            )
            for project in projects
        ]

        return rx.box(
            rx.heading(
                "Certifications",
                font_size="2rem",
                font_weight="600",
                font_family="monospace",
                color="rgba(0, 255, 0, 0.8)",
                margin_bottom="0.5rem",
                text_align="center",
            ),
            rx.vstack(
                rx.hstack(
                    rx.icon(tag="shield", box_size="24px", color="rgba(0, 255, 0, 0.8)"),
                    rx.text("AWS Certified Security – Specialty (In Progress)"),
                    spacing="2",
                    align_items="center",
                ),
                rx.hstack(
                    rx.icon(tag="cloud", box_size="24px", color="rgba(0, 255, 0, 0.8)"),
                    rx.text("AWS SysOps Administrator Associate (To be renewed)"),
                    spacing="2",
                    align_items="center",
                ),
                rx.hstack(
                    rx.icon(tag="award", box_size="24px", color="rgba(0, 255, 0, 0.8)"),
                    rx.text("CCNA Routing & Switching (To be renewed)"),
                    spacing="2",
                    align_items="center",
                ),
                align_items="center",
                justify_content="center",
                spacing="2",
                dark={"color": "rgba(255, 255, 255, 0.7)"},
                margin_top="2rem",
                margin_bottom="4rem",
            ),
            rx.heading(
                "Projects",
                font_size="2rem",
                font_weight="600",
                font_family="monospace",
                color="rgba(0, 255, 0, 0.8)",
                margin_top="1rem",
                margin_bottom="0.5rem",
                text_align="center",
            ),
            rx.hstack(
                *project_cards,
                spacing="2",
                justify_content="center",
                align_items="center",
                wrap="wrap",
            ),
            spacing="6",
            align_items="center",
            justify_content="center",
            padding="6",
            margin_top="20rem",
        )

    def compile_desktop_component(self):
        return rx.tablet_and_desktop(
            rx.vstack(
                self.name,
                self.badge_stack_max,
                self.crumbs,
                self.whoami,
                self.skills_section,
                self.cloud_security_section,
                self.contact,
                self.scroll_to_top_button,
                style=css.get("main").get("property"),
                spacing="7",
                flex="1",
            )
        )
    
    def compile_mobile_component(self):
        return rx.mobile_only(
            rx.vstack(
                self.name,
                self.badge_stack_min,
                self.crumbs,
                self.whoami,
                self.skills_section,
                self.cloud_security_section,
                self.contact,
                self.scroll_to_top_button,
                style=css.get("main").get("property"),
            )
        )
    
    def build(self):
        self.box.children = [self.compile_desktop_component(), self.compile_mobile_component()]
        return self.box

# footer class
class Footer:
    def __init__(self) -> None:
        self.footer: rx.Hstack = rx.hstack(
            id="footer",
            style={**css.get("footer")},
        )
        self.footer.children.append(
            rx.text(
                "Copyright 2025 Lewis McDonald",
                font_size="10px",
                font_weight="semibold",
            )
        )
    
    def build(self):
        return self.footer


@rx.page(route="/", on_load=State.on_mount, title="Lewis McDonald")
def landing() -> rx.Component:
    header: object = Header().build()
    main: object = Main().build()
    footer: object = Footer().build()
    return rx.vstack(
        # Components
        header,
        main,
        footer,
        # Styles
        #background
        light={
            "background": "radial-gradient(circle, rgba(0,0,0,0.35) 1px, transparent 1px)",
            "background_size":"25px 25px",
            "animation": "dots 4s linear infinite alternate-reverse both",
        },
        dark={
            "background": "radial-gradient(circle, rgba(255,255,255,0.09) 1px, transparent 1px)",
            "background_size": "25px 25px",
            "animation": "dots 4s linear infinite alternate-reverse both",
        }, 
        style=dots,
    )

app = rx.App(style=css.get("app"))
app._compile()