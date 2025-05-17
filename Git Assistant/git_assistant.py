import os
import json
import pathlib
import traceback
from datetime import datetime
from git import Repo, GitCommandError, InvalidGitRepositoryError, NoSuchPathError
import customtkinter as ctk
from tkinter import filedialog, scrolledtext, messagebox
import threading
from typing import Optional, Dict, Any
import webbrowser

class CustomButton(ctk.CTkButton):
    """Custom button with hover effects and modern styling"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.configure(
            corner_radius=8,
            border_width=2,
            hover_color=("#164B60" if kwargs.get("fg_color") != "transparent" else "#2B4865")
        )

class ModernGitGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Window setup
        self.title("Modern Git Assistant")
        self.geometry("1300x800")
        self.minsize(1100, 700)
        
        # Color scheme
        self.colors = {
            'primary': "#164B60",
            'secondary': "#2B4865",
            'accent': "#4FC0D0",
            'bg_dark': "#1B2430",
            'bg_light': "#F5F5F5",
            'text_dark': "#333333",
            'text_light': "#FFFFFF",
            'success': "#4CAF50",
            'error': "#FF5252",
            'warning': "#FFA726"
        }
        
        # Initialize variables
        self.repo: Optional[Repo] = None
        self.max_log_entries = 100
        self.active_branch = None
        self.is_loading = False
        
        # Config setup
        self.setup_config()
        self.setup_theme()
        self.initialize_gui_elements()
        self.create_gui()
        
        # Restore last session
        if self.config.get('auto_load_last_session', True):
            self.restore_last_session()

        # Bind events
        self.bind_events()

    def setup_config(self):
        """Initialize configuration and session files"""
        self.config_path = os.path.join(str(pathlib.Path.home()), ".modern_git_assistant")
        self.config_file = os.path.join(self.config_path, "config.json")
        self.session_file = os.path.join(self.config_path, "session.json")
        os.makedirs(self.config_path, exist_ok=True)
        
        self.config = self.load_json_file(self.config_file, default={
            'theme': 'dark',
            'auto_load_last_session': True,
            'max_log_entries': 100,
            'font_size': 12
        })
        self.session = self.load_json_file(self.session_file, default={})

    def setup_theme(self):
        """Set up application theme"""
        self.current_theme = self.config.get('theme', 'dark')
        ctk.set_appearance_mode(self.current_theme)
        ctk.set_default_color_theme("blue")

    def create_gui(self):
        """Create the main GUI layout"""
        try:
            # Main container
            self.main_container = ctk.CTkFrame(self)
            self.main_container.pack(fill="both", expand=True, padx=15, pady=15)

            # Create header with logo
            self.create_header()
            
            # Create main content
            self.create_main_content()
            
            # Create footer
            self.create_footer()

        except Exception as e:
            self.show_error(f"Error creating GUI: {str(e)}")
            traceback.print_exc()

    def create_header(self):
        """Create application header with logo and controls"""
        header = ctk.CTkFrame(self.main_container, corner_radius=10)
        header.pack(fill="x", pady=(0, 10))

        # Logo and title
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(side="left", padx=10)

        title = ctk.CTkLabel(
            title_frame,
            text="Modern Git Assistant",
            font=("Helvetica", 20, "bold"),
            text_color=self.colors['accent']
        )
        title.pack(side="left", padx=10)

        # Controls frame
        controls = ctk.CTkFrame(header, fg_color="transparent")
        controls.pack(side="right", padx=10)

        # Theme toggle
        self.theme_switch = ctk.CTkSwitch(
            controls,
            text="Dark Mode",
            command=self.toggle_theme,
            onvalue="dark",
            offvalue="light",
            button_color=self.colors['accent'],
            button_hover_color=self.colors['primary']
        )
        self.theme_switch.pack(side="right", padx=10)
        if self.current_theme == "dark":
            self.theme_switch.select()

        # Auto-load toggle
        self.auto_load_var = ctk.BooleanVar(value=self.config.get('auto_load_last_session', True))
        auto_load_cb = ctk.CTkCheckBox(
            controls,
            text="Auto-load session",
            variable=self.auto_load_var,
            command=self.toggle_auto_load,
            fg_color=self.colors['accent'],  # Changed from checkbox_color to fg_color
            hover_color=self.colors['primary']
        )
        auto_load_cb.pack(side="right", padx=10)

    def create_main_content(self):
        """Create main content area with repository and commit sections"""
        content = ctk.CTkFrame(self.main_container, corner_radius=10)
        content.pack(fill="both", expand=True, pady=10)

        # Left panel - Repository controls and commit section
        left_panel = ctk.CTkFrame(content, corner_radius=10)
        left_panel.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        self.create_repository_section(left_panel)
        self.create_commit_section(left_panel)

        # Right panel - Log section
        right_panel = ctk.CTkFrame(content, corner_radius=10)
        right_panel.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.create_log_section(right_panel)

    def create_repository_section(self, parent):
        """Create repository controls section"""
        repo_frame = ctk.CTkFrame(parent, corner_radius=10)
        repo_frame.pack(fill="x", pady=(0, 10))

        # Title
        title = ctk.CTkLabel(
            repo_frame,
            text="Repository",
            font=("Helvetica", 16, "bold"),
            text_color=self.colors['accent']
        )
        title.pack(pady=10)

        # Repository controls
        controls = ctk.CTkFrame(repo_frame, fg_color="transparent")
        controls.pack(fill="x", padx=10, pady=5)

        buttons = [
            ("Open Repository", self.open_repo, self.colors['primary']),
            ("Init Repository", self.init_repo, self.colors['secondary']),
            ("Refresh", self.refresh_repo, self.colors['accent'])
        ]

        for text, command, color in buttons:
            CustomButton(
                controls,
                text=text,
                command=command,
                font=("Helvetica", 12, "bold"),
                height=35,
                fg_color=color
            ).pack(side="left", padx=5, expand=True, fill="x")

        # Branch info
        self.branch_label = ctk.CTkLabel(
            repo_frame,
            text="Branch: -",
            font=("Helvetica", 12)
        )
        self.branch_label.pack(fill="x", padx=10, pady=10)

        # Status label
        self.status_label = ctk.CTkLabel(
            repo_frame,
            text="Status: Not initialized",
            font=("Helvetica", 12)
        )
        self.status_label.pack(fill="x", padx=10, pady=(0, 10))

    def create_commit_section(self, parent):
        """Create commit section with message input and operations"""
        commit_frame = ctk.CTkFrame(parent, corner_radius=10)
        commit_frame.pack(fill="both", expand=True, pady=10)

        # Title
        title = ctk.CTkLabel(
            commit_frame,
            text="Commit Operations",
            font=("Helvetica", 16, "bold"),
            text_color=self.colors['accent']
        )
        title.pack(pady=10)

        # Commit message
        msg_label = ctk.CTkLabel(
            commit_frame,
            text="Commit Message:",
            font=("Helvetica", 12, "bold")
        )
        msg_label.pack(padx=10, pady=(10, 5), anchor="w")

        self.commit_input = ctk.CTkTextbox(
            commit_frame,
            height=100,
            font=("Helvetica", 12)
        )
        self.commit_input.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Git operations
        self.create_git_buttons(commit_frame)

    def create_git_buttons(self, parent):
        """Create buttons for git operations"""
        # Main operations
        main_ops = ctk.CTkFrame(parent, fg_color="transparent")
        main_ops.pack(fill="x", padx=10, pady=5)

        operations = [
            ("Commit", self.make_commit, self.colors['success']),
            ("Push", lambda: self.git_command("push"), self.colors['primary']),
            ("Pull", lambda: self.git_command("pull"), self.colors['secondary']),
            ("Fetch", lambda: self.git_command("fetch"), self.colors['accent'])
        ]

        for text, command, color in operations:
            CustomButton(
                main_ops,
                text=text,
                command=command,
                font=("Helvetica", 12, "bold"),
                height=35,
                fg_color=color
            ).pack(side="left", padx=2, expand=True, fill="x")

        # Stash operations
        stash_frame = ctk.CTkFrame(parent, fg_color="transparent")
        stash_frame.pack(fill="x", padx=10, pady=5)

        stash_ops = [
            ("Stash Changes", self.stash_changes),
            ("Apply Stash", self.apply_stash),
            ("Pop Stash", self.pop_stash)
        ]

        for text, command in stash_ops:
            CustomButton(
                stash_frame,
                text=text,
                command=command,
                font=("Helvetica", 12),
                height=35,
                fg_color=self.colors['secondary']
            ).pack(side="left", padx=2, expand=True, fill="x")

    def create_log_section(self, parent):
        """Create commit history log section"""
        log_frame = ctk.CTkFrame(parent, corner_radius=10)
        log_frame.pack(fill="both", expand=True)

        # Header with refresh button
        header = ctk.CTkFrame(log_frame, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=10)

        title = ctk.CTkLabel(
            header,
            text="Commit History",
            font=("Helvetica", 16, "bold"),
            text_color=self.colors['accent']
        )
        title.pack(side="left")

        CustomButton(
            header,
            text="Refresh Log",
            command=self.update_log,
            width=100,
            height=30,
            fg_color=self.colors['accent']
        ).pack(side="right")

        # Log area
        self.log_area = scrolledtext.ScrolledText(
            log_frame,
            wrap='word',
            font=('Courier', 10),
            bg=self.colors['bg_dark'] if self.current_theme == 'dark' else self.colors['bg_light'],
            fg=self.colors['text_light'] if self.current_theme == 'dark' else self.colors['text_dark']
        )
        self.log_area.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def create_footer(self):
        """Create application footer"""
        footer = ctk.CTkFrame(self.main_container, corner_radius=10, height=40)
        footer.pack(fill="x", pady=(10, 0))

        # Version
        version = ctk.CTkLabel(
            footer,
            text="v2.0.0",
            font=("Helvetica", 10)
        )
        version.pack(side="left", padx=10)

        # Credits
        credits = CustomButton(
            footer,
            text="Made by robbiee09",
            command=lambda: webbrowser.open('https://github.com/robbiee09'),
            font=("Helvetica", 10, "bold"),
            fg_color="transparent",
            hover_color=self.colors['secondary']
        )
        credits.pack(side="right", padx=10)

        # Add any additional footer content here

    # [Rest of the methods remain the same as in the previous version]

    def initialize_gui_elements(self):
        """Initialize GUI elements"""
        # Frames and labels initialization
        pass  # Removed to declutter and as there's no direct initialization here

    def bind_events(self):
        """Bind keyboard shortcuts"""
        self.bind("<Control-r>", lambda event: self.refresh_repo())
        self.bind("<Control-l>", lambda event: self.update_log())
        self.bind("<Control-o>", lambda event: self.open_repo())

    def load_json_file(self, file_path: str, default: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Load JSON data from a file"""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return default or {}

    def save_json_file(self, file_path: str, data: Dict[str, Any]):
        """Save JSON data to a file"""
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            self.show_error(f"Error saving file: {str(e)}")

    def open_repo(self):
        """Open an existing Git repository"""
        path = filedialog.askdirectory(title="Select Git Repository")
        if path:
            self.load_repository(path)

    def load_repository(self, path: str):
        """Load repository and update UI"""
        try:
            self.start_loading("Loading repository...")
            self.repo = Repo(path)
            self.update_all()
            self.session['last_repo'] = path
            self.save_session()
            self.show_success("Repository loaded successfully.")
        except InvalidGitRepositoryError:
            self.show_error("Invalid Git repository!")
        except NoSuchPathError:
            self.show_error("No such path exists!")
        except Exception as e:
            self.show_error(f"Error opening repository: {str(e)}")
            traceback.print_exc()
        finally:
            self.stop_loading()

    def init_repo(self):
        """Initialize a new Git repository"""
        path = filedialog.askdirectory(title="Initialize Git Repository")
        if path:
            try:
                self.start_loading("Initializing repository...")
                self.repo = Repo.init(path)
                self.update_all()
                self.session['last_repo'] = path
                self.save_session()
                self.show_success("Repository initialized successfully.")
            except Exception as e:
                self.show_error(f"Init error: {str(e)}")
                traceback.print_exc()
            finally:
                self.stop_loading()

    def make_commit(self):
        """Create a new commit"""
        if not self.repo:
            self.show_error("No repository opened")
            return
            
        msg = self.commit_input.get("1.0", "end-1c").strip()
        if not msg:
            self.show_error("Empty commit message.")
            return
            
        try:
            self.start_loading("Committing changes...")
            self.repo.git.add(A=True)
            self.repo.index.commit(msg)
            self.commit_input.delete("1.0", "end")
            self.update_all()
            self.show_success("Committed successfully.")
        except GitCommandError as e:
            self.show_error(f"Commit error: {str(e)}")
            traceback.print_exc()
        finally:
            self.stop_loading()

    def git_command(self, command: str):
        """Execute a Git command in a separate thread"""
        if not self.repo:
            self.show_error("No repository opened")
            return
            
        def execute():
            try:
                self.start_loading(f"Executing {command}...")
                remote = self.repo.remote()
                getattr(remote, command)()
                self.update_all()
                self.show_success(f"{command.capitalize()} successful.")
            except Exception as e:
                self.show_error(f"{command} error: {str(e)}")
                traceback.print_exc()
            finally:
                self.stop_loading()
        
        thread = threading.Thread(target=execute)
        thread.start()

    def stash_changes(self):
        """Stash uncommitted changes"""
        if not self.repo:
            self.show_error("No repository opened")
            return
            
        try:
            self.start_loading("Stashing changes...")
            self.repo.git.stash()
            self.show_success("Changes stashed successfully.")
            self.update_all()
        except GitCommandError as e:
            self.show_error(f"Stash error: {str(e)}")
            traceback.print_exc()
        finally:
            self.stop_loading()

    def apply_stash(self):
        """Apply the most recent stash"""
        if not self.repo:
            self.show_error("No repository opened")
            return
            
        try:
            self.start_loading("Applying stash...")
            self.repo.git.stash("apply")
            self.show_success("Stash applied successfully.")
            self.update_all()
        except GitCommandError as e:
            self.show_error(f"Apply stash error: {str(e)}")
            traceback.print_exc()
        finally:
            self.stop_loading()

    def pop_stash(self):
        """Pop the most recent stash"""
        if not self.repo:
            self.show_error("No repository opened")
            return
            
        try:
            self.start_loading("Popping stash...")
            self.repo.git.stash("pop")
            self.show_success("Stash popped successfully.")
            self.update_all()
        except GitCommandError as e:
            self.show_error(f"Pop stash error: {str(e)}")
            traceback.print_exc()
        finally:
            self.stop_loading()

    def refresh_repo(self):
        """Refresh the repository status"""
        if self.repo:
            self.update_all()
            self.show_success("Repository refreshed.")
        else:
            self.show_error("No repository opened")

    def update_all(self):
        """Update all UI elements with current repository status"""
        if not self.repo:
            self.branch_label.configure(text="Branch: -")
            self.status_label.configure(text="Status: Not initialized")
            return
            
        try:
            self.active_branch = self.repo.active_branch.name
            self.branch_label.configure(text=f"Branch: {self.active_branch}")
            status = "Dirty" if self.repo.is_dirty() else "Clean"
            self.status_label.configure(text=f"Status: {status}")
            self.update_log()
            self.save_session()
        except Exception as e:
            self.show_error(f"Update error: {str(e)}")
            traceback.print_exc()

    def update_log(self):
        """Update the commit history log"""
        if not self.repo:
            self.log_area.delete("1.0", "end")
            return
            
        try:
            self.log_area.delete("1.0", "end")
            for commit in list(self.repo.iter_commits())[:self.config.get('max_log_entries', 100)]:
                commit_date = datetime.fromtimestamp(commit.committed_date)
                log_entry = (f"{commit.hexsha[:7]} | {commit.author.name} | "
                           f"{commit_date.strftime('%Y-%m-%d %H:%M')}\n"
                           f"  {commit.message}\n\n")
                self.log_area.insert("end", log_entry)
        except Exception as e:
            self.show_error(f"Error updating log: {str(e)}")
            traceback.print_exc()

    def show_error(self, message: str):
        """Display an error message"""
        messagebox.showerror("Error", message)
        self.status_label.configure(text=f"Error: {message}", text_color=self.colors['error'])

    def show_success(self, message: str):
        """Display a success message"""
        messagebox.showinfo("Success", message)
        self.status_label.configure(text=message, text_color=self.colors['success'])

    def start_loading(self, message: str = "Loading..."):
        """Start loading indicator"""
        self.is_loading = True
        self.status_label.configure(text=message, text_color=self.colors['warning'])
        self.update()

    def stop_loading(self):
        """Stop loading indicator"""
        self.is_loading = False
        self.update_all()
        self.update()

    def save_session(self):
        """Save current session information"""
        if self.repo:
            self.session['last_repo'] = self.repo.working_tree_dir
            self.session['last_branch'] = self.active_branch

        self.save_json_file(self.session_file, self.session)

    def restore_last_session(self):
        """Restore the last session"""
        last_repo = self.session.get('last_repo')
        last_branch = self.session.get('last_branch')
        
        if last_repo and os.path.exists(last_repo):
            try:
                self.start_loading("Restoring last session...")
                self.repo = Repo(last_repo)
                if last_branch and last_branch in self.repo.heads:
                    self.repo.git.checkout(last_branch)
                self.update_all()
                self.show_success("Last session restored.")
            except Exception as e:
                self.show_error(f"Failed to restore last session: {str(e)}")
                traceback.print_exc()
            finally:
                self.stop_loading()
        else:
            self.show_error("No previous session found.")

    def toggle_theme(self):
        """Toggle between dark and light themes"""
        new_theme = "light" if self.theme_switch.get() == "dark" else "dark"
        self.config['theme'] = new_theme
        self.current_theme = new_theme
        ctk.set_appearance_mode(new_theme)
        self.log_area.configure(
            bg=self.colors['bg_dark'] if new_theme == 'dark' else self.colors['bg_light'],
            fg=self.colors['text_light'] if new_theme == 'dark' else self.colors['text_dark']
        )
        self.save_config()

    def toggle_auto_load(self):
        """Toggle auto-load session"""
        self.config['auto_load_last_session'] = self.auto_load_var.get()
        self.save_config()

    def save_config(self):
        """Save the configuration settings"""
        self.save_json_file(self.config_file, self.config)

def main():
    try:
        app = ModernGitGUI()
        app.mainloop()
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    main()