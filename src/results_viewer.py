"""
Results display and management functionality for QR Generator Pro
Handles thumbnail generation, results display, and folder operations
"""

import os
import tkinter as tk
import customtkinter as ctk
from src.gui_config import GUIConfig


class ResultsViewer:
    """Manages the results display section with thumbnails and actions"""
    
    def __init__(self, parent_frame, parent_app):
        """
        Initialize the ResultsViewer
        
        Args:
            parent_frame: The parent frame to attach the results section to
            parent_app: Reference to the main application for accessing shared state
        """
        self.parent_frame = parent_frame
        self.parent_app = parent_app
        self.last_result_folder = None
        self.setup_ui()
    
    def setup_ui(self):
        """Create the results viewer UI components"""
        # Initialize fonts
        GUIConfig.init_fonts()
        
        # Main results frame
        self.results_frame = ctk.CTkFrame(self.parent_frame)
        self.results_frame.grid(row=7, column=0, sticky=GUIConfig.STICKY_EW, 
                               padx=GUIConfig.SECTION_PADX, pady=GUIConfig.SECTION_PADY)
        self.results_frame.grid_columnconfigure(0, weight=1)
        
        # Section title
        self.results_title = ctk.CTkLabel(
            self.results_frame,
            text="Generation Results:",
            font=GUIConfig.SECTION_FONT
        )
        self.results_title.grid(row=0, column=0, padx=GUIConfig.CONTENT_PADX, 
                               pady=(15, 10), sticky=GUIConfig.STICKY_W)
        
        # Results summary
        self.results_summary = ctk.CTkLabel(
            self.results_frame,
            text="No QR codes generated yet",
            font=GUIConfig.LABEL_FONT,
            text_color="gray"
        )
        self.results_summary.grid(row=1, column=0, padx=GUIConfig.CONTENT_PADX, 
                                 pady=5, sticky=GUIConfig.STICKY_W)
        
        # Scrollable frame for thumbnails
        self.thumbnails_frame = ctk.CTkScrollableFrame(
            self.results_frame,
            height=200,
            orientation="horizontal"
        )
        self.thumbnails_frame.grid(row=2, column=0, padx=GUIConfig.CONTENT_PADX, 
                                  pady=10, sticky=GUIConfig.STICKY_EW)
        
        # Action buttons
        buttons_frame = ctk.CTkFrame(self.results_frame)
        buttons_frame.grid(row=3, column=0, padx=GUIConfig.CONTENT_PADX, 
                          pady=(0, 15), sticky=GUIConfig.STICKY_EW)
        buttons_frame.grid_columnconfigure(0, weight=1)
        
        # Open folder button
        self.open_folder_btn = ctk.CTkButton(
            buttons_frame,
            text="Open Output Folder",
            width=150,
            command=self.open_output_folder,
            state="disabled"
        )
        self.open_folder_btn.grid(row=0, column=0, padx=10, pady=10, sticky=GUIConfig.STICKY_W)
        
        # Clear results button
        self.clear_results_btn = ctk.CTkButton(
            buttons_frame,
            text="Clear Results",
            width=120,
            command=self.clear_results,
            fg_color="gray",
            hover_color="darkgray",
            state="disabled"
        )
        self.clear_results_btn.grid(row=0, column=1, padx=10, pady=10, sticky=GUIConfig.STICKY_W)
        
        # Initially hide the results section
        self.results_frame.grid_remove()
    
    def display_generation_results(self, result_folder, file_count):
        """Display generation results with thumbnails"""
        try:
            # Show results section
            self.results_frame.grid()
            
            # Update summary
            self.results_summary.configure(
                text=f"Generated {file_count} QR code(s) in: {result_folder}",
                text_color="green"
            )
            
            # Clear existing thumbnails
            for widget in self.thumbnails_frame.winfo_children():
                widget.destroy()
            
            # Load thumbnails for PNG files only (SVG thumbnails are more complex)
            png_files = []
            if os.path.exists(result_folder):
                for file in os.listdir(result_folder):
                    if file.lower().endswith('.png'):
                        png_files.append(os.path.join(result_folder, file))
            
            # Display thumbnails (limit to first 10 for performance)
            for i, file_path in enumerate(png_files[:10]):
                self.create_thumbnail(file_path, i)
            
            # Enable buttons
            self.open_folder_btn.configure(state="normal")
            self.clear_results_btn.configure(state="normal")
            
            # Store result folder for opening
            self.last_result_folder = result_folder
            
        except Exception as e:
            self.results_summary.configure(
                text=f"Error displaying results: {str(e)}",
                text_color="red"
            )
    
    def create_thumbnail(self, file_path, index):
        """Create a thumbnail widget for a QR code file"""
        try:
            from PIL import Image, ImageTk
            
            # Create thumbnail frame
            thumb_frame = ctk.CTkFrame(self.thumbnails_frame, width=120, height=140)
            thumb_frame.grid(row=0, column=index, padx=5, pady=5)
            thumb_frame.grid_propagate(False)
            
            # Load and resize image
            image = Image.open(file_path)
            image.thumbnail((80, 80), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            
            # Image label
            image_label = tk.Label(
                thumb_frame, 
                image=photo,
                bg=thumb_frame.cget("fg_color")[1]
            )
            image_label.image = photo  # Keep reference
            image_label.pack(pady=(10, 5))
            
            # Filename label
            filename = os.path.basename(file_path)
            if len(filename) > 15:
                filename = filename[:12] + "..."
            
            name_label = ctk.CTkLabel(
                thumb_frame,
                text=filename,
                font=GUIConfig.TINY_FONT
            )
            name_label.pack(pady=(0, 5))
            
            # Click to open file
            def open_file():
                try:
                    import subprocess
                    import platform
                    
                    if platform.system() == "Darwin":  # macOS
                        subprocess.call(["open", file_path])
                    elif platform.system() == "Windows":
                        os.startfile(file_path)
                    else:  # Linux
                        subprocess.call(["xdg-open", file_path])
                except Exception:
                    pass
            
            image_label.bind("<Button-1>", lambda e: open_file())
            thumb_frame.bind("<Button-1>", lambda e: open_file())
            
        except ImportError:
            # Fallback if PIL is not available
            thumb_frame = ctk.CTkFrame(self.thumbnails_frame, width=120, height=140)
            thumb_frame.grid(row=0, column=index, padx=5, pady=5)
            
            ctk.CTkLabel(
                thumb_frame,
                text="📄\nQR Code",
                font=GUIConfig.LABEL_FONT
            ).pack(expand=True)
            
        except Exception as e:
            # Error creating thumbnail
            thumb_frame = ctk.CTkFrame(self.thumbnails_frame, width=120, height=140)
            thumb_frame.grid(row=0, column=index, padx=5, pady=5)
            
            ctk.CTkLabel(
                thumb_frame,
                text="❌\nError",
                font=GUIConfig.LABEL_FONT,
                text_color="red"
            ).pack(expand=True)
    
    def open_output_folder(self):
        """Open the output folder in file manager"""
        try:
            if hasattr(self, 'last_result_folder') and os.path.exists(self.last_result_folder):
                import subprocess
                import platform
                
                if platform.system() == "Darwin":  # macOS
                    subprocess.call(["open", self.last_result_folder])
                elif platform.system() == "Windows":
                    os.startfile(self.last_result_folder)
                else:  # Linux
                    subprocess.call(["xdg-open", self.last_result_folder])
            else:
                self.results_summary.configure(
                    text="Output folder no longer exists",
                    text_color="orange"
                )
        except Exception as e:
            self.results_summary.configure(
                text=f"Error opening folder: {str(e)}",
                text_color="red"
            )
    
    def clear_results(self):
        """Clear the results display"""
        try:
            # Clear thumbnails
            for widget in self.thumbnails_frame.winfo_children():
                widget.destroy()
            
            # Reset labels
            self.results_summary.configure(
                text="No QR codes generated yet",
                text_color="gray"
            )
            
            # Disable buttons
            self.open_folder_btn.configure(state="disabled")
            self.clear_results_btn.configure(state="disabled")
            
            # Hide results section
            self.results_frame.grid_remove()
            
        except Exception as e:
            self.results_summary.configure(
                text=f"Error clearing results: {str(e)}",
                text_color="red"
            )
    
    def hide_results(self):
        """Hide the results section"""
        self.results_frame.grid_remove()
    
    def show_results(self):
        """Show the results section"""
        self.results_frame.grid()