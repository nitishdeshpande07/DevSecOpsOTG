import sys
import pyfiglet

def animated_text(text, delay=0.01):
    """Display text one character at a time with a minimal delay."""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()

def display_cli_opening():
    """Displays an animated opening for the CLI tool."""
    
    # Create the large ASCII art for the title using a clear and readable font
    title = pyfiglet.figlet_format("DevSecOps \n On the Go", font="big")  # 'big' font is clear and readable
    subtitle = "Hassle Free DevSecOps Provisioning"
    tagline = "  \n Shift Left Made Real!"

    # Display the large title with animation
    animated_text(title, delay=0.01)

    # Display subtitle with animation
    animated_text(subtitle, delay=0.01)
    
    # Display tagline with animation
    animated_text(tagline, delay=0.01)

# Example usage
if __name__ == "__main__":
    display_cli_opening()

