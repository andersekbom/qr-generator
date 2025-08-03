import qrcode
import qrcode.image.svg
import os
import xml.etree.ElementTree as ET

def generate_colored_qr_code_svg(data: str, file_name: str, qr_color: str = "#4CAF50", background_color: str = "white"):
    """
    Generates a QR code in SVG format with a specified foreground and background color,
    ensuring the fill attribute is correctly set in the SVG XML.

    Args:
        data (str): The data to encode in the QR code (e.g., a URL, text).
        file_name (str): The name of the SVG file to save (e.g., "my_qrcode.svg").
        qr_color (str): The hexadecimal color code for the QR code modules (e.g., "#FF0000" for red).
                        Defaults to a shade of green.
        background_color (str): The hexadecimal color code for the background of the QR code.
                                Defaults to white.
    """
    try:
        # Create a QRCode object
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
            image_factory=qrcode.image.svg.SvgPathImage # Use SvgPathImage for a single path
        )

        # Add data to the QR code
        qr.add_data(data)
        qr.make(fit=True)

        # Generate the SVG image. We'll initially let it generate with default coloring
        # or whatever fill_color might attempt, and then modify it.
        # The back_color is usually applied to the <rect> background element.
        img = qr.make_image(back_color=background_color)
        svg_string = img.to_string()

        # --- XML Manipulation to ensure correct fill color ---
        # Parse the SVG string
        # qrcode.image.svg.SvgPathImage generates an SVG with a <path> element
        # that contains the QR code modules. We need to find this path and set its fill.
        root = ET.fromstring(svg_string)

        # Find the main path element that represents the QR code modules.
        # This is typically the first <path> element in the SVG.
        # We need to handle namespaces for robust parsing.
        # Default namespace for SVG is "http://www.w3.org/2000/svg"
        namespace = "{http://www.w3.org/2000/svg}"
        path_element = root.find(f".//{namespace}path")

        if path_element is not None:
            # Set the fill attribute of the path element to the desired QR color
            path_element.set("fill", qr_color)
        else:
            print("Warning: Could not find the main path element in the SVG. QR code color might not be applied.")

        # If there's a background rectangle, ensure its fill is set too
        rect_element = root.find(f".//{namespace}rect")
        if rect_element is not None:
            rect_element.set("fill", background_color)

        # Serialize the modified XML tree back to a string
        # We need to ensure the SVG declaration is present and namespaces are handled correctly.
        # ET.tostring adds the XML declaration, but we might need to add the SVG namespace
        # if it's not automatically preserved or if we want to be explicit.
        # For simplicity, let's assume ET.tostring handles basic namespace preservation.
        modified_svg_string = ET.tostring(root, encoding='unicode', xml_declaration=True)

        # Save the modified SVG to a file
        with open(file_name, "w") as f: # Open in text mode for unicode string
            f.write(modified_svg_string)

        print(f"QR code '{file_name}' generated successfully with color {qr_color}!")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # --- Example Usage ---
    my_data = "https://www.google.com/search?q=custom+colored+qr+code+svg+python"
    output_file = "my_guaranteed_colored_qrcode.svg"
    custom_qr_color = "#E74C3C" # A vibrant red
    custom_bg_color = "#ECF0F1" # Light gray/off-white

    generate_colored_qr_code_svg(my_data, output_file, custom_qr_color, custom_bg_color)

    # You can open 'my_guaranteed_colored_qrcode.svg' in a web browser or SVG viewer
    # to confirm the color.
